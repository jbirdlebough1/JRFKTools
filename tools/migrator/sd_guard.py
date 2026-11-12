"""
Strict SD-only target guard for JRFK on Windows.

Allows read/write operations ONLY on verified removable SD / SD+USB adapter
media sized between 16 GB and 64 GB nominal (15,000,000,000 .. 70,000,000,000 bytes).
Hard-blocks internal SSDs/HDDs, external USB SSDs/HDDs, system/boot disks,
and out-of-range storage devices.
"""

import base64
import ctypes
from ctypes import wintypes
import json
import os
import re
import struct
import subprocess
import threading

MIN_SD_BYTES = 15_000_000_000  # ~13.97 GiB: admits genuine 16 GB nominal SD cards
MAX_SD_BYTES = 70_000_000_000  # ~65.19 GiB: admits genuine 64 GB nominal SD cards

ALLOWED_BUS_TYPES = {"USB", "SD", "MMC"}
BLOCKED_BUS_TYPES = {
    "NVME",
    "SATA",
    "ATA",
    "ATAPI",
    "SCSI",
    "SAS",
    "RAID",
    "ISCSI",
    "SPACES",
    "VIRTUAL",
    "FILEBACKEDVIRTUAL",
    "STORAGESPACES",
}
BLOCKED_MEDIA_TYPES = {"SSD", "HDD"}
REMOVABLE_LOGICAL_DRIVE_TYPE = 2


class SDGuardError(PermissionError):
    """Raised when a target disk or drive letter fails SD-only safety checks."""


def get_system_drive_letter():
    sys_drv = os.environ.get("SystemDrive", "C:")
    return normalize_drive_letter(sys_drv) or "C"


def normalize_drive_letter(letter):
    if not letter:
        return ""
    cleaned = str(letter).strip().replace(":", "").replace("\\", "").replace("/", "").upper()
    if len(cleaned) == 1 and cleaned.isalpha():
        return cleaned
    return ""


def parse_disk_index(value):
    if value is None or isinstance(value, bool):
        raise SDGuardError("Missing required disk_index.")
    try:
        idx = int(str(value).strip())
    except (TypeError, ValueError) as exc:
        raise SDGuardError(f"Invalid disk_index: {value!r}") from exc
    if idx < 0:
        raise SDGuardError(f"Invalid negative disk_index: {idx}")
    return idx


def _norm_upper(val):
    return str(val or "").strip().upper()


def _effective_bus_type(disk):
    for key in ("bus_type", "pd_bus_type", "interface"):
        val = _norm_upper(disk.get(key))
        if val and val not in {"UNKNOWN", "UNSPECIFIED"}:
            return val
    return "UNKNOWN"


def _effective_size_bytes(disk):
    size = int(disk.get("size_bytes") or 0)
    if size <= 0:
        size = int(disk.get("pd_size_bytes") or 0)
    return size


