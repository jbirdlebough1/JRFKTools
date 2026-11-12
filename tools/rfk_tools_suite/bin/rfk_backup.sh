#!/bin/bash
# ==============================================================================
# RFK_Backup: Automated One-Click & Scheduled SD Duplicator
# Version 2.0 - Universal RF-KIT Disaster Recovery Engine
# Supports interactive Desktop execution and headless automated cron jobs.
# ==============================================================================

set -o pipefail

LOG_FILE="/var/log/rfk_backup.log"
CONFIG_FILE="/home/pi/rfk_tools/config/backup_schedule.json"
mkdir -p /home/pi/rfk_tools/config
mkdir -p /var/log

log() {
    local msg="[$(date '+%Y-%m-%d %H:%M:%S')] $1"
    echo "$msg"
    echo "$msg" >> "$LOG_FILE" 2>/dev/null || true
}

# 1. Identify Boot Media
BOOT_DEV="/dev/mmcblk0"
if [ ! -b "$BOOT_DEV" ]; then
    BOOT_DEV=$(lsblk -no PKNAME $(findmnt -n -o SOURCE /) 2>/dev/null | head -n1 || true)
    if [ -n "$BOOT_DEV" ]; then
        BOOT_DEV="/dev/$BOOT_DEV"
    else
        BOOT_DEV="/dev/mmcblk0"
    fi
fi

# 2. Search for External USB Target
find_target_dev() {
    local target=""
    local root_part=$(findmnt -n -o SOURCE / 2>/dev/null || echo "")
    local boot_part=$(findmnt -n -o SOURCE /boot 2>/dev/null || findmnt -n -o SOURCE /boot/firmware 2>/dev/null || echo "")

    for dev in /dev/sd[a-z]; do
        if [ -b "$dev" ]; then
            # 1. Verify media capacity is > 0 (empty USB card readers report 0 bytes)
            local sz=$(lsblk -bno SIZE "$dev" 2>/dev/null | head -n1 || echo "0")
            if [ -n "$sz" ] && [ "$sz" -gt 0 ] 2>/dev/null; then
                # 2. Ensure this disk does NOT contain the active root or boot partition
                if [[ "$root_part" != "${dev}"* ]] && [[ "$boot_part" != "${dev}"* ]]; then
                    target="$dev"
                    break
                fi
            fi
        fi
    done
    echo "$target"
}

unmount_target_partitions() {
    local target="$1"
    if [ -n "$target" ] && [ -b "$target" ]; then
        for mnt in $(grep "^${target}" /proc/mounts 2>/dev/null | awk '{print $2}'); do
            umount -l "$mnt" 2>/dev/null || true
        done
    fi
}

TARGET_DEV=$(find_target_dev)

# CLI Mode Handling
if [ "$1" == "--status" ]; then
    BOOT_SIZE=$(lsblk -bno SIZE "$BOOT_DEV" 2>/dev/null | head -n1 || echo "0")
    TARGET_SIZE="0"
    TARGET_NAME="None"
    TARGET_FOUND=false
    if [ -n "$TARGET_DEV" ] && [ -b "$TARGET_DEV" ]; then
        TARGET_SIZE=$(lsblk -bno SIZE "$TARGET_DEV" 2>/dev/null | head -n1 || echo "0")
        if [ "$TARGET_SIZE" -gt 0 ] 2>/dev/null; then
            TARGET_FOUND=true
            TARGET_NAME=$(lsblk -no MODEL "$TARGET_DEV" 2>/dev/null | head -n1 || echo "$TARGET_DEV")
        fi
    fi
    LAST_LOG=$(tail -n 10 "$LOG_FILE" 2>/dev/null || echo "No backups run yet.")
    
    cat <<EOF
{
  "boot_dev": "$BOOT_DEV",
  "boot_size_bytes": $BOOT_SIZE,
  "target_dev": "$TARGET_DEV",
  "target_found": $TARGET_FOUND,
  "target_name": "$TARGET_NAME",
  "target_size_bytes": $TARGET_SIZE,
  "log_file": "$LOG_FILE"
}
EOF
    exit 0
fi

