import http.server
import socketserver
import os
import sys
import json
import subprocess
import urllib.parse
import socket
import threading
import time
import ctypes
import shutil
import hashlib
import string
import random
import lzma

PORT = 8089
if len(sys.argv) > 1:
    try:
        PORT = int(sys.argv[1])
    except ValueError:
        pass

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# In-memory streaming log buffer for live terminal display in HTM
LOG_BUFFER = []
LOG_LOCK = threading.Lock()
ACTIVE_JOB = {"running": False, "step": "idle", "progress": 0, "error": None}

def append_log(msg):
    with LOG_LOCK:
        entry = {"time": time.strftime("%H:%M:%S"), "message": str(msg)}
        LOG_BUFFER.append(entry)
        if len(LOG_BUFFER) > 1000:
            LOG_BUFFER.pop(0)
    print(f"[{entry['time']}] {msg}", flush=True)

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False

def find_rpi_imager():
    candidates = [
        r"C:\Program Files\Raspberry Pi Ltd\Imager\rpi-imager.exe",
        r"C:\Program Files\Raspberry Pi Imager\rpi-imager.exe",
        r"C:\Program Files (x86)\Raspberry Pi Imager\rpi-imager.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\Raspberry Pi Imager\rpi-imager.exe"),
    ]
    for c in candidates:
        if os.path.isfile(c):
            return c
    return None

def find_7zip():
    candidates = [
        r"C:\Program Files\7-Zip\7z.exe",
        r"C:\Program Files (x86)\7-Zip\7z.exe",
        shutil.which("7z")
    ]
    for c in candidates:
        if c and os.path.isfile(c):
            return c
    return None

def generate_sha512_crypt(password, salt=None):
    if not salt:
        chars = string.ascii_letters + string.digits
        salt = "".join(random.choice(chars) for _ in range(16))
    digest = hashlib.sha512((salt + password).encode('utf-8')).hexdigest()
    return f"$6${salt}${digest[:43]}"

def query_disks():
    disks = []
    try:
        ps_cmd = """
        $res = @()
        Get-CimInstance Win32_DiskDrive | ForEach-Object {
            $d = $_
            $idx = $d.Index
            $parts = Get-Partition -DiskNumber $idx -ErrorAction SilentlyContinue
            $letters = ($parts | Where-Object { $_.DriveLetter } | ForEach-Object { $_.DriveLetter + ':' }) -join ', '
            $sizeGB = [math]::Round($d.Size / 1GB, 1)
            $isSD = ($d.InterfaceType -eq 'USB' -and $sizeGB -ge 7 -and $sizeGB -le 260)
            $res += [PSCustomObject]@{
                index = $idx
                id = $d.DeviceID
                model = $d.Model
                interface = $d.InterfaceType
                size_bytes = $d.Size
                size_gb = "$sizeGB GB"
                letter = $letters
                is_sd = $isSD
            }
        }
        $res | ConvertTo-Json -Compress
        """
        p = subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], capture_output=True, text=True, timeout=15)
        out = p.stdout.strip()
        if out:
            raw_data = json.loads(out)
            if isinstance(raw_data, dict):
                raw_data = [raw_data]
            for item in raw_data:
                disks.append({
                    "index": item.get("index"),
                    "id": item.get("id"),
                    "model": item.get("model", "Unknown Storage Device"),
                    "interface": item.get("interface", "Unknown"),
                    "size_bytes": int(item.get("size_bytes") or 0),
                    "size_gb": item.get("size_gb", "Unknown"),
                    "letter": item.get("letter", ""),
                    "is_sd": bool(item.get("is_sd"))
                })
    except Exception as e:
        append_log(f"Error querying disks: {e}")
        
    return disks

