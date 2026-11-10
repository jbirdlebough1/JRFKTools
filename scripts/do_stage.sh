#!/bin/bash
set -e

echo "[*] Step 1: Unpacking rfk_bundle.tar.gz into /mnt/new_rootfs/..."
tar -xzf /mnt/d/JRFK/extracted/rfk_bundle.tar.gz -C /mnt/new_rootfs/

echo "[*] Step 2: Restoring user settings (config.json with K7BIT)..."
mkdir -p /mnt/new_rootfs/home/pi/rf-kit-statics
cp -a /mnt/d/JRFK/extracted/user_settings_backup/* /mnt/new_rootfs/home/pi/rf-kit-statics/
cp -a /mnt/d/JRFK/extracted/user_settings_backup/.migration.json /mnt/new_rootfs/home/pi/rf-kit-statics/ 2>/dev/null || true
cp -a /mnt/d/JRFK/extracted/user_settings_backup/.rf-kit-gui.log.ts /mnt/new_rootfs/home/pi/rf-kit-statics/ 2>/dev/null || true

echo "[*] Step 3: Copying K7BIT Cookbook to /home/pi/Desktop/..."
mkdir -p /mnt/new_rootfs/home/pi/Desktop
cp -a "/mnt/d/JRFK/docs/K7BIT B26 Cookbook Vol 1 R1.5.docx" /mnt/new_rootfs/home/pi/Desktop/
cp -a /mnt/d/JRFK/docs/K7BIT_B26_Cookbook.html /mnt/new_rootfs/home/pi/Desktop/

echo "[*] Step 4: Creating Desktop shortcut for K7BIT Cookbook..."
cat << 'EOF' > /mnt/new_rootfs/home/pi/Desktop/K7BIT_B26_Cookbook.desktop
[Desktop Entry]
Name=K7BIT B26 Cookbook Manual
Comment=Open K7BIT End-to-End Builders and Operators Guide
Type=Application
Exec=xdg-open /home/pi/Desktop/K7BIT_B26_Cookbook.html
Icon=help-browser
Terminal=false
Categories=Documentation;HamRadio;
EOF
chmod +x /mnt/new_rootfs/home/pi/Desktop/K7BIT_B26_Cookbook.desktop

echo "[*] Step 5: Creating Universal udev rules for Pi 4 & Pi 5..."
mkdir -p /mnt/new_rootfs/etc/udev/rules.d
cat << 'EOF' > /mnt/new_rootfs/etc/udev/rules.d/99-rfk-controller.rules
# Universal RF-KIT Microcontroller Link for both Pi 4 and Pi 5
KERNEL=="ttyACM*|ttyUSB*", SUBSYSTEM=="tty", MODE="0666", GROUP="dialout", SYMLINK+="rfk_controller"
KERNEL=="ttyACM*|ttyUSB*", SUBSYSTEM=="tty", MODE="0666", GROUP="dialout", SYMLINK+="serial/by-path/platform-fd500000.pcie-pci-0000:01:00.0-usb-0:1.3:1.0-port0"
EOF

echo "[*] Step 6: Staging first-boot auto-migration script and payload..."
mkdir -p /mnt/new_rootfs/opt/jrfk
cp -a /mnt/d/JRFK/extracted/rfk_bundle.tar.gz /mnt/new_rootfs/opt/jrfk/
cp -a /mnt/d/JRFK/extracted/user_settings_backup /mnt/new_rootfs/opt/jrfk/
cp -a /mnt/d/JRFK/scripts/firstboot_setup.sh /mnt/new_rootfs/opt/jrfk/firstboot_setup.sh
chmod +x /mnt/new_rootfs/opt/jrfk/firstboot_setup.sh

echo "[*] Step 7: Installing rfk-firstboot systemd service unit..."
cat << 'EOF' > /mnt/new_rootfs/etc/systemd/system/rfk-firstboot.service
[Unit]
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
EOF

mkdir -p /mnt/new_rootfs/etc/systemd/system/multi-user.target.wants
ln -sf /etc/systemd/system/rfk-firstboot.service /mnt/new_rootfs/etc/systemd/system/multi-user.target.wants/rfk-firstboot.service

echo "[*] Step 8: Configuring /boot/firmware/cmdline.txt and config.txt..."
if [ -f /mnt/new_boot/cmdline.txt ]; then
    if ! grep -q 'video=HDMI-A-1:1024x600' /mnt/new_boot/cmdline.txt; then
        sed -i 's/$/ video=HDMI-A-1:1024x600M@60D/' /mnt/new_boot/cmdline.txt
    fi
fi

if [ -f /mnt/new_boot/config.txt ]; then
    if ! grep -q 'dtoverlay=vc4-kms-v3d' /mnt/new_boot/config.txt; then
        echo 'dtoverlay=vc4-kms-v3d' >> /mnt/new_boot/config.txt
    fi
    if ! grep -q 'dtoverlay=disable-bt' /mnt/new_boot/config.txt; then
        echo 'dtoverlay=disable-bt' >> /mnt/new_boot/config.txt
    fi
fi

echo "[*] Step 9: Setting ownership to user pi (UID 1000)..."
chown -R 1000:1000 /mnt/new_rootfs/home/pi

echo "[*] Step 10: Syncing all files to SD card..."
sync

echo "[+] SUCCESS: Staging complete!"
