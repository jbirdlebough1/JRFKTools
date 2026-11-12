import http.server
import json
import os
import sys
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from unittest.mock import patch

MIGRATOR_DIR = os.path.abspath(os.path.dirname(__file__))
if MIGRATOR_DIR not in sys.path:
    sys.path.insert(0, MIGRATOR_DIR)

import ext4_ro
import gold_extractor
import sd_guard
import server as migrator_server

BASE_DIR = os.path.abspath(os.path.join(MIGRATOR_DIR, "..", ".."))
CACHED_RPI_IMG = os.path.join(BASE_DIR, "images", "raspios_bookworm_arm64.img")


def _sample_gold_and_new_disks():
    gold_disk = sd_guard.enrich_disk_record(
        {
            "index": 2,
            "id": r"\\.\PHYSICALDRIVE2",
            "model": "MXT-USB Storage Device USB Device",
            "interface": "USB",
            "bus_type": "USB",
            "wmi_media_type": "Removable Media",
            "media_loaded": True,
            "size_bytes": 31914086400,
            "serial_number": "150101v01",
            "signature": 4237476252,  # 0xfc92c19c
            "pd_media_type": "Unspecified",
            "is_system": False,
            "is_boot": False,
            "partitions": [{"letter": "E:", "drive_type": 2, "volume_name": "boot", "file_system": "FAT32"}],
            "letter": "E:",
        },
        system_drive="C",
    )
    new_blank_disk_same_adapter = sd_guard.enrich_disk_record(
        {
            "index": 2,
            "id": r"\\.\PHYSICALDRIVE2",
            "model": "MXT-USB Storage Device USB Device",
            "interface": "USB",
            "bus_type": "USB",
            "wmi_media_type": "Removable Media",
            "media_loaded": True,
            "size_bytes": 31914086400,
            "serial_number": "150101v01",
            "signature": 305419896,  # 0x12345678
            "pd_media_type": "Unspecified",
            "is_system": False,
            "is_boot": False,
            "partitions": [],
            "letter": "",
        },
        system_drive="C",
    )
    return gold_disk, new_blank_disk_same_adapter


class GoldExtractorAndLockTests(unittest.TestCase):
    @unittest.skipUnless(os.path.isfile(CACHED_RPI_IMG), "Cached RPi OS image not present")
    def test_ext4_ro_and_extract_against_real_rpi_image(self):
        gold_disk, _ = _sample_gold_and_new_disks()
        with tempfile.TemporaryDirectory() as tmpdir:
            manifest = gold_extractor.extract_gold_sd(
                2,
                drive_letter=None,
                backup_root=tmpdir,
                device_path_override=CACHED_RPI_IMG,
                disks=[gold_disk],
            )
            self.assertEqual(manifest["status"], "ok")
            self.assertGreaterEqual(len(manifest["partitions"]), 2)
            self.assertEqual(manifest["metadata"]["hostname"], "raspberrypi")
            self.assertIn("bookworm", manifest["metadata"]["os_release"].lower())
            self.assertTrue(manifest["gold_fingerprint"]["ext4_uuid"])
            self.assertTrue(os.path.isfile(manifest["archive_path"]))
            self.assertTrue(os.path.isfile(os.path.join(tmpdir, gold_extractor.LATEST_MANIFEST_NAME)))

    def test_gold_fingerprint_lock_blocks_gold_and_allows_new_sd_in_same_adapter(self):
        gold_disk, new_sd = _sample_gold_and_new_disks()
        with tempfile.TemporaryDirectory() as tmpdir:
            manifest = {
                "gold_fingerprint": {
                    "disk_signature": 4237476252,
                    "ext4_uuid": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
                    "boot_partuuid": "fc92c19c-02",
                }
            }
            with open(os.path.join(tmpdir, gold_extractor.LATEST_MANIFEST_NAME), "w", encoding="utf-8") as f:
                json.dump(manifest, f)

            # GOLD card must be blocked by signature
            with self.assertRaises(sd_guard.SDGuardError) as ctx:
                gold_extractor.check_not_gold_target(gold_disk, backup_root=tmpdir)
            self.assertIn("GOLDEN MASTER", str(ctx.exception))

            # Same adapter, different signature & no GOLD ext4 UUID -> ALLOWED
            with patch.object(ext4_ro, "read_disk_signature_and_ext4_uuid", return_value=(0x12345678, "11111111-2222-3333-4444-555555555555")):
                gold_extractor.check_not_gold_target(new_sd, backup_root=tmpdir)

            # Even if signature were 0, matching ext4_uuid must still be blocked
            zero_sig_gold = dict(gold_disk, signature=0)
            with patch.object(ext4_ro, "read_disk_signature_and_ext4_uuid", return_value=(0, "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee")):
                with self.assertRaises(sd_guard.SDGuardError):
                    gold_extractor.check_not_gold_target(zero_sig_gold, backup_root=tmpdir)