def evaluate_sd_eligibility(disk, system_drive=None):
    """
    Evaluate whether a disk dict represents a writable 16-64 GB SD / SD+USB target.

    Returns (is_sd: bool, writable: bool, blocked_reasons: list[str]).
    """
    sys_letter = normalize_drive_letter(system_drive) if system_drive else get_system_drive_letter()
    reasons = []

    idx = disk.get("index")
    if idx is None or isinstance(idx, bool) or int(idx) < 0:
        reasons.append("Invalid disk index")

    if disk.get("is_system"):
        reasons.append("System disk")
    if disk.get("is_boot"):
        reasons.append("Boot disk")

    partitions = disk.get("partitions") or []
    for p in partitions:
        pletter = normalize_drive_letter(p.get("letter"))
        if pletter and pletter == sys_letter:
            reasons.append(f"Contains system drive {sys_letter}:")
            break

    bus_type = _effective_bus_type(disk)
    if bus_type in BLOCKED_BUS_TYPES:
        reasons.append(f"Blocked bus type ({bus_type})")
    elif bus_type not in ALLOWED_BUS_TYPES:
        reasons.append(f"Unsupported bus type ({bus_type}); only SD/MMC/USB allowed")

    wmi_media = str(disk.get("wmi_media_type") or "").strip()
    if wmi_media.lower() != "removable media":
        reasons.append(
            f"Non-removable media type ({wmi_media or 'Unknown'}); fixed/external disks and SSDs are blocked"
        )

    if not disk.get("media_loaded"):
        reasons.append("No SD media loaded in slot/adapter")

    for mt_key in ("msft_media_type", "pd_media_type"):
        mt_val = _norm_upper(disk.get(mt_key))
        if mt_val in BLOCKED_MEDIA_TYPES:
            reasons.append(f"Blocked hardware media type ({mt_val})")

    model = str(disk.get("model") or "")
    if re.search(r"\b(SSD|NVME|HDD)\b", model, re.IGNORECASE):
        reasons.append(f"Model indicates SSD/HDD ({model})")

    size_bytes = _effective_size_bytes(disk)
    if size_bytes <= 0:
        reasons.append("Disk reports 0 bytes")
    elif size_bytes < MIN_SD_BYTES:
        reasons.append(
            f"Capacity too small ({size_bytes / 1e9:.1f} GB); minimum is 16 GB nominal SD card"
        )
    elif size_bytes > MAX_SD_BYTES:
        reasons.append(
            f"Capacity too large ({size_bytes / 1e9:.1f} GB); maximum is 64 GB nominal SD card"
        )

    for p in partitions:
        pletter = normalize_drive_letter(p.get("letter"))
        if not pletter:
            continue
        dtype = p.get("drive_type")
        if dtype != REMOVABLE_LOGICAL_DRIVE_TYPE:
            reasons.append(
                f"Partition {pletter}: has DriveType={dtype} (expected Removable DriveType=2)"
            )

    ok = len(reasons) == 0
    return ok, ok, reasons


_WIN_BUS_NAMES = {
    0: "UNKNOWN",
    1: "SCSI",
    2: "ATAPI",
    3: "ATA",
    4: "1394",
    5: "SSA",
    6: "FIBRE",
    7: "USB",
    8: "RAID",
    9: "ISCSI",
    10: "SAS",
    11: "SATA",
    12: "SD",
    13: "MMC",
    14: "VIRTUAL",
    15: "FILEBACKEDVIRTUAL",
    16: "SPACES",
    17: "NVME",
    18: "SCM",
    19: "UFS",
}


def _cstr_at(raw, off):
    if off and 0 < off < len(raw):
        end = raw.find(b"\x00", off)
        return raw[off : (end if end != -1 else len(raw))].decode("ascii", errors="ignore").strip()
    return ""


def _get_volume_info_safe(k32, root, timeout_sec=1.0):
    """Fetch volume label & filesystem without allowing wedged USB readers to hang the process."""
    res = ["", ""]

    def _probe():
        try:
            k32.SetThreadErrorMode(0x0001 | 0x0002 | 0x8000, None)
        except Exception:
            pass
        vn = ctypes.create_unicode_buffer(128)
        fs = ctypes.create_unicode_buffer(64)
        if k32.GetVolumeInformationW(root, vn, 128, None, None, None, fs, 64):
            res[0] = vn.value or ""
            res[1] = fs.value or ""

    t = threading.Thread(target=_probe, daemon=True)
    t.start()
    t.join(timeout_sec)
    return res[0], res[1]


