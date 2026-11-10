import os
import sys
import subprocess
import time
from pathlib import Path

"""
jrfk_stage_new_sd.py
Pre-boot provisioner for Raspberry Pi 4 / 5 64-bit SD Card.
Runs in Windows/WSL right after Raspberry Pi Imager writes the clean 64-bit OS.
Mounts the new partitions, injects the automigration bundle, udev rules, 
and firstboot service unit.
"""

JRFK_DIR = Path(r"D:\JRFK")
BUNDLE_FILE = JRFK_DIR / "extracted" / "rfk_bundle.tar.gz"
SETTINGS_DIR = JRFK_DIR / "extracted" / "user_settings_backup"
FIRSTBOOT_SCRIPT = JRFK_DIR / "scripts" / "firstboot_setup.sh"

def run_wsl(cmd):
    full_cmd = f'wsl -u root sh -c "{cmd}"'
    res = subprocess.run(full_cmd, shell=True, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"Error running: {cmd}\n{res.stderr}")
    return res.stdout.strip()

def stage():
    print("==========================================================")
    print("JRFK 64-Bit New SD Pre-Boot Provisioner")
    print("==========================================================")

    # 1. Verify files exist in D:\JRFK
    if not BUNDLE_FILE.exists():
        print(f"[!] Error: {BUNDLE_FILE} not found!")
        return
    if not SETTINGS_DIR.exists():
        print(f"[!] Error: {SETTINGS_DIR} not found!")
        return
    if not FIRSTBOOT_SCRIPT.exists():
        print(f"[!] Error: {FIRSTBOOT_SCRIPT} not found!")
        return

    print("[*] Re-attaching USB SD Reader to WSL...")
    subprocess.run(r'& "C:\Program Files\usbipd-win\usbipd.exe" attach --wsl --busid 3-4', shell=True)
    time.sleep(3)

    # 2. Find SD partitions
    lsblk_out = run_wsl("lsblk -o NAME,SIZE,TYPE,MOUNTPOINTS -l | grep sde")
    print(f"[*] Block devices:\n{lsblk_out}")

    # 3. Mount boot and rootfs partitions
    print("[*] Mounting newly flashed 64-bit partitions...")
    run_wsl("mkdir -p /mnt/new_boot /mnt/new_rootfs")
    run_wsl("mount /dev/sde1 /mnt/new_boot || mount /dev/sde1 /mnt/new_boot -t vfat")
    run_wsl("mount /dev/sde2 /mnt/new_rootfs || mount /dev/sde2 /mnt/new_rootfs -t ext4")

    # 4. Stage migration assets into /opt/jrfk/ on new rootfs
    print("[*] Staging migration payload into /opt/jrfk/...")
    run_wsl("mkdir -p /mnt/new_rootfs/opt/jrfk")
    run_wsl("cp -a /mnt/d/JRFK/extracted/rfk_bundle.tar.gz /mnt/new_rootfs/opt/jrfk/")
    run_wsl("cp -a /mnt/d/JRFK/extracted/user_settings_backup /mnt/new_rootfs/opt/jrfk/")
    run_wsl("cp -a /mnt/d/JRFK/scripts/firstboot_setup.sh /mnt/new_rootfs/opt/jrfk/firstboot_setup.sh")
    run_wsl("chmod +x /mnt/new_rootfs/opt/jrfk/firstboot_setup.sh")

    # 5. Install systemd firstboot service unit
    print("[*] Installing rfk-firstboot systemd service...")
    unit_content = """[Unit]
Description=JRFK Universal 64-bit Auto-Migration Service
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
ExecStart=/opt/jrfk/firstboot_setup.sh
RemainAfterExit=yes
StandardOutput=journal+console
StandardError=journal+console

[Install]
WantedBy=multi-user.target
"""
    run_wsl(f"cat << 'EOF' > /mnt/new_rootfs/etc/systemd/system/rfk-firstboot.service\n{unit_content}\nEOF")
    run_wsl("mkdir -p /mnt/new_rootfs/etc/systemd/system/multi-user.target.wants")
    run_wsl("ln -sf /etc/systemd/system/rfk-firstboot.service /mnt/new_rootfs/etc/systemd/system/multi-user.target.wants/rfk-firstboot.service")

    # 6. Pre-configure display timings in cmdline.txt & config.txt
    print("[*] Configuring 1024x600 Full KMS display mode...")
    run_wsl("sed -i 's/$/ video=HDMI-A-1:1024x600M@60D/' /mnt/new_boot/cmdline.txt || true")
    run_wsl("echo 'dtoverlay=vc4-kms-v3d' >> /mnt/new_boot/config.txt || true")
    run_wsl("echo 'dtoverlay=disable-bt' >> /mnt/new_boot/config.txt || true")

    # 7. Sync and unmount
    print("[*] Syncing and unmounting...")
    run_wsl("sync")
    run_wsl("umount /mnt/new_boot 2>/dev/null || true")
    run_wsl("umount /mnt/new_rootfs 2>/dev/null || true")
    run_wsl("sync")

    # 8. Detach USB from WSL
    subprocess.run(r'& "C:\Program Files\usbipd-win\usbipd.exe" detach --busid 3-4', shell=True)

    print("\n[+] SUCCESS! The 64-bit SD card is pre-configured and ready.")
    print("    Insert it into the Raspberry Pi 4 or Pi 5 in the amplifier and power on.")
    print("    First boot will auto-provision all drivers, settings, and launch the RFK GUI.")

if __name__ == "__main__":
    stage()
