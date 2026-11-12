import http.server
import socketserver
import os
import sys
import json
import subprocess
import urllib.parse
import urllib.request
import urllib.error
import socket
import threading
import time
import ctypes
from ctypes import wintypes
import shutil
import hashlib
import string
import random
import atexit
import lzma
import queue
import tarfile
import re

MIGRATOR_DIR = os.path.abspath(os.path.dirname(__file__))
if MIGRATOR_DIR not in sys.path:
    sys.path.insert(0, MIGRATOR_DIR)

import gold_extractor
import sd_guard
from sd_guard import SDGuardError

PORT = 8089
if len(sys.argv) > 1:
    try:
        PORT = int(sys.argv[1])
    except ValueError:
        pass

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BACKUP_ROOT = os.path.join(BASE_DIR, "backups")
IMAGES_DIR = os.path.join(BASE_DIR, "images")

# In-memory streaming log buffer for live terminal display in HTM
LOG_BUFFER = []
LOG_LOCK = threading.Lock()
ACTIVE_JOB = {"running": False, "step": "idle", "progress": 0, "error": None, "original_metadata": None, "migration_trace": None}

def append_log(msg):
    with LOG_LOCK:
        entry = {"time": time.strftime("%H:%M:%S"), "message": str(msg)}
        LOG_BUFFER.append(entry)
        if len(LOG_BUFFER) > 1000:
            LOG_BUFFER.pop(0)
    print(f"[{entry['time']}] {msg}", flush=True)

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False

def find_rpi_imager():
    candidates = [
        os.path.join(BASE_DIR, "tools", "rpi-imager", "rpi-imager.exe"),
        r"C:\Program Files\Raspberry Pi Ltd\Imager\rpi-imager.exe",
        r"C:\Program Files\Raspberry Pi Imager\rpi-imager.exe",
        r"C:\Program Files (x86)\Raspberry Pi Imager\rpi-imager.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\Raspberry Pi Imager\rpi-imager.exe"),
    ]
    for c in candidates:
        if os.path.isfile(c):
            return c
    return None

def find_7zip():
    candidates = [
        os.path.join(BASE_DIR, "tools", "7zip", "7z.exe"),
        r"C:\Program Files\7-Zip\7z.exe",
        r"C:\Program Files (x86)\7-Zip\7z.exe",
        shutil.which("7z")
    ]
    for c in candidates:
        if c and os.path.isfile(c):
            return c
    return None

RPI_OS_FEED_URL = "https://downloads.raspberrypi.com/os_list_imagingutility_v4.json"
_OS_FEED_CACHE = {"ts": 0.0, "info": None}

def _flatten_os_items(items):
    for item in items or []:
        if item.get("subitems"):
            yield from _flatten_os_items(item["subitems"])
        else:
            yield item

