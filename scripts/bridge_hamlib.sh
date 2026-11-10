#!/bin/bash
set -e

echo "[*] Bridging Hamlib 64-bit native bindings..."
for APP in /mnt/sd_rootfs/home/pi/rf-kit-gui_v200 /mnt/sd_rootfs/home/pi/rf-kit-gui_v198; do
    if [ -d "$APP" ]; then
        for DIR in v4_6_5_bindings_backport v4_0_rc2; do
            TARGET="$APP/hamlib/$DIR/lib/python3_7/site_packages"
            mkdir -p "$TARGET"
            rm -f "$TARGET/Hamlib.py" "$TARGET/_Hamlib.so" "$TARGET/_Hamlib.cpython-313-aarch64-linux-gnu.so"
            cp -a /mnt/sd_rootfs/usr/lib/python3/dist-packages/Hamlib.py "$TARGET/Hamlib.py"
            cp -a /mnt/sd_rootfs/usr/lib/python3/dist-packages/_Hamlib.cpython-313-aarch64-linux-gnu.so "$TARGET/_Hamlib.cpython-313-aarch64-linux-gnu.so"
            ln -sf _Hamlib.cpython-313-aarch64-linux-gnu.so "$TARGET/_Hamlib.so"
        done
    fi
done

echo "[*] Testing native Hamlib import from rf-kit-gui_v200..."
chroot /mnt/sd_rootfs python3 - << 'PYTEST'
import sys
sys.path.insert(0, '/home/pi/rf-kit-gui_v200')
from hamlib.v4_6_5_bindings_backport.lib.python3_7.site_packages import Hamlib
print(f"SUCCESS: RIG_MODEL_IC7610 = {Hamlib.RIG_MODEL_IC7610}")
PYTEST

echo "[+] Done!"
