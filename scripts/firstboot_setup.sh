#!/bin/bash
# ==============================================================================
# JRFK Universal 64-bit First-Boot Auto-Migrator
# Target Hardware: Raspberry Pi 4 Model B (4GB) & Raspberry Pi 5
# Target OS: Raspberry Pi OS 64-bit (Debian Bookworm aarch64)
# Author: John Birdlebough (K7BIT/AE)
# Contributor: John Stafford
# ==============================================================================

set +e
LOGFILE="/var/log/jrfk_firstboot.log"
exec > >(tee -a "$LOGFILE") 2>&1

# ------------------------------------------------------------------------------
# Progress Display Helper: Writes high-contrast visual status to HDMI screen
# ------------------------------------------------------------------------------
show_step() {
    local num="$1"
    local title="$2"
    echo ""
    echo "=========================================================="
    echo ">>> [RF-KIT MIGRATION STEP $num] $title"
    echo "=========================================================="
    echo ""

    # Send message to Plymouth splash if active
    if command -v plymouth >/dev/null 2>&1; then
        plymouth display-message --text="[RF-KIT STEP $num] $title" 2>/dev/null || true
    fi

    # Output directly to active virtual terminal /dev/tty1 and /dev/console
    echo -e "\n\033[1;32m>>> [RF-KIT MIGRATION STEP $num] $title\033[0m\n" > /dev/tty1 2>/dev/null || true
    echo -e "\n>>> [RF-KIT MIGRATION STEP $num] $title\n" > /dev/console 2>/dev/null || true
}

# ------------------------------------------------------------------------------
# 0. Initialize Display Console
# ------------------------------------------------------------------------------
if command -v plymouth >/dev/null 2>&1; then
    plymouth quit 2>/dev/null || true
fi
chvt 1 2>/dev/null || true
clear > /dev/tty1 2>/dev/null || true

cat << 'BANNER' > /dev/tty1 2>/dev/null || true

 ================================================================
           RF-KIT 64-BIT AUTOMATED APPLIANCE MIGRATION           
               K7BIT / RF2K+ & RF2K-S Amplifier System           
 ================================================================

BANNER

# ------------------------------------------------------------------------------
# Locate Boot Partition and Payload Directory
# ------------------------------------------------------------------------------
BOOT_DIR="/boot/firmware"
[ ! -d "$BOOT_DIR" ] && BOOT_DIR="/boot"

PAYLOAD_DIR="$BOOT_DIR/jrfk_payload"
[ ! -d "$PAYLOAD_DIR" ] && PAYLOAD_DIR="/boot/jrfk_payload"
[ ! -d "$PAYLOAD_DIR" ] && PAYLOAD_DIR="/opt/jrfk"

# ------------------------------------------------------------------------------
# Step 1: Filesystem & Environment Preparation
# ------------------------------------------------------------------------------
show_step "1/6" "Preparing 64-bit environment and expanding storage..."
if command -v raspi-config >/dev/null 2>&1; then
    raspi-config nonint do_expand_rootfs 2>/dev/null || true
fi

# ------------------------------------------------------------------------------
# Step 2: Unpack RF-KIT Application Suite
# ------------------------------------------------------------------------------
show_step "2/6" "Deploying RF-KIT v2.00 & v1.98 Application Suite..."
cd /home/pi
if [ -f "$PAYLOAD_DIR/rfk_bundle.tar.gz" ]; then
    tar -xzf "$PAYLOAD_DIR/rfk_bundle.tar.gz" -C /
elif [ -f /opt/jrfk/rfk_bundle.tar.gz ]; then
    tar -xzf /opt/jrfk/rfk_bundle.tar.gz -C /
fi

# ------------------------------------------------------------------------------
# Step 3: Restore Operator Calibrations, Settings & Documentation
# ------------------------------------------------------------------------------
show_step "3/6" "Restoring Operator Calibrations & K7BIT Cookbook..."
mkdir -p /home/pi/rf-kit-statics /home/pi/Desktop /home/pi/.config/autostart

