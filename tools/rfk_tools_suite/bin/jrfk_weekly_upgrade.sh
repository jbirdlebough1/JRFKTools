#!/bin/bash
# Weekly OS Package Upgrade Automation for RF-KIT 64-Bit Appliance
# Scheduled via /etc/cron.d/jrfk_weekly_upgrade (Sundays at 04:00 AM)

LOGFILE="/var/log/jrfk_os_upgrade.log"
exec >> "$LOGFILE" 2>&1

echo "=========================================================="
echo "Starting JRFK Weekly System Upgrade at $(date)"
echo "=========================================================="

export DEBIAN_FRONTEND=noninteractive

# Update package lists
echo "[*] Updating package indexes..."
apt-get update -y

# Perform non-interactive package upgrade
echo "[*] Upgrading installed system packages..."
apt-get upgrade -y -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold"

# Clean up stale cached deb archives
echo "[*] Cleaning up package cache..."
apt-get autoremove -y
apt-get autoclean -y

# Verify Hamlib and Pillow compatibility shims remain intact after any upgrade
echo "[*] Verifying critical RF-KIT shims..."
if [ -f /usr/lib/python3/dist-packages/PIL/Image.py ]; then
    if ! grep -q "ANTIALIAS = Resampling.LANCZOS" /usr/lib/python3/dist-packages/PIL/Image.py; then
        sed -i 's/_filters_support = {/ANTIALIAS = Resampling.LANCZOS\n\n_filters_support = {/' /usr/lib/python3/dist-packages/PIL/Image.py 2>/dev/null || true
    fi
fi

echo "[+] Weekly system upgrade completed successfully at $(date)"
echo "=========================================================="
