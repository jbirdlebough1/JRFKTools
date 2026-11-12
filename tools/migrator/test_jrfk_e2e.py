import json
import os
import sys
import tempfile
import unittest
from unittest import mock

MIGRATOR_DIR = os.path.abspath(os.path.dirname(__file__))
BASE_DIR = os.path.abspath(os.path.join(MIGRATOR_DIR, "..", ".."))
if MIGRATOR_DIR not in sys.path:
    sys.path.insert(0, MIGRATOR_DIR)

import server


class JrfkEndToEndUnitTests(unittest.TestCase):
    def test_jrfk_exe_has_uac_manifest_and_payload(self):
        exe_path = os.path.join(BASE_DIR, "JRFK.exe")
        self.assertTrue(os.path.isfile(exe_path), "JRFK.exe missing at project root")
        with open(exe_path, "rb") as f:
            raw = f.read()
        self.assertIn(b"requireAdministrator", raw)
        self.assertIn(b"JRFK.payload.zip", raw)

    def test_firstboot_has_completion_popup_and_reboot_button(self):
        sh_path = os.path.join(BASE_DIR, "scripts", "firstboot_setup.sh")
        with open(sh_path, "r", encoding="utf-8") as f:
            txt = f.read()
        self.assertIn("32-64Bit RFK migration complete", txt)
        self.assertIn("rfk_postboot_prompt.py", txt)
        self.assertIn(".jrfk_migration_complete_prompt", txt)
        self.assertIn('text="Reboot"', txt)
        self.assertIn('<application class="Tk">', txt)
        self.assertIn("labwc/autostart", txt)
        self.assertIn("labwc/rc.xml", txt)
        self.assertIn("flock -n 9", txt)
        self.assertIn("systemd-run --no-block", txt)
        self.assertIn("simple_rpc", txt)
        self.assertIn("pysftp", txt)
        self.assertIn("python3-hamlib", txt)
        self.assertIn("relink_64bit_hamlib", txt)
        self.assertIn("python3-websocket", txt)

    def test_inject_trixie_uses_cloudinit_runcmd_and_omits_systemd_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            boot_dir = os.path.join(tmp, "boot")
            os.makedirs(boot_dir, exist_ok=True)
            with open(os.path.join(boot_dir, "cmdline.txt"), "w", encoding="utf-8") as f:
                f.write("console=serial0,115200 rootwait\n")
            with open(os.path.join(boot_dir, "config.txt"), "w", encoding="utf-8") as f:
                f.write("[all]\n")
            fake_disk = {
                "index": 2,
                "is_sd": True,
                "writable": True,
                "partition_letters": ["Z"],
                "partitions": [{"letter": "Z:", "drive_type": 2}],
            }
            with mock.patch.object(server, "assert_writable_non_gold_sd", return_value=fake_disk):
                server.inject_jrfk_bits(
                    boot_dir + os.sep,
                    "pi",
                    "raspberry",
                    "k7bit",
                    "",
                    "",
                    disk_index=2,
                    drive_letter="Z",
                    mode="fresh",
                    os_info={"init_format": "cloudinit-rpi", "filename": "2026-10-06-raspios-trixie-arm64.img.xz"},
                )
            with open(os.path.join(boot_dir, "user-data"), "r", encoding="utf-8") as f:
                ud = f.read()
            self.assertIn("runcmd:", ud)
            self.assertIn("/boot/firmware/jrfk_payload/firstboot_setup.sh", ud)
            self.assertIn("--cloudinit", ud)
            self.assertNotIn("enable_ssh:", ud)
            with open(os.path.join(boot_dir, "cmdline.txt"), "r", encoding="utf-8") as f:
                cm = f.read()
            self.assertNotIn("systemd.run=", cm)
            self.assertIn("video=HDMI-A-1:1024x600M@60D", cm)

    def test_fetch_latest_rpi_os_info_selects_pi4_pi5_desktop_64bit(self):
        sample_feed = {
            "os_list": [
                {
                    "name": "Raspberry Pi OS (64-bit)",
                    "description": "Debian Trixie with Raspberry Pi Desktop",
                    "release_date": "2026-10-06",
                    "url": "https://downloads.raspberrypi.com/raspios_arm64/images/2026-10-06-raspios-trixie-arm64.img.xz",
                    "extract_sha256": "abc123",
                    "image_download_size": 1364720984,
                    "extract_size": 6744440832,
                    "devices": ["pi5-64bit", "pi4-64bit", "pi3-64bit"],
                },
                {
                    "name": "Raspberry Pi OS Lite (64-bit)",
                    "release_date": "2026-10-06",
                    "url": "https://downloads.raspberrypi.com/raspios_lite_arm64/2026-10-06-lite.img.xz",
                    "devices": ["pi5-64bit", "pi4-64bit"],
                },
            ]
        }

        class _FakeResp:
            def __init__(self, data):
                self._data = json.dumps(data).encode("utf-8")

            def read(self):
                return self._data

            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

        server._OS_FEED_CACHE["ts"] = 0.0
        server._OS_FEED_CACHE["info"] = None
        with mock.patch("urllib.request.urlopen", return_value=_FakeResp(sample_feed)):
            info = server.fetch_latest_rpi_os_info(force_refresh=True)
        self.assertEqual(info["name"], "Raspberry Pi OS (64-bit)")
        self.assertEqual(info["release_date"], "2026-10-06")
        self.assertIn("pi4-64bit", info["devices"])
        self.assertIn("pi5-64bit", info["devices"])
        self.assertEqual(info["filename"], "2026-10-06-raspios-trixie-arm64.img.xz")

    def test_ensure_latest_rpi_os_falls_back_to_local_cache_when_offline(self):
        with tempfile.TemporaryDirectory() as tmp:
            fake_img = os.path.join(tmp, "cached_arm64.img.xz")
            with open(fake_img, "wb") as f:
                f.write(b"fake-xz-bytes")

            orig_images_dir = server.IMAGES_DIR
            server.IMAGES_DIR = tmp
            server._OS_FEED_CACHE["ts"] = 0.0
            server._OS_FEED_CACHE["info"] = None
            try:
                with mock.patch("urllib.request.urlopen", side_effect=OSError("offline")):
                    with mock.patch.object(server, "resolve_os_image_path", return_value=fake_img):
                        path, info = server.ensure_latest_rpi_os_image()
                self.assertEqual(path, fake_img)
                self.assertEqual(info["source"], "cached")
            finally:
                server.IMAGES_DIR = orig_images_dir

    def test_run_pipeline_uses_flash_raw_image_and_restores_automount(self):
        with tempfile.TemporaryDirectory() as tmp:
            boot_dir = os.path.join(tmp, "Z_boot")
            os.makedirs(boot_dir, exist_ok=True)
            fake_disk = {
                "index": 2,
                "is_sd": True,
                "writable": True,
                "partition_letters": ["Z"],
                "partitions": [{"letter": "Z:", "drive_type": 2, "file_system": "FAT32"}],
            }
            os_info = {"name": "Raspberry Pi OS (64-bit)", "release_date": "2026-10-06", "init_format": "cloudinit-rpi"}
            with mock.patch.object(server, "assert_writable_non_gold_sd", return_value=fake_disk), \
                 mock.patch.object(server.sd_guard, "resolve_verified_drive_letter", return_value="Z"), \
                 mock.patch.object(server, "ensure_latest_rpi_os_image", return_value=(os.path.join(tmp, "os.img.xz"), os_info)), \
                 mock.patch.object(server, "flash_raw_image") as mock_flash, \
                 mock.patch.object(server, "find_target_boot_drive", return_value=boot_dir + os.sep), \
                 mock.patch.object(server, "inject_jrfk_bits"), \
                 mock.patch.object(server, "validate_sd_partitions", return_value={"boot_partition_ok": True, "linux_partition_ok": True, "details": ["ok"]}), \
                 mock.patch.object(server, "safely_eject_drive"), \
                 mock.patch.object(server, "_set_windows_automount") as mock_automount:
                server.run_pipeline(2, "Z", "pi", "raspberry", "k7bit", "", "", mode="fresh")
            mock_flash.assert_called_once()
            self.assertEqual(mock_automount.call_args_list[0].args, (False,))
            self.assertEqual(mock_automount.call_args_list[-1].args, (True,))


if __name__ == "__main__":
    unittest.main()
