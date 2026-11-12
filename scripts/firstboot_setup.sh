#!/bin/bash
# ==============================================================================
# JRFK Universal 64-bit First-Boot Auto-Migrator
# Target Hardware: Raspberry Pi 4 Model B & Raspberry Pi 5 (Single-SD Parity)
# Target OS: Raspberry Pi OS 64-bit (Debian Bookworm/Trixie aarch64)
# Author: John Birdlebough (K7BIT/AE)
# Contributor: John Stafford
# ==============================================================================

set +e
CLOUDINIT_MODE=0
for _arg in "$@"; do
    [ "$_arg" = "--cloudinit" ] && CLOUDINIT_MODE=1
done

LOGFILE="/var/log/jrfk_firstboot.log"
# Log directly to file without async process substitution so cloud-init never hangs waiting on tee pipe FDs
exec >>"$LOGFILE" 2>&1

show_step() {
    local num="$1"
    local title="$2"
    echo ""
    echo "=========================================================="
    echo ">>> [RF-KIT MIGRATION STEP $num] $title"
    echo "=========================================================="
    echo ""
    if command -v plymouth >/dev/null 2>&1; then
        plymouth display-message --text="[RF-KIT STEP $num] $title" 2>/dev/null || true
    fi
}

if [ "$CLOUDINIT_MODE" != "1" ]; then
    if command -v plymouth >/dev/null 2>&1; then
        plymouth quit 2>/dev/null || true
    fi
    chvt 1 2>/dev/null || true
    clear > /dev/tty1 2>/dev/null || true
fi

BOOT_DIR="/boot/firmware"
[ ! -d "$BOOT_DIR" ] && BOOT_DIR="/boot"

PAYLOAD_DIR="$BOOT_DIR/jrfk_payload"
[ ! -d "$PAYLOAD_DIR" ] && PAYLOAD_DIR="/boot/jrfk_payload"
[ ! -d "$PAYLOAD_DIR" ] && PAYLOAD_DIR="/opt/jrfk"

# Optional station metadata passed from migrator
TARGET_USER="pi"
TARGET_HOST=""
TARGET_PASS_HASH=""
AUTO_UPGRADE="1"
if [ -f "$PAYLOAD_DIR/jrfk_meta.env" ]; then
    # shellcheck disable=SC1090
    source "$PAYLOAD_DIR/jrfk_meta.env"
fi

TARGET_HOME="/home/$TARGET_USER"
if ! id "$TARGET_USER" >/dev/null 2>&1; then
    useradd -m -s /bin/bash -G sudo,dialout,tty,video,audio,netdev "$TARGET_USER" 2>/dev/null || true
fi
if [ -n "$TARGET_PASS_HASH" ]; then
    usermod -p "$TARGET_PASS_HASH" "$TARGET_USER" 2>/dev/null || true
fi
mkdir -p "$TARGET_HOME"

# ------------------------------------------------------------------------------
# Step 1/7: Filesystem & Environment Preparation
# ------------------------------------------------------------------------------
show_step "1/7" "Preparing 64-bit root filesystem..."
if [ "$CLOUDINIT_MODE" != "1" ] && command -v raspi-config >/dev/null 2>&1; then
    raspi-config nonint do_expand_rootfs 2>/dev/null || true
fi

# ------------------------------------------------------------------------------
# Step 2/7: Deploy RF-KIT App, User Data & Tuning Data (from GOLD or Bundle)
# ------------------------------------------------------------------------------
show_step "2/7" "Deploying RF-KIT app, user data & antenna/tuning data..."
mkdir -p "$TARGET_HOME/rf-kit-statics" "$TARGET_HOME/PA-Files" "$TARGET_HOME/Desktop" "$TARGET_HOME/.config/autostart"

if [ -f "$PAYLOAD_DIR/rfk_bundle.tar.gz" ]; then
    tar -xzf "$PAYLOAD_DIR/rfk_bundle.tar.gz" -C / 2>/dev/null || true
fi

if [ -d "$PAYLOAD_DIR/gold_rootfs" ]; then
    echo "[*] Restoring validated GOLD rootfs payload..."
    if [ -d "$PAYLOAD_DIR/gold_rootfs/home/$TARGET_USER" ]; then
        cp -a "$PAYLOAD_DIR/gold_rootfs/home/$TARGET_USER/." "$TARGET_HOME/" 2>/dev/null || true
    elif [ -d "$PAYLOAD_DIR/gold_rootfs/home/pi" ]; then
        cp -a "$PAYLOAD_DIR/gold_rootfs/home/pi/." "$TARGET_HOME/" 2>/dev/null || true
    fi
    if [ -f "$PAYLOAD_DIR/gold_rootfs/etc/wpa_supplicant/wpa_supplicant.conf" ]; then
        mkdir -p /etc/wpa_supplicant
        cp -f "$PAYLOAD_DIR/gold_rootfs/etc/wpa_supplicant/wpa_supplicant.conf" /etc/wpa_supplicant/wpa_supplicant.conf
        chmod 600 /etc/wpa_supplicant/wpa_supplicant.conf
    fi
    if [ -f "$PAYLOAD_DIR/gold_rootfs/etc/hostname" ] && [ -z "$TARGET_HOST" ]; then
        TARGET_HOST=$(tr -d ' \t\r\n' < "$PAYLOAD_DIR/gold_rootfs/etc/hostname")
    fi
