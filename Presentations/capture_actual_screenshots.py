import asyncio
import os
from playwright.async_api import async_playwright

OUT_DIR = r"D:\JRFK\Presentations\Deck_1_Intro\real_screenshots"
STATIC_DIR = r"D:\JRFK\tools\rfk_tools_suite\static"
MIGRATOR_DIR = r"D:\JRFK\tools\migrator"

SCREENS = [
    # JRFK Migrator tool
    ("jrfk_migrator.png", os.path.join(MIGRATOR_DIR, "JRFK_32_to_64Bit_Migration_tool.htm")),
    # 8088 Web Suite screens
    ("screen_health_monitor.png", os.path.join(STATIC_DIR, "health_monitor.html")),
    ("screen_antenna_mapper.png", os.path.join(STATIC_DIR, "antenna_mapper.html")),
    ("screen_health_manager.png", os.path.join(STATIC_DIR, "health_manager.html")),
    ("screen_backup_manager.png", os.path.join(STATIC_DIR, "backup_manager.html")),
    ("screen_docs_viewer.png", os.path.join(STATIC_DIR, "docs_viewer.html")),
    ("screen_log_viewer.png", os.path.join(STATIC_DIR, "log_viewer.html")),
    ("screen_system_report.png", os.path.join(STATIC_DIR, "system_report.html")),
    ("screen_screen_viewer.png", os.path.join(STATIC_DIR, "screen_viewer.html")),
]

async def capture():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1280, "height": 800})
        
        for name, file_path in SCREENS:
            if not os.path.exists(file_path):
                print(f"Skipping {name}: file not found {file_path}")
                continue
            
            url = f"file:///{file_path.replace(os.sep, '/')}"
            print(f"Capturing {name} from {url}...")
            await page.goto(url, wait_until="networkidle")
            await page.wait_for_timeout(500)
            
            out_file = os.path.join(OUT_DIR, name)
            await page.screenshot(path=out_file)
            print(f"  [OK] Saved screenshot to {out_file}")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(capture())
