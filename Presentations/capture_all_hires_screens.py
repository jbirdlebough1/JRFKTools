import os
import asyncio
from playwright.async_api import async_playwright

BASE_URL = "http://192.168.12.193:8088"
OUT_DIR = r"D:\JRFK\Presentations\Deck_1_Intro\real_screenshots"
os.makedirs(OUT_DIR, exist_ok=True)

# High-resolution captures of the real running tools (1920x1080 viewport)
CAPTURES = [
    ("migrator_main.png", "file:///D:/JRFK/tools/migrator/JRFK_32_to_64Bit_Migration_tool.htm", "JRFK Standalone Migrator UI"),
    ("web_health_overview.png", f"{BASE_URL}/health", "JRFK Web Tools - Health Overview & Live RF Meters"),
    ("web_antenna_matrix.png", f"{BASE_URL}/antenna", "JRFK Web Tools - 4-Way Antenna Matrix Configurator"),
    ("web_backup_manager.png", f"{BASE_URL}/backup", "JRFK Web Tools - Standby Card Backup & Calibration Extractor"),
    ("web_system_report.png", f"{BASE_URL}/report", "JRFK Web Tools - Debian Trixie 64-Bit System Diagnostics"),
    ("web_log_viewer.png", f"{BASE_URL}/logs", "JRFK Web Tools - Live Event & Fault Log Viewer"),
    ("web_screen_viewer.png", f"{BASE_URL}/screen", "JRFK Web Tools - Live Resistive LCD Framebuffer Viewer"),
    ("web_docs_viewer.png", f"{BASE_URL}/docs", "JRFK Web Tools - Master Engineering Library & Cookbook Viewer"),
    ("web_portal_index.png", f"{BASE_URL}/", "JRFK Web Tools - Blueprint Portal Dashboard Index"),
]

async def snap_all():
    print("Capturing full-fidelity 1920x1080 screenshots of running tools...")
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1920, "height": 1080})
        
        for filename, url, desc in CAPTURES:
            out_path = os.path.join(OUT_DIR, filename)
            try:
                print(f"Capturing {desc} from {url}...")
                await page.goto(url, wait_until="domcontentloaded", timeout=8000)
                await page.wait_for_timeout(1000)
                await page.screenshot(path=out_path)
                print(f"  [OK] Saved {filename} ({os.path.getsize(out_path)} bytes)")
            except Exception as e:
                print(f"  [ERROR] {filename}: {e}")
                
        await browser.close()
    print("Finished screenshot captures.")

if __name__ == "__main__":
    asyncio.run(snap_all())