fi

SETTINGS_DIR="$PAYLOAD_DIR/user_settings_backup"
if [ -d "$SETTINGS_DIR" ]; then
    cp -a "$SETTINGS_DIR"/. "$TARGET_HOME/rf-kit-statics/" 2>/dev/null || true
    cp -a "$SETTINGS_DIR"/*Cookbook* "$TARGET_HOME/Desktop/" 2>/dev/null || true
fi

# Keep PA-Files and rf-kit-statics aligned so both v1.98 and v2.00 find calibrations
for f in calibration.json config.json gui_path.json gui_starter.py touch.cal touchscreen_axes.cal antenna_matrix.json band_matrix.cfg; do
    if [ -f "$TARGET_HOME/PA-Files/$f" ] && [ ! -f "$TARGET_HOME/rf-kit-statics/$f" ]; then
        cp -a "$TARGET_HOME/PA-Files/$f" "$TARGET_HOME/rf-kit-statics/$f" 2>/dev/null || true
    elif [ -f "$TARGET_HOME/rf-kit-statics/$f" ] && [ ! -f "$TARGET_HOME/PA-Files/$f" ]; then
        cp -a "$TARGET_HOME/rf-kit-statics/$f" "$TARGET_HOME/PA-Files/$f" 2>/dev/null || true
    fi
done

# ------------------------------------------------------------------------------
# Step 3/7: Apply 64-Bit Python / Pillow & Hamlib Compatibility Shims
# ------------------------------------------------------------------------------
show_step "3/7" "Applying 64-bit Pillow ANTIALIAS & Hamlib compatibility fixes..."
if [ -f "$PAYLOAD_DIR/patch_antialias.py" ]; then
    python3 "$PAYLOAD_DIR/patch_antialias.py" "$TARGET_HOME"/rf-kit* 2>/dev/null || true
fi

relink_64bit_hamlib() {
    local hl_path
    hl_path=$(python3 -c "import Hamlib, os; print(os.path.dirname(Hamlib.__file__))" 2>/dev/null || true)
    [ -z "$hl_path" ] || [ ! -d "$hl_path" ] && return 0
    local first_so
    first_so=$(ls "$hl_path"/_Hamlib*.so 2>/dev/null | head -n 1 || true)
    for GUI_DIR in "$TARGET_HOME"/rf-kit-gui*; do
        [ -d "$GUI_DIR" ] || continue
        mkdir -p "$GUI_DIR/hamlib/v4_6_5_bindings_backport/lib/python3_7/site_packages" \
                 "$GUI_DIR/hamlib/v4_0_rc2/lib/python3_7/site_packages"
        touch "$GUI_DIR/hamlib/__init__.py" \
              "$GUI_DIR/hamlib/v4_6_5_bindings_backport/__init__.py" \
              "$GUI_DIR/hamlib/v4_6_5_bindings_backport/lib/__init__.py" \
              "$GUI_DIR/hamlib/v4_6_5_bindings_backport/lib/python3_7/__init__.py" \
              "$GUI_DIR/hamlib/v4_6_5_bindings_backport/lib/python3_7/site_packages/__init__.py" \
              "$GUI_DIR/hamlib/v4_0_rc2/__init__.py" \
              "$GUI_DIR/hamlib/v4_0_rc2/lib/__init__.py" \
              "$GUI_DIR/hamlib/v4_0_rc2/lib/python3_7/__init__.py" \
              "$GUI_DIR/hamlib/v4_0_rc2/lib/python3_7/site_packages/__init__.py" 2>/dev/null || true
        for SUB_SP in "$GUI_DIR"/hamlib/*/lib/*/site*packages; do
            [ -d "$SUB_SP" ] || continue
            ln -sf "$hl_path/Hamlib.py" "$SUB_SP/Hamlib.py" 2>/dev/null || true
            rm -f "$SUB_SP"/_Hamlib*.so 2>/dev/null || true
            for _so in "$hl_path"/_Hamlib*.so; do
                [ -e "$_so" ] && ln -sf "$_so" "$SUB_SP/$(basename "$_so")" 2>/dev/null || true
            done
            if [ -n "$first_so" ] && [ ! -e "$SUB_SP/_Hamlib.so" ]; then
                ln -sf "$first_so" "$SUB_SP/_Hamlib.so" 2>/dev/null || true
            fi
        done
        # Replace bundled 32-bit libhamlib*.so* with 64-bit system libs so CatBaseProcess LD_LIBRARY_PATH works on aarch64
        if ls /usr/lib/aarch64-linux-gnu/libhamlib.so* >/dev/null 2>&1; then
            for HAM_LIB_DIR in "$GUI_DIR"/hamlib/*/lib; do
                [ -d "$HAM_LIB_DIR" ] || continue
                rm -f "$HAM_LIB_DIR"/libhamlib*.so* 2>/dev/null || true
                for _sys_so in /usr/lib/aarch64-linux-gnu/libhamlib*.so*; do
                    [ -e "$_sys_so" ] && ln -sf "$_sys_so" "$HAM_LIB_DIR/$(basename "$_sys_so")" 2>/dev/null || true
                done
            done
        fi
    done
}