def _query_disks_win32():
    """
    Fast synchronous native Win32 disk enumeration via kernel32 DeviceIoControl.
    Runs cleanly without PowerShell or stalled Storage WMI providers.
    """
    k32 = ctypes.windll.kernel32
    try:
        k32.SetErrorMode(0x0001 | 0x0002 | 0x8000)
    except Exception:
        pass
    file_share_rw = 0x00000001 | 0x00000002
    open_existing = 3
    generic_read = 0x80000000
    invalid_handle = ctypes.c_void_p(-1).value
    sys_letter = get_system_drive_letter()

    # 1. Map mounted drive letters -> physical disk indices via IOCTL_VOLUME_GET_VOLUME_DISK_EXTENTS
    buf_drv = ctypes.create_unicode_buffer(512)
    n = k32.GetLogicalDriveStringsW(512, buf_drv)
    disk_parts = {}
    for root in buf_drv[:n].split("\x00"):
        if len(root) < 2:
            continue
        ltr = normalize_drive_letter(root[0])
        if not ltr:
            continue
        dtype = int(k32.GetDriveTypeW(root))
        if dtype not in (2, 3):
            continue
        h = k32.CreateFileW(f"\\\\.\\{ltr}:", 0, file_share_rw, None, open_existing, 0, None)
        if h != invalid_handle and h != -1:
            try:
                out = ctypes.create_string_buffer(256)
                ret = wintypes.DWORD(0)
                if k32.DeviceIoControl(h, 0x00560000, None, 0, out, 256, ctypes.byref(ret), None):
                    cnt = struct.unpack_from("<I", out.raw, 0)[0]
                    vol_name_val, fs_name_val = _get_volume_info_safe(k32, root, timeout_sec=0.3)
                    for i in range(cnt):
                        off = 8 + i * 24
                        if off + 4 <= ret.value:
                            dn = struct.unpack_from("<I", out.raw, off)[0]
                            parts = disk_parts.setdefault(dn, {})
                            dl = f"{ltr}:"
                            if dl not in parts:
                                parts[dl] = {
                                    "letter": dl,
                                    "drive_type": dtype,
                                    "volume_name": vol_name_val,
                                    "file_system": fs_name_val,
                                }
            finally:
                k32.CloseHandle(h)

    # 2. Query \\.\PhysicalDrive0..31 directly via IOCTL_STORAGE_QUERY_PROPERTY & GET_DRIVE_GEOMETRY_EX
    results = []
    for idx in range(32):
        dev_path = f"\\\\.\\PhysicalDrive{idx}"
        h = k32.CreateFileW(dev_path, 0, file_share_rw, None, open_existing, 0, None)
        if h == invalid_handle or h == -1:
            continue
        try:
            q = struct.pack("<III", 0, 0, 0)
            out = ctypes.create_string_buffer(1024)
            ret = wintypes.DWORD(0)
            bus = "UNKNOWN"
            rem = False
            vendor = ""
            prod = ""
            ser = ""
            if k32.DeviceIoControl(h, 0x002D1400, q, len(q), out, 1024, ctypes.byref(ret), None):
                raw = out.raw[: ret.value]
                if len(raw) >= 32:
                    rem = bool(raw[10])
                    v_off, p_off, _r_off, s_off, bus_id = struct.unpack_from("<IIIII", raw, 12)
                    bus = _WIN_BUS_NAMES.get(bus_id, f"BUS_{bus_id}")
                    vendor = _cstr_at(raw, v_off)
                    prod = _cstr_at(raw, p_off)
                    ser = _cstr_at(raw, s_off)

            gbuf = ctypes.create_string_buffer(256)
            gret = wintypes.DWORD(0)
            size_bytes = 0
            media_loaded = False
            if k32.DeviceIoControl(h, 0x000700A0, None, 0, gbuf, 256, ctypes.byref(gret), None):
                if gret.value >= 32:
                    size_bytes = struct.unpack_from("<Q", gbuf.raw, 24)[0]
                    media_loaded = size_bytes > 0
        finally:
            k32.CloseHandle(h)

        # Best-effort read of MBR sector 0 signature (works when elevated; ignored un-elevated)
        sig = 0
        h_ro = k32.CreateFileW(dev_path, generic_read, file_share_rw, None, open_existing, 0, None)
        if h_ro != invalid_handle and h_ro != -1:
            try:
                mbr = ctypes.create_string_buffer(512)
                rbytes = wintypes.DWORD(0)
                if k32.ReadFile(h_ro, mbr, 512, ctypes.byref(rbytes), None) and rbytes.value >= 512:
                    if mbr.raw[510:512] == b"\x55\xaa":
                        sig = struct.unpack("<I", mbr.raw[440:444])[0]
            finally:
                k32.CloseHandle(h_ro)

        model = " ".join(x for x in (vendor, prod) if x).strip() or f"Disk {idx}"
        if rem:
            wmi_media_type = "Removable Media"
        elif bus == "USB":
            wmi_media_type = "External hard disk media"
        else:
            wmi_media_type = "Fixed hard disk media"

        part_list = sorted(disk_parts.get(idx, {}).values(), key=lambda p: p["letter"])
        letters = ", ".join(p["letter"] for p in part_list)
        has_sys = any(normalize_drive_letter(p["letter"]) == sys_letter for p in part_list)

        results.append(
            {
                "index": idx,
                "id": f"\\\\.\\PHYSICALDRIVE{idx}",
                "model": model,
                "interface": bus,
                "wmi_media_type": wmi_media_type,
                "media_loaded": media_loaded,
                "size_bytes": size_bytes,
                "pnp_device_id": "",
                "serial_number": ser,
                "signature": sig,
                "bus_type": bus,
                "msft_media_type": "",
                "is_system": has_sys,
                "is_boot": has_sys,
                "pd_bus_type": bus,
                "pd_media_type": "",
                "pd_size_bytes": size_bytes,
                "partitions": part_list,
                "letter": letters,
            }
        )
    return results


