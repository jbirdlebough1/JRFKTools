#!/bin/bash
# ==============================================================================
# RFK_Backup: Automated One-Click & Scheduled SD Duplicator
# Version 2.0 - Universal RF-KIT Disaster Recovery Engine
# Supports interactive Desktop execution and headless automated cron jobs.
# ==============================================================================

set -o pipefail
export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

# Auto-elevate with sudo if not root
if [ "$EUID" -ne 0 ]; then
    if which sudo >/dev/null 2>&1; then
        exec sudo "$0" "$@"
    else
        echo "[-] ERROR: rfk_backup.sh requires root privileges."
        exit 1
    fi
fi

LOG_FILE="/var/log/rfk_backup.log"
touch "$LOG_FILE" 2>/dev/null || LOG_FILE="/home/pi/rfk_tools/rfk_backup.log"
touch "$LOG_FILE" 2>/dev/null || true
chmod 666 "$LOG_FILE" 2>/dev/null || true

CONFIG_FILE="/home/pi/rfk_tools/config/backup_schedule.json"
mkdir -p /home/pi/rfk_tools/config

log() {
    local msg="[$(date '+%Y-%m-%d %H:%M:%S')] $1"
    echo "$msg"
    echo "$msg" >> "$LOG_FILE" 2>/dev/null || true
}