relink_64bit_hamlib

# ------------------------------------------------------------------------------
# Step 4/7: Configure Wi-Fi (NetworkManager + wpa_supplicant) & Hostname
# ------------------------------------------------------------------------------
show_step "4/7" "Configuring station hostname & Wi-Fi..."
[ -z "$TARGET_HOST" ] && TARGET_HOST="k7bit"
hostnamectl set-hostname "$TARGET_HOST" 2>/dev/null || echo "$TARGET_HOST" > /etc/hostname
if grep -q "^127\.0\.1\.1" /etc/hosts 2>/dev/null; then
    sed -i "s/^127\.0\.1\.1.*/127.0.1.1\t$TARGET_HOST rfk/" /etc/hosts 2>/dev/null || true
else
    echo -e "127.0.1.1\t$TARGET_HOST rfk" >> /etc/hosts
fi

WPA_SRC=""
[ -f "$BOOT_DIR/wpa_supplicant.conf" ] && WPA_SRC="$BOOT_DIR/wpa_supplicant.conf"
[ -z "$WPA_SRC" ] && [ -f /etc/wpa_supplicant/wpa_supplicant.conf ] && WPA_SRC="/etc/wpa_supplicant/wpa_supplicant.conf"
if [ -n "$WPA_SRC" ]; then
    mkdir -p /etc/wpa_supplicant
    [ "$WPA_SRC" != "/etc/wpa_supplicant/wpa_supplicant.conf" ] && cp -f "$WPA_SRC" /etc/wpa_supplicant/wpa_supplicant.conf
    sed -i 's/^country=GB$/country=US/' /etc/wpa_supplicant/wpa_supplicant.conf 2>/dev/null || true
    chmod 600 /etc/wpa_supplicant/wpa_supplicant.conf 2>/dev/null || true

    WIFI_SSID=$(python3 -c "import re,sys; t=open(sys.argv[1],errors='ignore').read(); m=re.search(r'ssid\s*=\s*\"([^\"]+)\"',t); print(m.group(1) if m else '')" "$WPA_SRC" 2>/dev/null || true)
    WIFI_PSK=$(python3 -c "import re,sys; t=open(sys.argv[1],errors='ignore').read(); m=re.search(r'psk\s*=\s*\"([^\"]+)\"',t); print(m.group(1) if m else '')" "$WPA_SRC" 2>/dev/null || true)
    command -v rfkill >/dev/null 2>&1 && rfkill unblock wifi 2>/dev/null || true
    command -v raspi-config >/dev/null 2>&1 && raspi-config nonint do_wifi_country US 2>/dev/null || true
    if [ -n "$WIFI_SSID" ] && command -v nmcli >/dev/null 2>&1; then
        nmcli radio wifi on 2>/dev/null || true
        nmcli con delete "$WIFI_SSID" 2>/dev/null || true
        if [ -n "$WIFI_PSK" ]; then
            nmcli con add type wifi ifname wlan0 con-name "$WIFI_SSID" ssid "$WIFI_SSID" wifi-sec.key-mgmt wpa-psk wifi-sec.psk "$WIFI_PSK" connection.autoconnect yes 2>/dev/null || true
        else
            nmcli con add type wifi ifname wlan0 con-name "$WIFI_SSID" ssid "$WIFI_SSID" connection.autoconnect yes 2>/dev/null || true
        fi
        timeout 15 nmcli con up "$WIFI_SSID" 2>/dev/null || true
    fi
fi

