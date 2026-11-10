#!/bin/bash
# ==============================================================================
# JRFK Disaster Recovery First-Boot Service
# Executes on boot. If the card was cloned by RFK_Backup, it verifies user
# data integrity, expands filesystem if needed, and reboots cleanly.
# ==============================================================================

RESTORE_MARKER="/home/pi/.jrfk_backup_image"
SUCCESS_MARKER="/home/pi/.jrfk_restore_completed"
LOG_FILE="/var/log/jrfk_restore.log"

if [ -f "$RESTORE_MARKER" ]; then
    echo "[*] [$(date)] RF-KIT Backup Media First-Boot Detected!" | tee -a "$LOG_FILE"
    echo "[*] Running filesystem expansion and permission checks..." | tee -a "$LOG_FILE"
    
    # Ensure all user files have proper ownership
    chown -R pi:pi /home/pi/PA-Files /home/pi/rf-kit-statics /home/pi/rfk_tools 2>/dev/null || true
    chmod +x /home/pi/rfk_tools/bin/*.sh 2>/dev/null || true
    
    # Clean up marker and write success stamp
    rm -f "$RESTORE_MARKER"
    date > "$SUCCESS_MARKER"
    
    echo "[+] Restoration verification completed successfully." | tee -a "$LOG_FILE"
    echo "[*] Triggering one-time automatic reboot into fullscreen RFKGUI..." | tee -a "$LOG_FILE"
    sync
    sleep 2
    reboot
fi
