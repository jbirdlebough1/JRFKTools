"""
Strictly READ-ONLY Golden Master (32-bit SD) extractor, validator, and GOLD-lock guard.

Reads Partition 0 (FAT32 boot, via mounted Windows drive) and Partition 1 (Linux ext4
rootfs, via ext4_ro with GENERIC_READ only) to pull RFK application files, user data,
tuning/antenna/calibration data, and Wi-Fi/station settings into backups/ inside the project directory.
"""

import hashlib
import json
import os
import posixpath
import re
import struct
import tarfile
import threading
import time

import ext4_ro
import sd_guard
from sd_guard import SDGuardError

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DEFAULT_BACKUP_ROOT = os.path.join(BASE_DIR, "backups")
LATEST_MANIFEST_NAME = "gold_latest_manifest.json"

SKIP_DIR_NAMES = {"__pycache__", ".git", "node_modules", ".cache", "Trash"}


def _categorize_path(posix_p):
    low = posix_p.lower()
    if any(k in low for k in ("/pa-files", "tuning_data", "calibration", "antenna", "touch.cal", "touchscreen", "band_matrix")):
        return "tuning_data"
    if any(k in low for k in ("/rf-kit-gui", "/rf-kit-statics", "start_gui", "rf-kit-gui.desktop", "/autostart/")):
        return "rfk_app"
    if any(k in low for k in ("wpa_supplicant", "/etc/hostname", "/etc/hosts", "/etc/network")):
        return "network"
    if low.startswith("/boot/"):
        return "boot"
    return "user_data"


def _validate_file_bytes(posix_p, data):
    if posix_p.lower().endswith(".json"):
        try:
            json.loads(data.decode("utf-8"))
            return "VALID", "Valid JSON"
        except Exception as exc:
            return "INVALID_JSON", f"JSON parse error: {exc}"
    if len(data) == 0:
        return "WARN_EMPTY", "0-byte file"
    return "VALID", f"{len(data)} bytes"


def _parse_wifi_ssid(wpa_text):
    m = re.search(r'ssid\s*=\s*"([^"]+)"', wpa_text or "")
    return m.group(1) if m else ""


def _parse_partuuid(cmdline_text):
    m = re.search(r"root=PARTUUID=([a-fA-F0-9-]+)", cmdline_text or "")
    return m.group(1).lower() if m else ""


def _collect_ext4_targets(vol):
    """Collect candidate POSIX file paths from the Linux ext4 rootfs."""
    targets = []
    seen = set()

    def _add_file(p):
        if p not in seen:
            seen.add(p)
            targets.append(p)

    # 1. Exact system/station files
    for exact in (
        "/etc/os-release",
        "/etc/hostname",
        "/etc/hosts",
        "/etc/wpa_supplicant/wpa_supplicant.conf",
        "/etc/network/interfaces",
        "/etc/udev/rules.d/99-rfk-controller.rules",
    ):
        inode = vol.resolve_path(exact, follow_symlinks=True)
        if inode and inode.is_reg:
            _add_file(exact)

    # 2. Walk targeted directories on rootfs
    dir_roots = [
        "/home/pi/PA-Files",
        "/home/pi/rf-kit-statics",
        "/home/pi/Desktop",
        "/home/pi/.config/autostart",
        "/etc/network/interfaces.d",
        "/etc/xdg/autostart",
    ]
    # Also dynamically discover any /home/pi/rf-kit* or /home/pi/*tuning* directories
    for name, child_ino, _ in vol.list_dir("/home/pi"):
        low = name.lower()
        child = vol.read_inode(child_ino)
        full_p = f"/home/pi/{name}"
        if child.is_dir and (
            low.startswith("rf-kit")
            or "tuning" in low
            or "pa-files" in low
            or "antenna" in low
        ):
            if full_p not in dir_roots:
                dir_roots.append(full_p)
        elif child.is_reg and (
            "tuning" in low
            or "cal" in low
            or "antenna" in low
            or "cookbook" in low
            or low.endswith((".json", ".sh", ".py", ".cal"))
        ):
            _add_file(full_p)

    for root in dir_roots:
        for p, inode in vol.walk(root):
            parts = set(p.split("/"))
            if parts & SKIP_DIR_NAMES:
                continue
            if inode.is_reg:
                # Filter /etc/xdg/autostart to RFK-related desktop entries only
                if root == "/etc/xdg/autostart" and "rf-kit" not in p.lower() and "rfk" not in p.lower():
                    continue
                _add_file(p)

    return sorted(targets)


