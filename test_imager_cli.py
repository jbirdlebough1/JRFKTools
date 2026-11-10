import subprocess

cmd = [
    "powershell", "-NoProfile", "-Command",
    "Start-Process -FilePath 'C:\\Program Files\\Raspberry Pi Ltd\\Imager\\rpi-imager.exe' -ArgumentList '--cli', '--disable-verify', 'C:\\RFK_Backups\\images\\raspios_bookworm_arm64.img.xz', '\\\\.\\PHYSICALDRIVE2' -Verb RunAs -Wait -PassThru"
]
p = subprocess.run(cmd, capture_output=True, text=True)
print("Returncode:", p.returncode)
print("Stdout:", p.stdout)
print("Stderr:", p.stderr)
