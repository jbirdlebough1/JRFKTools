import http.server
import json
import os
import sys
import threading
import unittest
import urllib.error
import urllib.request
from unittest.mock import patch

MIGRATOR_DIR = os.path.abspath(os.path.dirname(__file__))
if MIGRATOR_DIR not in sys.path:
    sys.path.insert(0, MIGRATOR_DIR)

import sd_guard
import server as migrator_server


def make_sample_disks():
    return [
        {
            "index": 0,
            "id": r"\\.\PHYSICALDRIVE0",
            "model": "EXT X200E SSD",
            "interface": "SCSI",
            "bus_type": "NVMe",
            "pd_bus_type": "NVMe",
            "wmi_media_type": "Fixed hard disk media",
            "media_loaded": True,
            "size_bytes": 1024203640320,
            "pd_size_bytes": 1024209543168,
            "msft_media_type": "",
            "pd_media_type": "SSD",
            "is_system": True,
            "is_boot": True,
            "partitions": [
                {"letter": "C:", "drive_type": 3, "volume_name": "Windows", "file_system": "NTFS"}
            ],
            "letter": "C:",
        },
        {
            "index": 1,
            "id": r"\\.\PHYSICALDRIVE1",
            "model": "WD My Book 25EE USB Device",
            "interface": "USB",
            "bus_type": "USB",
            "pd_bus_type": "USB",
            "wmi_media_type": "External hard disk media",
            "media_loaded": True,
            "size_bytes": 4000784417280,
            "pd_size_bytes": 4000786153472,
            "msft_media_type": "",
            "pd_media_type": "HDD",
            "is_system": False,
            "is_boot": False,
            "partitions": [
                {"letter": "D:", "drive_type": 3, "volume_name": "Projects", "file_system": "NTFS"}
            ],
            "letter": "D:",
        },
        {
            "index": 2,
            "id": r"\\.\PHYSICALDRIVE2",
            "model": "MXT-USB Storage Device USB Device",
            "interface": "USB",
            "bus_type": "USB",
            "pd_bus_type": "USB",
            "wmi_media_type": "Removable Media",
            "media_loaded": True,
            "size_bytes": 31914086400,
            "pd_size_bytes": 31914983424,
            "msft_media_type": "",
            "pd_media_type": "Unspecified",
            "is_system": False,
            "is_boot": False,
            "is_offline": True,
            "partitions": [
                {"letter": "E:", "drive_type": 2, "volume_name": "boot", "file_system": "FAT32"}
            ],
            "letter": "E:",
        },
    ]


