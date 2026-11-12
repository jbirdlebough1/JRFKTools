import glob
import os
import sys

DEFAULT_DIRS = [
    "/home/pi/rf-kit-gui_v200",
    "/home/pi/rf-kit-gui_v198",
    "/home/pi/rf-kit-gui",
    "/mnt/sd_rootfs/home/pi/rf-kit-gui_v200",
    "/mnt/sd_rootfs/home/pi/rf-kit-gui_v198",
]


def patch_dirs(target_dirs=None):
    dirs = list(target_dirs) if target_dirs else list(DEFAULT_DIRS)
    for dynamic in glob.glob("/home/pi/rf-kit*"):
        if os.path.isdir(dynamic) and dynamic not in dirs:
            dirs.append(dynamic)

    count = 0
    for d in dirs:
        if not os.path.isdir(d):
            continue
        for py_file in glob.glob(os.path.join(d, "**", "*.py"), recursive=True):
            with open(py_file, "r", encoding="utf-8", errors="ignore") as f:
                c = f.read()
            if "Image.ANTIALIAS" in c:
                c_new = c.replace("Image.ANTIALIAS", "getattr(Image, 'Resampling', Image).LANCZOS")
                with open(py_file, "w", encoding="utf-8") as f:
                    f.write(c_new)
                count += 1
                print(f"Patched: {py_file}")
    print(f"Done! Patched {count} files.")
    return count


if __name__ == "__main__":
    patch_dirs(sys.argv[1:] or None)
