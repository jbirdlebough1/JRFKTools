import subprocess

imager_exe = r"C:\Program Files\Raspberry Pi Ltd\Imager\rpi-imager.exe"
image_path = r"C:\RFK_Backups\images\raspios_bookworm_arm64.img.xz"
target_dev = r"\\.\PHYSICALDRIVE2"

# Test passing arguments as an array in PowerShell
ps_script = f"""
$args = @('--cli', '--disable-verify', '{image_path}', '{target_dev}')
Start-Process -FilePath '{imager_exe}' -ArgumentList $args -Wait -PassThru
"""

p = subprocess.run(["powershell", "-NoProfile", "-Command", ps_script], capture_output=True, text=True)
print("Returncode:", p.returncode)
print("Stdout:", p.stdout)
print("Stderr:", p.stderr)
