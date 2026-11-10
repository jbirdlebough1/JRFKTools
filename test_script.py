import os
import subprocess

def prepare_diskpart_script(disk_index, drive_letter="E"):
    script_path = r"C:\RFK_Backups\partition_setup.txt"
    os.makedirs(r"C:\RFK_Backups", exist_ok=True)
    
    # Diskpart script to clean disk, create 512MB FAT32 boot partition, and create rootfs partition
    content = f"""select disk {disk_index}
clean
create partition primary size=512
format fs=fat32 quick label="BOOT"
assign letter={drive_letter}
active
create partition primary
"""
    with open(script_path, "w") as f:
        f.write(content)
        
    return script_path

print("Prepared script:", prepare_diskpart_script(2, "E"))