class GoldHttpLockTests(unittest.TestCase):
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

    def test_write_endpoints_block_gold_sd_via_http(self):
        gold_disk, _ = _sample_gold_and_new_disks()
        manifest = {
            "gold_fingerprint": {
                "disk_signature": 4237476252,
                "ext4_uuid": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
                "boot_partuuid": "fc92c19c-02",
            }
        }
        with patch.object(sd_guard, "query_disks_raw", return_value=[gold_disk]), \
             patch.object(gold_extractor, "load_latest_gold_manifest", return_value=manifest), \
             patch.object(migrator_server, "find_rpi_imager", return_value=r"C:\fake\rpi-imager.exe"):
            # /api/disks marks GOLD as is_sd=True, is_gold=True, writable=False
            code, disks_resp = self._req("GET", "/api/disks")
            self.assertEqual(code, 200)
            self.assertTrue(disks_resp["disks"][0]["is_sd"])
            self.assertTrue(disks_resp["disks"][0]["is_gold"])
            self.assertFalse(disks_resp["disks"][0]["writable"])

            # All write endpoints must refuse GOLD with 403
            for ep in ("/api/start_clean_build", "/api/erase_sd", "/api/inject_bits", "/api/launch_imager"):
                code, resp = self._req("POST", ep, {"disk_index": 2, "drive_letter": "E:"})
                self.assertEqual(code, 403, f"{ep} should have blocked GOLD: {resp}")
                self.assertIn("GOLDEN MASTER", resp["message"])


class Step3PipelineTests(unittest.TestCase):
    def test_inject_jrfk_bits_stages_gold_rootfs_wifi_and_antialias(self):
        _, new_sd = _sample_gold_and_new_disks()
        new_sd_mounted = dict(new_sd, partitions=[{"letter": "F:", "drive_type": 2}], partition_letters=["F"], letter="F:")
        with tempfile.TemporaryDirectory() as tmp:
            gold_stage = os.path.join(tmp, "gold_stage")
            target_boot = os.path.join(tmp, "target_boot")
            os.makedirs(os.path.join(gold_stage, "rootfs", "home", "pi", "PA-Files"), exist_ok=True)
            os.makedirs(os.path.join(gold_stage, "rootfs", "etc", "wpa_supplicant"), exist_ok=True)
            os.makedirs(target_boot, exist_ok=True)

            with open(os.path.join(gold_stage, "rootfs", "home", "pi", "PA-Files", "calibration.json"), "w", encoding="utf-8") as f:
                f.write('{"swr": 1.0}')
            with open(os.path.join(gold_stage, "rootfs", "etc", "wpa_supplicant", "wpa_supplicant.conf"), "w", encoding="utf-8") as f:
                f.write('network={\n  ssid="MyRealShack"\n  psk="secret123"\n}\n')
            with open(os.path.join(target_boot, "cmdline.txt"), "w", encoding="utf-8") as f:
                f.write("console=serial0,115200 rootwait quiet\n")

            gold_manifest = {"staging_dir": gold_stage, "metadata": {"hostname": "k7bit", "wifi_ssid": "MyRealShack"}}

            with patch.object(migrator_server, "assert_writable_non_gold_sd", return_value=new_sd_mounted):
                migrator_server.inject_jrfk_bits(
                    target_boot + os.sep,
                    "pi",
                    "pi",
                    "k7bit",
                    "MyRealShack",
                    "",
                    disk_index=2,
                    drive_letter="F",
                    mode="migrate",
                    gold_manifest=gold_manifest,
                    auto_upgrade=True,
                    inject_cal=True,
                )

            with open(os.path.join(target_boot, "wpa_supplicant.conf"), "r", encoding="utf-8") as f:
                self.assertIn("MyRealShack", f.read())
            self.assertTrue(os.path.isfile(os.path.join(target_boot, "jrfk_payload", "gold_rootfs", "home", "pi", "PA-Files", "calibration.json")))
            self.assertTrue(os.path.isfile(os.path.join(target_boot, "jrfk_payload", "firstboot_setup.sh")))
            self.assertTrue(os.path.isfile(os.path.join(target_boot, "jrfk_payload", "patch_antialias.py")))
            self.assertTrue(os.path.isdir(os.path.join(target_boot, "jrfk_payload", "rfk_tools_suite")))
            with open(os.path.join(target_boot, "cmdline.txt"), "r", encoding="utf-8") as f:
                cmd = f.read()
                self.assertIn("video=HDMI-A-1:1024x600M@60D", cmd)
                self.assertIn("systemd.run=/boot/firmware/jrfk_payload/firstboot_setup.sh", cmd)

    def test_patch_antialias_replaces_deprecated_pillow_attr(self):
        scripts_dir = os.path.abspath(os.path.join(MIGRATOR_DIR, "..", "..", "scripts"))
        sys.path.insert(0, scripts_dir)
        import patch_antialias

        with tempfile.TemporaryDirectory() as tmp:
            sample_py = os.path.join(tmp, "themes.py")
            with open(sample_py, "w", encoding="utf-8") as f:
                f.write("img.resize((200, 200), Image.ANTIALIAS)\n")
            count = patch_antialias.patch_dirs([tmp])
            self.assertEqual(count, 1)
            with open(sample_py, "r", encoding="utf-8") as f:
                self.assertIn("getattr(Image, 'Resampling', Image).LANCZOS", f.read())



if __name__ == "__main__":
    unittest.main(verbosity=2)
