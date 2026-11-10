#!/bin/bash
set -e

echo "=========================================================="
echo "JRFK Finalization: 64-bit Turnkey Appliance Mode"
echo "=========================================================="

# 1. Hostname configuration
echo "[*] Setting hostname to K7BIT..."
echo "K7BIT" > /mnt/sd_rootfs/etc/hostname
cat << 'EOF' > /mnt/sd_rootfs/etc/hosts
127.0.0.1	localhost
::1		localhost ip6-localhost ip6-loopback
ff02::1		ip6-allnodes
ff02::2		ip6-allrouters

127.0.1.1	K7BIT rfk
EOF

# 2. Autologin and Session (User pi, pure X11 LXDE/Openbox)
echo "[*] Configuring LightDM and autologin for user pi (Session: rpd-x)..."
sed -i 's/^autologin-user=.*/autologin-user=pi/' /mnt/sd_rootfs/etc/lightdm/lightdm.conf
sed -i 's/^autologin-session=.*/autologin-session=rpd-x/' /mnt/sd_rootfs/etc/lightdm/lightdm.conf
sed -i 's/--autologin [a-zA-Z0-9_-]*/--autologin pi/' /mnt/sd_rootfs/etc/systemd/system/getty@tty1.service.d/autologin.conf 2>/dev/null || true

# 3. Purge setup wizards & prompts
echo "[*] Ensuring setup wizards and first-boot prompts are purged..."
rm -f /mnt/sd_rootfs/etc/xdg/autostart/pprompt.desktop
rm -f /mnt/sd_rootfs/etc/xdg/autostart/piwiz.desktop
rm -f /mnt/sd_rootfs/etc/systemd/system/multi-user.target.wants/rfk-firstboot.service
rm -f /mnt/sd_rootfs/etc/systemd/system/rfk-firstboot.service

# 4. SocketCAN can0 configuration
echo "[*] Configuring can0 network interface & systemd service..."
mkdir -p /mnt/sd_rootfs/etc/network/interfaces.d
cat << 'EOF' > /mnt/sd_rootfs/etc/network/interfaces.d/can0
auto can0
iface can0 can static
    bitrate 250000
    up ifconfig can0 txqueuelen 1000
EOF

cat << 'EOF' > /mnt/sd_rootfs/etc/systemd/system/can0.service
[Unit]
Description=SocketCAN can0 Interface Setup
After=network.target

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/sbin/ip link set can0 type can bitrate 250000
ExecStart=/sbin/ip link set can0 txqueuelen 1000
ExecStart=/sbin/ip link set can0 up
ExecStop=/sbin/ip link set can0 down

[Install]
WantedBy=multi-user.target
EOF
mkdir -p /mnt/sd_rootfs/etc/systemd/system/multi-user.target.wants
ln -sf /etc/systemd/system/can0.service /mnt/sd_rootfs/etc/systemd/system/multi-user.target.wants/can0.service

# 5. Disable Bluetooth to free UART and prevent serial contention
echo "[*] Disabling Bluetooth services..."
rm -f /mnt/sd_rootfs/etc/systemd/system/multi-user.target.wants/bluetooth.service 2>/dev/null || true
rm -f /mnt/sd_rootfs/etc/systemd/system/multi-user.target.wants/hciuart.service 2>/dev/null || true

# 6. Ensure RF-KIT Autostart on boot
echo "[*] Configuring RF-KIT autostart for user pi..."
mkdir -p /mnt/sd_rootfs/home/pi/.config/autostart
cat << 'EOF' > /mnt/sd_rootfs/home/pi/.config/autostart/rf-kit-gui.desktop
[Desktop Entry]
Name=rf-kit-gui
Comment=starts rf kit gui
Type=Application
Exec=/home/pi/Desktop/start_gui.sh
Terminal=false
EOF

# 7. Desktop shortcuts
echo "[*] Creating Desktop shortcuts (RF-KIT GUI & K7BIT Cookbook)..."
mkdir -p /mnt/sd_rootfs/home/pi/Desktop
cat << 'EOF' > /mnt/sd_rootfs/home/pi/Desktop/rf-kit-gui.desktop
[Desktop Entry]
Name=RF-KIT Amplifier GUI
Comment=Start RF-KIT Linear Amplifier Application
Type=Application
Exec=/home/pi/Desktop/start_gui.sh
Icon=utilities-terminal
Terminal=false
Categories=HamRadio;Utility;
EOF

cat << 'EOF' > /mnt/sd_rootfs/home/pi/Desktop/K7BIT_B26_Cookbook.desktop
[Desktop Entry]
Name=K7BIT B26 Cookbook Manual
Comment=Open K7BIT End-to-End Builders and Operators Guide
Type=Application
Exec=xdg-open /home/pi/Desktop/K7BIT_B26_Cookbook.html
Icon=help-browser
Terminal=false
Categories=Documentation;HamRadio;
EOF

# 8. Clean up stale log files in Desktop
rm -f /mnt/sd_rootfs/home/pi/Desktop/rf-kit-gui.log*

# 9. Verify start_gui.sh
cat << 'EOF' > /mnt/sd_rootfs/home/pi/Desktop/start_gui.sh
#!/bin/bash
cd /home/pi/rf-kit-statics

if [[ -f rf-kit-gui.log && \
      $(stat -c%s rf-kit-gui.log) -gt 0 && \
      -f .rf-kit-gui.log.ts && \
      .migration.json -ot .rf-kit-gui.log.ts ]]; then
  mv rf-kit-gui.log rf-kit-gui.log.old
fi

touch .rf-kit-gui.log.ts
python3 gui_starter.py &>> rf-kit-gui.log
EOF
chmod +x /mnt/sd_rootfs/home/pi/Desktop/start_gui.sh

# 10. Copy K7BIT Cookbook files to Desktop
cp -a "/mnt/d/JRFK/docs/K7BIT B26 Cookbook Vol 1 R1.5.docx" /mnt/sd_rootfs/home/pi/Desktop/
cp -a /mnt/d/JRFK/docs/K7BIT_B26_Cookbook.html /mnt/sd_rootfs/home/pi/Desktop/

# 11. Ensure proper permissions across /home/pi
echo "[*] Setting ownership of /home/pi to pi:pi (UID 1000)..."
chown -R 1000:1000 /mnt/sd_rootfs/home/pi
chmod +x /mnt/sd_rootfs/home/pi/Desktop/*.desktop
chmod +x /mnt/sd_rootfs/home/pi/rf-kit-statics/gui_starter.py

# 12. Display mode verification in boot cmdline.txt
if [ -f /mnt/sd_boot/cmdline.txt ]; then
    if ! grep -q 'video=HDMI-A-1:1024x600' /mnt/sd_boot/cmdline.txt; then
        sed -i 's/$/ video=HDMI-A-1:1024x600M@60D/' /mnt/sd_boot/cmdline.txt
    fi
fi

echo "[*] Syncing filesystems to SD card..."
sync

echo "[+] SUCCESS: Finalization completed cleanly!"
