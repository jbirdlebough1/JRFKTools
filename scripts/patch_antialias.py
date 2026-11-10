import glob

dirs = ['/mnt/sd_rootfs/home/pi/rf-kit-gui_v200', '/mnt/sd_rootfs/home/pi/rf-kit-gui_v198']
count = 0
for d in dirs:
    for py_file in glob.glob(d + '/**/*.py', recursive=True):
        with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
            c = f.read()
        if 'Image.ANTIALIAS' in c:
            c_new = c.replace('Image.ANTIALIAS', "getattr(Image, 'Resampling', Image).LANCZOS")
            with open(py_file, 'w', encoding='utf-8') as f:
                f.write(c_new)
            count += 1
            print(f"Patched: {py_file}")

print(f"Done! Patched {count} files.")