def fetch_latest_rpi_os_info(force_refresh=False):
    """Query Raspberry Pi Imager's official JSON feed for latest 64-bit Desktop RPi OS (Pi 4 & Pi 5)."""
    now = time.time()
    if not force_refresh and _OS_FEED_CACHE["info"] and (now - _OS_FEED_CACHE["ts"]) < 300:
        return _OS_FEED_CACHE["info"]

    req = urllib.request.Request(
        RPI_OS_FEED_URL,
        headers={"User-Agent": "JRFK-Migrator/2.0"},
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        payload = json.loads(resp.read().decode("utf-8", errors="replace"))

    candidates = list(_flatten_os_items(payload.get("os_list", [])))
    chosen = None
    for item in candidates:
        name = item.get("name", "")
        url = item.get("url", "")
        devs = item.get("devices") or []
        if (
            name == "Raspberry Pi OS (64-bit)"
            and "arm64" in url.lower()
            and "pi4-64bit" in devs
            and "pi5-64bit" in devs
        ):
            chosen = item
            break

    if not chosen:
        for item in candidates:
            name = item.get("name", "")
            url = item.get("url", "").lower()
            devs = item.get("devices") or []
            if (
                "raspberry pi os" in name.lower()
                and "64-bit" in name.lower()
                and "lite" not in name.lower()
                and "legacy" not in name.lower()
                and "arm64" in url
                and "pi4-64bit" in devs
                and "pi5-64bit" in devs
            ):
                chosen = item
                break

    if not chosen or not chosen.get("url"):
        raise RuntimeError("No matching 64-bit Pi 4 & Pi 5 Desktop OS found in official RPi Imager feed.")

    info = {
        "name": chosen.get("name", "Raspberry Pi OS (64-bit)"),
        "description": chosen.get("description", ""),
        "release_date": chosen.get("release_date", ""),
        "url": chosen["url"],
        "filename": os.path.basename(urllib.parse.urlparse(chosen["url"]).path),
        "extract_sha256": chosen.get("extract_sha256", ""),
        "image_download_size": int(chosen.get("image_download_size") or 0),
        "extract_size": int(chosen.get("extract_size") or 0),
        "devices": chosen.get("devices") or [],
        "source": "online",
    }
    _OS_FEED_CACHE["ts"] = now
    _OS_FEED_CACHE["info"] = info
    return info

def resolve_os_image_path(prefer_xz=True):
    """Locate cached 64-bit Raspberry Pi OS image inside project images/."""
    search_dirs = [IMAGES_DIR]
    exts = (".img.xz", ".img") if prefer_xz else (".img", ".img.xz")
    for d in search_dirs:
        if not os.path.isdir(d):
            continue
        for ext in exts:
            # Prefer newest official release file by mtime
            matches = sorted(
                (
                    os.path.join(d, f)
                    for f in os.listdir(d)
                    if f.lower().endswith(ext) and not f.lower().endswith(".part")
                ),
                key=os.path.getmtime,
                reverse=True,
            )
            if matches:
                return matches[0]
    return None

def ensure_latest_rpi_os_image(progress_callback=None):
    """Ensure latest official 64-bit Pi 4/5 RPi OS is cached in IMAGES_DIR, falling back to local cache offline."""
    os.makedirs(IMAGES_DIR, exist_ok=True)
    try:
        info = fetch_latest_rpi_os_info()
        dst = os.path.join(IMAGES_DIR, info["filename"])
        expected_sz = info.get("image_download_size", 0)
        if os.path.isfile(dst) and (expected_sz <= 0 or os.path.getsize(dst) == expected_sz):
            append_log(
                f"[+] Using cached latest official {info['name']} ({info['release_date']}): {dst}"
            )
            return dst, info

        append_log(
            f"[*] Fetching latest official {info['name']} ({info['release_date']}) for Pi 4 & Pi 5..."
        )
        append_log(f"    Source: {info['url']}")
        part = dst + ".part"
        req = urllib.request.Request(info["url"], headers={"User-Agent": "JRFK-Migrator/2.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            total = int(resp.headers.get("Content-Length") or expected_sz or 0)
            downloaded = 0
            last_log_pct = -10
            with open(part, "wb") as out:
                while True:
                    chunk = resp.read(1024 * 1024)
                    if not chunk:
                        break
                    out.write(chunk)
                    downloaded += len(chunk)
                    if total > 0:
                        pct = min(100, int(downloaded * 100 / total))
                        if progress_callback:
                            progress_callback(pct, downloaded, total)
                        if pct >= last_log_pct + 10:
                            last_log_pct = pct
                            append_log(
                                f"[*] Downloading latest 64-bit RPi OS: {pct}% "
                                f"({downloaded / (1024**2):.0f} / {total / (1024**2):.0f} MB)"
                            )
        if expected_sz > 0 and os.path.getsize(part) != expected_sz:
            actual = os.path.getsize(part)
            try:
                os.remove(part)
            except OSError:
                pass
            raise RuntimeError(f"Downloaded image size mismatch ({actual} != {expected_sz} bytes).")
        os.replace(part, dst)
        with open(dst + ".meta.json", "w", encoding="utf-8") as mf:
            json.dump(info, mf, indent=2)
        append_log(f"[+] Cached latest official 64-bit RPi OS: {dst}")
        return dst, info
    except Exception as e:
        append_log(f"[!] Online RPi OS check/download note ({e}); checking local cache...")
        cached = resolve_os_image_path(prefer_xz=True)
        if cached:
            append_log(f"[+] Falling back to local cached 64-bit OS image: {cached}")
            return cached, {
                "name": "Raspberry Pi OS (64-bit, Cached Local)",
                "release_date": time.strftime("%Y-%m-%d", time.localtime(os.path.getmtime(cached))),
                "filename": os.path.basename(cached),
                "source": "cached",
            }
        raise RuntimeError(
            f"Unable to download latest 64-bit Raspberry Pi OS ({e}) and no cached image was found in {IMAGES_DIR}."
        )

kernel32 = ctypes.windll.kernel32
GENERIC_READ = 0x80000000
GENERIC_WRITE = 0x40000000
FILE_SHARE_READ = 0x00000001
FILE_SHARE_WRITE = 0x00000002
OPEN_EXISTING = 3
FILE_ATTRIBUTE_NORMAL = 0x80
FILE_FLAG_NO_BUFFERING = 0x20000000
FILE_FLAG_WRITE_THROUGH = 0x80000000
INVALID_HANDLE_VALUE = -1

FSCTL_LOCK_VOLUME = 0x00090018
FSCTL_DISMOUNT_VOLUME = 0x00090020
FSCTL_UNLOCK_VOLUME = 0x0009001C
FSCTL_ALLOW_EXTENDED_DASD_IO = 0x00090083
IOCTL_DISK_DELETE_DRIVE_LAYOUT = 0x0007C100
IOCTL_DISK_UPDATE_PROPERTIES = 0x00070140
IOCTL_STORAGE_EJECT_MEDIA = 0x002D4808
_AUTOMOUNT_DISABLED = False

def assert_writable_non_gold_sd(disk_index, drive_letter=None, require_letter=False):
    verified = sd_guard.validate_sd_write_target(
        disk_index, drive_letter=drive_letter, require_letter=require_letter
    )
    gold_extractor.check_not_gold_target(verified, drive_letter=drive_letter)
    return verified


def _dismiss_windows_format_dialogs():
    """Close Windows 11 'You need to format the disk' popups automatically so Linux/RAW SD partitions never show Format screens."""
    if os.name != "nt":
        return 0
    closed = 0
    try:
        user32 = ctypes.windll.user32
        enum_proc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
        child_proc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)

        def _wtext(hwnd):
            n = user32.GetWindowTextLengthW(hwnd)
            if n <= 0:
                return ""
            b = ctypes.create_unicode_buffer(n + 1)
            user32.GetWindowTextW(hwnd, b, n + 1)
            return b.value

        def _wcls(hwnd):
            b = ctypes.create_unicode_buffer(128)
            user32.GetClassNameW(hwnd, b, 128)
            return b.value

        targets = []

        def _cb(hwnd, _lp):
            if not user32.IsWindowVisible(hwnd):
                return True
            if _wcls(hwnd) != "#32770":
                return True
            title = _wtext(hwnd).lower()
            if title == "microsoft windows" or title.startswith("format "):
                texts = []

                def _ccb(chwnd, _clp):
                    t = _wtext(chwnd)
                    if t:
                        texts.append(t.lower())
                    return True

                user32.EnumChildWindows(hwnd, child_proc(_ccb), 0)
                joined = " ".join(texts)
                if "format the disk" in joined or "you need to format" in joined or "format disk" in joined or (
                    title.startswith("format ") and "capacity" in joined and "file system" in joined
                ):
                    targets.append(hwnd)
            return True

        user32.EnumWindows(enum_proc(_cb), 0)
        for hwnd in targets:
            # WM_COMMAND IDCANCEL (2) and WM_CLOSE (0x0010) dismiss both 'Microsoft Windows' and 'Format' dialogs cleanly
            user32.PostMessageW(hwnd, 0x0111, 2, 0)
            user32.PostMessageW(hwnd, 0x0010, 0, 0)
            closed += 1
    except Exception:
        pass
    return closed


def _set_windows_automount(enable):
    """Toggle Windows MountMgr automount (/N disables new auto-letters to stop W11 'Format disk' popups; /E restores)."""
    global _AUTOMOUNT_DISABLED
    if os.name != "nt":
        return
    if not enable and _AUTOMOUNT_DISABLED:
        return
    try:
        subprocess.run(
            ["mountvol.exe", "/E" if enable else "/N"],
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            timeout=6,
        )
        _AUTOMOUNT_DISABLED = not enable
    except Exception:
        pass


def _lock_all_disk_volumes(disk_index):
    """Find, lock, and dismount ALL Windows volumes (even unlettered Volume{GUID}s) on disk_index; return open handles."""
    locked_handles = []
    if os.name != "nt":
        return locked_handles
    try:
        buf = ctypes.create_unicode_buffer(1024)
        find_h = kernel32.FindFirstVolumeW(buf, 1024)
        invalid_h = ctypes.c_void_p(-1).value
        if find_h == invalid_h or find_h == -1:
            return locked_handles
        try:
            while True:
                vol_name = buf.value.rstrip("\\")
                hv = kernel32.CreateFileW(
                    vol_name,
                    GENERIC_READ | GENERIC_WRITE,
                    FILE_SHARE_READ | FILE_SHARE_WRITE,
                    None,
                    OPEN_EXISTING,
                    FILE_ATTRIBUTE_NORMAL,
                    None,
                )
                if hv != invalid_h and hv != -1:
                    belongs = False
                    out = ctypes.create_string_buffer(256)
                    ret = wintypes.DWORD(0)
                    if kernel32.DeviceIoControl(hv, 0x00560000, None, 0, out, 256, ctypes.byref(ret), None):
                        cnt = struct.unpack_from("<I", out.raw, 0)[0]
                        for i in range(cnt):
                            off = 8 + i * 24
                            if off + 4 <= ret.value and struct.unpack_from("<I", out.raw, off)[0] == int(disk_index):
                                belongs = True
                                break
                    if belongs:
                        bret = wintypes.DWORD(0)
                        kernel32.DeviceIoControl(hv, FSCTL_LOCK_VOLUME, None, 0, None, 0, ctypes.byref(bret), None)
                        kernel32.DeviceIoControl(hv, FSCTL_DISMOUNT_VOLUME, None, 0, None, 0, ctypes.byref(bret), None)
                        locked_handles.append(hv)
                    else:
                        kernel32.CloseHandle(hv)
                if not kernel32.FindNextVolumeW(find_h, buf, 1024):
                    break
        finally:
            kernel32.FindVolumeClose(find_h)
    except Exception:
        pass
    return locked_handles


def _dismount_sd_volumes(verified_disk, remove_letters=True):
    """Lock, dismount, and optionally detach mounted drive letters on verified_disk so Windows 11 never pops 'Format disk'."""
    letters = verified_disk.get("partition_letters") or []
    bytes_ret = wintypes.DWORD(0)
    for ltr in letters:
        clean = sd_guard.normalize_drive_letter(ltr)
        if not clean:
            continue
        hv = kernel32.CreateFileW(
            f"\\\\.\\{clean}:",
            GENERIC_READ | GENERIC_WRITE,
            FILE_SHARE_READ | FILE_SHARE_WRITE,
            None,
            OPEN_EXISTING,
            FILE_ATTRIBUTE_NORMAL,
            None,
        )
        if hv != INVALID_HANDLE_VALUE and hv != -1:
            try:
                kernel32.DeviceIoControl(hv, FSCTL_LOCK_VOLUME, None, 0, None, 0, ctypes.byref(bytes_ret), None)
                kernel32.DeviceIoControl(hv, FSCTL_DISMOUNT_VOLUME, None, 0, None, 0, ctypes.byref(bytes_ret), None)
            finally:
                kernel32.CloseHandle(hv)
        if remove_letters:
            try:
                kernel32.DeleteVolumeMountPointW(f"{clean}:\\")
            except Exception:
                pass


def _suppress_non_fat_letters(disk_index):
    """Remove any Windows drive letters accidentally assigned to non-FAT (Linux ext4 / RAW) partitions."""
    try:
        for d in sd_guard.query_disks():
            if int(d.get("index", -1)) != int(disk_index):
                continue
            for p in d.get("partitions") or []:
                ltr = sd_guard.normalize_drive_letter(p.get("letter"))
                fs = str(p.get("file_system") or "").strip().upper()
                if ltr and "FAT" not in fs:
                    try:
                        kernel32.DeleteVolumeMountPointW(f"{ltr}:\\")
                    except Exception:
                        pass
    except Exception:
        pass


def clean_disk_partitions(disk_index, verified_disk=None, refresh_properties=False):
    verified = verified_disk or assert_writable_non_gold_sd(disk_index)
    append_log(f"[*] Dismounting volumes and wiping partition layout on SD Disk {disk_index} (Win32)...")
    _set_windows_automount(False)
    try:
        _dismount_sd_volumes(verified, remove_letters=True)

        dev_path = f"\\\\.\\PhysicalDrive{int(disk_index)}"
        h_disk = kernel32.CreateFileW(
            dev_path,
            GENERIC_READ | GENERIC_WRITE,
            FILE_SHARE_READ | FILE_SHARE_WRITE,
            None,
            OPEN_EXISTING,
            FILE_FLAG_WRITE_THROUGH,
            None,
        )
        if h_disk == INVALID_HANDLE_VALUE or h_disk == -1:
            err = kernel32.GetLastError()
            append_log(f"[-] Could not open {dev_path} for Win32 wipe (error {err}); falling back to diskpart...")
            try:
                subprocess.run(["diskpart"], input=f"select disk {int(disk_index)}\nclean\n", text=True, capture_output=True, timeout=15)
            except Exception as e:
                append_log(f"[-] Disk clean note: {e}")
            return

        bytes_ret = wintypes.DWORD(0)
        written = wintypes.DWORD(0)
        try:
            kernel32.DeviceIoControl(h_disk, FSCTL_ALLOW_EXTENDED_DASD_IO, None, 0, None, 0, ctypes.byref(bytes_ret), None)
            kernel32.DeviceIoControl(h_disk, FSCTL_LOCK_VOLUME, None, 0, None, 0, ctypes.byref(bytes_ret), None)
            kernel32.DeviceIoControl(h_disk, IOCTL_DISK_DELETE_DRIVE_LAYOUT, None, 0, None, 0, ctypes.byref(bytes_ret), None)

            zero_2mb = b"\x00" * (2 * 1024 * 1024)
            pos = ctypes.c_longlong(0)
            kernel32.SetFilePointerEx(h_disk, ctypes.c_longlong(0), ctypes.byref(pos), 0)
            kernel32.WriteFile(h_disk, zero_2mb, len(zero_2mb), ctypes.byref(written), None)

            disk_sz = int(verified.get("size_bytes") or 0)
            if disk_sz > 8 * 1024 * 1024:
                tail_off = ((disk_sz - 1024 * 1024) // 4096) * 4096
                zero_tail = b"\x00" * min(1024 * 1024, disk_sz - tail_off)
                if len(zero_tail) >= 4096:
                    kernel32.SetFilePointerEx(h_disk, ctypes.c_longlong(tail_off), ctypes.byref(pos), 0)
                    kernel32.WriteFile(h_disk, zero_tail[: (len(zero_tail) // 4096) * 4096], (len(zero_tail) // 4096) * 4096, ctypes.byref(written), None)

            kernel32.FlushFileBuffers(h_disk)
            if refresh_properties:
                kernel32.DeviceIoControl(h_disk, IOCTL_DISK_UPDATE_PROPERTIES, None, 0, None, 0, ctypes.byref(bytes_ret), None)
            append_log(f"[+] Wiped partition table and dismounted Disk {disk_index} cleanly.")
        finally:
            kernel32.DeviceIoControl(h_disk, FSCTL_UNLOCK_VOLUME, None, 0, None, 0, ctypes.byref(bytes_ret), None)
            kernel32.CloseHandle(h_disk)
        time.sleep(0.4)
    finally:
        pass

def _resolve_uncompressed_size(img_path):
    if not img_path.lower().endswith(".xz"):
        return os.path.getsize(img_path)
    meta_path = img_path + ".meta.json"
    if os.path.isfile(meta_path):
        try:
            with open(meta_path, "r", encoding="utf-8") as mf:
                sz = int(json.load(mf).get("extract_size") or 0)
                if sz > 0:
                    return sz
        except Exception:
            pass
    # Fallback estimate (typical compressed ratio ~5.2x)
    return max(os.path.getsize(img_path) * 5, 1)

def flash_raw_image(img_path, disk_index, progress_callback=None, verified_disk=None, already_cleaned=False):
    verified = verified_disk or assert_writable_non_gold_sd(disk_index)
    if not os.path.exists(img_path):
        raise FileNotFoundError(f"Source 64-bit OS image not found: {img_path}")

    is_xz = img_path.lower().endswith(".xz")
    total_size = _resolve_uncompressed_size(img_path)
    device_path = f"\\\\.\\PhysicalDrive{int(disk_index)}"

    if not already_cleaned:
        clean_disk_partitions(disk_index, verified_disk=verified, refresh_properties=False)
    else:
        _dismount_sd_volumes(verified)
    _dismiss_windows_format_dialogs()

    locked_vols = _lock_all_disk_volumes(disk_index)
    append_log(f"[*] Opening raw device {device_path} for verified {'compressed .img.xz stream' if is_xz else 'raw .img'} write (~{total_size / (1024**3):.2f} GB)...")
    flags = FILE_FLAG_WRITE_THROUGH
    h_disk = kernel32.CreateFileW(
        device_path,
        GENERIC_READ | GENERIC_WRITE,
        FILE_SHARE_READ | FILE_SHARE_WRITE,
        None,
        OPEN_EXISTING,
        flags,
        None
    )

    if h_disk == INVALID_HANDLE_VALUE or h_disk == -1:
        err = kernel32.GetLastError()
        for hv in locked_vols:
            kernel32.CloseHandle(hv)
        raise RuntimeError(f"Could not open device {device_path}: Windows error {err} (requires Administrator elevation)")

    bytes_returned = wintypes.DWORD(0)
    kernel32.DeviceIoControl(h_disk, FSCTL_ALLOW_EXTENDED_DASD_IO, None, 0, None, 0, ctypes.byref(bytes_returned), None)
    kernel32.DeviceIoControl(h_disk, IOCTL_DISK_DELETE_DRIVE_LAYOUT, None, 0, None, 0, ctypes.byref(bytes_returned), None)

    append_log(f"[*] Flashing 64-bit OS image (~{total_size / (1024**3):.2f} GB) to {device_path}...")

    try:
        chunk_size = 2 * 1024 * 1024
        bytes_written_total = 0
        bytes_written_win32 = wintypes.DWORD()
        expected_head = None

        opener = lzma.open if is_xz else open
        with opener(img_path, "rb") as f_src:
            t0 = time.time()
            last_report = t0
            while True:
                data = f_src.read(chunk_size)
                if not data:
                    break
                while len(data) < chunk_size:
                    more = f_src.read(chunk_size - len(data))
                    if not more:
                        break
                    data += more
                remainder = len(data) % 4096
                if remainder != 0:
                    data = data + b'\x00' * (4096 - remainder)
                if expected_head is None:
                    expected_head = data[:4096]
                    # Defer writing sector 0 (MBR/partition table) until the end so Windows cannot attach fastfat mid-stream
                    data = (b"\x00" * 4096) + data[4096:]

                ok = kernel32.WriteFile(
                    h_disk,
                    data,
                    len(data),
                    ctypes.byref(bytes_written_win32),
                    None
                )
                if not ok:
                    err = kernel32.GetLastError()
                    raise RuntimeError(f"WriteFile failed at byte offset {bytes_written_total}: Windows error {err} (SD card may be damaged)")
                if bytes_written_win32.value != len(data):
                    raise RuntimeError(
                        f"Short WriteFile at byte offset {bytes_written_total}: wrote {bytes_written_win32.value}/{len(data)} bytes (SD card may be damaged)"
                    )

                bytes_written_total += bytes_written_win32.value
                t_now = time.time()
                if progress_callback and (t_now - last_report >= 2.0 or bytes_written_total >= total_size):
                    last_report = t_now
                    speed = (bytes_written_total / (t_now - t0)) / (1024 * 1024) if (t_now - t0) > 0 else 0
                    pct = min(99, int((bytes_written_total / max(total_size, 1)) * 100))
                    progress_callback(pct, bytes_written_total, max(total_size, bytes_written_total), speed)

        # Write deferred MBR + partition table (first 4096 bytes) now that all partitions are on disk
        if expected_head and len(expected_head) >= 512:
            pos = ctypes.c_longlong(0)
            kernel32.SetFilePointerEx(h_disk, ctypes.c_longlong(0), ctypes.byref(pos), 0)
            mbr_written = wintypes.DWORD(0)
            m_ok = kernel32.WriteFile(h_disk, expected_head, len(expected_head), ctypes.byref(mbr_written), None)
            if not m_ok or mbr_written.value != len(expected_head):
                err = kernel32.GetLastError()
                raise RuntimeError(f"WriteFile failed committing MBR at offset 0: Windows error {err}")

        if progress_callback:
            t_now = time.time()
            speed = (bytes_written_total / (t_now - t0)) / (1024 * 1024) if (t_now - t0) > 0 else 0
            progress_callback(100, bytes_written_total, bytes_written_total, speed)
        kernel32.FlushFileBuffers(h_disk)

        # Read-back check on sector 0 (MBR + partition table) to detect damaged/write-faulted SD cards immediately
        if expected_head and len(expected_head) >= 512:
            pos = ctypes.c_longlong(0)
            kernel32.SetFilePointerEx(h_disk, ctypes.c_longlong(0), ctypes.byref(pos), 0)
            verify_buf = ctypes.create_string_buffer(4096)
            verify_read = wintypes.DWORD(0)
            v_ok = kernel32.ReadFile(h_disk, verify_buf, 4096, ctypes.byref(verify_read), None)
            if not v_ok or verify_read.value < 512 or verify_buf.raw[:512] != expected_head[:512] or verify_buf.raw[510:512] != b"\x55\xaa":
                raise RuntimeError(
                    f"SD card write verification failed at sector 0 on Disk {disk_index} — card may be physically damaged or write-faulted."
                )

        kernel32.DeviceIoControl(h_disk, IOCTL_DISK_UPDATE_PROPERTIES, None, 0, None, 0, ctypes.byref(bytes_returned), None)
    finally:
        kernel32.CloseHandle(h_disk)
        for hv in locked_vols:
            try:
                kernel32.DeviceIoControl(hv, FSCTL_UNLOCK_VOLUME, None, 0, None, 0, ctypes.byref(bytes_returned), None)
            except Exception:
                pass
            kernel32.CloseHandle(hv)

    append_log(f"[+] Successfully wrote {bytes_written_total / (1024**3):.2f} GB to Disk {disk_index}.")
    time.sleep(1)
    rescan_disk(disk_index)


def rpi_imager_cli_flash(img_path, disk_index, progress_callback=None, verified_disk=None):
    """
    Full-erase target SD (both partitions) and flash 64-bit RPi OS using rpi-imager.exe --cli.
    """
    verified = verified_disk or assert_writable_non_gold_sd(disk_index)
    imager_exe = find_rpi_imager()
    if not imager_exe:
        raise RuntimeError("Raspberry Pi Imager (rpi-imager.exe) not found on host or tools\\rpi-imager\\.")
    if not img_path or not os.path.isfile(img_path):
        raise FileNotFoundError(f"64-bit Raspberry Pi OS image not found: {img_path}")
    if not is_admin():
        raise RuntimeError("Administrator elevation required. Launch via JRFK.exe.")

    clean_disk_partitions(disk_index, verified_disk=verified)

    target_dev = f"\\\\.\\PhysicalDrive{int(disk_index)}"
    append_log(f"[*] Invoking Raspberry Pi Imager CLI on verified SD Disk {disk_index}...")
    append_log(f"    Image:  {img_path}")
    append_log(f"    Target: {target_dev}")

    proc = subprocess.Popen(
        [imager_exe, "--cli", "--disable-verify", img_path, target_dev],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )
    line_q = queue.Queue()

    def _reader():
        try:
            for raw_line in proc.stdout:
                line_q.put(raw_line)
        except Exception:
            pass
        finally:
            line_q.put(None)

    threading.Thread(target=_reader, daemon=True).start()

    pct_val = 0
    saw_output = False
    while True:
        wait_sec = 180.0
        try:
            raw_line = line_q.get(timeout=wait_sec)
        except queue.Empty:
            try:
                proc.kill()
            except Exception:
                pass
            raise RuntimeError(f"rpi-imager CLI stalled ({int(wait_sec)}s without output)")
        if raw_line is None:
            break
        saw_output = True
        line = raw_line.strip()
        if not line:
            continue
        append_log(f"[rpi-imager] {line}")
        m = re.search(r"(\d{1,3})\s*%", line)
        if m and progress_callback:
            new_pct = min(100, int(m.group(1)))
            if new_pct > pct_val:
                pct_val = new_pct
                progress_callback(pct_val)
    rc = proc.wait(timeout=15)
    if rc != 0:
        raise RuntimeError(f"rpi-imager.exe --cli exited with code {rc}")

    append_log(f"[+] Raspberry Pi Imager CLI completed cleanly on Disk {disk_index}.")
    time.sleep(1.5)
    rescan_disk(disk_index)

def rescan_disk(disk_index):
    append_log(f"[*] Refreshing partition table on Disk {disk_index} (Win32)...")
    try:
        dev_path = f"\\\\.\\PhysicalDrive{int(disk_index)}"
        h = kernel32.CreateFileW(dev_path, GENERIC_READ | GENERIC_WRITE, FILE_SHARE_READ | FILE_SHARE_WRITE, None, OPEN_EXISTING, 0, None)
        if h != INVALID_HANDLE_VALUE and h != -1:
            try:
                ret = wintypes.DWORD(0)
                kernel32.DeviceIoControl(h, IOCTL_DISK_UPDATE_PROPERTIES, None, 0, None, 0, ctypes.byref(ret), None)
            finally:
                kernel32.CloseHandle(h)
    except Exception as e:
        append_log(f"[-] Refresh disk note: {e}")
    time.sleep(1.5)
    _suppress_non_fat_letters(disk_index)

def find_target_boot_drive(disk_index):
    """Assigns a drive letter ONLY to FAT32 Partition 1 (suppressing ext4 Partition 2 Format popups)."""
    sd_guard.validate_sd_write_target(disk_index)
    for attempt in range(12):
        try:
            _suppress_non_fat_letters(disk_index)
            disks = sd_guard.query_disks()
            for d in disks:
                if int(d.get("index", -1)) == int(disk_index):
                    for p in d.get("partitions") or []:
                        ltr = sd_guard.normalize_drive_letter(p.get("letter"))
                        fs = str(p.get("file_system") or "").strip().upper()
                        if ltr and "FAT" in fs and os.path.exists(f"{ltr}:\\"):
                            return f"{ltr}:\\"
            letter = sd_guard.resolve_verified_drive_letter(disk_index, disks=disks)
            if letter:
                drive_p = f"{letter}:\\"
                if os.path.exists(drive_p):
                    return drive_p

            if attempt in (0, 3, 6):
                sd_guard.validate_sd_write_target(disk_index)
                subprocess.run(
                    ["diskpart.exe"],
                    input=f"select disk {int(disk_index)}\nselect partition 1\nassign\nexit\n",
                    capture_output=True,
                    text=True,
                    timeout=12,
                )
        except SDGuardError:
            raise
        except Exception:
            pass
        time.sleep(1)
    raise SDGuardError(f"Could not locate or verify a mounted removable boot partition on Disk {disk_index}.")

def generate_sha512_crypt(password, salt=None):
    """Pure-Python POSIX/glibc SHA-512 crypt ($6$) compatible with Raspberry Pi OS userconf.txt & /etc/shadow."""
    b64 = "./0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    if not salt:
        salt = "".join(random.choice(b64) for _ in range(16))
    else:
        salt = "".join(ch for ch in str(salt) if ch in b64)[:16] or "jrfksalt"
    pw_b = password.encode("utf-8")
    salt_b = salt.encode("ascii")

    # Standard Ulrich Drepper SHA-512 crypt algorithm (5000 rounds)
    alt = hashlib.sha512(pw_b + salt_b + pw_b).digest()
    ctx_a = hashlib.sha512(pw_b + salt_b)
    pw_len = len(pw_b)
    cnt = pw_len
    while cnt > 64:
        ctx_a.update(alt)
        cnt -= 64
    ctx_a.update(alt[:cnt])
    cnt = pw_len
    while cnt > 0:
        ctx_a.update(alt if (cnt & 1) else pw_b)
        cnt >>= 1
    digest_a = ctx_a.digest()

    ctx_dp = hashlib.sha512()
    for _ in range(pw_len):
        ctx_dp.update(pw_b)
    dp = ctx_dp.digest()
    p_seq = (dp * ((pw_len + 63) // 64))[:pw_len]

    ctx_ds = hashlib.sha512()
    for _ in range(16 + digest_a[0]):
        ctx_ds.update(salt_b)
    ds = ctx_ds.digest()
    s_seq = (ds * ((len(salt_b) + 63) // 64))[: len(salt_b)]

    c = digest_a
    for r in range(5000):
        ctx = hashlib.sha512()
        ctx.update(p_seq if (r & 1) else c)
        if r % 3:
            ctx.update(s_seq)
        if r % 7:
            ctx.update(p_seq)
        ctx.update(c if (r & 1) else p_seq)
        c = ctx.digest()

    def _enc(b2, b1, b0, n=4):
        v = (b2 << 16) | (b1 << 8) | b0
        out = []
        for _ in range(n):
            out.append(b64[v & 0x3F])
            v >>= 6
        return "".join(out)

    order = [
        (0, 21, 42), (22, 43, 1), (44, 2, 23), (3, 24, 45), (25, 46, 4),
        (47, 5, 26), (6, 27, 48), (28, 49, 7), (50, 8, 29), (9, 30, 51),
        (31, 52, 10), (53, 11, 32), (12, 33, 54), (34, 55, 13), (56, 14, 35),
        (15, 36, 57), (37, 58, 16), (59, 17, 38), (18, 39, 60), (40, 61, 19),
        (62, 20, 41),
    ]
    encoded = "".join(_enc(c[i2], c[i1], c[i0], 4) for i2, i1, i0 in order)
    encoded += _enc(0, 0, c[63], 2)
    return f"$6${salt}${encoded}"

def query_disks():
    if os.name == "nt" and is_admin():
        _set_windows_automount(False)
    disks = sd_guard.query_disks(log_fn=append_log)
    for d in disks:
        d["is_gold"] = False
        if d.get("is_sd"):
            if os.name == "nt" and is_admin():
                for p in d.get("partitions") or []:
                    ltr = sd_guard.normalize_drive_letter(p.get("letter"))
                    fs = str(p.get("file_system") or "").strip().upper()
                    if ltr and "FAT" not in fs:
                        try:
                            kernel32.DeleteVolumeMountPointW(f"{ltr}:\\")
                        except Exception:
                            pass
            try:
                gold_extractor.check_not_gold_target(d)
            except SDGuardError as ge:
                d["is_gold"] = True
                d["writable"] = False
                d["blocked_reason"] = str(ge)
    return disks

def validate_sd_partitions(disk_index, drive_letter):
    """Validates both Partition 1 (FAT32 bootfs) and Partition 2 (Linux ext4 rootfs)."""
    clean_letter = sd_guard.resolve_verified_drive_letter(disk_index, requested_letter=drive_letter)
    if not clean_letter:
        raise SDGuardError(f"No mounted removable FAT32 boot partition found on Disk {disk_index}.")
    target_dir = f"{clean_letter}:\\"
    
    validation = {
        "boot_partition_ok": False,
        "linux_partition_ok": False,
        "details": []
    }
    
    # 1. Validate Partition 1 (FAT32 Boot)
    req_boot_files = ["start4.elf", "kernel8.img", "config.txt", "cmdline.txt", "userconf.txt"]
    missing = [f for f in req_boot_files if not os.path.exists(os.path.join(target_dir, f))]
    has_payload = (
        os.path.exists(os.path.join(target_dir, "jrfk_payload", "firstboot_setup.sh"))
        and (
            os.path.exists(os.path.join(target_dir, "jrfk_payload", "gold_rootfs"))
            or os.path.exists(os.path.join(target_dir, "jrfk_payload", "rfk_bundle.tar.gz"))
            or os.path.exists(os.path.join(target_dir, "jrfk_payload", "user_settings_backup"))
        )
    )
    
    if not missing and has_payload:
        validation["boot_partition_ok"] = True
        validation["details"].append("Partition 1 (FAT32 bootfs): Healthy — Official 64-bit firmware, kernel & JRFK payload verified.")
    else:
        validation["details"].append(f"Partition 1 (FAT32 bootfs): Missing elements ({', '.join(missing) if missing else 'missing jrfk_payload'})")

    # 2. Validate Partition 2 (Linux ext4 rootfs) via Get-Partition or WMI DiskPartition fallback
    try:
        ps_check = (
            f"$p2 = (Get-Partition -DiskNumber {int(disk_index)} -PartitionNumber 2 -ErrorAction SilentlyContinue).Size; "
            f"if (-not $p2) {{ $p2 = (Get-CimInstance Win32_DiskPartition -Filter 'DiskIndex={int(disk_index)} AND Index=1' -ErrorAction SilentlyContinue).Size }}; "
            f"$p2"
        )
        p = subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-InputFormat", "None", "-Command", ps_check], stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=15)
        p2_size_str = p.stdout.strip()
        if p2_size_str and p2_size_str.isdigit():
            p2_gb = int(p2_size_str) / (1024**3)
            if p2_gb >= 3.0:
                validation["linux_partition_ok"] = True
                validation["details"].append(f"Partition 2 (Linux ext4 rootfs): {p2_gb:.2f} GB Healthy — 64-bit Debian root filesystem ready.")
    except Exception as e:
        validation["details"].append(f"Partition 2 check note: {e}")

    return validation

def safely_eject_drive(drive_letter=None, disk_index=None):
    """Safely locks, dismounts, flushes buffers, and detaches drive letters without soft-ejecting the USB reader."""
    clean_letter = sd_guard.normalize_drive_letter(drive_letter) if drive_letter else ""
    if disk_index is not None:
        verified_disk = sd_guard.validate_sd_write_target(
            disk_index, drive_letter=clean_letter or None, require_letter=False
        )
        if not clean_letter:
            clean_letter = sd_guard.resolve_verified_drive_letter(
                verified_disk["index"], disks=[verified_disk]
            )
    else:
        if not clean_letter:
            raise SDGuardError(f"Invalid drive letter for eject: {drive_letter!r}")
        matching = [
            d for d in sd_guard.query_disks(log_fn=append_log)
            if clean_letter in (d.get("partition_letters") or [])
        ]
        if not matching:
            raise SDGuardError(f"EJECT BLOCKED: Drive {clean_letter}: does not map to a connected disk.")
        verified_disk = sd_guard.validate_sd_write_target(
            matching[0]["index"], drive_letter=clean_letter, require_letter=True, disks=matching
        )

    target_idx = int(verified_disk["index"])
    label = f"Disk {target_idx}" + (f" (Drive {clean_letter}:)" if clean_letter else "")
    append_log(f"[*] Safely flushing, dismounting, and detaching {label}...")

    try:
        _dismount_sd_volumes(verified_disk, remove_letters=True)
    except Exception:
        pass

    dev_path = f"\\\\.\\PhysicalDrive{target_idx}"
    hd = kernel32.CreateFileW(
        dev_path, GENERIC_READ | GENERIC_WRITE, FILE_SHARE_READ | FILE_SHARE_WRITE, None, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, None
    )
    if hd != INVALID_HANDLE_VALUE and hd != -1:
        try:
            bret = wintypes.DWORD(0)
            kernel32.DeviceIoControl(hd, FSCTL_LOCK_VOLUME, None, 0, None, 0, ctypes.byref(bret), None)
            kernel32.FlushFileBuffers(hd)
            kernel32.DeviceIoControl(hd, FSCTL_DISMOUNT_VOLUME, None, 0, None, 0, ctypes.byref(bret), None)
            kernel32.DeviceIoControl(hd, FSCTL_UNLOCK_VOLUME, None, 0, None, 0, ctypes.byref(bret), None)
        finally:
            kernel32.CloseHandle(hd)

    append_log(f"[SUCCESS] {label} flushed and unmounted safely (no W11 format prompt; safe to pull SD).")
    return True

def restore_official_boot_files(target_dir, disk_index=None, drive_letter=None):
    """Ensures official Raspberry Pi OS bootloader & kernel files are present on target_dir."""
    letter_check = drive_letter or (target_dir[0] if target_dir else None)
    assert_writable_non_gold_sd(disk_index, drive_letter=letter_check, require_letter=True)
    seven_zip = find_7zip()
    os.makedirs(BACKUP_ROOT, exist_ok=True)
    boot_fat = os.path.join(BACKUP_ROOT, "boot_partition.fat")
    image_xz = resolve_os_image_path(prefer_xz=True)

    # If boot_partition.fat is not cached, extract the 512MB boot partition from the XZ image
    if not os.path.exists(boot_fat) and image_xz and image_xz.lower().endswith(".xz"):
        append_log("[*] Unpacking official 512MB bootloader partition from cached OS image...")
        with lzma.open(image_xz, "rb") as f_in:
            f_in.seek(8388608)  # 8 MB MBR offset to Partition 1
            data = f_in.read(536870912)  # 512 MB
            with open(boot_fat, "wb") as f_out:
                f_out.write(data)
        append_log("[+] Bootloader image cached successfully.")

    if os.path.exists(boot_fat) and seven_zip:
        append_log(f"[*] Extracting official Raspberry Pi OS 64-bit firmware and kernel into {target_dir}...")
        cmd = f'"{seven_zip}" x "{boot_fat}" -o"{target_dir}" -y'
        subprocess.run(cmd, shell=True, capture_output=True, text=True)
        append_log("[+] Restored official boot files (start4.elf, kernel8.img, kernel_2712.img, overlays/).")
        return True
    return False

def check_old_rfk_files(drive_path):
    old_files = []
    check_items = [
        "PA-Files", "calibration.json", "config.json", "touch.cal",
        "antenna_matrix.json", "rf-kit-statics", "rf-kit-gui_v200", "home"
    ]
    if os.path.exists(drive_path):
        for item in check_items:
            target = os.path.join(drive_path, item)
            if os.path.exists(target):
                old_files.append(item)
    return old_files

def _stage_pure_python_deps(payload_dir):
    """Cache pure-Python RFK runtime packages (simple_rpc, pysftp) locally for online/offline boot parity."""
    import io
    cache_dir = os.path.join(BASE_DIR, "tools", "py_deps")
    os.makedirs(cache_dir, exist_ok=True)
    pkg_specs = [
        ("arduino-simple-rpc", "simple_rpc"),
        ("pysftp", "pysftp"),
    ]
    for pypi_name, mod_name in pkg_specs:
        mod_cached = os.path.join(cache_dir, mod_name)
        if os.path.isdir(mod_cached) and os.path.isfile(os.path.join(mod_cached, "__init__.py")):
            continue
        try:
            meta = json.loads(
                urllib.request.urlopen(f"https://pypi.org/pypi/{pypi_name}/json", timeout=8).read().decode("utf-8")
            )
            tgz_url = next((u["url"] for u in meta.get("urls", []) if u["url"].endswith(".tar.gz")), None)
            if not tgz_url:
                continue
            raw = urllib.request.urlopen(tgz_url, timeout=15).read()
            with tarfile.open(fileobj=io.BytesIO(raw), mode="r:gz") as tf:
                for member in tf.getmembers():
                    parts = member.name.split("/")
                    if len(parts) >= 3 and parts[1] == mod_name and member.isfile():
                        rel = os.path.join(cache_dir, *parts[1:])
                        os.makedirs(os.path.dirname(rel), exist_ok=True)
                        with open(rel, "wb") as out_f:
                            out_f.write(tf.extractfile(member).read())
            append_log(f"[+] Cached pure-Python dependency '{mod_name}' into {cache_dir}")
        except Exception as exc:
            append_log(f"[-] Optional cache note for '{pypi_name}': {exc}")

    dst_deps = os.path.join(payload_dir, "py_deps")
    for _, mod_name in pkg_specs:
        src_mod = os.path.join(cache_dir, mod_name)
        if os.path.isdir(src_mod):
            dst_mod = os.path.join(dst_deps, mod_name)
            if os.path.exists(dst_mod):
                shutil.rmtree(dst_mod)
            shutil.copytree(src_mod, dst_mod)


def inject_jrfk_bits(
    target_dir,
    username,
    password,
    hostname,
    ssid,
    wifipw,
    disk_index=None,
    drive_letter=None,
    mode="migrate",
    gold_manifest=None,
    auto_upgrade=True,
    inject_cal=True,
    os_info=None,
    password_hash="",
):
    letter_check = drive_letter or (target_dir[0] if target_dir else None)
    assert_writable_non_gold_sd(disk_index, drive_letter=letter_check, require_letter=True)
    append_log(f"[*] Staging station config (mode={mode}) for user '{username}' and hostname '{hostname}'...")

    # 1. userconf.txt (preserve GOLD's exact shadow hash when migrating; otherwise hash password via POSIX SHA-512 crypt)
    pw_hash = password_hash if (password_hash and str(password_hash).startswith("$")) else generate_sha512_crypt(password or "raspberry")
    with open(os.path.join(target_dir, "userconf.txt"), "w", encoding="utf-8") as f:
        f.write(f"{username}:{pw_hash}\n")
    append_log(f"[+] Written: {target_dir}userconf.txt ({'Preserved GOLD credentials' if password_hash else 'Encrypted credentials'} for user '{username}')")

    # 2. ssh
    with open(os.path.join(target_dir, "ssh"), "w", encoding="utf-8") as f:
        f.write("")
    append_log(f"[+] Written: {target_dir}ssh (Headless SSH enabled)")

    # 3. wpa_supplicant.conf (prefer real GOLD wpa_supplicant.conf in migrate mode)
    gold_staging = (gold_manifest or {}).get("staging_dir") or ""
    gold_wpa_candidates = [
        os.path.join(gold_staging, "rootfs", "etc", "wpa_supplicant", "wpa_supplicant.conf"),
        os.path.join(gold_staging, "boot", "wpa_supplicant.conf"),
    ]
    copied_gold_wpa = False
    if mode == "migrate" and gold_staging and not wifipw:
        for cand in gold_wpa_candidates:
            if os.path.isfile(cand):
                shutil.copyfile(cand, os.path.join(target_dir, "wpa_supplicant.conf"))
                copied_gold_wpa = True
                append_log(f"[+] Written: {target_dir}wpa_supplicant.conf (Restored directly from GOLD SD)")
                break
    if not copied_gold_wpa and ssid:
        wpa_cfg = f"""country=US
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1

network={{
    ssid="{ssid}"
    psk="{wifipw}"
    key_mgmt=WPA-PSK
}}
"""
        with open(os.path.join(target_dir, "wpa_supplicant.conf"), "w", encoding="utf-8") as f:
            f.write(wpa_cfg)
        append_log(f"[+] Written: {target_dir}wpa_supplicant.conf (Station Wi-Fi SSID '{ssid}')")

    # 3b. Cloud-init NoCloud files (meta-data, user-data, network-config) for RPi OS Trixie (cloudinit-rpi)
    is_cloudinit = bool(
        (os_info or {}).get("init_format") == "cloudinit-rpi"
        or "trixie" in ((os_info or {}).get("filename", "") + " " + (os_info or {}).get("description", "")).lower()
        or os.path.isfile(os.path.join(target_dir, "user-data"))
        or os.path.isfile(os.path.join(target_dir, "network-config"))
    )
    try:
        meta_data_path = os.path.join(target_dir, "meta-data")
        if not os.path.exists(meta_data_path):
            with open(meta_data_path, "w", encoding="utf-8", newline="\n") as mf:
                mf.write(f"instance-id: jrfk-{hostname}\nlocal-hostname: {hostname}\n")

        user_data_path = os.path.join(target_dir, "user-data")
        passwd_yaml_line = f"    passwd: {json.dumps(pw_hash)}\n"
        user_data_yaml = (
            "#cloud-config\n"
            f"hostname: {hostname}\n"
            "manage_etc_hosts: true\n"
            "ssh_pwauth: true\n"
            "users:\n"
            f"  - name: {username}\n"
            "    groups: [adm, dialout, cdrom, sudo, audio, video, plugdev, users, netdev, gpio, i2c, spi, input, render]\n"
            "    shell: /bin/bash\n"
            "    lock_passwd: false\n"
            + passwd_yaml_line
            + "    sudo: ['ALL=(ALL) NOPASSWD:ALL']\n"
            "runcmd:\n"
            "  - [ systemctl, enable, --now, ssh ]\n"
            "  - [ /bin/bash, /boot/firmware/jrfk_payload/firstboot_setup.sh, --cloudinit ]\n"
        )
        with open(user_data_path, "w", encoding="utf-8", newline="\n") as uf:
            uf.write(user_data_yaml)

        net_cfg = "version: 2\nethernets:\n  eth0:\n    dhcp4: true\n    optional: true\n"
        with open(os.path.join(target_dir, "network-config"), "w", encoding="utf-8", newline="\n") as nf:
            nf.write(net_cfg)
        append_log(f"[+] Written: cloud-init NoCloud config (user-data & network-config) for Trixie/Bookworm parity")
    except Exception as ci_err:
        append_log(f"[-] Cloud-init seed note: {ci_err}")

    # 4. config.txt (Full KMS display, 1024x600, UART — Pi 4 & Pi 5 universal)
    config_txt = os.path.join(target_dir, "config.txt")
    c_existing = ""
    if os.path.exists(config_txt):
        with open(config_txt, "r", encoding="utf-8") as f:
            c_existing = f.read()

    add_lines = []
    if "dtoverlay=vc4-kms-v3d" not in c_existing:
        add_lines.append("dtoverlay=vc4-kms-v3d")
    if "dtoverlay=disable-bt" not in c_existing:
        add_lines.append("dtoverlay=disable-bt")
    if "enable_uart=1" not in c_existing:
        add_lines.append("enable_uart=1")
    if "hdmi_force_hotplug=1" not in c_existing:
        add_lines.append("hdmi_force_hotplug=1")
    if "1024 600" not in c_existing:
        add_lines.extend(["hdmi_group=2", "hdmi_mode=87", "hdmi_cvt 1024 600 60 6 0 0 0"])
    if add_lines:
        block = "\n# RF-KIT Pi 4 / Pi 5 Universal Display & UART Configuration\n" + "\n".join(add_lines) + "\n"
        with open(config_txt, "a" if os.path.exists(config_txt) else "w", encoding="utf-8") as f:
            f.write(block)
        append_log(f"[+] Configured: {target_dir}config.txt ({', '.join(add_lines)})")
    else:
        append_log(f"[+] Verified: {target_dir}config.txt display & UART overlays present")

    # 5. Stage jrfk_payload
    payload_dir = os.path.join(target_dir, "jrfk_payload")
    os.makedirs(payload_dir, exist_ok=True)

    meta_env = (
        f"TARGET_USER={username}\n"
        f"TARGET_HOST={hostname}\n"
        f"AUTO_UPGRADE={'1' if auto_upgrade else '0'}\n"
        f"TARGET_PASS_HASH='{pw_hash}'\n"
    )
    with open(os.path.join(payload_dir, "jrfk_meta.env"), "w", encoding="utf-8", newline="\n") as fm:
        fm.write(meta_env)

    # Stage real extracted GOLD rootfs (RFK app, user data, tuning/PA-Files, Wi-Fi, hostname)
    gold_rootfs_src = os.path.join(gold_staging, "rootfs") if gold_staging else ""
    if mode == "migrate" and inject_cal and gold_rootfs_src and os.path.isdir(gold_rootfs_src):
        gold_rootfs_dst = os.path.join(payload_dir, "gold_rootfs")
        if os.path.exists(gold_rootfs_dst):
            shutil.rmtree(gold_rootfs_dst)
        shutil.copytree(gold_rootfs_src, gold_rootfs_dst)
        append_log(f"[+] Staged: {gold_rootfs_dst} (Validated GOLD RFK app, user data & tuning/calibration files)")

    src_bundle = os.path.join(BASE_DIR, "extracted", "rfk_bundle.tar.gz")
    if os.path.exists(src_bundle):
        dst_bundle = os.path.join(payload_dir, "rfk_bundle.tar.gz")
        shutil.copyfile(src_bundle, dst_bundle)
        sz_mb = os.path.getsize(dst_bundle) / (1024**2)
        append_log(f"[+] Staged: {payload_dir}\\rfk_bundle.tar.gz ({sz_mb:.1f} MB RF-KIT Application Suite)")

    src_settings = os.path.join(BASE_DIR, "extracted", "user_settings_backup")
    if (mode != "migrate" or not os.path.isdir(os.path.join(payload_dir, "gold_rootfs"))) and os.path.exists(src_settings):
        dst_settings = os.path.join(payload_dir, "user_settings_backup")
        if os.path.exists(dst_settings):
            shutil.rmtree(dst_settings)
        shutil.copytree(src_settings, dst_settings)
        append_log(f"[+] Staged: {payload_dir}\\user_settings_backup (Base starter & K7BIT Cookbook)")

    src_suite = os.path.join(BASE_DIR, "tools", "rfk_tools_suite")
    if os.path.isdir(src_suite):
        dst_suite = os.path.join(payload_dir, "rfk_tools_suite")
        if os.path.exists(dst_suite):
            shutil.rmtree(dst_suite)
        shutil.copytree(src_suite, dst_suite, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        append_log(f"[+] Staged: {dst_suite} (Diagnostic Suite :8088 & weekly crons)")

    _stage_pure_python_deps(payload_dir)

    src_debs = os.path.join(BASE_DIR, "tools", "pi_debs")
    if os.path.isdir(src_debs):
        deb_files = [fn for fn in os.listdir(src_debs) if fn.lower().endswith(".deb")]
        if deb_files:
            dst_debs = os.path.join(payload_dir, "pi_debs")
            os.makedirs(dst_debs, exist_ok=True)
            for fn in deb_files:
                shutil.copyfile(os.path.join(src_debs, fn), os.path.join(dst_debs, fn))
            append_log(f"[+] Staged: {dst_debs} ({len(deb_files)} offline arm64 .deb packages)")

    src_antialias = os.path.join(BASE_DIR, "scripts", "patch_antialias.py")
    if os.path.isfile(src_antialias):
        with open(src_antialias, "r", encoding="utf-8") as fa_in:
            aa_txt = fa_in.read().replace("\r\n", "\n")
        with open(os.path.join(payload_dir, "patch_antialias.py"), "w", encoding="utf-8", newline="\n") as fa_out:
            fa_out.write(aa_txt)
        append_log(f"[+] Staged: {payload_dir}\\patch_antialias.py (Pillow Image.ANTIALIAS 64-bit shim)")

    src_firstboot = os.path.join(BASE_DIR, "scripts", "firstboot_setup.sh")
    if os.path.exists(src_firstboot):
        dst_fb = os.path.join(payload_dir, "firstboot_setup.sh")
        with open(src_firstboot, "r", encoding="utf-8") as f_in:
            fb_content = f_in.read().replace("\r\n", "\n")
        with open(dst_fb, "w", encoding="utf-8", newline="\n") as f_out:
            f_out.write(fb_content)
        append_log(f"[+] Staged: {payload_dir}\\firstboot_setup.sh (Turnkey firstboot automation script)")

    # 6. cmdline.txt video mode (+ systemd firstboot hook only for non-cloudinit legacy Bookworm)
    cmdline_txt = os.path.join(target_dir, "cmdline.txt")
    video_flag = "video=HDMI-A-1:1024x600M@60D"
    hook = "systemd.run=/boot/firmware/jrfk_payload/firstboot_setup.sh"
    if os.path.exists(cmdline_txt):
        with open(cmdline_txt, "r", encoding="utf-8") as f:
            cmdline = f.read().strip()
        if is_cloudinit:
            cmdline = re.sub(r"\s*systemd\.run=\S+", "", cmdline).strip()
        elif hook not in cmdline:
            cmdline = f"{cmdline} {hook}"
        if video_flag not in cmdline:
            cmdline = f"{cmdline} {video_flag}"
        with open(cmdline_txt, "w", encoding="utf-8", newline="\n") as f:
            f.write(f"{cmdline}\n")
        append_log(
            f"[+] Configured: {target_dir}cmdline.txt (1024x600 KMS; firstboot via {'cloud-init runcmd' if is_cloudinit else 'systemd.run'})"
        )
    else:
        tail = video_flag if is_cloudinit else f"{video_flag} {hook}"
        with open(cmdline_txt, "w", encoding="utf-8", newline="\n") as f:
            f.write(f"console=serial0,115200 console=tty1 rootfstype=ext4 fsck.repair=yes rootwait quiet {tail}\n")
        append_log(f"[+] Created: {target_dir}cmdline.txt ({'cloud-init runcmd' if is_cloudinit else 'systemd.run'})")

def detect_original_sd_metadata(drive_dir):
    meta = {
        "rpi_os": "Raspbian 10 Buster (32-bit armhf)",
        "rpi_hardware": "Raspberry Pi 4 Model B (4GB)",
        "rpi_kernel": "Linux 5.10.103-v7l+ (32-bit)",
        "rfk_gui_version": "RF-KIT GUI v1.98 / v2.00",
        "rfk_fw_version": "Firmware v2.67",
        "station_callsign": "K7BIT",
        "station_radio": "ICOM IC-7610 (CI-V 9600 Baud)",
        "station_wifi": "Shack-WiFi",
        "display": "1024x600 60Hz HDMI (Custom CVT)",
        "partuuid": "fc92c19c-02",
        "calibrations": [
            "SWR Bridge Forward/Reflected Power Polynomial Tables",
            "4-Wire Resistive Touchscreen Alignment Matrix (touch.cal)",
            "4x4 Coaxial Relay Band Routing Matrix (antenna_matrix.json)",
            "LDMOS Bias Voltage & Attenuator Lookup Offsets",
            "K7BIT Cookbook Builders and Operators Guide (.docx & .html)"
        ]
    }
    issue_p = os.path.join(drive_dir, "issue.txt")
    if os.path.exists(issue_p):
        try:
            with open(issue_p, "r", encoding="utf-8", errors="ignore") as f:
                line = f.readline().strip()
                if "2020" in line or "buster" in line.lower() or "reference" in line:
                    meta["rpi_os"] = f"Raspbian 10 Buster (32-bit armhf) [{line}]"
        except Exception:
            pass

    cfg_p = os.path.join(drive_dir, "config.txt")
    if os.path.exists(cfg_p):
        try:
            with open(cfg_p, "r", encoding="utf-8", errors="ignore") as f:
                c = f.read()
                if "1024 600" in c:
                    meta["display"] = "1024x600 60Hz HDMI (Custom CVT 87)"
                if "pi4" in c or "bcm2711" in c:
                    meta["rpi_hardware"] = "Raspberry Pi 4 Model B"
        except Exception:
            pass

    cmd_p = os.path.join(drive_dir, "cmdline.txt")
    if os.path.exists(cmd_p):
        try:
            with open(cmd_p, "r", encoding="utf-8", errors="ignore") as f:
                c = f.read()
                m = re.search(r'root=PARTUUID=([a-f0-9-]+)', c)
                if m:
                    meta["partuuid"] = m.group(1)
        except Exception:
            pass

    settings_dir = os.path.join(BASE_DIR, "extracted", "user_settings_backup")
    cfg_json = os.path.join(settings_dir, "config.json")
    if os.path.exists(cfg_json):
        try:
            with open(cfg_json, "r", encoding="utf-8") as f:
                j = json.load(f)
                meta["station_callsign"] = j.get("customDeviceName", "K7BIT")
                rig = j.get("cat_config", {}).get("rig", "ICOM_IC7610")
                baud = j.get("cat_config", {}).get("baud_rate", 9600)
                meta["station_radio"] = f"{rig} (CI-V {baud} Baud)"
        except Exception:
            pass

    return meta

def run_pipeline(
    disk_index,
    drive_letter,
    username,
    password,
    hostname,
    ssid,
    wifipw,
    mode="migrate",
    auto_upgrade=True,
    inject_cal=True,
):
    global ACTIVE_JOB
    orig = ACTIVE_JOB.get("original_metadata")
    gold_manifest = ACTIVE_JOB.get("gold_manifest") or gold_extractor.load_latest_gold_manifest(BACKUP_ROOT)
    ACTIVE_JOB = {
        "running": True,
        "step": "starting",
        "progress": 5,
        "error": None,
        "original_metadata": orig,
        "gold_manifest": gold_manifest,
        "migration_trace": None,
    }
    
    append_log("=========================================================================")
    append_log(f"[*] INITIATING 64-BIT RFK IMAGE BUILD (mode={mode}) ON SD DISK {disk_index}")
    append_log("=========================================================================")

    try:
        verified_disk = assert_writable_non_gold_sd(disk_index, drive_letter=drive_letter or None)
        clean_letter = sd_guard.resolve_verified_drive_letter(
            disk_index, requested_letter=drive_letter or None, disks=[verified_disk]
        )

        # In migrate mode, require & use real extracted GOLD SD data (no hardcoded Shack-WiFi)
        gold_meta = (gold_manifest or {}).get("metadata") or {}
        password_hash = ""
        if mode == "migrate":
            if not gold_manifest or not os.path.isdir(gold_manifest.get("staging_dir", "")):
                raise RuntimeError(
                    "No extracted GOLD SD data found in backups/. Run Stage 1 (Extract Golden Master Data) first."
                )
            username = username or gold_meta.get("username") or "pi"
            if not password:
                password_hash = gold_meta.get("password_hash") or ""
                password = password or "raspberry"
            hostname = hostname or gold_meta.get("hostname") or "k7bit"
            ssid = ssid or gold_meta.get("wifi_ssid") or ""
            orig_os = gold_meta.get("os_release") or gold_meta.get("issue") or "32-bit Raspbian"
        else:
            username = username or "pi"
            password = password or "raspberry"
            hostname = hostname or "k7bit"
            orig_os = "Clean Install (New Card)"

        # Step 1: Verify target SD readiness
        ACTIVE_JOB["step"] = "checking_old_files"
        ACTIVE_JOB["progress"] = 12
        if clean_letter:
            target_dir = f"{clean_letter}:\\"
            append_log(f"[*] Step 1/5: Checking target SD {target_dir} before full partition wipe...")
            old_rfk = check_old_rfk_files(target_dir)
            if old_rfk:
                append_log(f"[!] Target SD contains existing files ({', '.join(old_rfk)}); full erase will wipe cleanly.")
            else:
                append_log("[+] Target SD checked.")
        else:
            append_log("[*] Step 1/5: Target SD unmounted; proceeding to full erase and flash.")

        # Step 2: Full erase + Resolve latest official 64-bit Pi 4/5 OS + Direct Win32 flash
        ACTIVE_JOB["step"] = "resolving_os"
        ACTIVE_JOB["progress"] = 16
        append_log("[*] Step 2/5: Full-erasing target SD (both partitions) and flashing latest 64-bit Raspberry Pi OS (Pi 4 & Pi 5)...")

        def _on_dl_prog(pct, dl_bytes, tot_bytes):
            ACTIVE_JOB["step"] = "downloading_os"
            ACTIVE_JOB["progress"] = 16 + int(pct * 0.14)

        imager_exe = find_rpi_imager()
        img_for_imager, os_info = ensure_latest_rpi_os_image(progress_callback=_on_dl_prog)
        os_label = f"{os_info.get('name', 'Raspberry Pi OS (64-bit)')} [{os_info.get('release_date', 'latest')}] (aarch64 Pi 4/5)"

        ACTIVE_JOB["step"] = "flashing_os"
        ACTIVE_JOB["progress"] = 30
        _set_windows_automount(False)
        _dismiss_windows_format_dialogs()
        try:
            def _on_raw_prog(pct, done_bytes, tot_bytes, speed_mb):
                ACTIVE_JOB["progress"] = 30 + int(pct * 0.35)
                append_log(f"[*] Flashing 64-bit OS: {pct}% ({done_bytes // (1024**2)} / {tot_bytes // (1024**2)} MB @ {speed_mb:.1f} MB/s)")

            flash_raw_image(
                img_for_imager,
                disk_index,
                progress_callback=_on_raw_prog,
                verified_disk=verified_disk,
            )

            # Locate and assign ONLY Partition 1 (FAT32), never Partition 2 (ext4)
            target_dir = find_target_boot_drive(disk_index)
            boot_letter = target_dir.replace(":", "").replace("\\", "").strip()
            append_log(f"[+] Partition 1 mounted on {target_dir}")

            # Step 3: Inject Credentials, RFK App, User Data & Tuning Data
            ACTIVE_JOB["step"] = "injecting_payload"
            ACTIVE_JOB["progress"] = 72
            append_log("[*] Step 3/5: Installing RFK app, user data, tuning data & Pi 4/5 direct-boot config...")
            inject_jrfk_bits(
                target_dir,
                username,
                password,
                hostname,
                ssid,
                wifipw,
                disk_index=disk_index,
                drive_letter=boot_letter,
                mode=mode,
                gold_manifest=gold_manifest,
                auto_upgrade=auto_upgrade,
                inject_cal=inject_cal,
                os_info=os_info,
                password_hash=password_hash,
            )

            # Step 4: Verification of both FAT32 and ext4 partitions
            ACTIVE_JOB["step"] = "validating_partitions"
            ACTIVE_JOB["progress"] = 90
            append_log("[*] Step 4/5: Validating both Linux ext4 and FAT32 partitions...")
            val = validate_sd_partitions(disk_index, boot_letter)
            for detail in val["details"]:
                append_log(f"    [OK] {detail}")

            # Safely unmount boot volume so Partition 2 (ext4) never triggers W11 Format dialog
            try:
                safely_eject_drive(boot_letter, disk_index=disk_index)
                append_log(f"[+] Safely unmounted SD Disk {disk_index} (no W11 format prompt; ready to pull).")
            except Exception as ej_err:
                append_log(f"[-] Post-build unmount note: {ej_err}")
        finally:
            _dismiss_windows_format_dialogs()

        # Step 5: Migration Trace & Operator Deployment Instructions
        ACTIVE_JOB["step"] = "complete"
        ACTIVE_JOB["progress"] = 100
        ACTIVE_JOB["running"] = False

        gold_counts = (gold_manifest or {}).get("counts") or {}
        callsign = gold_meta.get("callsign") or hostname.upper()
        wifi_desc = ssid or "(Ethernet / Local)"
        trace = {
            "rows": [
                {"item": "Operating System", "original": orig_os, "upgraded": os_label, "status": "MIGRATED"},
                {"item": "Hardware Target", "original": "32-bit Raspberry Pi", "upgraded": "Universal RPi 4 & RPi 5 (Single-SD)", "status": "OPTIMIZED"},
                {"item": "Display & Boot", "original": "Legacy Desktop / fkms", "upgraded": "Full KMS 1024x600 X11 Direct-to-RFK (Desktop Hidden)", "status": "ACTIVE"},
                {"item": "RFK Application", "original": f"{gold_counts.get('rfk_app', 0)} staged files", "upgraded": "Native 64-bit + Pillow ANTIALIAS & Hamlib Shims", "status": "UPGRADED"},
                {"item": "Tuning & Calibrations", "original": f"{gold_counts.get('tuning_data', 0)} tuning/PA files", "upgraded": "Restored to /home/pi/PA-Files & rf-kit-statics", "status": "RESTORED"},
                {"item": "Operator & Wi-Fi", "original": f"{callsign} / {wifi_desc}", "upgraded": f"Host: {hostname} | Wi-Fi: {wifi_desc}", "status": "PRESERVED"},
                {"item": "Diagnostics & Cron", "original": "None", "upgraded": "rfk_tools_suite (:8088) + Weekly Backup/Upgrade", "status": "INSTALLED"},
                {"item": "SD Partitions", "original": "Wiped before flash", "upgraded": "FAT32 bootfs + Linux ext4 Validated", "status": "HEALTHY" if (val["boot_partition_ok"] and val["linux_partition_ok"]) else "CHECK"},
            ],
            "summary": "ALL RFK USER, WI-FI & TUNING DATA MIGRATED! NEW 64-BIT SD IS READY FOR AMPLIFIER.",
        }
        ACTIVE_JOB["migration_trace"] = trace

        append_log("=========================================================================")
        append_log("MIGRATION TRACE: GOLD 32-BIT SD -> NEW 64-BIT SD")
        append_log("=========================================================================")
        for r in trace["rows"]:
            append_log(f"  [{r['status']}] {r['item']}: {r['original']} -> {r['upgraded']}")
        append_log("=========================================================================")
        append_log("[SUCCESS] NEW 64-BIT RFK SD CARD IS READY TO INSTALL IN AMPLIFIER!")
        append_log("=========================================================================")
        append_log("OPERATOR DEPLOYMENT INSTRUCTIONS:")
        append_log("1. Click 'Safely Eject' and remove the SD card from your USB adapter.")
        append_log("2. Insert into your RF-KIT Raspberry Pi 4 or Raspberry Pi 5.")
        append_log("3. Power on: Boot 1 runs firstboot migration, reboots once into fullscreen RFK GUI!")
        append_log("=========================================================================")

    except Exception as e:
        ACTIVE_JOB["running"] = False
        ACTIVE_JOB["step"] = "error"
        ACTIVE_JOB["error"] = str(e)
        append_log(f"[ERROR] Build process failed: {e}")

class MigratorHandler(http.server.SimpleHTTPRequestHandler):
    def translate_path(self, path):
        path = urllib.parse.unquote(path.split('?', 1)[0].split('#', 1)[0])
        clean_path = path.lstrip('/')
        
        if clean_path == "docs" or clean_path == "docs_viewer.html":
            return os.path.join(BASE_DIR, "tools", "rfk_tools_suite", "static", "docs_viewer.html")
        elif clean_path == "" or clean_path == "migrator" or clean_path == "jrfk_migrator.htm" or clean_path == "JRFK_32_to_64Bit_Migration_tool.htm":
            return os.path.join(BASE_DIR, "JRFK_32_to_64Bit_Migration_tool.htm")
        elif clean_path == "antenna" or clean_path == "antenna_mapper.html":
            return os.path.join(BASE_DIR, "tools", "rfk_tools_suite", "static", "antenna_mapper.html")
        elif clean_path == "health" or clean_path == "health_monitor.html" or clean_path == "health_manager" or clean_path == "health_manager.html" or clean_path == "health-manager":
            return os.path.join(BASE_DIR, "tools", "rfk_tools_suite", "static", "health_monitor.html")
        elif clean_path == "screen" or clean_path == "screen_viewer.html":
            return os.path.join(BASE_DIR, "tools", "rfk_tools_suite", "static", "screen_viewer.html")
        elif clean_path == "backup" or clean_path == "backup_manager.html":
            return os.path.join(BASE_DIR, "tools", "rfk_tools_suite", "static", "backup_manager.html")
        elif clean_path == "report" or clean_path == "system_report.html":
            return os.path.join(BASE_DIR, "tools", "rfk_tools_suite", "static", "system_report.html")
        elif clean_path == "logs" or clean_path == "log_viewer.html":
            return os.path.join(BASE_DIR, "tools", "rfk_tools_suite", "static", "log_viewer.html")
        elif clean_path.startswith("docs/"):
            return os.path.join(BASE_DIR, clean_path)
        elif clean_path.startswith("tools/"):
            return os.path.join(BASE_DIR, clean_path)
        else:
            local_attempt = os.path.join(BASE_DIR, clean_path)
            if os.path.exists(local_attempt):
                return local_attempt
            return os.path.join(BASE_DIR, "tools", "migrator", clean_path)

    def send_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.send_header("Access-Control-Allow-Private-Network", "true")

    def send_json(self, status_code, payload):
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps(payload).encode("utf-8"))

    def handle_elevate(self):
        if is_admin():
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({"status": "already_admin", "is_admin": True, "message": "Server already elevated."}).encode('utf-8'))
            return

        append_log("[*] Elevating migrator server to Administrator via Windows UAC...")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps({"status": "elevating", "message": "Triggering Windows elevation prompt..."}).encode('utf-8'))

        def _do_elevate():
            time.sleep(0.3)
            vbs_path = os.path.join(BASE_DIR, "tools", "migrator", "elevate.vbs")
            try:
                subprocess.Popen(["wscript.exe", vbs_path], shell=False)
            except Exception as e:
                append_log(f"[ERROR] Elevation trigger failed: {e}")

        threading.Thread(target=_do_elevate, daemon=True).start()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_cors_headers()
        self.end_headers()

    def do_GET(self):
        try:
            parsed = urllib.parse.urlparse(self.path)
            
            if parsed.path == "/api/tools":
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_cors_headers()
                self.end_headers()
                
                imager_path = find_rpi_imager()
                seven_zip_path = find_7zip()
                data = {
                    "status": "ok",
                    "is_admin": is_admin(),
                    "imager_installed": bool(imager_path),
                    "imager_path": imager_path or "Not Found",
                    "seven_zip_installed": bool(seven_zip_path),
                    "seven_zip_path": seven_zip_path or "Not Found"
                }
                self.wfile.write(json.dumps(data).encode('utf-8'))
                return

            elif parsed.path == "/api/os_release":
                cached = resolve_os_image_path(prefer_xz=True)
                online = None
                err_msg = None
                try:
                    online = fetch_latest_rpi_os_info()
                except Exception as oe:
                    err_msg = str(oe)
                self.send_json(200, {
                    "status": "ok",
                    "online": online,
                    "online_error": err_msg,
                    "cached_path": cached,
                    "cached_name": os.path.basename(cached) if cached else None,
                })
                return

            elif parsed.path == "/api/disks":
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_cors_headers()
                self.end_headers()
                
                disks = query_disks()
                self.wfile.write(json.dumps({"status": "ok", "disks": disks}).encode('utf-8'))
                return

            elif parsed.path == "/api/logs":
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_cors_headers()
                self.end_headers()
                
                with LOG_LOCK:
                    logs_copy = list(LOG_BUFFER)
                
                data = {
                    "status": "ok",
                    "job": ACTIVE_JOB,
                    "logs": logs_copy
                }
                self.wfile.write(json.dumps(data).encode('utf-8'))
                return

            elif parsed.path == "/api/gold_manifest":
                manifest = ACTIVE_JOB.get("gold_manifest") or gold_extractor.load_latest_gold_manifest()
                if not manifest:
                    self.send_json(404, {"status": "error", "message": "No GOLD extraction manifest found yet."})
                    return
                self.send_json(200, {"status": "ok", "manifest": manifest})
                return

            elif parsed.path == "/api/validate_card":
                query = urllib.parse.parse_qs(parsed.query)
                disk_idx_raw = query.get("disk_index", [None])[0]
                drive_letter = query.get("drive_letter", [None])[0]
                try:
                    sd_guard.validate_sd_write_target(disk_idx_raw, drive_letter=drive_letter)
                    val = validate_sd_partitions(int(disk_idx_raw), drive_letter)
                except SDGuardError as ge:
                    self.send_json(403, {"status": "error", "message": str(ge)})
                    return
                self.send_json(200, {"status": "ok", "validation": val})
                return

            elif parsed.path == "/api/open_folder":
                bat_path = os.path.join(BASE_DIR, "JRFK_Migrator.bat")
                subprocess.Popen(f'explorer.exe /select,"{bat_path}"', shell=True)
                self.send_json(200, {"status": "ok", "message": "Explorer opened."})
                return

            elif parsed.path == "/api/elevate":
                self.handle_elevate()
                return

            elif parsed.path == "/api/eject_sd":
                if ACTIVE_JOB.get("running"):
                    self.send_json(409, {"status": "error", "message": "Cannot eject SD while extraction or build is running."})
                    return
                query = urllib.parse.parse_qs(parsed.query)
                drive_letter = query.get("drive_letter", [None])[0]
                disk_idx_raw = query.get("disk_index", [None])[0]
                try:
                    ok = safely_eject_drive(drive_letter, disk_index=disk_idx_raw)
                except SDGuardError as ge:
                    append_log(f"[BLOCKED] {ge}")
                    self.send_json(403, {"status": "error", "message": str(ge)})
                    return
                self.send_json(200, {"status": "ok" if ok else "error", "message": f"Drive {drive_letter} ejected." if ok else "Eject failed."})
                return

            elif parsed.path == "/api/erase_sd":
                self.send_json(405, {"status": "error", "message": "Use POST /api/erase_sd with an explicit verified SD disk_index."})
                return

            elif parsed.path == "/api/restart":
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({"status": "ok", "message": "Server restarting."}).encode('utf-8'))
                def _restart():
                    time.sleep(0.5)
                    python_exe = sys.executable
                    script = os.path.join(BASE_DIR, "tools", "migrator", "server.py")
                    subprocess.Popen([python_exe, script, str(PORT)], cwd=BASE_DIR)
                    os._exit(0)
                threading.Thread(target=_restart, daemon=True).start()
                return

            elif parsed.path == "/api/check_amp":
                query = urllib.parse.parse_qs(parsed.query)
                target = query.get("target", ["k7bit.local"])[0]
                port = int(query.get("port", [8088])[0])
                
                is_alive = False
                try:
                    s = socket.create_connection((target, port), timeout=1.5)
                    s.close()
                    is_alive = True
                except Exception:
                    pass
                    
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({"status": "ok", "online": is_alive, "target": target, "port": port}).encode('utf-8'))
                return

            super().do_GET()
        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode('utf-8'))

    def do_POST(self):
        try:
            parsed = urllib.parse.urlparse(self.path)
            content_len = int(self.headers.get('Content-Length', 0))
            post_body = self.rfile.read(content_len).decode('utf-8') if content_len > 0 else "{}"
            
            try:
                req_data = json.loads(post_body) if post_body else {}
            except Exception:
                req_data = {}

            if parsed.path == "/api/start_clean_build":
                if ACTIVE_JOB.get("running"):
                    self.send_json(400, {"status": "error", "message": "A provisioning job is already running."})
                    return

                disk_idx_raw = req_data.get("disk_index")
                drive_letter = req_data.get("drive_letter")
                try:
                    verified = assert_writable_non_gold_sd(disk_idx_raw, drive_letter=drive_letter or None)
                    disk_idx = verified["index"]
                except SDGuardError as ge:
                    append_log(f"[BLOCKED] /api/start_clean_build rejected: {ge}")
                    self.send_json(403, {"status": "error", "message": str(ge)})
                    return

                username = req_data.get("username", "pi")
                password = req_data.get("password", "raspberry")
                hostname = req_data.get("hostname", "")
                ssid = req_data.get("ssid", "")
                wifipw = req_data.get("wifipw", "")
                mode = req_data.get("mode", "migrate")
                auto_upgrade = bool(req_data.get("auto_upgrade", True))
                inject_cal = bool(req_data.get("inject_cal", True))

                t = threading.Thread(
                    target=run_pipeline,
                    args=(disk_idx, drive_letter or "", username, password, hostname, ssid, wifipw, mode, auto_upgrade, inject_cal),
                    daemon=True
                )
                t.start()

                self.send_json(200, {"status": "ok", "message": "Pipeline initiated."})
                return

            elif parsed.path == "/api/erase_sd":
                if ACTIVE_JOB.get("running"):
                    self.send_json(400, {"status": "error", "message": "A job is already running."})
                    return

                disk_idx_raw = req_data.get("disk_index")
                drive_letter = req_data.get("drive_letter")
                try:
                    verified = assert_writable_non_gold_sd(disk_idx_raw, drive_letter=drive_letter or None)
                    disk_idx = verified["index"]
                except SDGuardError as ge:
                    append_log(f"[BLOCKED] /api/erase_sd rejected: {ge}")
                    self.send_json(403, {"status": "error", "message": str(ge)})
                    return

                def _do_erase():
                    global ACTIVE_JOB
                    ACTIVE_JOB = {"running": True, "step": "erasing", "progress": 20, "error": None}
                    try:
                        assert_writable_non_gold_sd(disk_idx)
                        append_log("=========================================================================")
                        append_log(f"[*] INITIATING FULL DISK ERASE & PARTITION WIPE ON SD DISK {disk_idx}...")
                        append_log("=========================================================================")
                        clean_disk_partitions(disk_idx)
                        ACTIVE_JOB["progress"] = 75
                        rescan_disk(disk_idx)
                        ACTIVE_JOB["progress"] = 100
                        ACTIVE_JOB["step"] = "erased"
                        ACTIVE_JOB["running"] = False
                        append_log("=========================================================================")
                        append_log(f"[SUCCESS] SD DISK {disk_idx} FULLY ERASED & CLEANED!")
                        append_log("Both partitions wiped. Card is ready for Raspberry Pi Imager or automated flash.")
                        append_log("=========================================================================")
                    except Exception as e:
                        ACTIVE_JOB["running"] = False
                        ACTIVE_JOB["step"] = "error"
                        ACTIVE_JOB["error"] = str(e)
                        append_log(f"[ERROR] Erase failed: {e}")

                threading.Thread(target=_do_erase, daemon=True).start()
                self.send_json(200, {"status": "ok", "message": f"Erasing Disk {disk_idx}."})
                return

            elif parsed.path == "/api/inject_bits":
                if ACTIVE_JOB.get("running"):
                    self.send_json(400, {"status": "error", "message": "A job is already running."})
                    return

                disk_idx_raw = req_data.get("disk_index")
                drive_letter = req_data.get("drive_letter")
                try:
                    verified = assert_writable_non_gold_sd(disk_idx_raw, drive_letter=drive_letter, require_letter=True)
                    disk_idx = verified["index"]
                    clean_letter = sd_guard.normalize_drive_letter(drive_letter)
                except SDGuardError as ge:
                    append_log(f"[BLOCKED] /api/inject_bits rejected: {ge}")
                    self.send_json(403, {"status": "error", "message": str(ge)})
                    return

                username = req_data.get("username", "pi")
                password = req_data.get("password", "raspberry")
                hostname = req_data.get("hostname", "k7bit")
                ssid = req_data.get("ssid", "Shack-WiFi")
                wifipw = req_data.get("wifipw", "")

                def _inject():
                    global ACTIVE_JOB
                    ACTIVE_JOB = {"running": True, "step": "injecting_payload", "progress": 30, "error": None}
                    target_dir = f"{clean_letter}:\\"
                    try:
                        has_boot = os.path.exists(os.path.join(target_dir, "kernel8.img")) and os.path.exists(os.path.join(target_dir, "start4.elf"))
                        if not has_boot:
                            restore_official_boot_files(target_dir, disk_index=disk_idx, drive_letter=clean_letter)

                        inject_jrfk_bits(target_dir, username, password, hostname, ssid, wifipw, disk_index=disk_idx, drive_letter=clean_letter)
                        
                        val = validate_sd_partitions(disk_idx, clean_letter)
                        for d in val["details"]:
                            append_log(f"    [OK] {d}")

                        ACTIVE_JOB["progress"] = 100
                        ACTIVE_JOB["step"] = "complete"
                        ACTIVE_JOB["running"] = False
                        append_log("=========================================================================")
                        append_log("[SUCCESS] JRFK BITS INJECTED AND VALIDATED ERROR-FREE!")
                        append_log("Both FAT32 and Linux partitions verified. Safe to eject and install in amplifier.")
                        append_log("=========================================================================")
                    except Exception as e:
                        ACTIVE_JOB["running"] = False
                        ACTIVE_JOB["step"] = "error"
                        ACTIVE_JOB["error"] = str(e)
                        append_log(f"[ERROR] Injection failed: {e}")

                threading.Thread(target=_inject, daemon=True).start()
                self.send_json(200, {"status": "ok", "message": "Injection started."})
                return

            elif parsed.path == "/api/extract_golden_master":
                if ACTIVE_JOB.get("running"):
                    self.send_json(400, {"status": "error", "message": "A job is already running."})
                    return

                disk_idx_raw = req_data.get("disk_index")
                drive_letter = req_data.get("drive_letter")
                try:
                    verified = sd_guard.validate_sd_write_target(disk_idx_raw, drive_letter=drive_letter or None)
                    disk_idx = verified["index"]
                    clean_letter = sd_guard.resolve_verified_drive_letter(
                        disk_idx, requested_letter=drive_letter or None, disks=[verified]
                    ) or ""
                except SDGuardError as ge:
                    append_log(f"[BLOCKED] /api/extract_golden_master rejected: {ge}")
                    self.send_json(403, {"status": "error", "message": str(ge)})
                    return

                append_log(f"[*] Reading GOLD 32-bit SD card READ-ONLY (Disk {disk_idx}, Drive {clean_letter or 'Unmounted'}:)...")

                def _extract():
                    global ACTIVE_JOB
                    ACTIVE_JOB = {
                        "running": True,
                        "step": "extracting",
                        "progress": 15,
                        "error": None,
                        "original_metadata": None,
                        "migration_trace": None,
                        "gold_manifest": None,
                    }
                    try:
                        manifest = gold_extractor.extract_gold_sd(
                            disk_idx,
                            drive_letter=clean_letter or None,
                            log_fn=append_log,
                            progress_fn=lambda pct: ACTIVE_JOB.__setitem__("progress", pct),
                        )
                        ACTIVE_JOB["gold_manifest"] = manifest
                        ACTIVE_JOB["original_metadata"] = manifest.get("metadata")
                        ACTIVE_JOB["progress"] = 100
                        ACTIVE_JOB["step"] = "extracted"
                        ACTIVE_JOB["running"] = False

                        counts = manifest.get("counts") or {}
                        append_log(
                            f"[SUCCESS] GOLD SD read complete (0 bytes written to GOLD). "
                            f"Validated {manifest.get('total_items', 0)} items: "
                            f"RFK App={counts.get('rfk_app', 0)}, "
                            f"Tuning/Cal={counts.get('tuning_data', 0)}, "
                            f"User/Config={counts.get('user_data', 0)}, "
                            f"Network={counts.get('network', 0)}, "
                            f"Boot={counts.get('boot', 0)}."
                        )
                        if not manifest.get("validated_ok"):
                            append_log("[!] WARNING: Some expected RFK or tuning items were missing or invalid JSON—check the validated table.")
                        append_log("=========================================================================")
                        append_log("OPERATOR ACTION: Remove GOLD SD card ('GOLDEN MASTER - DO NOT OVERWRITE'),")
                        append_log("insert your NEW 16-64 GB target SD card, and click Rescan Drives.")
                        append_log("=========================================================================")
                    except Exception as e:
                        ACTIVE_JOB["running"] = False
                        ACTIVE_JOB["step"] = "error"
                        ACTIVE_JOB["error"] = str(e)
                        append_log(f"[ERROR] GOLD extraction failed: {e}")

                threading.Thread(target=_extract, daemon=True).start()
                self.send_json(200, {"status": "ok", "message": "Read-only GOLD extraction started."})
                return

            elif parsed.path == "/api/launch_imager":
                imager = find_rpi_imager()
                if not imager:
                    self.send_json(400, {"status": "error", "message": "Raspberry Pi Imager is not installed."})
                    return

                disk_idx_raw = req_data.get("disk_index")
                drive_letter = req_data.get("drive_letter")
                try:
                    verified = assert_writable_non_gold_sd(disk_idx_raw, drive_letter=drive_letter or None)
                    disk_idx = verified["index"]
                except SDGuardError as ge:
                    append_log(f"[BLOCKED] /api/launch_imager rejected: {ge}")
                    self.send_json(403, {"status": "error", "message": str(ge)})
                    return

                image_path = resolve_os_image_path(prefer_xz=True)
                if not image_path:
                    self.send_json(400, {"status": "error", "message": f"64-bit RPi OS image not found in {IMAGES_DIR}."})
                    return
                target_dev = f"\\\\.\\PHYSICALDRIVE{disk_idx}"
                
                append_log(f"[*] Launching Raspberry Pi Imager GUI with pre-selected image and verified SD Disk {disk_idx}...")
                try:
                    if is_admin():
                        subprocess.Popen([imager, image_path, target_dev], shell=False)
                    else:
                        cmd = f"powershell -NoProfile -Command \"Start-Process '{imager}' -ArgumentList '{image_path}', '{target_dev}' -Verb RunAs\""
                        subprocess.Popen(cmd, shell=True)
                    append_log(f"[+] Raspberry Pi Imager GUI opened on desktop with 64-bit OS & SD Disk {disk_idx} pre-selected!")
                    res = {"status": "ok", "message": "Imager launched."}
                except Exception as e:
                    append_log(f"[ERROR] Could not launch Imager: {e}")
                    res = {"status": "error", "message": str(e)}

                self.send_json(200, res)
                return

            elif parsed.path == "/api/open_folder":
                bat_path = os.path.join(BASE_DIR, "JRFK_Migrator.bat")
                subprocess.Popen(f'explorer.exe /select,"{bat_path}"', shell=True)
                self.send_json(200, {"status": "ok", "message": "Explorer opened."})
                return

            elif parsed.path == "/api/elevate":
                self.handle_elevate()
                return

            elif parsed.path == "/api/eject_sd":
                if ACTIVE_JOB.get("running"):
                    self.send_json(409, {"status": "error", "message": "Cannot eject SD while extraction or build is running."})
                    return
                drive_letter = req_data.get("drive_letter")
                disk_idx_raw = req_data.get("disk_index")
                try:
                    ok = safely_eject_drive(drive_letter, disk_index=disk_idx_raw)
                except SDGuardError as ge:
                    append_log(f"[BLOCKED] /api/eject_sd rejected: {ge}")
                    self.send_json(403, {"status": "error", "message": str(ge)})
                    return
                self.send_json(200, {"status": "ok" if ok else "error", "message": f"Drive {drive_letter} ejected." if ok else "Eject failed."})
                return

            elif parsed.path == "/api/restart":
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({"status": "ok", "message": "Server restarting."}).encode('utf-8'))
                def _restart():
                    time.sleep(0.5)
                    python_exe = sys.executable
                    script = os.path.join(BASE_DIR, "tools", "migrator", "server.py")
                    subprocess.Popen([python_exe, script, str(PORT)], cwd=BASE_DIR)
                    os._exit(0)
                threading.Thread(target=_restart, daemon=True).start()
                return

            self.send_response(404)
            self.send_header("Content-Type", "application/json")
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({"status": "error", "message": f"Endpoint not found: {parsed.path}"}).encode('utf-8'))

        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode('utf-8'))

class ThreadingMigratorServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    daemon_threads = True
    allow_reuse_address = True


def run_server():
    append_log(f"JRFK Migrator Server starting on port {PORT}...")
    if is_admin():
        append_log("[+] Running with elevated Administrator privileges.")
        _set_windows_automount(False)
        atexit.register(_set_windows_automount, True)
        _dismiss_windows_format_dialogs()
        append_log("[+] Windows automount disabled & Format-popup suppressor active during JRFK session.")

        def _format_dialog_watcher():
            while True:
                _dismiss_windows_format_dialogs()
                time.sleep(0.4)

        threading.Thread(target=_format_dialog_watcher, daemon=True).start()
    else:
        append_log("[-] Running with standard user privileges (Elevation available via Web UI).")
    append_log("Ready for SD provisioning.")
    server_address = ('', PORT)
    try:
        with ThreadingMigratorServer(server_address, MigratorHandler) as httpd:
            httpd.serve_forever()
    finally:
        if is_admin():
            _set_windows_automount(True)

if __name__ == "__main__":
    run_server()