class SDGuardUnitTests(unittest.TestCase):
    def test_blocks_nvme_ssd_and_usb_hdd_allows_mxt_usb_sd(self):
        disks = [sd_guard.enrich_disk_record(d, system_drive="C") for d in make_sample_disks()]
        self.assertFalse(disks[0]["writable"])
        self.assertFalse(disks[1]["writable"])
        self.assertTrue(disks[2]["writable"])
        self.assertTrue(disks[2]["is_sd"])

        with self.assertRaises(sd_guard.SDGuardError):
            sd_guard.validate_sd_write_target(0, disks=disks, system_drive="C")
        with self.assertRaises(sd_guard.SDGuardError):
            sd_guard.validate_sd_write_target(1, disks=disks, system_drive="C")

        verified = sd_guard.validate_sd_write_target(2, drive_letter="E:", disks=disks, system_drive="C")
        self.assertEqual(verified["index"], 2)

    def test_blocks_usb_ssd_even_in_sd_size_range(self):
        usb_ssd = {
            "index": 3,
            "id": r"\\.\PHYSICALDRIVE3",
            "model": "Portable USB SSD 32GB",
            "interface": "USB",
            "bus_type": "USB",
            "pd_bus_type": "USB",
            "wmi_media_type": "Removable Media",
            "media_loaded": True,
            "size_bytes": 32_000_000_000,
            "pd_media_type": "SSD",
            "is_system": False,
            "is_boot": False,
            "partitions": [{"letter": "F:", "drive_type": 2}],
        }
        with self.assertRaises(sd_guard.SDGuardError):
            sd_guard.validate_sd_write_target(3, disks=[usb_ssd], system_drive="C")

        external_ssd = dict(usb_ssd, model="SanDisk Extreme", pd_media_type="Unspecified", wmi_media_type="External hard disk media")
        with self.assertRaises(sd_guard.SDGuardError):
            sd_guard.validate_sd_write_target(3, disks=[external_ssd], system_drive="C")

    def test_size_bounds_16gb_to_64gb_nominal(self):
        base = {
            "index": 4,
            "id": r"\\.\PHYSICALDRIVE4",
            "model": "USB SD Reader",
            "interface": "USB",
            "bus_type": "USB",
            "wmi_media_type": "Removable Media",
            "media_loaded": True,
            "pd_media_type": "Unspecified",
            "is_system": False,
            "is_boot": False,
            "partitions": [],
        }
        # 8 GB -> blocked
        with self.assertRaises(sd_guard.SDGuardError):
            sd_guard.validate_sd_write_target(4, disks=[dict(base, size_bytes=8_000_000_000)], system_drive="C")
        # 128 GB -> blocked
        with self.assertRaises(sd_guard.SDGuardError):
            sd_guard.validate_sd_write_target(4, disks=[dict(base, size_bytes=127_865_454_592)], system_drive="C")
        # 16 GB nominal (~14.4 GiB / 15.46 billion bytes) -> allowed
        ok16 = sd_guard.validate_sd_write_target(4, disks=[dict(base, size_bytes=15_460_000_000)], system_drive="C")
        self.assertTrue(ok16["writable"])
        # 64 GB nominal (~59.5 GiB / 63.9 billion bytes) -> allowed
        ok64 = sd_guard.validate_sd_write_target(4, disks=[dict(base, size_bytes=63_900_000_000)], system_drive="C")
        self.assertTrue(ok64["writable"])

    def test_allows_native_sd_bus_and_blocks_cross_drive_letter(self):
        native_sd = {
            "index": 5,
            "id": r"\\.\PHYSICALDRIVE5",
            "model": "Realtek SD/MMC Card",
            "interface": "SD",
            "bus_type": "SD",
            "wmi_media_type": "Removable Media",
            "media_loaded": True,
            "size_bytes": 31_914_086_400,
            "pd_media_type": "Unspecified",
            "is_system": False,
            "is_boot": False,
            "partitions": [{"letter": "G:", "drive_type": 2}],
        }
        disks = make_sample_disks() + [native_sd]
        self.assertTrue(sd_guard.validate_sd_write_target(5, drive_letter="G:", disks=disks, system_drive="C")["writable"])
        # Cross-drive letter C: or D: paired with Disk 5 must be blocked
        with self.assertRaises(sd_guard.SDGuardError):
            sd_guard.validate_sd_write_target(5, drive_letter="C:", disks=disks, system_drive="C")
        with self.assertRaises(sd_guard.SDGuardError):
            sd_guard.validate_sd_write_target(5, drive_letter="D:", disks=disks, system_drive="C")
        # Missing disk_index must be blocked
        with self.assertRaises(sd_guard.SDGuardError):
            sd_guard.validate_sd_write_target(None, disks=disks, system_drive="C")


class ServerEndpointGuardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 0), migrator_server.MigratorHandler)
        cls.port = cls.httpd.server_address[1]
        cls.thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()

    def _req(self, method, path, body=None):
        url = f"http://127.0.0.1:{self.port}{path}"
        data = json.dumps(body).encode("utf-8") if body is not None else None
        headers = {"Content-Type": "application/json"} if body is not None else {}
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=5) as resp:
                return resp.status, json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as err:
            return err.code, json.loads(err.read().decode("utf-8"))

    def test_endpoints_reject_ssd_hdd_and_missing_target(self):
        with patch.object(sd_guard, "query_disks_raw", return_value=make_sample_disks()), \
             patch.object(migrator_server, "clean_disk_partitions"), \
             patch.object(migrator_server, "rescan_disk"):
            for endpoint in ("/api/start_clean_build", "/api/erase_sd", "/api/inject_bits", "/api/extract_golden_master"):
                for payload in (
                    {},
                    {"disk_index": 0, "drive_letter": "C:"},
                    {"disk_index": 1, "drive_letter": "D:"},
                    {"disk_index": 2, "drive_letter": "C:"},
                ):
                    code, data = self._req("POST", endpoint, payload)
                    self.assertEqual(code, 403, f"{endpoint} with {payload} returned {code}: {data}")
                    self.assertEqual(data["status"], "error")

            # GET /api/erase_sd must be disallowed
            code, _ = self._req("GET", "/api/erase_sd?disk_index=2")
            self.assertEqual(code, 405)

            # Eject & validate_card reject Disk 0 / C:
            code, _ = self._req("POST", "/api/eject_sd", {"disk_index": 0, "drive_letter": "C:"})
            self.assertEqual(code, 403)
            code, _ = self._req("GET", "/api/validate_card?disk_index=0&drive_letter=C:")
            self.assertEqual(code, 403)

            # /api/launch_imager rejects Disk 0 / Disk 1 / cross-drive C: when Imager exists
            with patch.object(migrator_server, "find_rpi_imager", return_value=r"C:\fake\rpi-imager.exe"):
                for payload in ({}, {"disk_index": 0}, {"disk_index": 1}, {"disk_index": 2, "drive_letter": "C:"}):
                    code, data = self._req("POST", "/api/launch_imager", payload)
                    self.assertEqual(code, 403, f"/api/launch_imager with {payload} returned {code}: {data}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
