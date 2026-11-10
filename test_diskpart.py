import subprocess
import os

script_path = r"C:\RFK_Backups\clean_disk2.txt"
with open(script_path, "w") as f:
    f.write("select disk 2\nclean\ncreate partition primary\nformat fs=fat32 quick label=\"BOOT\"\nassign letter=E\nactive\n")

# Test running diskpart via Start-Process
cmd = f"Start-Process diskpart.exe -ArgumentList '/s \"{script_path}\"' -Verb RunAs -Wait"
p = subprocess.run(["powershell", "-NoProfile", "-Command", cmd], capture_output=True, text=True)
print("Returncode:", p.returncode)
print("Stdout:", p.stdout)
print("Stderr:", p.stderr)