SETTINGS_DIR="$PAYLOAD_DIR/user_settings_backup"
[ ! -d "$SETTINGS_DIR" ] && SETTINGS_DIR="/opt/jrfk/user_settings_backup"

if [ -d "$SETTINGS_DIR" ]; then
    cp -a "$SETTINGS_DIR"/* /home/pi/rf-kit-statics/ 2>/dev/null || true
    cp -a "$SETTINGS_DIR"/.* /home/pi/rf-kit-statics/ 2>/dev/null || true
    # Place K7BIT Cookbook on Desktop
    cp -a "$SETTINGS_DIR"/*Cookbook* /home/pi/Desktop/ 2>/dev/null || true
fi

# Create Desktop Shortcut for K7BIT Cookbook
cat << 'EOF' > /home/pi/Desktop/K7BIT_B26_Cookbook.desktop
[Desktop Entry]
Name=K7BIT B26 Cookbook Manual
Comment=Open K7BIT End-to-End Builders and Operators Guide
Type=Application
Exec=xdg-open /home/pi/Desktop/K7BIT_B26_Cookbook.html
Icon=help-browser
Terminal=false
Categories=Documentation;HamRadio;
EOF
chmod +x /home/pi/Desktop/K7BIT_B26_Cookbook.desktop 2>/dev/null || true

# ------------------------------------------------------------------------------
# Step 4: Hardware Interfaces (USB Serial MCU, CAN bus, Bluetooth disable)
# ------------------------------------------------------------------------------
show_step "4/6" "Configuring Hardware Interfaces (USB MCU & SocketCAN)..."

# Free UART / prevent port contention
systemctl disable --now hciuart.service 2>/dev/null || true
systemctl disable --now bluealsa.service 2>/dev/null || true
systemctl disable --now bluetooth.service 2>/dev/null || true

# Universal udev rules for Pi 4 & Pi 5 Controller MCU
cat << 'EOF' > /etc/udev/rules.d/99-rfk-controller.rules
# Universal RF-KIT Microcontroller Link for both Pi 4 and Pi 5
KERNEL=="ttyACM*|ttyUSB*", SUBSYSTEM=="tty", MODE="0666", GROUP="dialout", SYMLINK+="rfk_controller"
KERNEL=="ttyACM*|ttyUSB*", SUBSYSTEM=="tty", MODE="0666", GROUP="dialout", SYMLINK+="serial/by-path/platform-fd500000.pcie-pci-0000:01:00.0-usb-0:1.3:1.0-port0"
EOF
udevadm control --reload-rules 2>/dev/null || true
udevadm trigger 2>/dev/null || true

# SocketCAN can0 interface
cat << 'EOF' > /etc/network/interfaces.d/can0
auto can0
iface can0 can static
    bitrate 250000
    up ifconfig can0 txqueuelen 1000
EOF

# Ensure user pi is in hardware groups
usermod -aG dialout,tty,video,audio pi 2>/dev/null || true

# Setup 64-bit Hamlib Bridge for Python 3.11 if module is available
for GUI_DIR in /home/pi/rf-kit-gui_v200 /home/pi/rf-kit-gui_v198; do
    if [ -d "$GUI_DIR" ]; then
        mkdir -p "$GUI_DIR/hamlib/v4_6_5_bindings_backport/lib/python3_7/site_packages"
        python3 -c "import Hamlib; import os; p=os.path.dirname(Hamlib.__file__); print(p)" > /tmp/hamlib_path 2>/dev/null || true
        if [ -s /tmp/hamlib_path ]; then
            HL_PATH=$(cat /tmp/hamlib_path)
            ln -sf "$HL_PATH/Hamlib.py" "$GUI_DIR/hamlib/v4_6_5_bindings_backport/lib/python3_7/site_packages/Hamlib.py" 2>/dev/null || true
            ln -sf "$HL_PATH/_Hamlib.so" "$GUI_DIR/hamlib/v4_6_5_bindings_backport/lib/python3_7/site_packages/_Hamlib.so" 2>/dev/null || true
        fi
    fi
done

# ------------------------------------------------------------------------------
# Step 5: Configure Fullscreen X11 Touchscreen & Autostart
# ------------------------------------------------------------------------------
show_step "5/6" "Configuring Fullscreen Touchscreen & X11 Autostart..."

# Switch Bookworm desktop backend to X11 (Openbox) for rock-solid Tkinter touchscreen operation
if command -v raspi-config >/dev/null 2>&1; then
    raspi-config nonint do_wayland W1 2>/dev/null || true
    raspi-config nonint do_boot_behaviour B4 2>/dev/null || true
fi

# Ensure Desktop launcher start_gui.sh exists
if [ ! -f /home/pi/Desktop/start_gui.sh ]; then
    cat << 'EOF' > /home/pi/Desktop/start_gui.sh
#!/bin/bash
cd /home/pi/rf-kit-statics
python3 gui_starter.py &>> rf-kit-gui.log
EOF
fi
chmod +x /home/pi/Desktop/start_gui.sh 2>/dev/null || true
chmod +x /home/pi/rf-kit-statics/gui_starter.py 2>/dev/null || true

# User autostart
cat << 'EOF' > /home/pi/.config/autostart/rf-kit-gui.desktop
[Desktop Entry]
Name=rf-kit-gui
Comment=Starts RF-KIT Touchscreen Interface
Type=Application
Exec=/home/pi/Desktop/start_gui.sh
Terminal=false
X-GNOME-Autostart-enabled=true
EOF
chmod +x /home/pi/.config/autostart/rf-kit-gui.desktop 2>/dev/null || true

# System-wide autostart to guarantee startup regardless of session type
mkdir -p /etc/xdg/autostart
cp -f /home/pi/.config/autostart/rf-kit-gui.desktop /etc/xdg/autostart/rf-kit-gui.desktop 2>/dev/null || true

# Set station hostname
hostnamectl set-hostname K7BIT 2>/dev/null || true
sed -i 's/127.0.1.1.*/127.0.1.1\tK7BIT rfk/' /etc/hosts 2>/dev/null || true