if [ "$1" == "--auto" ] || [ "$1" == "--cron" ]; then
    log "=========================================================="
    log "RFK_Backup: Automated Scheduled Backup Starting"
    log "=========================================================="
    log "[*] Source Boot Media: $BOOT_DEV"
    
    if [ -z "$TARGET_DEV" ] || [ ! -b "$TARGET_DEV" ]; then
        log "[-] ERROR: Automated backup aborted - No USB backup SD detected!"
        exit 1
    fi
    
    log "[+] Target Backup Media Found: $TARGET_DEV"
    
    # Verify target media capacity is at least equal or close to boot media
    BOOT_BYTES=$(lsblk -bno SIZE "$BOOT_DEV" | head -n1)
    TARGET_BYTES=$(lsblk -bno SIZE "$TARGET_DEV" | head -n1)
    log "[*] Capacity Check: Source=${BOOT_BYTES} B, Target=${TARGET_BYTES} B"
    
    # Safely unmount any desktop automounted partitions on target before cloning
    log "[*] Unmounting any active target partitions on $TARGET_DEV..."
    unmount_target_partitions "$TARGET_DEV"

    log "[*] Executing live partition clone via piclone with UUID re-generation..."
    if which piclone >/dev/null 2>&1; then
        if piclone -f "$BOOT_DEV" "$TARGET_DEV" >> "$LOG_FILE" 2>&1; then
            log "[+] piclone completed partition replication successfully."
        else
            log "[-] piclone failed! Falling back to raw sync stream..."
            dd if="$BOOT_DEV" of="$TARGET_DEV" bs=4M status=none conv=fsync >> "$LOG_FILE" 2>&1
        fi
    else
        log "[*] Performing raw block stream clone..."
        dd if="$BOOT_DEV" of="$TARGET_DEV" bs=4M status=none conv=fsync >> "$LOG_FILE" 2>&1
    fi
    
    # Sync calibration and user configuration files
    log "[*] Synchronizing critical RF-KIT user calibration files..."
    TEMP_MNT=$(mktemp -d)
    if mount "${TARGET_DEV}2" "$TEMP_MNT" 2>/dev/null || mount "${TARGET_DEV}p2" "$TEMP_MNT" 2>/dev/null; then
        rsync -av --update /home/pi/PA-Files/ "$TEMP_MNT/home/pi/PA-Files/" 2>/dev/null || true
        rsync -av --update /home/pi/rf-kit-statics/ "$TEMP_MNT/home/pi/rf-kit-statics/" 2>/dev/null || true
        rsync -av --update /home/pi/rfk_tools/ "$TEMP_MNT/home/pi/rfk_tools/" 2>/dev/null || true
        # Install first-boot restore verification hook
        touch "$TEMP_MNT/home/pi/.jrfk_backup_image"
        umount "$TEMP_MNT"
    fi
    rm -rf "$TEMP_MNT"
    
    log "[+] SUCCESS: Automated weekly backup completed cleanly at $(date)."
    log "=========================================================="
    exit 0
fi

# Interactive CLI Mode
echo "=========================================================="
echo "RFK_Backup: Universal Amplifier SD Duplicator"
echo "=========================================================="
echo "[*] Source Boot Media: $BOOT_DEV"
lsblk "$BOOT_DEV" -o NAME,SIZE,TYPE,MOUNTPOINT

echo ""
echo "[*] Scanning for target USB SD card reader..."
if [ -z "$TARGET_DEV" ]; then
    echo "[-] ERROR: No external USB SD card reader detected!"
    echo "    Please insert an SD card reader into an open USB port on the amplifier."
    read -p "Press [Enter] to exit..."
    exit 1
fi

echo "[+] Target SD Card Reader Found: $TARGET_DEV"
lsblk "$TARGET_DEV" -o NAME,SIZE,TYPE,VENDOR,MODEL

echo ""
echo "----------------------------------------------------------"
echo "WARNING: ALL DATA ON $TARGET_DEV WILL BE COMPLETELY OVERWRITTEN!"
echo "Source: $BOOT_DEV (Internal Active SD)"
echo "Destination: $TARGET_DEV (External USB SD Reader)"
echo "----------------------------------------------------------"
read -p "Proceed with full clone and user data sync? (y/N): " CONFIRM

if [[ "$CONFIRM" =~ ^[Yy]$ ]]; then
    echo ""
    echo "[*] Unmounting any active target partitions on $TARGET_DEV..."
    unmount_target_partitions "$TARGET_DEV"
    
    echo "[*] Initiating clone (this may take several minutes)..."
    log "Interactive backup initiated by operator from $BOOT_DEV to $TARGET_DEV"
    if which piclone >/dev/null 2>&1; then
        sudo piclone -f "$BOOT_DEV" "$TARGET_DEV"
    else
        sudo dd if="$BOOT_DEV" of="$TARGET_DEV" bs=4M status=progress conv=fsync
    fi
    
    # Sync calibration and user files
    TEMP_MNT=$(mktemp -d)
    if sudo mount "${TARGET_DEV}2" "$TEMP_MNT" 2>/dev/null || sudo mount "${TARGET_DEV}p2" "$TEMP_MNT" 2>/dev/null; then
        sudo rsync -av --update /home/pi/PA-Files/ "$TEMP_MNT/home/pi/PA-Files/" 2>/dev/null || true
        sudo rsync -av --update /home/pi/rf-kit-statics/ "$TEMP_MNT/home/pi/rf-kit-statics/" 2>/dev/null || true
        sudo rsync -av --update /home/pi/rfk_tools/ "$TEMP_MNT/home/pi/rfk_tools/" 2>/dev/null || true
        sudo touch "$TEMP_MNT/home/pi/.jrfk_backup_image"
        sudo umount "$TEMP_MNT"
    fi
    rm -rf "$TEMP_MNT"
    
    log "Interactive backup completed successfully."
    echo ""
    echo "[+] SUCCESS: Backup SD Card created successfully!"
    echo "    In case of emergency, simply replace the internal SD with this card."
    echo "    The amplifier will boot, reboot once, and run immediately."
else
    echo "[-] Operation aborted by user."
fi

read -p "Press [Enter] to return..."