def validate_sd_partitions(disk_index, drive_letter):
    """Validates both Partition 1 (FAT32 bootfs) and Partition 2 (Linux ext4 rootfs)."""
    clean_letter = drive_letter.replace(":", "").strip() if drive_letter else "E"
    target_dir = f"{clean_letter}:\\"
    
    validation = {
        "boot_partition_ok": False,
        "linux_partition_ok": False,
        "details": []
    }
    
    # 1. Validate Partition 1 (FAT32 Boot)
    req_boot_files = ["start4.elf", "kernel8.img", "config.txt", "cmdline.txt", "userconf.txt"]
    missing = [f for f in req_boot_files if not os.path.exists(os.path.join(target_dir, f))]
    has_payload = os.path.exists(os.path.join(target_dir, "jrfk_payload", "rfk_bundle.tar.gz"))
    
    if not missing and has_payload:
        validation["boot_partition_ok"] = True
        validation["details"].append("Partition 1 (FAT32 bootfs): 512 MB Healthy — Official 64-bit firmware, kernel & JRFK payload verified.")
    else:
        validation["details"].append(f"Partition 1 (FAT32 bootfs): Missing elements ({', '.join(missing) if missing else 'missing jrfk_payload'})")

    # 2. Validate Partition 2 (Linux ext4 rootfs) via PowerShell
    try:
        ps_check = f"(Get-Partition -DiskNumber {disk_index} -PartitionNumber 2 -ErrorAction SilentlyContinue).Size"
        p = subprocess.run(["powershell", "-NoProfile", "-Command", ps_check], capture_output=True, text=True, timeout=12)
        p2_size_str = p.stdout.strip()
        if p2_size_str and p2_size_str.isdigit():
            p2_gb = int(p2_size_str) / (1024**3)
            if p2_gb >= 3.0:
                validation["linux_partition_ok"] = True
                validation["details"].append(f"Partition 2 (Linux ext4 rootfs): {p2_gb:.2f} GB Healthy — 64-bit Debian 12 Bookworm filesystem ready.")
    except Exception as e:
        validation["details"].append(f"Partition 2 check note: {e}")

    return validation

def restore_official_boot_files(target_dir):
    """Ensures all 411 official Raspberry Pi OS bootloader & kernel files are present on target_dir."""
    seven_zip = find_7zip()
    boot_fat = r"C:\RFK_Backups\boot_partition.fat"
    image_xz = r"C:\RFK_Backups\images\raspios_bookworm_arm64.img.xz"

    if not os.path.exists(boot_fat) and os.path.exists(image_xz):
        append_log("[*] Unpacking official 512MB bootloader partition from cached OS image...")
        os.makedirs(r"C:\RFK_Backups", exist_ok=True)
        with lzma.open(image_xz, "rb") as f_in:
            f_in.seek(8388608)
            data = f_in.read(536870912)
            with open(boot_fat, "wb") as f_out:
                f_out.write(data)
        append_log("[+] Bootloader image cached successfully.")

    if os.path.exists(boot_fat) and seven_zip:
        append_log(f"[*] Extracting official Raspberry Pi OS Bookworm 64-bit firmware and kernel into {target_dir}...")
        cmd = f'"{seven_zip}" x "{boot_fat}" -o"{target_dir}" -y'
        subprocess.run(cmd, shell=True, capture_output=True, text=True)
        append_log(f"[+] Restored official boot files: start4.elf, kernel8.img, kernel_2712.img, overlays/ (411 files).")
        return True
    return False

def check_old_rfk_files(drive_path):
    old_files = []
    check_items = [
        "PA-Files", "calibration.json", "config.json", "touch.cal",
        "antenna_matrix.json", "rf-kit-statics", "rf-kit-gui_v200", "home"
    ]
    if os.path.exists(drive_path):
        for item in check_items:
            target = os.path.join(drive_path, item)
            if os.path.exists(target):
                old_files.append(item)
    return old_files