def query_disks_raw():
    """
    Query live Windows disk inventory via native Win32 DeviceIoControl (<0.05s, zero WMI hangs),
    with pure Win32_* CIM PowerShell fallback only if Win32 API enumeration yields nothing.
    """
    if os.name == "nt":
        try:
            disks = _query_disks_win32()
            if disks:
                return disks
        except Exception:
            pass

    ps_cmd = r"""
    $ErrorActionPreference = 'SilentlyContinue'
    $ldMap = @{}
    Get-CimInstance Win32_LogicalDisk | ForEach-Object { $ldMap[[string]$_.DeviceID] = $_ }

    $sysDrive = if ($env:SystemDrive) { $env:SystemDrive.Trim().ToUpper() } else { 'C:' }
    $partBootDiskIds = @{}
    Get-CimInstance Win32_DiskPartition | ForEach-Object {
        if ($_.BootPartition -or $_.Bootable) {
            $partBootDiskIds[[int]$_.DiskIndex] = $true
        }
    }
    $partIdToDiskId = @{}
    Get-CimInstance Win32_DiskDriveToDiskPartition | ForEach-Object {
        $partIdToDiskId[[string]$_.Dependent.DeviceID] = [string]$_.Antecedent.DeviceID
    }
    $diskIdToLetters = @{}
    Get-CimInstance Win32_LogicalDiskToPartition | ForEach-Object {
        $diskId = $partIdToDiskId[[string]$_.Antecedent.DeviceID]
        if ($diskId) {
            if (-not $diskIdToLetters.ContainsKey($diskId)) { $diskIdToLetters[$diskId] = @() }
            $diskIdToLetters[$diskId] += [string]$_.Dependent.DeviceID
        }
    }

    $res = @()
    Get-CimInstance Win32_DiskDrive | Sort-Object Index | ForEach-Object {
        $d = $_
        $idx = [int]$d.Index

        $partByLetter = @{}
        $isSysDisk = $false
        $wmiLetters = $diskIdToLetters[[string]$d.DeviceID]
        if ($wmiLetters) {
            foreach ($dlRaw in $wmiLetters) {
                $dl = ([string]$dlRaw).Trim().ToUpper()
                if ($dl -eq $sysDrive) { $isSysDisk = $true }
                if ($dl -and -not $partByLetter.ContainsKey($dl)) {
                    $ld = $ldMap[$dl]
                    $partByLetter[$dl] = @{
                        letter = $dl
                        drive_type = if ($ld) { [int]$ld.DriveType } else { $null }
                        volume_name = if ($ld) { [string]$ld.VolumeName } else { '' }
                        file_system = if ($ld) { [string]$ld.FileSystem } else { '' }
                    }
                }
            }
        }

        $pnp = [string]$d.PNPDeviceID
        $iface = [string]$d.InterfaceType
        $bus = $iface
        if ($pnp -match '(?i)NVME') { $bus = 'NVME' }
        elseif ($pnp -match '(?i)^SD\\') { $bus = 'SD' }
        elseif ($pnp -match '(?i)^USBSTOR\\') { $bus = 'USB' }

        $partList = @($partByLetter.Values | Sort-Object { $_.letter })
        $letters = ($partList | ForEach-Object { $_.letter }) -join ', '

        $res += [PSCustomObject]@{
            index = $idx
            id = [string]$d.DeviceID
            model = [string]$d.Model
            interface = $iface
            wmi_media_type = [string]$d.MediaType
            media_loaded = [bool]$d.MediaLoaded
            size_bytes = if ($d.Size) { [int64]$d.Size } else { 0 }
            pnp_device_id = $pnp
            serial_number = [string]$d.SerialNumber
            signature = if ($d.Signature) { [int64]$d.Signature } else { 0 }
            bus_type = $bus
            msft_media_type = ''
            is_system = [bool]$isSysDisk
            is_boot = [bool]($isSysDisk -or $partBootDiskIds.ContainsKey($idx))
            pd_bus_type = ''
            pd_media_type = ''
            pd_size_bytes = 0
            partitions = $partList
            letter = $letters
        }
    }
    $res | ConvertTo-Json -Depth 4 -Compress
    """
    encoded_cmd = base64.b64encode(ps_cmd.encode("utf-16le")).decode("ascii")
    p = subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-NonInteractive",
            "-InputFormat",
            "None",
            "-EncodedCommand",
            encoded_cmd,
        ],
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
        timeout=60,
    )
    if p.returncode != 0 and not p.stdout.strip():
        raise RuntimeError(f"Disk query failed: {p.stderr.strip()}")
    out = p.stdout.strip()
    if not out:
        return []
    raw_data = json.loads(out)
    if isinstance(raw_data, dict):
        raw_data = [raw_data]
    return raw_data


