import subprocess

imager_exe = r"C:\Program Files\Raspberry Pi Ltd\Imager\rpi-imager.exe"
image_path = r"C:\RFK_Backups\images\raspios_bookworm_arm64.img.xz"
target_dev = r"\\.\PHYSICALDRIVE2"

cmd = [
    "powershell", "-NoProfile", "-Command",
    f"Start-Process '{imager_exe}' -ArgumentList '{image_path}', '{target_dev}' -Verb RunAs"
]
p = subprocess.run(cmd)
print("Launch result:", p.returncode)
