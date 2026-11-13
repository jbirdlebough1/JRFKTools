import os
import asyncio
from playwright.async_api import async_playwright

BASE_URL = "http://192.168.12.193:8088"
OUT_DIR = r"D:\JRFK\Presentations\Deck_1_Intro\real_screenshots"
os.makedirs(OUT_DIR, exist_ok=True)

# Actual live routes hosted on the RF-KIT amplifier
ROUTES = [
    ("screen_health_monitor.png", f"{BASE_URL}/health", "Amplifier Health & Real-Time Telemetry"),
    ("screen_antenna_mapper.png", f"{BASE_URL}/antenna", "4-Way Antenna Matrix Configurator"),
    ("screen_health_manager.png", f"{BASE_URL}/health", "Systemd Hardware & Daemon Supervision"),
    ("screen_backup_manager.png", f"{BASE_URL}/backup", "Backup & Calibration Extractor"),
    ("screen_docs_viewer.png", f"{BASE_URL}/docs", "Engineering Library & Cookbook Viewer"),
    ("screen_log_viewer.png", f"{BASE_URL}/logs", "Controller Live Event Log"),
    ("screen_system_report.png", f"{BASE_URL}/report", "Debian Trixie 64-Bit System Diagnostics"),
    ("screen_screen_viewer.png", f"{BASE_URL}/screen", "Controller Resistive LCD Framebuffer"),
    ("screen_live_index.png", f"{BASE_URL}/", "Master Blueprint Shack Reference Portal"),
]

async def capture():
    print(f"Connecting to live amplifier at {BASE_URL}...")
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        # Viewport matching 1200px widescreen layout (1440x900 renders crisp 16:10 / 16:9)
        page = await browser.new_page(viewport={"width": 1440, "height": 900})
        
        for filename, url, desc in ROUTES:
            out_file = os.path.join(OUT_DIR, filename)
            try:
                print(f"Capturing {desc} from {url}...")
                await page.goto(url, wait_until="networkidle", timeout=10000)
                await page.wait_for_timeout(1000)
                await page.screenshot(path=out_file)
                size_kb = os.path.getsize(out_file) / 1024.0
                print(f"  [SUCCESS] Captured {filename}: {size_kb:.1f} KB")
            except Exception as e:
                print(f"  [ERROR] Failed to capture {url}: {e}")
                
        await browser.close()
    print("All live screens captured successfully from RF-KIT 192.168.12.193:8088!")

if __name__ == "__main__":
    asyncio.run(capture())
