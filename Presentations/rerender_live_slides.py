import os
import asyncio
from playwright.async_api import async_playwright

DECK_DIR = r"D:\JRFK\Presentations\Deck_1_Intro"

async def rerender_slides():
    print("Re-rendering all 13 1080p slide PNGs using the live 192.168.12.193:8088 screenshots...")
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1920, "height": 1080})
        
        for i in range(1, 14):
            html_path = os.path.join(DECK_DIR, f"slide_{i:02d}.html")
            png_path = os.path.join(DECK_DIR, f"slide_{i:02d}.png")
            url = f"file:///{html_path.replace(chr(92), '/')}"
            await page.goto(url, wait_until="networkidle")
            await page.screenshot(path=png_path)
            print(f"  [OK] Rerendered slide_{i:02d}.png (1920x1080 Blueprint Master with live 193:8088 screens)")
            
        await browser.close()
    print("Successfully completed slide graphics update.")

if __name__ == "__main__":
    asyncio.run(rerender_slides())