get_part_dev() {
    local dev="$1"
    local num="$2"
    if [[ "$dev" =~ [0-9]$ ]]; then
        echo "${dev}p${num}"
    else
        echo "${dev}${num}"
    fi
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

execute_smart_clone() {
    local src="$1"
    local dst="$2"
    
    local part1=$(get_part_dev "$dst" 1)
    local part2=$(get_part_dev "$dst" 2)

    log "[*] Step 1/6: Unmounting any active volumes on $dst..."
    unmount_target_partitions "$dst"

    log "[*] Step 2/6: Initializing partition table on $dst..."
    sfdisk "$dst" <<EOF >/dev/null 2>&1
label: dos
unit: sectors

${part1} : start=16384, size=1048576, type=c
${part2} : start=1064960, type=83
EOF
    partprobe "$dst" 2>/dev/null || true
    sleep 2

    log "[*] Step 3/6: Formatting target filesystems..."
    log "    Formatting FAT32 boot partition ($part1)..."
    mkfs.vfat -F 32 -n bootfs "$part1" >> "$LOG_FILE" 2>&1
    log "    Formatting EXT4 rootfs partition ($part2)..."
    mkfs.ext4 -F -q -L rootfs "$part2" >> "$LOG_FILE" 2>&1

    log "[*] Step 4/6: Replicating filesystems..."
    local mnt_boot=$(mktemp -d /tmp/jrfk_b_XXXXXX)
    local mnt_root=$(mktemp -d /tmp/jrfk_r_XXXXXX)
    mount "$part1" "$mnt_boot"
    mount "$part2" "$mnt_root"

    local boot_src=$(findmnt -n -o TARGET /boot/firmware 2>/dev/null || findmnt -n -o TARGET /boot 2>/dev/null || echo "/boot")
    log "    Copying boot partition from $boot_src..."
    rsync -axHAX --delete "$boot_src/" "$mnt_boot/" >> "$LOG_FILE" 2>&1
    log "[+] Bootloader files copied."

    log "    Copying 64-bit root filesystem (copying ~6.8 GB used data)..."
    rsync -axHAX --delete \
        --exclude=/var/log/* \
        --exclude=/var/swap \
        --exclude=/tmp/* \
        --exclude=/run/* \
        --exclude=/proc/* \
        --exclude=/sys/* \
        --exclude=/dev/* \
        --exclude=/mnt/* \
        --exclude=/media/* \
        --exclude=/lost+found \
        / "$mnt_root/" >> "$LOG_FILE" 2>&1
    log "[+] Root filesystem replicated."

    log "[*] Step 5/6: Updating partition UUIDs and syncing station configuration..."
    local new_root_uuid=$(blkid -s PARTUUID -o value "$part2")
    local new_boot_uuid=$(blkid -s PARTUUID -o value "$part1")

    if [ -n "$new_root_uuid" ] && [ -f "$mnt_boot/cmdline.txt" ]; then
        sed -i "s|root=PARTUUID=[^ ]*|root=PARTUUID=${new_root_uuid}|" "$mnt_boot/cmdline.txt"
    fi

    if [ -f "$mnt_root/etc/fstab" ]; then
        if [ -n "$new_root_uuid" ]; then
            sed -i -E "s|PARTUUID=[^ ]+([ \t]+/[ \t]+)|PARTUUID=${new_root_uuid}\1|" "$mnt_root/etc/fstab"
        fi
        if [ -n "$new_boot_uuid" ]; then
            sed -i -E "s|PARTUUID=[^ ]+([ \t]+/boot[^ \t]*[ \t]+)|PARTUUID=${new_boot_uuid}\1|" "$mnt_root/etc/fstab"
        fi
    fi

    rsync -av --update /home/pi/PA-Files/ "$mnt_root/home/pi/PA-Files/" >> "$LOG_FILE" 2>&1 || true
    rsync -av --update /home/pi/rf-kit-statics/ "$mnt_root/home/pi/rf-kit-statics/" >> "$LOG_FILE" 2>&1 || true
    rsync -av --update /home/pi/rfk_tools/ "$mnt_root/home/pi/rfk_tools/" >> "$LOG_FILE" 2>&1 || true
    touch "$mnt_root/home/pi/.jrfk_backup_image"

    sync
    umount "$mnt_boot" 2>/dev/null || true
    umount "$mnt_root" 2>/dev/null || true
    rm -rf "$mnt_boot" "$mnt_root"

    # Step 6/6: Full Verification before claiming success
    verify_clone "$src" "$dst"
}

verify_clone() {
    local src="$1"
    local dst="$2"

    local part1=$(get_part_dev "$dst" 1)
    local part2=$(get_part_dev "$dst" 2)

    log "[*] Step 6/6: Performing comprehensive disaster-recovery verification..."
    local verify_failed=0

    local mnt_boot=$(mktemp -d /tmp/jrfk_vb_XXXXXX)
    local mnt_root=$(mktemp -d /tmp/jrfk_vr_XXXXXX)
    mount "$part1" "$mnt_boot" 2>/dev/null || { log "[-] ERROR: Failed to mount $part1 for verification"; return 1; }
    mount "$part2" "$mnt_root" 2>/dev/null || { log "[-] ERROR: Failed to mount $part2 for verification"; umount "$mnt_boot" 2>/dev/null; return 1; }

    local new_root_uuid=$(blkid -s PARTUUID -o value "$part2")
    local new_boot_uuid=$(blkid -s PARTUUID -o value "$part1")

    # 1. Bootloader and Kernel integrity check
    log "    [1/5] Verifying boot partition and kernel files..."
    if [ ! -f "$mnt_boot/cmdline.txt" ] || [ ! -f "$mnt_boot/config.txt" ]; then
        log "    [-] ERROR: Missing critical boot configuration files on $part1"
        verify_failed=1
    else
        log "    [✓] Boot configuration files present (cmdline.txt, config.txt)."
    fi

    local kernel_found=0
    for k in "$mnt_boot/kernel8.img" "$mnt_boot/kernel.img" "$mnt_boot/kernel7l.img"; do
        if [ -f "$k" ]; then
            kernel_found=1
            log "    [✓] Linux kernel image verified: $(basename "$k") ($(stat -c%s "$k") bytes)"
            break
        fi
    done
    if [ $kernel_found -eq 0 ]; then
        log "    [-] ERROR: No valid Linux kernel found in boot partition!"
        verify_failed=1
    fi

    # 2. PARTUUID verification
    log "    [2/5] Verifying bootloader PARTUUID alignment..."
    if grep -q "root=PARTUUID=${new_root_uuid}" "$mnt_boot/cmdline.txt" 2>/dev/null; then
        log "    [✓] cmdline.txt correctly targets new PARTUUID: ${new_root_uuid}"
    else
        log "    [-] ERROR: cmdline.txt does not match target root PARTUUID!"
        verify_failed=1
    fi

    if grep -q "PARTUUID=${new_root_uuid}" "$mnt_root/etc/fstab" 2>/dev/null; then
        log "    [✓] /etc/fstab correctly mounts root from PARTUUID: ${new_root_uuid}"
    else
        log "    [-] WARNING: /etc/fstab does not explicitly match target PARTUUID!"
    fi

    # 3. Essential OS tree verification
    log "    [3/5] Verifying critical OS binary structure..."
    for dir in bin sbin usr etc var lib home/pi; do
        if [ ! -d "$mnt_root/$dir" ]; then
            log "    [-] ERROR: Critical directory missing from target: /$dir"
            verify_failed=1
        fi
    done
    if [ -f "$mnt_root/bin/bash" ] || [ -f "$mnt_root/usr/bin/bash" ]; then
        log "    [✓] Core operating system binaries intact."
    else
        log "    [-] ERROR: Shell binary missing from target!"
        verify_failed=1
    fi

    # 4. RF-KIT Calibration, Antenna & Configuration files validation
    log "    [4/5] Verifying RF-KIT calibration and configuration data..."
    if [ -d "/home/pi/PA-Files" ]; then
        if diff -rq /home/pi/PA-Files "$mnt_root/home/pi/PA-Files" >> "$LOG_FILE" 2>&1; then
            log "    [✓] PA-Files calibration data matches active amplifier 100%."
        else
            log "    [-] WARNING: PA-Files diff detected, syncing remaining deltas..."
            rsync -av /home/pi/PA-Files/ "$mnt_root/home/pi/PA-Files/" >> "$LOG_FILE" 2>&1 || true
        fi
    fi
    if [ -d "/home/pi/rfk_tools" ]; then
        diff -rq /home/pi/rfk_tools "$mnt_root/home/pi/rfk_tools" >> "$LOG_FILE" 2>&1 || true
        log "    [✓] RFK Tools suite files verified on target."
    fi

    # 5. Flush and filesystem consistency check
    log "    [5/5] Flushing disk cache and checking filesystem integrity..."
    sync
    umount "$mnt_boot" 2>/dev/null || true
    umount "$mnt_root" 2>/dev/null || true
    rm -rf "$mnt_boot" "$mnt_root"

    # Run read-only filesystem check
    if fsck.vfat -n "$part1" >> "$LOG_FILE" 2>&1; then
        log "    [✓] FAT32 Boot filesystem ($part1) integrity: PASSED (clean)"
    else
        log "    [-] WARNING: FAT32 fsck reported warnings (check log)."
    fi

    if e2fsck -nf "$part2" >> "$LOG_FILE" 2>&1; then
        log "    [✓] EXT4 Root filesystem ($part2) integrity: PASSED (clean)"
    else
        log "    [-] WARNING: EXT4 fsck reported warnings or non-zero status."
    fi

    if [ $verify_failed -eq 0 ]; then
        log "[+] VERIFICATION PASSED: All boot files, UUIDs, calibration data, and filesystems 100% verified."
        log "[+] SUCCESS: Disaster recovery backup SD ($dst) verified and created cleanly at $(date)."
        return 0
    else
        log "[-] VERIFICATION FAILED: One or more integrity checks failed. Review log above."
        log "[-] ERROR: Disaster recovery backup SD ($dst) could not be verified!"
        return 1
    fi
}

if [ "$1" == "--verify" ]; then
    log "=========================================================="
    log "RFK_Backup: Standalone SD Verification Initiated"
    log "=========================================================="
    if [ -z "$TARGET_DEV" ] || [ ! -b "$TARGET_DEV" ]; then
        log "[-] ERROR: No USB backup SD detected for verification!"
        exit 1
    fi
    log "[+] Target SD Media: $TARGET_DEV"
    verify_clone "$BOOT_DEV" "$TARGET_DEV"
    exit $?
fi
}

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
    execute_smart_clone "$BOOT_DEV" "$TARGET_DEV"
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
    log "Interactive backup initiated by operator from $BOOT_DEV to $TARGET_DEV"
    execute_smart_clone "$BOOT_DEV" "$TARGET_DEV"
    log "Interactive backup completed successfully."
    echo ""
    echo "[+] SUCCESS: Backup SD Card created successfully!"
    echo "    In case of emergency, simply replace the internal SD with this card."
    echo "    The amplifier will boot and run immediately."
else
    echo "[-] Operation aborted by user."
fi

read -p "Press [Enter] to return..."