# ------------------------------------------------------------------------------
# Step 5/7: Pi 4 & Pi 5 Hardware Parity + RFK Tools Suite (:8088)
# ------------------------------------------------------------------------------
show_step "5/7" "Configuring Pi 4 & Pi 5 hardware links, SocketCAN & Tools Suite..."
systemctl disable --now hciuart.service bluealsa.service bluetooth.service 2>/dev/null || true

cat << 'EOF' > /etc/udev/rules.d/99-rfk-controller.rules
# Universal RF-KIT Microcontroller Link for both Raspberry Pi 4 and Raspberry Pi 5
KERNEL=="ttyACM*|ttyUSB*", SUBSYSTEM=="tty", MODE="0666", GROUP="dialout", SYMLINK+="rfk_controller"
KERNEL=="ttyACM*|ttyUSB*", SUBSYSTEM=="tty", MODE="0666", GROUP="dialout", SYMLINK+="serial/by-path/platform-fd500000.pcie-pci-0000:01:00.0-usb-0:1.3:1.0-port0"
EOF
udevadm control --reload-rules 2>/dev/null || true
udevadm trigger 2>/dev/null || true

mkdir -p /etc/network/interfaces.d
cat << 'EOF' > /etc/network/interfaces.d/can0
auto can0
iface can0 can static
    bitrate 250000
    up ifconfig can0 txqueuelen 1000
EOF

usermod -aG dialout,tty,video,audio "$TARGET_USER" 2>/dev/null || true

if [ -d "$PAYLOAD_DIR/rfk_tools_suite" ]; then
    mkdir -p "$TARGET_HOME/rfk_tools"
    cp -a "$PAYLOAD_DIR/rfk_tools_suite/." "$TARGET_HOME/rfk_tools/" 2>/dev/null || true
    chmod +x "$TARGET_HOME/rfk_tools/bin/"*.sh 2>/dev/null || true
    cp -f "$TARGET_HOME/rfk_tools/bin/"*.desktop "$TARGET_HOME/Desktop/" 2>/dev/null || true
    chmod +x "$TARGET_HOME/Desktop/"*.desktop 2>/dev/null || true
    if [ -f "$TARGET_HOME/rfk_tools/bin/jrfk_weekly_backup.cron" ]; then
        cp -f "$TARGET_HOME/rfk_tools/bin/jrfk_weekly_backup.cron" /etc/cron.d/jrfk_weekly_backup
        chmod 644 /etc/cron.d/jrfk_weekly_backup
    fi
    if [ "$AUTO_UPGRADE" = "1" ] && [ -f "$TARGET_HOME/rfk_tools/bin/jrfk_weekly_upgrade.cron" ]; then
        cp -f "$TARGET_HOME/rfk_tools/bin/jrfk_weekly_upgrade.cron" /etc/cron.d/jrfk_weekly_upgrade
        chmod 644 /etc/cron.d/jrfk_weekly_upgrade
    fi
    cat << EOF > /etc/systemd/system/rfk-tools-suite.service
[Unit]
Description=JRFK Amplifier Diagnostic & Backup Web Suite (:8088)
After=network.target

[Service]
Type=simple
User=$TARGET_USER
WorkingDirectory=$TARGET_HOME/rfk_tools
ExecStart=/usr/bin/python3 $TARGET_HOME/rfk_tools/server.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF
    systemctl daemon-reload 2>/dev/null || true
    systemctl enable rfk-tools-suite.service 2>/dev/null || true
fi

# ------------------------------------------------------------------------------
# Step 6/7: Direct-to-RFK Boot (Install All RFK Deps + X11 Openbox + Wayland labwc Parity)
# ------------------------------------------------------------------------------
show_step "6/7" "Installing RFK Python & UI dependencies and configuring Direct-to-RFK fullscreen boot..."
export DEBIAN_FRONTEND=noninteractive
compute_need_pkgs() {
    local pkgs=""
    python3 -c "import can" 2>/dev/null || pkgs="$pkgs python3-can can-utils"
    python3 -c "from PIL import ImageTk" 2>/dev/null || pkgs="$pkgs python3-pil.imagetk"
    python3 -c "import tkinter" 2>/dev/null || pkgs="$pkgs python3-tk"
    python3 -c "import serial" 2>/dev/null || pkgs="$pkgs python3-serial"
    python3 -c "import paramiko" 2>/dev/null || pkgs="$pkgs python3-paramiko"
    python3 -c "import Hamlib" 2>/dev/null || pkgs="$pkgs python3-hamlib"
    python3 -c "import websocket" 2>/dev/null || pkgs="$pkgs python3-websocket"
    python3 -c "import yaml" 2>/dev/null || pkgs="$pkgs python3-yaml"
    python3 -c "import cgi" 2>/dev/null || pkgs="$pkgs python3-legacy-cgi"
    fc-list 2>/dev/null | grep -qi "Lato" || pkgs="$pkgs fonts-lato"
    command -v openbox >/dev/null 2>&1 || pkgs="$pkgs openbox"
    command -v pip3 >/dev/null 2>&1 || pkgs="$pkgs python3-pip"
    echo "$pkgs"
}