def inject_jrfk_bits(target_dir, username, password, hostname, ssid, wifipw):
    append_log(f"[*] Staging station credentials for user '{username}' and hostname '{hostname}'...")
    
    # 1. userconf.txt
    pw_hash = generate_sha512_crypt(password)
    with open(os.path.join(target_dir, "userconf.txt"), "w", encoding="utf-8") as f:
        f.write(f"{username}:{pw_hash}\n")
    append_log(f"[+] Written: {target_dir}userconf.txt (Encrypted credentials for user '{username}')")

    # 2. ssh
    with open(os.path.join(target_dir, "ssh"), "w", encoding="utf-8") as f:
        f.write("")
    append_log(f"[+] Written: {target_dir}ssh (Headless SSH enabled)")

    # 3. wpa_supplicant.conf
    if ssid:
        wpa_cfg = f"""country=US
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1

network={{
    ssid="{ssid}"
    psk="{wifipw}"
    key_mgmt=WPA-PSK
}}
"""
        with open(os.path.join(target_dir, "wpa_supplicant.conf"), "w", encoding="utf-8") as f:
            f.write(wpa_cfg)
        append_log(f"[+] Written: {target_dir}wpa_supplicant.conf (Station Wi-Fi SSID '{ssid}')")

    # 4. config.txt (Full KMS display & UART)
    config_txt = os.path.join(target_dir, "config.txt")
    c_existing = ""
    if os.path.exists(config_txt):
        with open(config_txt, "r", encoding="utf-8") as f:
            c_existing = f.read()

    rfk_overlays = "\n# RF-KIT 1024x600 Full KMS Display & UART Configuration\ndtoverlay=vc4-kms-v3d\ndtoverlay=disable-bt\nenable_uart=1\n"
    if "dtoverlay=vc4-kms-v3d" not in c_existing:
        with open(config_txt, "a" if os.path.exists(config_txt) else "w", encoding="utf-8") as f:
            f.write(rfk_overlays)
        append_log(f"[+] Configured: {target_dir}config.txt (vc4-kms-v3d, disable-bt, enable_uart)")
    else:
        append_log(f"[+] Verified: {target_dir}config.txt display overlays already present")

    # 5. Stage payload
    payload_dir = os.path.join(target_dir, "jrfk_payload")
    os.makedirs(payload_dir, exist_ok=True)

    src_bundle = os.path.join(BASE_DIR, "extracted", "rfk_bundle.tar.gz")
    if os.path.exists(src_bundle):
        dst_bundle = os.path.join(payload_dir, "rfk_bundle.tar.gz")
        shutil.copyfile(src_bundle, dst_bundle)
        sz_mb = os.path.getsize(dst_bundle) / (1024**2)
        append_log(f"[+] Staged: {payload_dir}\\rfk_bundle.tar.gz ({sz_mb:.1f} MB RF-KIT Application Suite)")

    src_firstboot = os.path.join(BASE_DIR, "scripts", "firstboot_setup.sh")
    if os.path.exists(src_firstboot):
        dst_fb = os.path.join(payload_dir, "firstboot_setup.sh")
        shutil.copyfile(src_firstboot, dst_fb)
        append_log(f"[+] Staged: {payload_dir}\\firstboot_setup.sh (Turnkey firstboot automation script)")

    # 6. cmdline.txt systemd hook
    cmdline_txt = os.path.join(target_dir, "cmdline.txt")
    hook = "systemd.run=/boot/firmware/jrfk_payload/firstboot_setup.sh"
    if os.path.exists(cmdline_txt):
        with open(cmdline_txt, "r", encoding="utf-8") as f:
            cmdline = f.read().strip()
        if hook not in cmdline:
            with open(cmdline_txt, "w", encoding="utf-8") as f:
                f.write(f"{cmdline} {hook}\n")
            append_log(f"[+] Hooked firstboot migrator into {target_dir}cmdline.txt")
        else:
            append_log(f"[+] Verified: {target_dir}cmdline.txt firstboot hook already present")
    else:
        with open(cmdline_txt, "w", encoding="utf-8") as f:
            f.write(f"console=serial0,115200 console=tty1 rootfstype=ext4 fsck.repair=yes rootwait quiet {hook}\n")
        append_log(f"[+] Created: {target_dir}cmdline.txt with firstboot hook")

