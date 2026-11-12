"""Build standalone JRFK.exe with embedded UAC manifest and self-installing JRFK payload."""
import os
import subprocess
import sys
import zipfile

MIGRATOR_DIR = os.path.abspath(os.path.dirname(__file__))
BASE_DIR = os.path.abspath(os.path.join(MIGRATOR_DIR, "..", ".."))

CSC_CANDIDATES = [
    os.path.join(os.environ.get("WINDIR", r"C:\Windows"), r"Microsoft.NET\Framework64\v4.0.30319\csc.exe"),
    os.path.join(os.environ.get("WINDIR", r"C:\Windows"), r"Microsoft.NET\Framework\v4.0.30319\csc.exe"),
]

PAYLOAD_FILES = [
    "JRFK_32_to_64Bit_Migration_tool.htm",
    "README.md",
    "JRFK_Migrator.bat",
]

PAYLOAD_DIRS = [
    "tools/migrator",
    "tools/rfk_tools_suite",
    "tools/py_deps",
    "tools/pi_debs",
    "scripts",
    "extracted",
]

SKIP_EXTENSIONS = {".pyc", ".exe", ".zip", ".part"}
SKIP_NAMES = {"__pycache__", ".git"}


def find_csc():
    for c in CSC_CANDIDATES:
        if os.path.isfile(c):
            return c
    raise FileNotFoundError("Windows .NET csc.exe compiler not found.")


def build_payload_zip(zip_path):
    count = 0
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for rel in PAYLOAD_FILES:
            full = os.path.join(BASE_DIR, rel)
            if os.path.isfile(full):
                zf.write(full, rel.replace("\\", "/"))
                count += 1
        for rel_dir in PAYLOAD_DIRS:
            full_dir = os.path.join(BASE_DIR, rel_dir)
            if not os.path.isdir(full_dir):
                continue
            for root, dirs, files in os.walk(full_dir):
                dirs[:] = [d for d in dirs if d not in SKIP_NAMES]
                for fn in files:
                    ext = os.path.splitext(fn)[1].lower()
                    if ext in SKIP_EXTENSIONS or fn == "jrfk_payload.zip":
                        continue
                    fp = os.path.join(root, fn)
                    arc = os.path.relpath(fp, BASE_DIR).replace("\\", "/")
                    zf.write(fp, arc)
                    count += 1
    return count


def main():
    csc = find_csc()
    out_exe = os.path.join(BASE_DIR, "JRFK.exe")
    cs_src = os.path.join(MIGRATOR_DIR, "jrfk_launcher.cs")
    manifest = os.path.join(MIGRATOR_DIR, "jrfk.manifest")
    payload_zip = os.path.join(MIGRATOR_DIR, "jrfk_payload.zip")

    file_count = build_payload_zip(payload_zip)
    print(f"[+] Built embedded payload zip: {file_count} files ({os.path.getsize(payload_zip) / 1024:.1f} KB)")

    cmd = [
        csc,
        "/nologo",
        "/target:winexe",
        "/platform:x64",
        "/optimize+",
        f"/win32manifest:{manifest}",
        f"/resource:{payload_zip},JRFK.payload.zip",
        "/reference:System.dll",
        "/reference:System.Drawing.dll",
        "/reference:System.Windows.Forms.dll",
        "/reference:System.IO.Compression.dll",
        "/reference:System.IO.Compression.FileSystem.dll",
        "/reference:Microsoft.CSharp.dll",
        f"/out:{out_exe}",
        cs_src,
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    try:
        os.remove(payload_zip)
    except OSError:
        pass
    if proc.returncode != 0:
        print(proc.stdout)
        print(proc.stderr)
        sys.exit(proc.returncode)

    print(f"[+] Built {out_exe} ({os.path.getsize(out_exe) / 1024:.1f} KB)")


if __name__ == "__main__":
    main()
