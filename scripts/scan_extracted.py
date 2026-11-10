import os
import sys
import re
import sqlite3
import hashlib
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
EXTRACTED_DIR = _ROOT / "extracted"
DB_PATH = _ROOT / "db" / "rfk_discovery.db"
DOC_PATH = _ROOT / "docs" / "JRFK_EM.md"

def get_file_hash(filepath):
    try:
        h = hashlib.sha256()
        with open(filepath, 'rb') as f:
            while chunk := f.read(65536):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return ""

def is_binary(filepath):
    try:
        with open(filepath, 'rb') as f:
            chunk = f.read(1024)
            return b'\0' in chunk
    except Exception:
        return True

def scan():
    if not EXTRACTED_DIR.exists():
        print(f"Directory {EXTRACTED_DIR} does not exist yet.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print(f"Scanning {EXTRACTED_DIR}...")
    
    rfk_files = []
    database_files = []
    services = []
    cron_jobs = []
    all_files_count = 0

    rfk_pattern = re.compile(r'rfk', re.IGNORECASE)

    for root, dirs, files in os.walk(EXTRACTED_DIR):
        for fname in files:
            all_files_count += 1
            fpath = Path(root) / fname
            rel_path = str(fpath.relative_to(EXTRACTED_DIR)).replace('\\', '/')
            
            # Check for RFK in filename
            name_match = bool(rfk_pattern.search(fname) or rfk_pattern.search(rel_path))
            content_match = False
            file_category = "general"

            # Check database signatures
            try:
                with open(fpath, 'rb') as f:
                    header = f.read(100)
                    if header.startswith(b'SQLite format 3'):
                        file_category = "sqlite_db"
                        database_files.append((rel_path, "SQLite 3", fpath.stat().st_size))
                    elif b'Berkeley DB' in header or header.startswith(b'\x00\x05\x31\x62') or header.startswith(b'\x62\x31\x05\x00'):
                        file_category = "berkeley_db"
                        database_files.append((rel_path, "Berkeley DB", fpath.stat().st_size))
            except Exception:
                pass

            # Search content for text files
            if not is_binary(fpath) and fpath.stat().st_size < 10 * 1024 * 1024:
                try:
                    with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        if rfk_pattern.search(content):
                            content_match = True
                except Exception:
                    pass

            # Check services
            if "systemd" in rel_path or "init.d" in rel_path or "rc.local" in fname:
                if name_match or content_match:
                    services.append(rel_path)

            # Check crons
            if "cron" in rel_path:
                if name_match or content_match:
                    cron_jobs.append(rel_path)

            if name_match or content_match or file_category.endswith("_db"):
                rfk_files.append({
                    "path": rel_path,
                    "name_match": name_match,
                    "content_match": content_match,
                    "category": file_category,
                    "size": fpath.stat().st_size,
                    "hash": get_file_hash(fpath)
                })

                # Insert into DB
                cursor.execute("""
                    INSERT OR REPLACE INTO artifacts (
                        file_path, partition, file_type, category, sha256_hash, description
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    rel_path,
                    "rootfs (Partition 2)",
                    fpath.suffix if fpath.suffix else "file",
                    file_category,
                    get_file_hash(fpath),
                    f"NameMatch={name_match}, ContentMatch={content_match}"
                ))

    # Record database engines
    for db_rel, engine_type, sz in database_files:
        cursor.execute("""
            INSERT OR REPLACE INTO database_engines (
                engine_name, database_file_path, file_size_bytes, notes
            ) VALUES (?, ?, ?, ?)
        """, (
            engine_type,
            db_rel,
            sz,
            "Discovered in ext4 rootfs extraction"
        ))

    conn.commit()
    conn.close()

    print(f"\nScan completed:")
    print(f"- Total files scanned: {all_files_count}")
    print(f"- RFK / DB relevant artifacts found: {len(rfk_files)}")
    print(f"- Database files: {len(database_files)}")
    print(f"- Services / Startup: {len(services)}")
    print(f"- Cron entries: {len(cron_jobs)}")

    if rfk_files:
        print("\nDiscovered Relevant Files:")
        for af in rfk_files[:50]:
            print(f"  [{af['category']}] {af['path']} ({af['size']} bytes) - NameMatch:{af['name_match']} ContentMatch:{af['content_match']}")

if __name__ == "__main__":
    scan()