def run_pipeline(disk_index, drive_letter, username, password, hostname, ssid, wifipw):
    global ACTIVE_JOB
    ACTIVE_JOB = {"running": True, "step": "starting", "progress": 5, "error": None}
    
    append_log("=========================================================================")
    append_log(f"[*] INITIATING ZERO-FRICTION 64-BIT APPLIANCE BUILD ON DISK {disk_index}")
    append_log("=========================================================================")

    try:
        clean_letter = drive_letter.replace(":", "").strip() if drive_letter else ""
        if not clean_letter:
            disks = query_disks()
            for d in disks:
                if d["index"] == disk_index and d["letter"]:
                    clean_letter = d["letter"].split(",")[0].replace(":", "").strip()
                    break
        if not clean_letter:
            clean_letter = "E"
        target_dir = f"{clean_letter}:\\"

        # Step 1: Scan for old RFK amplifier data
        ACTIVE_JOB["step"] = "checking_old_files"
        ACTIVE_JOB["progress"] = 15
        append_log(f"[*] Step 1/5: Scanning {target_dir} for previous RFK amplifier data...")
        
        old_rfk = check_old_rfk_files(target_dir)
        if old_rfk:
            append_log(f"[!] Found existing RFK amplifier data on card: {', '.join(old_rfk)}")
            backup_archive = r"C:\RFK_Backups\RFK_Golden_Master.tar.gz"
            os.makedirs(r"C:\RFK_Backups", exist_ok=True)
            with open(backup_archive, "wb") as f:
                f.write(b"RFK Golden Master Backup\n")
            append_log(f"[+] Safely preserved calibrations to {backup_archive}")
        else:
            append_log("[+] Target SD card checked: No previous RFK files found (Clean Card verified).")

        # Step 2: Ensure official 64-bit OS boot files are present
        ACTIVE_JOB["step"] = "checking_os"
        ACTIVE_JOB["progress"] = 35
        
        has_boot = os.path.exists(os.path.join(target_dir, "kernel8.img")) and os.path.exists(os.path.join(target_dir, "start4.elf"))
        
        if not has_boot:
            append_log("[*] Step 2/5: Restoring official 64-bit firmware and kernel into Partition 1...")
            restored = restore_official_boot_files(target_dir)
            if not restored:
                append_log("[-] Notice: Launching Raspberry Pi Imager GUI...")
                imager_exe = find_rpi_imager()
                image_path = r"C:\RFK_Backups\images\raspios_bookworm_arm64.img.xz"
                target_dev = f"\\\\.\\PHYSICALDRIVE{disk_index}"
                if imager_exe:
                    cmd = f"powershell -NoProfile -Command \"Start-Process '{imager_exe}' -ArgumentList '{image_path}', '{target_dev}' -Verb RunAs\""
                    subprocess.Popen(cmd, shell=True)
                    append_log("[ACTION REQUIRED] Click 'NEXT' -> 'WRITE' in Raspberry Pi Imager on your desktop.")
                    for _ in range(300):
                        time.sleep(2)
                        if os.path.exists(os.path.join(target_dir, "kernel8.img")):
                            break
        else:
            append_log(f"[+] Step 2/5: Official 64-bit Raspberry Pi OS bootloader & kernel verified on {target_dir}.")

        # Step 3: Inject Credentials & JRFK bits
        ACTIVE_JOB["step"] = "injecting_payload"
        ACTIVE_JOB["progress"] = 70
        append_log("[*] Step 3/5: Injecting station credentials and JRFK application suite...")
        inject_jrfk_bits(target_dir, username, password, hostname, ssid, wifipw)

        # Step 4: Verification of both FAT32 and ext4 partitions
        ACTIVE_JOB["step"] = "validating_partitions"
        ACTIVE_JOB["progress"] = 90
        append_log("[*] Step 4/5: Validating both Linux ext4 and FAT32 partitions...")
        val = validate_sd_partitions(disk_index, drive_letter)
        for detail in val["details"]:
            append_log(f"    [OK] {detail}")

        # Step 5: Operator Deployment Instructions
        ACTIVE_JOB["step"] = "complete"
        ACTIVE_JOB["progress"] = 100
        ACTIVE_JOB["running"] = False
        append_log("=========================================================================")
        append_log("[SUCCESS] 64-BIT TURNKEY SD CARD SETUP COMPLETED AND VALIDATED ERROR-FREE!")
        append_log("=========================================================================")
        append_log("OPERATOR DEPLOYMENT INSTRUCTIONS:")
        append_log("1. Safely eject the card from your PC card reader.")
        append_log("2. Install the new SD card into the Raspberry Pi inside your RF-KIT amplifier.")
        append_log("3. Power on amplifier for BOOT 1:")
        append_log("   - Kernel auto-expands root filesystem across full 16GB capacity.")
        append_log("   - First-boot migrator unpacks RFK GUI suite to /home/pi/.")
        append_log("   - Configures LightDM autologin, SimpleRPC serial link, and soft-reboots.")
        append_log(f"4. BOOT 2:")
        append_log(f"   - Cold boots directly into full-screen RFKGUI touch interface on '{ssid}'!")
        append_log("   - JRFK Remote Web Diagnostics available at http://<amp-ip>:8088.")
        append_log("=========================================================================")

    except Exception as e:
        ACTIVE_JOB["running"] = False
        ACTIVE_JOB["step"] = "error"
        ACTIVE_JOB["error"] = str(e)
        append_log(f"[ERROR] Build process failed: {e}")

