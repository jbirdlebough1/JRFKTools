"""
Pure-Python strictly READ-ONLY MBR + ext2/ext3/ext4 reader for Windows & image files.

Opens Windows physical devices with GENERIC_READ only (never requests write access)
and aligns all raw device I/O to 512-byte sectors with an in-memory block cache.
"""

from collections import OrderedDict
import ctypes
from ctypes import wintypes
import os
import posixpath
import stat
import struct
import time

kernel32 = ctypes.windll.kernel32
GENERIC_READ = 0x80000000
FILE_SHARE_READ = 0x00000001
FILE_SHARE_WRITE = 0x00000002
OPEN_EXISTING = 3
FILE_ATTRIBUTE_NORMAL = 0x80
INVALID_HANDLE_VALUE = ctypes.c_void_p(-1).value

EXT4_SUPER_MAGIC = 0xEF53
EXT4_EXTENTS_FL = 0x00080000
EXT4_EXTENT_MAGIC = 0xF30A
EXT4_FEATURE_INCOMPAT_64BIT = 0x0080

S_IFMT = 0xF000
S_IFREG = 0x8000
S_IFDIR = 0x4000
S_IFLNK = 0xA000


class Ext4ReadError(RuntimeError):
    """Raised on invalid MBR/ext4 structure or read failure."""