def load_latest_gold_manifest(backup_root=DEFAULT_BACKUP_ROOT):
    path = os.path.join(backup_root, LATEST_MANIFEST_NAME)
    if not os.path.isfile(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def _run_with_timeout(fn, timeout_sec=1.5, default=None):
    """Run potentially blocking Windows removable-drive I/O with a bounded wait."""
    result = [default]

    def _worker():
        try:
            result[0] = fn()
        except Exception:
            pass

    t = threading.Thread(target=_worker, daemon=True)
    t.start()
    t.join(timeout_sec)
    return result[0]


def _read_file_bytes_if_exists(path, max_bytes=None):
    if not os.path.isfile(path):
        return None
    with open(path, "rb") as f:
        return f.read(max_bytes) if max_bytes else f.read()


def check_not_gold_target(disk_info, drive_letter=None, backup_root=DEFAULT_BACKUP_ROOT):
    """
    Block write/erase/Imager operations if disk_info matches the extracted GOLD SD card.
    """
    manifest = load_latest_gold_manifest(backup_root)
    if not manifest:
        return
    fp = manifest.get("gold_fingerprint") or {}
    gold_sig = int(fp.get("disk_signature") or 0)
    gold_uuid = str(fp.get("ext4_uuid") or "").strip().lower()
    gold_partuuid = str(fp.get("boot_partuuid") or "").strip().lower()

    target_sig = int(disk_info.get("signature") or 0)
    if gold_sig and target_sig == gold_sig:
        raise SDGuardError(
            f"WRITE BLOCKED: Disk {disk_info.get('index')} matches your GOLDEN MASTER SD card "
            f"(MBR signature 0x{gold_sig:08x}). Remove GOLD and insert your NEW target SD card."
        )

    dev_path = disk_info.get("id")
    if dev_path and (gold_sig or gold_uuid):
        live_sig, live_uuid = _run_with_timeout(
            lambda: ext4_ro.read_disk_signature_and_ext4_uuid(dev_path),
            timeout_sec=2.0,
            default=(0, ""),
        )
        if gold_sig and live_sig == gold_sig:
            raise SDGuardError(
                f"WRITE BLOCKED: Disk {disk_info.get('index')} matches your GOLDEN MASTER SD card "
                f"(MBR signature 0x{gold_sig:08x}). Remove GOLD and insert your NEW target SD card."
            )
        if gold_uuid and live_uuid and live_uuid.lower() == gold_uuid:
            raise SDGuardError(
                f"WRITE BLOCKED: Disk {disk_info.get('index')} contains your GOLDEN MASTER ext4 volume "
                f"(UUID {gold_uuid}). Remove GOLD and insert your NEW target SD card."
            )

    clean_letter = sd_guard.normalize_drive_letter(drive_letter)
    clean_is_fat = True
    if not clean_letter:
        parts = disk_info.get("partitions") or []
        fat_part = next(
            (p for p in parts if sd_guard.normalize_drive_letter(p.get("letter")) and "FAT" in str(p.get("file_system") or "").upper()),
            None,
        )
        if fat_part:
            clean_letter = sd_guard.normalize_drive_letter(fat_part.get("letter"))
            clean_is_fat = True
        else:
            letters = disk_info.get("partition_letters") or []
            clean_letter = letters[0] if letters else ""
            clean_is_fat = not parts
    if clean_letter and clean_is_fat and gold_partuuid:
        cmdline_path = f"{clean_letter}:\\cmdline.txt"
        raw_cmd = _run_with_timeout(
            lambda p=cmdline_path: _read_file_bytes_if_exists(p, max_bytes=65536),
            timeout_sec=1.0,
            default=None,
        )
        if raw_cmd:
            txt = raw_cmd.decode("utf-8", errors="ignore")
            if gold_partuuid in txt.lower():
                raise SDGuardError(
                    f"WRITE BLOCKED: Drive {clean_letter}: matches your GOLDEN MASTER boot PARTUUID "
                    f"({gold_partuuid}). Remove GOLD and insert your NEW target SD card."
                )


def extract_gold_sd(
    disk_index,
    drive_letter=None,
    backup_root=DEFAULT_BACKUP_ROOT,
    log_fn=None,
    device_path_override=None,
    disks=None,
):
    """
    Strictly read-only extraction & validation of the installed GOLD SD card.

    Returns the complete manifest dict including partition table and validated item list.
    """
    def _log(msg):
        if log_fn:
            log_fn(msg)

    verified_disk = sd_guard.validate_sd_write_target(
        disk_index, drive_letter=drive_letter or None, disks=disks
    )
    clean_letter = sd_guard.resolve_verified_drive_letter(
        verified_disk["index"], requested_letter=drive_letter or None, disks=[verified_disk]
    )

    device_path = device_path_override or verified_disk["id"]
    _log(f"[*] Opening GOLD SD {device_path} strictly READ-ONLY (GENERIC_READ)...")

    os.makedirs(backup_root, exist_ok=True)
    ts = time.strftime("%Y%m%d_%H%M%S")

    partitions_summary = []
    items = []
    extracted_meta = {
        "os_release": "Unknown",
        "hostname": "",
        "wifi_ssid": "",
        "callsign": "",
        "rig": "",
        "boot_partuuid": "",
        "issue": "",
    }
    gold_sig = int(verified_disk.get("signature") or 0)
    ext4_uuid = ""

    with ext4_ro.RawReadOnlyStream(device_path) as stream:
        mbr = stream.read_at(0, 512)
        if len(mbr) >= 512 and mbr[510:512] == b"\x55\xaa":
            mbr_sig = struct.unpack("<I", mbr[440:444])[0]
            if mbr_sig:
                gold_sig = mbr_sig

        raw_parts = ext4_ro.read_mbr_partitions(stream)
        ext4_vol = None
        for p in raw_parts:
            p_info = {
                "index": p["index"],
                "type_hex": f"0x{p['type']:02x}",
                "offset": p["offset"],
                "size_bytes": p["size"],
                "size_mb": round(p["size"] / (1024 * 1024), 1),
                "filesystem": "FAT32 (boot)" if p["type"] in (0x0B, 0x0C, 0x0E) else "Unknown",
                "mount": f"{clean_letter}:\\" if (p["index"] == 0 and clean_letter) else "Unmounted",
                "item_count": 0,
            }
            if p["type"] == 0x83 or ext4_vol is None:
                try:
                    candidate = ext4_ro.Ext4Volume(stream, p["offset"])
                    ext4_vol = candidate
                    ext4_uuid = candidate.uuid
                    p_info["filesystem"] = f"Linux ext4 ({candidate.volume_name or 'rootfs'})"
                except ext4_ro.Ext4ReadError:
                    pass
            partitions_summary.append(p_info)

        if ext4_vol is None:
            raise ext4_ro.Ext4ReadError("No Linux ext4 rootfs partition found on GOLD SD.")

        sig_hex = f"{gold_sig:08x}"
        staging_dir = os.path.join(backup_root, "gold_staging", f"gold_{ts}_{sig_hex}")
        os.makedirs(staging_dir, exist_ok=True)

        # 1. Read Partition 0 (boot FAT32): try raw GENERIC_READ FAT32 first when unmounted/override, else mounted Windows FAT32
        boot_files = []
        wanted_boot = ("issue.txt", "config.txt", "cmdline.txt", "wpa_supplicant.conf")
        boot_raw_map = {}
        if (
            not device_path_override
            and clean_letter
            and _run_with_timeout(lambda: os.path.isdir(f"{clean_letter}:\\"), timeout_sec=1.5, default=False)
        ):
            boot_root = f"{clean_letter}:\\"
            for fname in wanted_boot:
                fpath = os.path.join(boot_root, fname)
                data = _run_with_timeout(
                    lambda p=fpath: _read_file_bytes_if_exists(p),
                    timeout_sec=1.5,
                    default=None,
                )
                if data is not None:
                    boot_raw_map[fname] = (f"{clean_letter}:\\{fname}", data)

        if not boot_raw_map and raw_parts:
            p0 = raw_parts[0]
            if p0.get("type") in (0x0B, 0x0C, 0x0E, 0x06, 0x04):
                raw_fat_files = ext4_ro.read_fat32_root_files(stream, p0["offset"], wanted_boot)
                for fname, data in raw_fat_files.items():
                    boot_raw_map[fname] = (f"/boot/{fname}", data)

        for fname in wanted_boot:
            if fname not in boot_raw_map:
                continue
            src_label, data = boot_raw_map[fname]
            dst = os.path.join(staging_dir, "boot", fname)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            with open(dst, "wb") as fo:
                fo.write(data)
            status, note = _validate_file_bytes(fname, data)
            items.append(
                {
                    "partition": 0,
                    "category": "boot",
                    "source_path": src_label,
                    "staged_rel": f"boot/{fname}",
                    "size_bytes": len(data),
                    "sha256": hashlib.sha256(data).hexdigest()[:16],
                    "status": status,
                    "note": note,
                }
            )
            boot_files.append(fname)
            txt = data.decode("utf-8", errors="ignore")
            if fname == "issue.txt":
                extracted_meta["issue"] = txt.strip().splitlines()[0] if txt.strip() else ""
            elif fname == "cmdline.txt":
                extracted_meta["boot_partuuid"] = _parse_partuuid(txt)
            elif fname == "wpa_supplicant.conf" and not extracted_meta["wifi_ssid"]:
                extracted_meta["wifi_ssid"] = _parse_wifi_ssid(txt)
        if boot_files and partitions_summary:
            partitions_summary[0]["item_count"] = len(boot_files)
            _log(f"[+] Partition 0 (boot FAT32): Read {len(boot_files)} config/boot files strictly READ-ONLY.")

        # 2. Read Partition 1 (Linux ext4 rootfs) targets
        ext4_paths = _collect_ext4_targets(ext4_vol)
        _log(f"[*] Partition 1 (ext4 rootfs, UUID={ext4_uuid}): Extracting {len(ext4_paths)} RFK/user/tuning files...")

        for posix_p in ext4_paths:
            data = ext4_vol.read_file(posix_p)
            rel_p = "rootfs/" + posix_p.lstrip("/")
            dst = os.path.join(staging_dir, *rel_p.split("/"))
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            with open(dst, "wb") as fo:
                fo.write(data)

            status, note = _validate_file_bytes(posix_p, data)
            cat = _categorize_path(posix_p)
            items.append(
                {
                    "partition": 1,
                    "category": cat,
                    "source_path": posix_p,
                    "staged_rel": rel_p,
                    "size_bytes": len(data),
                    "sha256": hashlib.sha256(data).hexdigest()[:16],
                    "status": status,
                    "note": note,
                }
            )

            low = posix_p.lower()
            if posix_p == "/etc/os-release":
                m = re.search(r'PRETTY_NAME="([^"]+)"', data.decode("utf-8", errors="ignore"))
                if m:
                    extracted_meta["os_release"] = m.group(1)
            elif posix_p == "/etc/hostname":
                extracted_meta["hostname"] = data.decode("utf-8", errors="ignore").strip()
            elif low.endswith("wpa_supplicant.conf"):
                ssid = _parse_wifi_ssid(data.decode("utf-8", errors="ignore"))
                if ssid:
                    extracted_meta["wifi_ssid"] = ssid
            elif low.endswith("/config.json") and status == "VALID":
                try:
                    cfg = json.loads(data.decode("utf-8"))
                    extracted_meta["callsign"] = cfg.get("customDeviceName") or extracted_meta["callsign"]
                    rig = (cfg.get("cat_config") or {}).get("rig")
                    if rig:
                        extracted_meta["rig"] = rig
                except Exception:
                    pass

        for p_info in partitions_summary:
            if p_info["filesystem"].startswith("Linux ext4"):
                p_info["item_count"] = len(ext4_paths)

    counts = {}
    invalid_items = []
    for it in items:
        counts[it["category"]] = counts.get(it["category"], 0) + 1
        if it["status"] == "INVALID_JSON":
            invalid_items.append(it["source_path"])

    has_rfk = counts.get("rfk_app", 0) > 0
    has_tuning_or_user = (counts.get("tuning_data", 0) + counts.get("user_data", 0)) > 0
    validated_ok = bool(has_rfk and has_tuning_or_user and not invalid_items)

    archive_path = os.path.join(backup_root, f"RFK_Golden_Master_{ts}.tar.gz")
    manifest = {
        "status": "ok",
        "extracted_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "gold_fingerprint": {
            "disk_index": verified_disk["index"],
            "model": verified_disk["model"],
            "size_bytes": verified_disk["size_bytes"],
            "disk_signature": gold_sig,
            "ext4_uuid": ext4_uuid,
            "boot_partuuid": extracted_meta["boot_partuuid"],
        },
        "metadata": extracted_meta,
        "partitions": partitions_summary,
        "counts": counts,
        "total_items": len(items),
        "invalid_items": invalid_items,
        "validated_ok": validated_ok,
        "staging_dir": staging_dir,
        "archive_path": archive_path,
        "items": items,
    }

    manifest_in_stage = os.path.join(staging_dir, "manifest.json")
    with open(manifest_in_stage, "w", encoding="utf-8") as fm:
        json.dump(manifest, fm, indent=2)

    with tarfile.open(archive_path, "w:gz") as tf:
        tf.add(staging_dir, arcname=".")

    latest_manifest_path = os.path.join(backup_root, LATEST_MANIFEST_NAME)
    with open(latest_manifest_path, "w", encoding="utf-8") as fl:
        json.dump(manifest, fl, indent=2)

    _log(
        f"[+] Archived {len(items)} items ({counts}) -> {archive_path} "
        f"[validated_ok={validated_ok}]"
    )
    return manifest