def enrich_disk_record(raw_disk, system_drive=None):
    is_sd, writable, reasons = evaluate_sd_eligibility(raw_disk, system_drive=system_drive)
    eff_bytes = _effective_size_bytes(raw_disk)
    size_gib = round(eff_bytes / (1024 ** 3), 1) if eff_bytes > 0 else 0.0
    size_dec_gb = round(eff_bytes / 1e9, 1) if eff_bytes > 0 else 0.0
    partitions = raw_disk.get("partitions") or []
    part_letters = [
        normalize_drive_letter(p.get("letter"))
        for p in partitions
        if normalize_drive_letter(p.get("letter"))
    ]
    return {
        "index": int(raw_disk.get("index")),
        "id": raw_disk.get("id"),
        "model": raw_disk.get("model") or "Unknown Storage Device",
        "interface": raw_disk.get("interface") or "Unknown",
        "bus_type": _effective_bus_type(raw_disk),
        "wmi_media_type": raw_disk.get("wmi_media_type") or "",
        "media_loaded": bool(raw_disk.get("media_loaded")),
        "size_bytes": eff_bytes,
        "size_gb": f"{size_gib} GB" if eff_bytes > 0 else "0 GB",
        "size_decimal_gb": size_dec_gb,
        "letter": raw_disk.get("letter") or ", ".join(f"{l}:" for l in part_letters),
        "partitions": partitions,
        "partition_letters": part_letters,
        "pnp_device_id": raw_disk.get("pnp_device_id") or "",
        "serial_number": raw_disk.get("serial_number") or "",
        "signature": int(raw_disk.get("signature") or 0),
        "is_system": bool(raw_disk.get("is_system")),
        "is_boot": bool(raw_disk.get("is_boot")),
        "is_sd": is_sd,
        "writable": writable,
        "blocked_reason": "; ".join(reasons),
    }