class RawReadOnlyStream:
    """Sector-aligned read-only stream with 4 KiB metadata cache and multi-MiB bulk coalesced reads."""

    def __init__(self, path, sector_size=512, cache_blocks=2048, chunk_size=4096):
        self.path = path
        self.sector_size = sector_size
        self.chunk_size = chunk_size
        self._is_win_device = path.startswith("\\\\.\\")
        self._handle = None
        self._file = None
        self._cache = OrderedDict()
        self._cache_max = max(64, int(cache_blocks))

        if self._is_win_device:
            handle = kernel32.CreateFileW(
                path,
                GENERIC_READ,
                FILE_SHARE_READ | FILE_SHARE_WRITE,
                None,
                OPEN_EXISTING,
                FILE_ATTRIBUTE_NORMAL,
                None,
            )
            if handle == INVALID_HANDLE_VALUE or handle == -1:
                err = kernel32.GetLastError()
                raise Ext4ReadError(
                    f"Cannot open {path} read-only (Windows error {err}; requires Administrator elevation)."
                )
            self._handle = handle
        else:
            self._file = open(path, "rb")

    def close(self):
        if self._handle is not None:
            kernel32.CloseHandle(self._handle)
            self._handle = None
        if self._file is not None:
            self._file.close()
            self._file = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()

    def _read_raw_aligned(self, offset, length):
        if not self._is_win_device:
            self._file.seek(offset)
            return self._file.read(length)

        last_err = 0
        for attempt in range(3):
            li = ctypes.c_longlong(offset)
            new_pos = ctypes.c_longlong(0)
            ok = kernel32.SetFilePointerEx(self._handle, li, ctypes.byref(new_pos), 0)
            if not ok:
                raise Ext4ReadError(f"SetFilePointerEx failed at {offset}: error {kernel32.GetLastError()}")

            buf = ctypes.create_string_buffer(length)
            read_bytes = wintypes.DWORD(0)
            ok = kernel32.ReadFile(self._handle, buf, length, ctypes.byref(read_bytes), None)
            if ok:
                return buf.raw[: read_bytes.value]
            last_err = kernel32.GetLastError()
            if last_err in (21, 121, 170, 1117) and attempt < 2:
                time.sleep(0.15 * (attempt + 1))
                continue
            break

        if last_err == 1117:
            raise Ext4ReadError(
                f"ReadFile failed at {offset}: error 1117 (USB/SD card reader I/O error; "
                f"reseat SD card or try another USB reader/port — opened strictly READ-ONLY, GOLD untouched)"
            )
        raise Ext4ReadError(f"ReadFile failed at {offset}: error {last_err}")

    def _read_chunk(self, chunk_idx):
        cached = self._cache.get(chunk_idx)
        if cached is not None:
            self._cache.move_to_end(chunk_idx)
            return cached

        offset = chunk_idx * self.chunk_size
        data = self._read_raw_aligned(offset, self.chunk_size)
        if len(self._cache) >= self._cache_max:
            self._cache.popitem(last=False)
        self._cache[chunk_idx] = data
        return data

    def read_at(self, offset, length):
        if length <= 0:
            return b""
        # Bulk sequential reads (e.g. coalesced file extents >= 16 KiB) go straight to aligned 512 KiB ReadFile chunks
        if length >= 16384:
            align = max(4096, self.sector_size)
            aligned_start = (offset // align) * align
            aligned_end = ((offset + length + align - 1) // align) * align
            total = aligned_end - aligned_start
            max_usb_xfer = 512 * 1024
            if total <= max_usb_xfer:
                raw = self._read_raw_aligned(aligned_start, total)
            else:
                buf_parts = []
                cur = aligned_start
                rem = total
                while rem > 0:
                    step = min(rem, max_usb_xfer)
                    buf_parts.append(self._read_raw_aligned(cur, step))
                    cur += step
                    rem -= step
                raw = b"".join(buf_parts)
            rel = offset - aligned_start
            return raw[rel : rel + length]

        cs = self.chunk_size
        start_chunk = offset // cs
        end_chunk = (offset + length - 1) // cs

        chunks = []
        for chunk_idx in range(start_chunk, end_chunk + 1):
            chunk_data = self._read_chunk(chunk_idx)
            p_start = 0 if chunk_idx > start_chunk else (offset % cs)
            p_end = cs if chunk_idx < end_chunk else (((offset + length - 1) % cs) + 1)
            chunks.append(chunk_data[p_start:p_end])
        return b"".join(chunks)


def read_mbr_partitions(stream):
    """Parse MBR (or protective GPT fallback) partitions from byte offset 0."""
    mbr = stream.read_at(0, 512)
    if len(mbr) < 512 or mbr[510:512] != b"\x55\xaa":
        raise Ext4ReadError("Valid MBR signature (0x55AA) not found at sector 0.")

    parts = []
    for idx in range(4):
        entry = mbr[446 + idx * 16 : 446 + (idx + 1) * 16]
        ptype = entry[4]
        lba_start, sectors = struct.unpack("<II", entry[8:16])
        if ptype != 0 and sectors > 0:
            parts.append(
                {
                    "index": idx,
                    "type": ptype,
                    "offset": lba_start * 512,
                    "size": sectors * 512,
                }
            )

    # Handle GPT if protective MBR (0xEE)
    if len(parts) == 1 and parts[0]["type"] == 0xEE:
        hdr = stream.read_at(512, 92)
        if hdr[:8] == b"EFI PART":
            part_lba, num_entries, entry_size = struct.unpack("<QII", hdr[72:88])
            gpt_parts = []
            raw_entries = stream.read_at(part_lba * 512, min(num_entries, 128) * entry_size)
            for idx in range(min(num_entries, 128)):
                ent = raw_entries[idx * entry_size : (idx + 1) * entry_size]
                if len(ent) < 56:
                    break
                type_guid = ent[:16]
                if type_guid == b"\x00" * 16:
                    continue
                first_lba, last_lba = struct.unpack("<QQ", ent[32:48])
                if last_lba >= first_lba:
                    gpt_parts.append(
                        {
                            "index": idx,
                            "type": 0x83,
                            "offset": first_lba * 512,
                            "size": (last_lba - first_lba + 1) * 512,
                        }
                    )
            return gpt_parts

    return parts


class Ext4Inode:
    def __init__(self, ino, mode, size, links_count, blocks_lo, flags, i_block):
        self.ino = ino
        self.mode = mode
        self.size = size
        self.links_count = links_count
        self.blocks_lo = blocks_lo
        self.flags = flags
        self.i_block = i_block

    @property
    def is_dir(self):
        return (self.mode & S_IFMT) == S_IFDIR

    @property
    def is_reg(self):
        return (self.mode & S_IFMT) == S_IFREG

    @property
    def is_symlink(self):
        return (self.mode & S_IFMT) == S_IFLNK


class Ext4Volume:
    """Strictly read-only ext2/ext3/ext4 volume reader."""

    def __init__(self, stream, part_offset):
        self.stream = stream
        self.part_offset = part_offset
        sb = self.stream.read_at(part_offset + 1024, 1024)
        if len(sb) < 1024:
            raise Ext4ReadError("Failed to read ext4 superblock.")

        magic = struct.unpack("<H", sb[0x38:0x3A])[0]
        if magic != EXT4_SUPER_MAGIC:
            raise Ext4ReadError(f"Not an ext2/ext3/ext4 filesystem (magic=0x{magic:04x}).")

        self.inodes_count = struct.unpack("<I", sb[0x00:0x04])[0]
        self.first_data_block = struct.unpack("<I", sb[0x14:0x18])[0]
        log_block_size = struct.unpack("<I", sb[0x18:0x1C])[0]
        self.block_size = 1024 << log_block_size
        self.blocks_per_group = struct.unpack("<I", sb[0x20:0x24])[0]
        self.inodes_per_group = struct.unpack("<I", sb[0x28:0x2C])[0]
        self.inode_size = struct.unpack("<H", sb[0x58:0x5A])[0] or 128
        self.incompat = struct.unpack("<I", sb[0x60:0x64])[0]
        raw_desc_sz = struct.unpack("<H", sb[0xFE:0x100])[0]
        self.desc_size = raw_desc_sz if (self.incompat & EXT4_FEATURE_INCOMPAT_64BIT) and raw_desc_sz >= 64 else 32
        u = sb[0x68:0x78]
        self.uuid = (
            f"{u[0:4].hex()}-{u[4:6].hex()}-{u[6:8].hex()}-{u[8:10].hex()}-{u[10:16].hex()}"
        )
        self.volume_name = sb[0x78:0x88].split(b"\x00", 1)[0].decode("utf-8", errors="replace")

        gdt_block = self.first_data_block + 1
        self.gdt_offset = self.part_offset + gdt_block * self.block_size
        self._group_inode_tables = {}

    def _read_block(self, block_num):
        if block_num == 0:
            return b"\x00" * self.block_size
        return self.stream.read_at(self.part_offset + block_num * self.block_size, self.block_size)

    def _get_inode_table_block(self, group):
        cached = self._group_inode_tables.get(group)
        if cached is not None:
            return cached
        gd = self.stream.read_at(self.gdt_offset + group * self.desc_size, self.desc_size)
        lo = struct.unpack("<I", gd[0x08:0x0C])[0]
        hi = struct.unpack("<I", gd[0x28:0x2C])[0] if self.desc_size >= 64 else 0
        tbl = (hi << 32) | lo
        self._group_inode_tables[group] = tbl
        return tbl

    def read_inode(self, ino):
        if ino <= 0 or ino > self.inodes_count:
            raise Ext4ReadError(f"Invalid inode number: {ino}")
        group = (ino - 1) // self.inodes_per_group
        index = (ino - 1) % self.inodes_per_group
        tbl_block = self._get_inode_table_block(group)
        off = self.part_offset + tbl_block * self.block_size + index * self.inode_size
        raw = self.stream.read_at(off, self.inode_size)

        mode = struct.unpack("<H", raw[0x00:0x02])[0]
        size_lo = struct.unpack("<I", raw[0x04:0x08])[0]
        links_count = struct.unpack("<H", raw[0x1A:0x1C])[0]
        blocks_lo = struct.unpack("<I", raw[0x1C:0x20])[0]
        flags = struct.unpack("<I", raw[0x20:0x24])[0]
        i_block = raw[0x28:0x64]
        size_hi = struct.unpack("<I", raw[0x6C:0x70])[0] if len(raw) >= 0x70 else 0
        size = ((size_hi << 32) | size_lo) if (mode & S_IFMT) == S_IFREG else size_lo
        return Ext4Inode(ino, mode, size, links_count, blocks_lo, flags, i_block)

    def _iter_extent_node(self, node_bytes):
        eh_magic, eh_entries, _eh_max, eh_depth = struct.unpack("<HHHH", node_bytes[:8])
        if eh_magic != EXT4_EXTENT_MAGIC:
            raise Ext4ReadError(f"Bad extent header magic: 0x{eh_magic:04x}")
        if eh_depth == 0:
            for idx in range(eh_entries):
                ent = node_bytes[12 + idx * 12 : 24 + idx * 12]
                ee_block, ee_len, ee_start_hi, ee_start_lo = struct.unpack("<IHHI", ent)
                unwritten = ee_len > 32768
                count = (ee_len - 32768) if unwritten else ee_len
                phys_start = (ee_start_hi << 32) | ee_start_lo
                yield ee_block, count, (0 if unwritten else phys_start)
        else:
            for idx in range(eh_entries):
                ent = node_bytes[12 + idx * 12 : 24 + idx * 12]
                _ei_block, ei_leaf_lo, ei_leaf_hi = struct.unpack("<IIH", ent[:10])
                child_block = (ei_leaf_hi << 32) | ei_leaf_lo
                child_bytes = self._read_block(child_block)
                yield from self._iter_extent_node(child_bytes)

    def _iter_indirect_blocks(self, block_num, depth):
        if block_num == 0:
            span = (self.block_size // 4) ** depth
            for _ in range(span):
                yield 0
            return
        data = self._read_block(block_num)
        ptrs = struct.unpack(f"<{self.block_size // 4}I", data)
        if depth == 1:
            for p in ptrs:
                yield p
        else:
            for p in ptrs:
                yield from self._iter_indirect_blocks(p, depth - 1)

    def _iter_inode_data_blocks(self, inode):
        total_blocks = (inode.size + self.block_size - 1) // self.block_size
        if total_blocks == 0:
            return

        if inode.flags & EXT4_EXTENTS_FL:
            cur_logical = 0
            for ee_block, count, phys_start in self._iter_extent_node(inode.i_block):
                while cur_logical < ee_block and cur_logical < total_blocks:
                    yield 0
                    cur_logical += 1
                for off in range(count):
                    if cur_logical >= total_blocks:
                        return
                    yield (phys_start + off) if phys_start else 0
                    cur_logical += 1
            while cur_logical < total_blocks:
                yield 0
                cur_logical += 1
        else:
            ptrs = struct.unpack("<15I", inode.i_block)
            yielded = 0
            for b in ptrs[:12]:
                if yielded >= total_blocks:
                    return
                yield b
                yielded += 1
            for depth, slot in ((1, 12), (2, 13), (3, 14)):
                if yielded >= total_blocks:
                    return
                for b in self._iter_indirect_blocks(ptrs[slot], depth):
                    if yielded >= total_blocks:
                        return
                    yield b
                    yielded += 1

    def read_inode_bytes(self, inode):
        if inode.size == 0:
            return b""
        if inode.is_symlink and inode.blocks_lo == 0 and inode.size <= 60:
            return inode.i_block[: inode.size]

        out = bytearray()
        remaining = inode.size
        run_phys = None
        run_blocks = 0
        max_run_blocks = max(1, (512 * 1024) // self.block_size)

        def _flush_run():
            nonlocal remaining
            if run_blocks <= 0 or remaining <= 0:
                return
            want = min(remaining, run_blocks * self.block_size)
            if run_phys == 0:
                out.extend(b"\x00" * want)
            else:
                off = self.part_offset + run_phys * self.block_size
                chunk = self.stream.read_at(off, want)
                if len(chunk) < want:
                    chunk = chunk + b"\x00" * (want - len(chunk))
                out.extend(chunk)
            remaining -= want

        for phys_block in self._iter_inode_data_blocks(inode):
            if remaining <= 0:
                break
            if (
                run_phys is not None
                and (
                    (phys_block == 0 and run_phys == 0)
                    or (phys_block > 0 and run_phys > 0 and phys_block == run_phys + run_blocks)
                )
                and run_blocks < max_run_blocks
            ):
                run_blocks += 1
            else:
                _flush_run()
                run_phys = phys_block
                run_blocks = 1

        _flush_run()
        return bytes(out)

    def list_dir_inode(self, inode):
        if not inode.is_dir:
            raise Ext4ReadError(f"Inode {inode.ino} is not a directory.")
        data = self.read_inode_bytes(inode)
        entries = []
        pos = 0
        while pos + 8 <= len(data):
            d_ino, rec_len, name_len, file_type = struct.unpack("<IHBB", data[pos : pos + 8])
            if rec_len < 8 or pos + rec_len > len(data):
                break
            if d_ino != 0 and name_len > 0 and pos + 8 + name_len <= len(data):
                name = data[pos + 8 : pos + 8 + name_len].decode("utf-8", errors="replace")
                if name not in (".", ".."):
                    entries.append((name, d_ino, file_type))
            pos += rec_len
        return entries

    def resolve_path(self, path, follow_symlinks=True, _depth=0):
        if _depth > 16:
            return None
        norm = posixpath.normpath("/" + str(path))
        parts = [p for p in norm.split("/") if p and p != "."]
        cur_ino = 2  # root inode
        for idx, part in enumerate(parts):
            inode = self.read_inode(cur_ino)
            if inode.is_symlink and follow_symlinks:
                target = self.read_inode_bytes(inode).decode("utf-8", errors="replace")
                if target.startswith("/"):
                    next_path = target
                else:
                    parent = "/" + "/".join(parts[:idx])
                    next_path = posixpath.normpath(posixpath.join(parent, target))
                resolved = self.resolve_path(next_path, follow_symlinks=True, _depth=_depth + 1)
                if resolved is None:
                    return None
                inode = resolved
                cur_ino = inode.ino
            if not inode.is_dir:
                return None
            match = next((d_ino for name, d_ino, _ in self.list_dir_inode(inode) if name == part), None)
            if match is None:
                return None
            cur_ino = match

        final = self.read_inode(cur_ino)
        if final.is_symlink and follow_symlinks:
            target = self.read_inode_bytes(final).decode("utf-8", errors="replace")
            if target.startswith("/"):
                next_path = target
            else:
                parent = "/" + "/".join(parts[:-1])
                next_path = posixpath.normpath(posixpath.join(parent, target))
            return self.resolve_path(next_path, follow_symlinks=True, _depth=_depth + 1)
        return final

    def read_file(self, path):
        inode = self.resolve_path(path, follow_symlinks=True)
        if inode is None or not inode.is_reg:
            raise FileNotFoundError(f"File not found on ext4 volume: {path}")
        return self.read_inode_bytes(inode)

    def list_dir(self, path="/"):
        inode = self.resolve_path(path, follow_symlinks=True)
        if inode is None or not inode.is_dir:
            return []
        return self.list_dir_inode(inode)

    def walk(self, root_path, max_files=25000):
        """Yield (posix_path, Ext4Inode) recursively under root_path (does not follow dir symlinks)."""
        start = self.resolve_path(root_path, follow_symlinks=True)
        if start is None or not start.is_dir:
            return
        seen_dirs = set()
        count = 0
        stack = [(root_path.rstrip("/") or "/", start)]
        while stack:
            cur_path, dir_inode = stack.pop()
            if dir_inode.ino in seen_dirs:
                continue
            seen_dirs.add(dir_inode.ino)
            for name, child_ino, _ in self.list_dir_inode(dir_inode):
                child_path = f"{cur_path}/{name}" if cur_path != "/" else f"/{name}"
                child = self.read_inode(child_ino)
                yield child_path, child
                count += 1
                if count >= max_files:
                    return
                if child.is_dir:
                    stack.append((child_path, child))


def read_fat32_root_files(stream, part_offset, wanted_names):
    """Best-effort strictly read-only FAT16/FAT32 root directory reader (zero Windows mount needed)."""
    wanted_low = {name.lower(): name for name in wanted_names}
    found = {}
    try:
        vbr = stream.read_at(part_offset, 512)
        if len(vbr) < 512 or vbr[510:512] != b"\x55\xaa":
            return found
        bytes_per_sec, sec_per_clus, rsvd_sec, num_fats, root_ent_cnt, _tot16, _media, fat_sz16 = struct.unpack_from(
            "<HBHBHHBH", vbr, 11
        )
        fat_sz32 = struct.unpack_from("<I", vbr, 36)[0]
        root_clus = struct.unpack_from("<I", vbr, 44)[0]
        if bytes_per_sec not in (512, 1024, 2048, 4096) or sec_per_clus == 0 or num_fats == 0:
            return found

        is_fat32 = fat_sz16 == 0 and root_ent_cnt == 0 and fat_sz32 > 0
        fat_sz = fat_sz32 if is_fat32 else fat_sz16
        fat_offset = part_offset + rsvd_sec * bytes_per_sec
        root_dir_secs = ((root_ent_cnt * 32) + (bytes_per_sec - 1)) // bytes_per_sec
        first_data_sec = rsvd_sec + (num_fats * fat_sz) + root_dir_secs
        clus_bytes = sec_per_clus * bytes_per_sec

        def _clus_off(clus):
            return part_offset + (first_data_sec + (clus - 2) * sec_per_clus) * bytes_per_sec

        def _read_chain(start_clus, max_bytes=4 * 1024 * 1024):
            if start_clus < 2:
                return b""
            out = bytearray()
            cur = start_clus
            seen = set()
            eoc = 0x0FFFFFF8 if is_fat32 else 0xFFF8
            mask = 0x0FFFFFFF if is_fat32 else 0xFFFF
            entry_sz = 4 if is_fat32 else 2
            while 2 <= cur < eoc and cur not in seen and len(out) < max_bytes:
                seen.add(cur)
                out.extend(stream.read_at(_clus_off(cur), clus_bytes))
                raw_next = stream.read_at(fat_offset + cur * entry_sz, entry_sz)
                if len(raw_next) < entry_sz:
                    break
                cur = (struct.unpack("<I", raw_next)[0] if is_fat32 else struct.unpack("<H", raw_next)[0]) & mask
            return bytes(out[:max_bytes])

        dir_bytes = _read_chain(root_clus, 512 * 1024) if is_fat32 else stream.read_at(
            part_offset + (rsvd_sec + num_fats * fat_sz) * bytes_per_sec,
            root_ent_cnt * 32,
        )
        lfn_parts = []
        for off in range(0, len(dir_bytes) - 31, 32):
            ent = dir_bytes[off : off + 32]
            first = ent[0]
            if first == 0x00:
                break
            if first == 0xE5:
                lfn_parts = []
                continue
            attr = ent[11]
            if attr == 0x0F:
                seq = first & 0x1F
                if first & 0x40:
                    lfn_parts = []
                raw_chars = ent[1:11] + ent[14:26] + ent[28:32]
                piece = raw_chars.decode("utf-16le", errors="ignore").split("\x00", 1)[0]
                lfn_parts.append((seq, piece))
                continue
            if attr & 0x18:  # volume id or subdir
                lfn_parts = []
                continue
            short_base = ent[0:8].decode("ascii", errors="ignore").rstrip(" ")
            short_ext = ent[8:11].decode("ascii", errors="ignore").rstrip(" ")
            short_name = f"{short_base}.{short_ext}" if short_ext else short_base
            long_name = "".join(p for _, p in sorted(lfn_parts, key=lambda x: x[0])) if lfn_parts else short_name
            lfn_parts = []
            match_key = wanted_low.get(long_name.lower()) or wanted_low.get(short_name.lower())
            if match_key:
                hi = struct.unpack_from("<H", ent, 20)[0]
                lo, fsize = struct.unpack_from("<HI", ent, 26)
                start_clus = ((hi << 16) | lo) if is_fat32 else lo
                data = _read_chain(start_clus, max_bytes=max(fsize, clus_bytes))[:fsize]
                found[match_key] = data
    except Exception:
        pass
    return found


def read_disk_signature_and_ext4_uuid(device_path):
    """Best-effort read-only probe of MBR disk signature and first ext4 partition UUID."""
    sig = 0
    ext4_uuid = ""
    try:
        with RawReadOnlyStream(device_path) as stream:
            mbr = stream.read_at(0, 512)
            if len(mbr) >= 512 and mbr[510:512] == b"\x55\xaa":
                sig = struct.unpack("<I", mbr[440:444])[0]
            for part in read_mbr_partitions(stream):
                try:
                    vol = Ext4Volume(stream, part["offset"])
                    ext4_uuid = vol.uuid
                    break
                except Ext4ReadError:
                    continue
    except Exception:
        pass
    return sig, ext4_uuid

