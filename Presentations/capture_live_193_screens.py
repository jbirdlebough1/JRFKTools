import os
import asyncio
from playwright.async_api import async_playwright

BASE_URL = "http://192.168.12.193:8088"
OUT_DIR = r"D:\JRFK\Presentations\Deck_1_Intro\real_screenshots"
os.makedirs(OUT_DIR, exist_ok=True)

TARGETS = [
    ("screen_health_monitor.png", f"{BASE_URL}/static/health_monitor.html"),
    ("screen_antenna_mapper.png", f"{BASE_URL}/static/antenna_mapper.html"),
    ("screen_health_manager.png", f"{BASE_URL}/static/health_manager.html"),
    ("screen_backup_manager.png", f"{BASE_URL}/static/backup_manager.html"),
    ("screen_docs_viewer.png", f"{BASE_URL}/static/docs_viewer.html"),
    ("screen_log_viewer.png", f"{BASE_URL}/static/log_viewer.html"),
    ("screen_system_report.png", f"{BASE_URL}/static/system_report.html"),
    ("screen_screen_viewer.png", f"{BASE_URL}/static/screen_viewer.html"),
    ("screen_live_index.png", f"{BASE_URL}/"),
]

async def capture_live_screens():
    print(f"Connecting to live amplifier at {BASE_URL}...")
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        # High-DPI 16:10 / 16:9 widescreen capture
        page = await browser.new_page(viewport={"width": 1440, "height": 900})
        
        for filename, url in TARGETS:
            out_path = os.path.join(OUT_DIR, filename)
            try:
                print(f"Capturing live screen: {url} -> {filename}...")
                resp = await page.goto(url, wait_until="networkidle", timeout=8000)
                await page.wait_for_timeout(800)
                await page.screenshot(path=out_path)
                print(f"  [SUCCESS] Saved {out_path} ({os.path.getsize(out_path)} bytes)")
            except Exception as e:
                print(f"  [ERROR] Failed {url}: {e}")
                
        await browser.close()
    print("Completed capturing live screens from 192.168.12.193:8088")

if __name__ == "__main__":
    asyncio.run(capture_live_screens())