# Stage offline pure-Python dependencies (simple_rpc, pysftp) from jrfk_payload if present
if [ -d "$PAYLOAD_DIR/py_deps" ]; then
    echo "[*] Staging pure-Python RFK modules (simple_rpc, pysftp)..."
    mkdir -p /usr/local/lib/python3/dist-packages
    cp -a "$PAYLOAD_DIR/py_deps/." /usr/local/lib/python3/dist-packages/ 2>/dev/null || true
    for PY_SITE in /usr/lib/python3/dist-packages /usr/local/lib/python3.*/dist-packages; do
        [ -d "$PY_SITE" ] && cp -a "$PAYLOAD_DIR/py_deps/." "$PY_SITE/" 2>/dev/null || true
    done
    for GUI_DIR in "$TARGET_HOME"/rf-kit-gui*; do
        if [ -d "$GUI_DIR" ]; then
            rm -rf "$GUI_DIR/simple_rpc" "$GUI_DIR/pysftp" 2>/dev/null || true
            cp -a "$PAYLOAD_DIR/py_deps/." "$GUI_DIR/" 2>/dev/null || true
        fi
    done
fi

# Install bundled offline arm64 .deb packages (python3-pil.imagetk, python3-can, python3-paramiko, python3-hamlib, python3-yaml, python3-legacy-cgi, etc.)
if [ -d "$PAYLOAD_DIR/pi_debs" ] && ls "$PAYLOAD_DIR/pi_debs"/*.deb >/dev/null 2>&1; then
    echo "[*] Installing bundled offline 64-bit .deb packages from $PAYLOAD_DIR/pi_debs..."
    dpkg -i --force-confdef --force-confold "$PAYLOAD_DIR/pi_debs"/*.deb || true
    dpkg --configure -a || true
    ldconfig 2>/dev/null || true
fi
NEED_PKGS=$(compute_need_pkgs)

NET_ONLINE=0
if [ -n "$NEED_PKGS" ]; then
    echo "[*] Waiting up to 15s for network reachability to install runtime packages:$NEED_PKGS"
    for _net_try in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15; do
        if timeout 3 getent hosts deb.debian.org >/dev/null 2>&1 || timeout 2 ping -c1 -W1 1.1.1.1 >/dev/null 2>&1; then
            NET_ONLINE=1
            break
        fi
        sleep 1
    done
    if [ "$NET_ONLINE" = "1" ]; then
        echo "[*] Installing required 64-bit runtime packages:$NEED_PKGS"
        timeout 90 apt-get update -qq -o Acquire::http::Timeout=8 -o Acquire::Retries=1 2>/dev/null && \
            timeout 180 apt-get install -y --no-install-recommends -qq -o Acquire::http::Timeout=8 $NEED_PKGS 2>/dev/null || true
    else
        echo "[!] Offline on first boot; skipping apt-get (will rely on preinstalled/staged libs)."
    fi
fi

# Ensure arduino-simple-rpc and pysftp are importable system-wide if missing
if ! python3 -c "from simple_rpc import Interface; import pysftp" 2>/dev/null; then
    if command -v pip3 >/dev/null 2>&1 && (timeout 4 getent hosts pypi.org >/dev/null 2>&1 || timeout 4 ping -c1 -W2 1.1.1.1 >/dev/null 2>&1); then
        timeout 90 pip3 install --break-system-packages --no-input arduino-simple-rpc pysftp 2>/dev/null || true
    fi
fi

# Re-link 64-bit Hamlib bindings & shared libs after python3-hamlib install
relink_64bit_hamlib

echo "[*] Verifying 64-bit RFK Python imports..."
python3 - << 'PYCHK' || true
for mod in ("tkinter", "PIL.ImageTk", "can", "serial", "paramiko", "yaml", "cgi", "simple_rpc", "pysftp", "Hamlib"):
    try:
        __import__(mod)
        print(f"    [OK] import {mod}")
    except Exception as e:
        print(f"    [WARN] import {mod} failed: {e}")
try:
    from simple_rpc import Interface  # noqa: F401
    print("    [OK] from simple_rpc import Interface")
except Exception as e:
    print(f"    [WARN] simple_rpc.Interface failed: {e}")
PYCHK

export USER="$TARGET_USER"
if command -v raspi-config >/dev/null 2>&1; then
    raspi-config nonint do_wayland W1 2>/dev/null || true
    raspi-config nonint do_boot_behaviour B4 2>/dev/null || true
fi

# Remove first-boot setup wizards so desktop goes straight to JRFK
rm -f /etc/xdg/autostart/piwiz.desktop /etc/xdg/autostart/pprompt.desktop /etc/xdg/autostart/*wiz*.desktop 2>/dev/null || true
mkdir -p "$TARGET_HOME/.config"
touch "$TARGET_HOME/.config/piwiz_done" 2>/dev/null || true
if [ -f /etc/lightdm/lightdm.conf ]; then
    sed -i "s|^#*autologin-user=.*|autologin-user=$TARGET_USER|" /etc/lightdm/lightdm.conf 2>/dev/null || true
fi

cat << EOF > "$TARGET_HOME/rfk_postboot_prompt.py"
#!/usr/bin/env python3
import os
import platform
import subprocess
import sys

FLAG_FILE = os.path.expanduser("~/.jrfk_migration_complete_prompt")

def read_os_name():
    try:
        with open("/etc/os-release", "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                if line.startswith("PRETTY_NAME="):
                    return line.split("=", 1)[1].strip().strip('"')
    except Exception:
        pass
    return "Raspberry Pi OS 64-bit"

def trigger_reboot():
    try:
        if os.path.exists(FLAG_FILE):
            os.remove(FLAG_FILE)
    except Exception:
        pass
    for cmd in (["sudo", "/sbin/reboot"], ["sudo", "systemctl", "reboot"], ["/sbin/reboot"]):
        try:
            subprocess.Popen(cmd)
            return
        except Exception:
            pass

try:
    import tkinter as tk
except ImportError:
    msg = (
        f"32-64Bit RFK migration complete\n\n"
        f"OS: {read_os_name()} ({platform.machine()})\n"
        f"RF-KIT GUI, station settings & calibration data are installed."
    )
    subprocess.run(
        ["zenity", "--info", "--title=32-64Bit RFK Migration Complete", "--text=" + msg, "--ok-label=Reboot"],
        check=False,
    )
    trigger_reboot()
    sys.exit(0)

def do_reboot():
    trigger_reboot()
    root.after(1500, root.destroy)

root = tk.Tk()
root.title("32-64Bit RFK Migration Complete")
root.configure(bg="#0b1120")
sw = max(800, root.winfo_screenwidth())
sh = max(480, root.winfo_screenheight())
root.geometry(f"{sw}x{sh}+0+0")
root.attributes("-fullscreen", True)
root.attributes("-topmost", True)
root.bind("<Map>", lambda _e: root.attributes("-fullscreen", True))

frame = tk.Frame(root, bg="#111827", bd=2, relief="ridge", padx=48, pady=40)
frame.place(relx=0.5, rely=0.5, anchor="center")

tk.Label(
    frame,
    text="32-64Bit RFK migration complete",
    font=("DejaVu Sans", 26, "bold"),
    fg="#34d399",
    bg="#111827",
).pack(pady=(0, 14))

tk.Label(
    frame,
    text=f"OS: {read_os_name()} ({platform.machine()})\n"
         f"RF-KIT GUI, station settings & calibration data are installed.\n"
         f"Press Reboot to start the RF-KIT amplifier display.",
    font=("DejaVu Sans", 14),
    fg="#e5e7eb",
    bg="#111827",
    justify="center",
).pack(pady=(0, 28))

tk.Button(
    frame,
    text="Reboot",
    command=do_reboot,
    font=("DejaVu Sans", 20, "bold"),
    fg="#ffffff",
    bg="#16a34a",
    activebackground="#15803d",
    activeforeground="#ffffff",
    padx=48,
    pady=16,
    relief="flat",
    cursor="hand2",
).pack()

root.mainloop()
EOF
chmod +x "$TARGET_HOME/rfk_postboot_prompt.py" 2>/dev/null || true
touch "$TARGET_HOME/.jrfk_migration_complete_prompt"

echo "$TARGET_USER ALL=(ALL) NOPASSWD: /sbin/reboot, /bin/systemctl" > /etc/sudoers.d/090_jrfk_reboot
chmod 0440 /etc/sudoers.d/090_jrfk_reboot 2>/dev/null || true

cat << EOF > "$TARGET_HOME/Desktop/start_gui.sh"
#!/bin/bash
exec 9>/tmp/jrfk_gui.lock
flock -n 9 || exit 0

export DISPLAY="\${DISPLAY:-:0}"
for _w in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15; do
    xset q >/dev/null 2>&1 && break
    sleep 0.4
done

xset s off 2>/dev/null || true
xset -dpms 2>/dev/null || true
xset s noblank 2>/dev/null || true

# Lock Waveshare / 7-inch display to native 1024x600 so Xorg does not pick 1152x864/1080p
for _out in HDMI-1 HDMI-2 HDMI-A-1 HDMI-A-2; do
    xrandr --output "\$_out" --mode 1024x600 2>/dev/null || true
done

# First graphical boot after firstboot setup: show completion popup with Reboot button
if [ -f "\$HOME/.jrfk_migration_complete_prompt" ] && [ -f "\$HOME/rfk_postboot_prompt.py" ]; then
    python3 "\$HOME/rfk_postboot_prompt.py"
    rm -f "\$HOME/.jrfk_migration_complete_prompt"
fi

# Fullscreen RFK GUI covers the desktop panel naturally without killing lxpanel/wf-panel-pi.
# Brief wait for USB controller symlink on Pi 4 / Pi 5
for _i in 1 2 3 4 5 6; do
    [ -e /dev/rfk_controller ] && break
    sleep 0.5
done

cd "$TARGET_HOME/rf-kit-statics"
python3 gui_starter.py &>> rf-kit-gui.log
EOF
chmod +x "$TARGET_HOME/Desktop/start_gui.sh" "$TARGET_HOME/rf-kit-statics/gui_starter.py" 2>/dev/null || true

# Pin Xorg modesetting driver to 1024x600 for 7-inch Waveshare/RFK HDMI display
mkdir -p /etc/X11/xorg.conf.d
cat << 'XORGEOF' > /etc/X11/xorg.conf.d/10-rfk-hdmi.conf
Section "Device"
    Identifier "Card0"
    Driver "modesetting"
    Option "Monitor-HDMI-1" "RFK-HDMI-1"
    Option "Monitor-HDMI-2" "RFK-HDMI-2"
EndSection

Section "Monitor"
    Identifier "RFK-HDMI-1"
    Option "PreferredMode" "1024x600"
EndSection

Section "Monitor"
    Identifier "RFK-HDMI-2"
    Option "PreferredMode" "1024x600"
EndSection

Section "Screen"
    Identifier "Screen0"
    Device "Card0"
    DefaultDepth 24
    SubSection "Display"
        Depth 24
        Modes "1024x600"
    EndSubSection
EndSection
XORGEOF

# Openbox rule (X11: Trixie rpd-rc.xml + Bookworm lxde-pi-rc.xml + rc.xml) keeps RFK fullscreen/on-top
mkdir -p "$TARGET_HOME/.config/openbox"
for _src_xml in /etc/xdg/openbox/lxde-pi-rc.xml /etc/xdg/openbox/rpd-rc.xml /etc/xdg/openbox/rc.xml; do
    _base=$(basename "$_src_xml")
    if [ -f "$_src_xml" ] && [ ! -f "$TARGET_HOME/.config/openbox/$_base" ]; then
        cp -f "$_src_xml" "$TARGET_HOME/.config/openbox/$_base" 2>/dev/null || true
    fi
done
python3 - << PYEOF
import os
home = "$TARGET_HOME"
targets = [
    os.path.join(home, ".config/openbox/lxde-pi-rc.xml"),
    os.path.join(home, ".config/openbox/rpd-rc.xml"),
    os.path.join(home, ".config/openbox/rc.xml"),
]
rule = """  <application class="Tk">
    <decor>no</decor>
    <maximized>yes</maximized>
    <fullscreen>yes</fullscreen>
    <layer>above</layer>
    <focus>yes</focus>
  </application>
  <application class="tk">
    <decor>no</decor>
    <maximized>yes</maximized>
    <fullscreen>yes</fullscreen>
    <layer>above</layer>
    <focus>yes</focus>
  </application>
"""
for rc_path in targets:
    if os.path.isfile(rc_path):
        with open(rc_path, "r", encoding="utf-8", errors="ignore") as f:
            txt = f.read()
        if '<application class="Tk">' not in txt:
            if "</applications>" in txt:
                txt = txt.replace("</applications>", rule + "</applications>", 1)
            elif "</openbox_config>" in txt:
                txt = txt.replace("</openbox_config>", f"<applications>\n{rule}</applications>\n</openbox_config>", 1)
            with open(rc_path, "w", encoding="utf-8") as f:
                f.write(txt)
    else:
        with open(rc_path, "w", encoding="utf-8") as f:
            f.write(f'<?xml version="1.0" encoding="UTF-8"?>\n<openbox_config xmlns="http://openbox.org/3.4/rc">\n<applications>\n{rule}</applications>\n</openbox_config>\n')
PYEOF

# Wayland labwc fallback (Trixie desktop) autostart + fullscreen window rules
mkdir -p "$TARGET_HOME/.config/labwc"
cat << EOF > "$TARGET_HOME/.config/labwc/autostart"
$TARGET_HOME/Desktop/start_gui.sh &
EOF
chmod +x "$TARGET_HOME/.config/labwc/autostart" 2>/dev/null || true

python3 - << PYEOF
import os
lrc_path = "$TARGET_HOME/.config/labwc/rc.xml"
lrule = """  <windowRule identifier="Tk" serverDecoration="no">
    <action name="Maximize" />
    <action name="ToggleFullscreen" />
  </windowRule>
  <windowRule identifier="tk" serverDecoration="no">
    <action name="Maximize" />
    <action name="ToggleFullscreen" />
  </windowRule>
"""
if os.path.isfile(lrc_path):
    with open(lrc_path, "r", encoding="utf-8", errors="ignore") as f:
        txt = f.read()
    if 'identifier="Tk"' not in txt:
        if "</windowRules>" in txt:
            txt = txt.replace("</windowRules>", lrule + "</windowRules>", 1)
        elif "</labwc_config>" in txt:
            txt = txt.replace("</labwc_config>", f"<windowRules>\n{lrule}</windowRules>\n</labwc_config>", 1)
        with open(lrc_path, "w", encoding="utf-8") as f:
            f.write(txt)
else:
    with open(lrc_path, "w", encoding="utf-8") as f:
        f.write(f'<?xml version="1.0" encoding="UTF-8"?>\n<labwc_config>\n<windowRules>\n{lrule}</windowRules>\n</labwc_config>\n')
PYEOF

# Standard XDG autostart (do not shadow /etc/xdg/lxsession/LXDE-pi/autostart which starts lxpanel)
mkdir -p "$TARGET_HOME/.config/autostart" /etc/xdg/autostart
cat << EOF > "$TARGET_HOME/.config/autostart/rf-kit-gui.desktop"
[Desktop Entry]
Name=rf-kit-gui
Comment=Starts RF-KIT Fullscreen Interface
Type=Application
Exec=$TARGET_HOME/Desktop/start_gui.sh
Terminal=false
X-GNOME-Autostart-enabled=true
EOF
chmod +x "$TARGET_HOME/.config/autostart/rf-kit-gui.desktop" 2>/dev/null || true
cp -f "$TARGET_HOME/.config/autostart/rf-kit-gui.desktop" /etc/xdg/autostart/rf-kit-gui.desktop 2>/dev/null || true
rm -f "$TARGET_HOME/.config/lxsession/LXDE-pi/autostart" 2>/dev/null || true

chown -R "$TARGET_USER:$TARGET_USER" "$TARGET_HOME" 2>/dev/null || true

# ------------------------------------------------------------------------------
# Step 7/7: Clean Hooks, Lock Cloud-Init, & Reboot to Completion Dialog
# ------------------------------------------------------------------------------
show_step "7/7" "Finalizing boot config, locking firstboot & rebooting to completion dialog..."
mkdir -p /etc/cloud && touch /etc/cloud/cloud-init.disabled 2>/dev/null || true

if [ -f "$BOOT_DIR/config.txt" ]; then
    grep -q "dtoverlay=vc4-kms-v3d" "$BOOT_DIR/config.txt" || echo "dtoverlay=vc4-kms-v3d" >> "$BOOT_DIR/config.txt"
    grep -q "dtoverlay=disable-bt" "$BOOT_DIR/config.txt" || echo "dtoverlay=disable-bt" >> "$BOOT_DIR/config.txt"
    grep -q "enable_uart=1" "$BOOT_DIR/config.txt" || echo "enable_uart=1" >> "$BOOT_DIR/config.txt"
fi
if [ -f "$BOOT_DIR/cmdline.txt" ]; then
    sed -i 's| *systemd\.run=[^ ]*||g' "$BOOT_DIR/cmdline.txt" 2>/dev/null || true
fi

echo "=========================================================="
echo "Firstboot Setup Complete! Booting desktop to show Reboot confirmation dialog..."
echo "=========================================================="
sync
if [ "$CLOUDINIT_MODE" = "1" ]; then
    # Schedule detached reboot so cloud-final.service exits cleanly without systemd shutdown deadlock
    if command -v systemd-run >/dev/null 2>&1; then
        systemd-run --no-block --unit=jrfk-firstboot-reboot --on-active=4 /sbin/reboot 2>/dev/null || \
            (sleep 4 && /sbin/reboot -f) >/dev/null 2>&1 </dev/null &
    else
        (sleep 4 && /sbin/reboot -f) >/dev/null 2>&1 </dev/null &
    fi
    exit 0
fi
sleep 2
reboot