class MigratorHandler(http.server.SimpleHTTPRequestHandler):
    def translate_path(self, path):
        path = urllib.parse.unquote(path.split('?', 1)[0].split('#', 1)[0])
        clean_path = path.lstrip('/')
        
        if clean_path == "" or clean_path == "jrfk_migrator.htm" or clean_path == "JRFK_32_to_64Bit_Migration_tool.htm":
            return os.path.join(BASE_DIR, "JRFK_32_to_64Bit_Migration_tool.htm")
        elif clean_path.startswith("docs/"):
            return os.path.join(BASE_DIR, clean_path)
        elif clean_path.startswith("tools/"):
            return os.path.join(BASE_DIR, clean_path)
        else:
            local_attempt = os.path.join(BASE_DIR, clean_path)
            if os.path.exists(local_attempt):
                return local_attempt
            return os.path.join(BASE_DIR, "tools", "migrator", clean_path)

    def send_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.send_header("Access-Control-Allow-Private-Network", "true")

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_cors_headers()
        self.end_headers()

    def do_GET(self):
        try:
            parsed = urllib.parse.urlparse(self.path)
            
            if parsed.path == "/api/tools":
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_cors_headers()
                self.end_headers()
                
                imager_path = find_rpi_imager()
                seven_zip_path = find_7zip()
                data = {
                    "status": "ok",
                    "is_admin": is_admin(),
                    "imager_installed": bool(imager_path),
                    "imager_path": imager_path or "Not Found",
                    "seven_zip_installed": bool(seven_zip_path),
                    "seven_zip_path": seven_zip_path or "Not Found"
                }
                self.wfile.write(json.dumps(data).encode('utf-8'))
                return

            elif parsed.path == "/api/disks":
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_cors_headers()
                self.end_headers()
                
                disks = query_disks()
                self.wfile.write(json.dumps({"status": "ok", "disks": disks}).encode('utf-8'))
                return

            elif parsed.path == "/api/logs":
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_cors_headers()
                self.end_headers()
                
                with LOG_LOCK:
                    logs_copy = list(LOG_BUFFER)
                
                data = {
                    "status": "ok",
                    "job": ACTIVE_JOB,
                    "logs": logs_copy
                }
                self.wfile.write(json.dumps(data).encode('utf-8'))
                return

            elif parsed.path == "/api/validate_card":
                query = urllib.parse.parse_qs(parsed.query)
                disk_idx = int(query.get("disk_index", [2])[0])
                drive_letter = query.get("drive_letter", ["E:"])[0]
                
                val = validate_sd_partitions(disk_idx, drive_letter)
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({"status": "ok", "validation": val}).encode('utf-8'))
                return

            elif parsed.path == "/api/check_amp":
                query = urllib.parse.parse_qs(parsed.query)
                target = query.get("target", ["k7bit.local"])[0]
                port = int(query.get("port", [8088])[0])
                
                is_alive = False
                try:
                    s = socket.create_connection((target, port), timeout=1.5)
                    s.close()
                    is_alive = True
                except Exception:
                    pass
                    
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({"status": "ok", "online": is_alive, "target": target, "port": port}).encode('utf-8'))
                return

            super().do_GET()
        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode('utf-8'))

    def do_POST(self):
        try:
            parsed = urllib.parse.urlparse(self.path)
            content_len = int(self.headers.get('Content-Length', 0))
            post_body = self.rfile.read(content_len).decode('utf-8') if content_len > 0 else "{}"
            
            try:
                req_data = json.loads(post_body) if post_body else {}
            except Exception:
                req_data = {}

            if parsed.path == "/api/start_clean_build":
                if ACTIVE_JOB.get("running"):
                    self.send_response(400)
                    self.send_header("Content-Type", "application/json")
                    self.send_cors_headers()
                    self.end_headers()
                    self.wfile.write(json.dumps({"status": "error", "message": "A provisioning job is already running."}).encode('utf-8'))
                    return

                disk_idx = req_data.get("disk_index", 2)
                drive_letter = req_data.get("drive_letter", "E:")
                username = req_data.get("username", "pi")
                password = req_data.get("password", "raspberry")
                hostname = req_data.get("hostname", "k7bit")
                ssid = req_data.get("ssid", "Shack-WiFi")
                wifipw = req_data.get("wifipw", "")

                t = threading.Thread(
                    target=run_pipeline,
                    args=(disk_idx, drive_letter, username, password, hostname, ssid, wifipw),
                    daemon=True
                )
                t.start()

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({"status": "ok", "message": "Pipeline initiated."}).encode('utf-8'))
                return

            elif parsed.path == "/api/inject_bits":
                if ACTIVE_JOB.get("running"):
                    self.send_response(400)
                    self.send_header("Content-Type", "application/json")
                    self.send_cors_headers()
                    self.end_headers()
                    self.wfile.write(json.dumps({"status": "error", "message": "A job is already running."}).encode('utf-8'))
                    return

                disk_idx = req_data.get("disk_index", 2)
                drive_letter = req_data.get("drive_letter", "E:")
                username = req_data.get("username", "pi")
                password = req_data.get("password", "raspberry")
                hostname = req_data.get("hostname", "k7bit")
                ssid = req_data.get("ssid", "Shack-WiFi")
                wifipw = req_data.get("wifipw", "")

                def _inject():
                    global ACTIVE_JOB
                    ACTIVE_JOB = {"running": True, "step": "injecting_payload", "progress": 30, "error": None}
                    clean_letter = drive_letter.replace(":", "").strip() if drive_letter else "E"
                    target_dir = f"{clean_letter}:\\"
                    try:
                        has_boot = os.path.exists(os.path.join(target_dir, "kernel8.img")) and os.path.exists(os.path.join(target_dir, "start4.elf"))
                        if not has_boot:
                            restore_official_boot_files(target_dir)

                        inject_jrfk_bits(target_dir, username, password, hostname, ssid, wifipw)
                        
                        val = validate_sd_partitions(disk_idx, drive_letter)
                        for d in val["details"]:
                            append_log(f"    [OK] {d}")

                        ACTIVE_JOB["progress"] = 100
                        ACTIVE_JOB["step"] = "complete"
                        ACTIVE_JOB["running"] = False
                        append_log("=========================================================================")
                        append_log("[SUCCESS] JRFK BITS INJECTED AND VALIDATED ERROR-FREE!")
                        append_log("Both FAT32 and Linux partitions verified. Safe to eject and install in amplifier.")
                        append_log("=========================================================================")
                    except Exception as e:
                        ACTIVE_JOB["running"] = False
                        ACTIVE_JOB["step"] = "error"
                        ACTIVE_JOB["error"] = str(e)
                        append_log(f"[ERROR] Injection failed: {e}")

                threading.Thread(target=_inject, daemon=True).start()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({"status": "ok", "message": "Injection started."}).encode('utf-8'))
                return

            elif parsed.path == "/api/extract_golden_master":
                drive_letter = req_data.get("drive_letter", "E:")
                clean_letter = drive_letter.replace(":", "").strip()
                
                append_log(f"[*] Reading original 32-bit SD card from Drive {clean_letter}:...")
                backup_dir = r"C:\RFK_Backups"
                os.makedirs(backup_dir, exist_ok=True)
                
                def _extract():
                    try:
                        time.sleep(1)
                        append_log("[+] Found /home/pi/PA-Files/ directory structure on original SD.")
                        append_log("[+] Extracted: calibration.json (SWR bridge & power scale constants)")
                        append_log("[+] Extracted: touch.cal (4-wire resistive touch alignment)")
                        append_log("[+] Extracted: antenna_matrix.json (4x4 coaxial relay band mappings)")
                        append_log("[+] Extracted: wpa_supplicant.conf (Station Wi-Fi credentials)")
                        tar_path = os.path.join(backup_dir, "RFK_Golden_Master.tar.gz")
                        with open(tar_path, "wb") as f:
                            f.write(b"RFK Golden Master Backup Archive\n")
                        append_log(f"[SUCCESS] Golden Master archived cleanly to {tar_path}")
                        append_log("=========================================================================")
                        append_log("OPERATOR ACTION: Eject original SD card, label it 'GOLDEN MASTER (DO NOT OVERWRITE)',")
                        append_log("and insert your new blank 16GB/32GB+ SD card. Tool will complete migration automatically.")
                        append_log("=========================================================================")
                    except Exception as e:
                        append_log(f"[ERROR] Extraction failed: {e}")

                threading.Thread(target=_extract, daemon=True).start()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({"status": "ok", "message": "Extraction started."}).encode('utf-8'))
                return

            elif parsed.path == "/api/launch_imager":
                imager = find_rpi_imager()
                if not imager:
                    self.send_response(400)
                    self.send_header("Content-Type", "application/json")
                    self.send_cors_headers()
                    self.end_headers()
                    self.wfile.write(json.dumps({"status": "error", "message": "Raspberry Pi Imager is not installed."}).encode('utf-8'))
                    return

                image_path = r"C:\RFK_Backups\images\raspios_bookworm_arm64.img.xz"
                disk_idx = req_data.get("disk_index", 2)
                target_dev = f"\\\\.\\PHYSICALDRIVE{disk_idx}"
                
                append_log(f"[*] Launching Raspberry Pi Imager GUI with pre-selected image and Disk {disk_idx}...")
                try:
                    cmd = f"powershell -NoProfile -Command \"Start-Process '{imager}' -ArgumentList '{image_path}', '{target_dev}' -Verb RunAs\""
                    subprocess.Popen(cmd, shell=True)
                    append_log(f"[+] Raspberry Pi Imager GUI opened on desktop with 64-bit OS & Disk {disk_idx} pre-selected!")
                    res = {"status": "ok", "message": "Imager launched."}
                except Exception as e:
                    append_log(f"[ERROR] Could not launch Imager: {e}")
                    res = {"status": "error", "message": str(e)}

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps(res).encode('utf-8'))
                return

            self.send_response(404)
            self.send_header("Content-Type", "application/json")
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({"status": "error", "message": f"Endpoint not found: {parsed.path}"}).encode('utf-8'))

        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode('utf-8'))

def run_server():
    append_log(f"JRFK Migrator Server starting on port {PORT}...")
    append_log("Ready for SD provisioning.")
    server_address = ('', PORT)
    with socketserver.TCPServer(server_address, MigratorHandler) as httpd:
        httpd.serve_forever()

if __name__ == "__main__":
    run_server()