def query_disks(log_fn=None):
    try:
        raw_list = query_disks_raw()
        return [enrich_disk_record(item) for item in raw_list]
    except Exception as exc:
        if log_fn:
            log_fn(f"Error querying disks: {exc}")
        return []


def validate_sd_write_target(
    disk_index,
    drive_letter=None,
    require_letter=False,
    disks=None,
    system_drive=None,
):
    """
    Strictly validate that disk_index (and optional drive_letter) targets a
    16-64 GB removable SD / SD+USB card and NOT an SSD, fixed disk, or system drive.

    Raises SDGuardError if validation fails; returns the enriched disk dict on success.
    """
    idx = parse_disk_index(disk_index)
    sys_letter = normalize_drive_letter(system_drive) if system_drive else get_system_drive_letter()

    if disks is None:
        raw_list = query_disks_raw()
        disk_list = [enrich_disk_record(item, system_drive=sys_letter) for item in raw_list]
    else:
        disk_list = [
            d if "writable" in d and "partition_letters" in d else enrich_disk_record(d, system_drive=sys_letter)
            for d in disks
        ]

    target = next((d for d in disk_list if int(d.get("index", -1)) == idx), None)
    if target is None:
        raise SDGuardError(f"WRITE BLOCKED: Disk {idx} is not connected or not found.")

    if not target.get("writable") or not target.get("is_sd"):
        reason = target.get("blocked_reason") or "Failed SD-only eligibility check"
        raise SDGuardError(
            f"WRITE BLOCKED on Disk {idx} ({target.get('model', 'Unknown')}): {reason}."
        )

    clean_req = normalize_drive_letter(drive_letter) if drive_letter else ""
    if drive_letter and not clean_req:
        raise SDGuardError(f"WRITE BLOCKED: Invalid drive letter {drive_letter!r}.")
    if require_letter and not clean_req:
        raise SDGuardError(f"WRITE BLOCKED: A mounted removable drive letter on Disk {idx} is required.")

    if clean_req:
        if clean_req == sys_letter:
            raise SDGuardError(f"WRITE BLOCKED: Refusing to target system drive {clean_req}:.")
        part_letters = target.get("partition_letters") or []
        if clean_req not in part_letters:
            raise SDGuardError(
                f"WRITE BLOCKED: Drive {clean_req}: does not belong to verified SD Disk {idx} "
                f"(found partitions: {target.get('letter') or 'none'})."
            )
        part_info = next(
            (p for p in (target.get("partitions") or []) if normalize_drive_letter(p.get("letter")) == clean_req),
            None,
        )
        if not part_info or part_info.get("drive_type") != REMOVABLE_LOGICAL_DRIVE_TYPE:
            dtype = part_info.get("drive_type") if part_info else None
            raise SDGuardError(
                f"WRITE BLOCKED: Drive {clean_req}: is not a Removable drive (DriveType={dtype})."
            )

    return target


def resolve_verified_drive_letter(disk_index, requested_letter=None, disks=None, system_drive=None):
    """
    Validate disk_index as an SD target and return a verified removable drive letter
    (without trailing colon) belonging to disk_index, or None if unmounted.
    """
    target = validate_sd_write_target(
        disk_index,
        drive_letter=requested_letter,
        require_letter=False,
        disks=disks,
        system_drive=system_drive,
    )
    if requested_letter:
        return normalize_drive_letter(requested_letter)
    part_letters = target.get("partition_letters") or []
    return part_letters[0] if part_letters else None