# Ensure proper ownership of user home directory
chown -R pi:pi /home/pi

# Configure boot partition settings (Display & Overlays)
if [ -f "$BOOT_DIR/config.txt" ]; then
    grep -q "dtoverlay=vc4-kms-v3d" "$BOOT_DIR/config.txt" || echo "dtoverlay=vc4-kms-v3d" >> "$BOOT_DIR/config.txt"
    grep -q "dtoverlay=disable-bt" "$BOOT_DIR/config.txt" || echo "dtoverlay=disable-bt" >> "$BOOT_DIR/config.txt"
fi

# ------------------------------------------------------------------------------
# Step 6: Finalize Migration & Reboot directly into RF-KIT GUI
# ------------------------------------------------------------------------------
show_step "6/6" "Finalizing Migration & Launching RF-KIT Touchscreen GUI..."

# Clean up cmdline.txt hook so firstboot does not run on subsequent boots
if [ -f "$BOOT_DIR/cmdline.txt" ]; then
    sed -i 's| *systemd\.run=[^ ]*||g' "$BOOT_DIR/cmdline.txt" 2>/dev/null || true
fi

# Non-blocking background package verification (does NOT delay boot)
(
    export DEBIAN_FRONTEND=noninteractive
    if ! python3 -c "import can" 2>/dev/null; then
        apt-get update -qq 2>/dev/null && apt-get install -y -qq python3-can can-utils 2>/dev/null || true
    fi
) &

echo "=========================================================="
echo "Migration Complete! System is rebooting directly into RF-KIT GUI..."
echo "=========================================================="
sync
sleep 2
reboot
