"""
Windows 11 Dialog, Explorer & Popup Suppressor for JRFK SD Provisioning.
Silences and automatically dismisses all unwanted Windows 11 shell alerts, including:
1. "Location is not available" (e.g. "E:\\ is not accessible. The volume does not contain a recognized file system.")
2. "Microsoft Windows" ("You need to format the disk in drive X: before you can use it.")
3. AutoPlay explorer windows opening on unformatted/ext4 partitions
4. "Format ..." (Auto-spawned disk format utility)
5. "AutoPlay" popups and toasts
6. "WD Drive Utilities"
7. "Windows - No Disk" / "There is no disk in the drive"
"""

import os
import sys
import time
import subprocess
import ctypes
from ctypes import wintypes
import threading

def disable_windows_autoplay():
    """Disable Windows AutoPlay and AutoRun across HKCU and HKLM so Explorer never auto-opens SD cards."""
    if os.name != "nt":
        return
    try:
        import winreg
        for root in [winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE]:
            try:
                with winreg.CreateKey(root, r"Software\Microsoft\Windows\CurrentVersion\Explorer\AutoplayHandlers") as k:
                    winreg.SetValueEx(k, "DisableAutoplay", 0, winreg.REG_DWORD, 1)
            except Exception:
                pass
            try:
                with winreg.CreateKey(root, r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer") as k:
                    winreg.SetValueEx(k, "NoDriveTypeAutoRun", 0, winreg.REG_DWORD, 255)
                    winreg.SetValueEx(k, "NoAutorun", 0, winreg.REG_DWORD, 1)
            except Exception:
                pass
            try:
                with winreg.CreateKey(root, r"Software\Policies\Microsoft\Windows\Explorer") as k:
                    winreg.SetValueEx(k, "NoAutoplayfornonVolume", 0, winreg.REG_DWORD, 1)
            except Exception:
                pass
    except Exception:
        pass


def disable_windows_automount():
    """Disable Windows MountMgr automount so new partitions don't get probed or mounted."""
    if os.name != "nt":
        return
    try:
        subprocess.run(["mountvol.exe", "/N"], stdin=subprocess.DEVNULL, capture_output=True, timeout=5)
    except Exception:
        pass


def suppress_drive_volume(letter_or_path):
    """Unmount and detach volume to permanently silence Windows Explorer probing."""
    if not letter_or_path or os.name != "nt":
        return
    clean = str(letter_or_path).replace("\\", "").replace("/", "").rstrip(":")
    if not clean or len(clean) != 1 or not clean.isalpha():
        return
    target = f"{clean.upper()}:"
    try:
        subprocess.run(["mountvol.exe", target, "/D"], stdin=subprocess.DEVNULL, capture_output=True, timeout=5)
    except Exception:
        pass
    try:
        subprocess.run(["mountvol.exe", target, "/P"], stdin=subprocess.DEVNULL, capture_output=True, timeout=5)
    except Exception:
        pass


def dismiss_matching_windows():
    """Single scan of top-level windows and dismissal of all format/error popups."""
    if os.name != "nt":
        return 0

    user32 = ctypes.windll.user32

    # Set explicit 64-bit signatures for user32 handles
    user32.OpenWindowStationW.restype = wintypes.HANDLE
    user32.OpenDesktopW.restype = wintypes.HANDLE
    user32.GetWindowTextLengthW.restype = ctypes.c_int
    user32.GetWindowTextLengthW.argtypes = [wintypes.HWND]
    user32.GetWindowTextW.restype = ctypes.c_int
    user32.GetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
    user32.GetClassNameW.restype = ctypes.c_int
    user32.GetClassNameW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
    user32.IsWindowVisible.restype = wintypes.BOOL
    user32.IsWindowVisible.argtypes = [wintypes.HWND]
    user32.PostMessageW.restype = wintypes.BOOL
    user32.PostMessageW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]

    # Attach to user desktop if running elevated
    hdesk = None
    try:
        hwinsta = user32.OpenWindowStationW('WinSta0', False, 0x037F)
        if hwinsta:
            user32.SetProcessWindowStation(hwinsta)
            hdesk = user32.OpenDesktopW('default', 0, False, 0x01FF)
            if hdesk:
                user32.SetThreadDesktop(hdesk)
    except Exception:
        pass

    enum_proc_t = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    child_proc_t = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)

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
    button_targets = []

    def _cb(hwnd, _lp):
        if not user32.IsWindowVisible(hwnd):
            return True
        title = _wtext(hwnd).lower()
        cls = _wcls(hwnd).lower()
        texts = []
        local_buttons = []

        def _ccb(chwnd, _clp):
            t = _wtext(chwnd)
            if t:
                tl = t.strip().lower()
                texts.append(tl)
                ccls = _wcls(chwnd).lower()
                if "button" in ccls or tl in ["ok", "cancel", "close", "format disk"]:
                    local_buttons.append(chwnd)
            return True

        c_fn = child_proc_t(_ccb)
        user32.EnumChildWindows(hwnd, c_fn, 0)
        joined = " ".join(texts)

        is_match = False
        if any(k in title for k in [
            "location is not available", "not available", "microsoft windows",
            "format ", "autoplay", "wddriveutilities", "no disk", "removable disk"
        ]):
            is_match = True
        elif any(phrase in joined for phrase in [
            "not contain a recognized file system",
            "is not accessible",
            "you need to format the disk",
            "format the disk in drive",
            "before you can use it",
            "volume does not contain",
            "parameter is incorrect",
            "there is no disk in the drive",
            "insert a disk"
        ]):
            is_match = True
        elif cls in ["cabinetwclass", "explorewclass"] and (
            "not accessible" in joined or "not recognized" in joined or "location is not available" in title
        ):
            is_match = True

        if is_match:
            targets.append(hwnd)
            for b in local_buttons:
                button_targets.append(b)
        return True

    e_fn = enum_proc_t(_cb)
    if hdesk:
        user32.EnumDesktopWindows(hdesk, e_fn, 0)
    else:
        user32.EnumWindows(e_fn, 0)

    # Click buttons with async PostMessage (never blocking SendMessage!)
    for btn_hwnd in button_targets:
        user32.PostMessageW(btn_hwnd, 0x00F5, 0, 0) # BM_CLICK

    # Dismiss dialogs
    for hwnd in targets:
        user32.PostMessageW(hwnd, 0x0111, 1, 0)      # IDOK
        user32.PostMessageW(hwnd, 0x0111, 2, 0)      # IDCANCEL
        user32.PostMessageW(hwnd, 0x0010, 0, 0)      # WM_CLOSE
        user32.PostMessageW(hwnd, 0x0112, 0xF060, 0) # SC_CLOSE

    return len(targets)


def start_suppressor_daemon(poll_interval=0.1):
    if os.name != "nt":
        return None

    disable_windows_autoplay()
    disable_windows_automount()

    def _worker():
        while True:
            try:
                dismiss_matching_windows()
            except Exception:
                pass
            time.sleep(poll_interval)

    t = threading.Thread(target=_worker, daemon=True)
    t.start()
    return t


if __name__ == "__main__":
    t = start_suppressor_daemon()
    if t:
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
