import os
import sys
import asyncio
import mutagen.mp3
import edge_tts
from playwright.async_api import async_playwright

sys.path.insert(0, r"D:\JRFK\Presentations")
from pronunciation_rules import clean_for_speech

DECK_DIR = r"D:\JRFK\Presentations\Deck_1_Intro"
VSDC_DIR = os.path.join(DECK_DIR, "vsdc_media_blueprint")
os.makedirs(VSDC_DIR, exist_ok=True)

TEMPLATE_FULLSCREEN = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    html, body { width: 1920px; height: 1080px; overflow: hidden; }
    body {
        background-color: #1a5695;
        background-image: 
            linear-gradient(rgba(255, 255, 255, 0.18) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255, 255, 255, 0.18) 1px, transparent 1px),
            linear-gradient(rgba(147, 197, 253, 0.35) 2px, transparent 2px),
            linear-gradient(90deg, rgba(147, 197, 253, 0.35) 2px, transparent 2px);
        background-size: 20px 20px, 20px 20px, 100px 100px, 100px 100px;
        color: #ffffff;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        padding: 6px 12px;
        border: 2px solid #93c5fd;
    }
    .master-header {
        width: 100%;
        height: 44px;
        border-bottom: 2px solid #93c5fd;
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: rgba(26, 86, 149, 0.96);
        padding: 0 10px;
        flex-shrink: 0;
    }
    .header-left { display: flex; align-items: baseline; gap: 12px; }
    .header-tagline {
        font-family: "Consolas", monospace;
        font-size: 12px;
        letter-spacing: 1.5px;
        color: #93c5fd;
        text-transform: uppercase;
        font-weight: 700;
    }
    .header-title {
        font-size: 24px;
        font-weight: 900;
        letter-spacing: -0.5px;
        color: #ffffff;
        text-shadow: 0 2px 6px rgba(0, 0, 0, 0.6);
    }
    .header-subtitle { font-size: 13.5px; color: #bfdbfe; font-weight: 500; }
    .header-right {
        display: flex;
        gap: 10px;
        align-items: center;
        font-family: "Consolas", monospace;
        font-size: 12px;
        color: #ffffff;
        letter-spacing: 1.5px;
        font-weight: bold;
    }
    .badge-callsign {
        background: #0284c7;
        padding: 3px 10px;
        border-radius: 4px;
        border: 1px solid #93c5fd;
    }
    .badge-slide {
        background: rgba(15, 45, 85, 0.95);
        padding: 3px 8px;
        border-radius: 4px;
        border: 1px solid #60a5fa;
        color: #7dd3fc;
    }
    .master-body-fullscreen {
        width: 100%;
        flex: 1 1 auto;
        min-height: 0;
        display: flex;
        justify-content: center;
        align-items: center;
        margin: 4px 0;
        overflow: hidden;
    }
    .graphic-frame-full {
        width: 100%;
        height: 100%;
        background: rgba(8, 26, 50, 0.98);
        border: 2px solid #93c5fd;
        border-radius: 4px;
        padding: 2px;
        display: flex;
        justify-content: center;
        align-items: center;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.6);
        overflow: hidden;
    }
    .graphic-frame-full img {
        width: 100%;
        height: 100%;
        border-radius: 2px;
        display: block;
        object-fit: contain;
    }
    .master-footer {
        width: 100%;
        height: 24px;
        border-top: 1px solid #93c5fd;
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-family: "Consolas", monospace;
        font-size: 11px;
        color: #bfdbfe;
        background: rgba(26, 86, 149, 0.96);
        padding: 0 10px;
        flex-shrink: 0;
    }
    .footer-left { color: #93c5fd; font-weight: 700; }
</style>
</head>
<body>
    <div class="master-header">
        <div class="header-left">
            <div class="header-tagline">{{PART}} • {{CATEGORY}}</div>
            <div class="header-title">{{TITLE}}</div>
            <div class="header-subtitle">{{SUBTITLE}}</div>
        </div>
        <div class="header-right">
            <div class="badge-callsign">K7BIT</div>
            <div class="badge-slide">SLIDE {{SLIDE_NUM}} OF {{TOTAL_SLIDES}}</div>
        </div>
    </div>
    <div class="master-body-fullscreen">
        <div class="graphic-frame-full">
            <img src="{{IMAGE_SRC}}" alt="{{TITLE}}">
        </div>
    </div>
    <div class="master-footer">
        <div class="footer-left">{{CAPTION}}</div>
        <div class="footer-right">JRFK 64-BIT MODERNIZATION SUITE • K7BIT</div>
    </div>
</body>
</html>
"""

# 13 TECHNICAL SLIDES
# Focus: Operations, Engineering, Disaster Recovery
# Cookbook de-emphasized to brief reference
# Last slide: Resources & Contact Info
SLIDES = [
    # -------------------------------------------------------------
    # SLIDE 1: INTRO (PC MIGRATION OVERVIEW)
    # -------------------------------------------------------------
    {
        "part": "PART 1: PC MIGRATOR",
        "category": "SUITE OVERVIEW • WINDOWS PC APP",
        "title": "JRFK 64-Bit Appliance Builder & Migrator",
        "subtitle": "Standalone PC utility to create a 64-bit Raspberry Pi OS card with RFK & Web Tools",
        "image": "migrator_step1_discovery.png",
        "caption": "MIGRATOR RUNNING ON PC: CREATES 64-BIT TRIXIE OS WITH RFK CONTROLLER & WEB TOOLS",
        "narration": "Thirty-two-bit Raspberry Pi O S is obsolete, leaving R F kit amplifier owners at risk from unmaintained kernels and S D card failures. On screen is the J R F K Migrator running on your Windows P C. Its purpose is to prepare a complete sixty-four-bit Raspberry Pi operating system containing all original R F kit calibrations, user data, and the J R F K Web Tools suite for your amplifier. Over the next four slides, we look at the P C migration process, and then we will explore each of the on-amplifier web tools."
    },
    # -------------------------------------------------------------
    # SLIDE 2: MIGRATOR OPTION A (GOLD TO PROD)
    # -------------------------------------------------------------
    {
        "part": "PART 1: PC MIGRATOR",
        "category": "BUILD OPTION A • GOLDEN MASTER MIGRATION",
        "title": "Migrator Option A: Gold to Production",
        "subtitle": "Extracts 100% of calibration.json, ADC offsets & Wi-Fi from your existing working card",
        "image": "migrator_optA_gold_to_prod.png",
        "caption": "OPTION A: EXTRACTS 100% OF CALIBRATIONS FROM WORKING AMPLIFIER CARD, THEN WRITES 64-BIT OS",
        "narration": "Examining the primary migration path, Option A: Gold to Production. Look at the upper selector tile on screen. In this mode, you take your existing working S D card from the amplifier and plug it into a U S B reader on your P C. The tool reads your card in read-only safety mode, extracting one hundred percent of your calibration files, directional coupler offsets, and station settings. Once extracted, you remove your original card and insert a new card, which the tool flashes with the complete sixty-four-bit Debian Trixie system."
    },
    # -------------------------------------------------------------
    # SLIDE 3: MIGRATOR OPTION B (NEW TO PROD / CLEAN INSTALL)
    # -------------------------------------------------------------
    {
        "part": "PART 1: PC MIGRATOR",
        "category": "BUILD OPTION B • CLEAN PRODUCTION INSTALL",
        "title": "Migrator Option B: Clean Install to Production",
        "subtitle": "Builds a fresh 64-bit card with user credentials, station Wi-Fi, and default profiles",
        "image": "migrator_optB_new_to_prod.png",
        "caption": "OPTION B: CONFIGURES NEW SYSTEM CREDENTIALS, WI-FI SSID, AND PARTITIONS FRESH 64-BIT SD CARD",
        "narration": "Now look at Option B on screen: Clean Install to Production. This option is used when you are starting fresh with a brand new card or building a spare backup without reading an original card first. On this screen, you directly configure your Raspberry Pi username, system password, hostname, and station Wi-Fi credentials. The tool formats the new target card, installs sixty-four-bit Debian Trixie, and provisions the native R F kit controller alongside the J R F K Web Tools suite."
    },
    # -------------------------------------------------------------
    # SLIDE 4: MIGRATOR CALIBRATION EXTRACTION DETAILS
    # -------------------------------------------------------------
    {
        "part": "PART 1: PC MIGRATOR",
        "category": "CALIBRATION RECOVERY • ADC OFFSET PRESERVATION",
        "title": "PC Migrator: Directional Coupler & ADC Calibration",
        "subtitle": "Raw ext4 inspection of factory forward/reflected power tables and relay timing",
        "image": "report_calibrations.png",
        "caption": "CALIBRATION ARCHIVE: ADC POWER MATRICES, ATTENUATOR STEPS, AND RELAY TIMING CONSTANTS",
        "narration": "This screen shows the exact calibration data recovered by the P C migrator from your original card. Listed here are the factory directional coupler forward and reflected power A D C lookup tables, attenuator step values, and P T T relay timings. The migrator transfers these exact matrices into the new sixty-four-bit operating system, ensuring that your amplifier retains its factory RF metering precision."
    },
    # -------------------------------------------------------------
    # SLIDE 5: AMPLIFIER TWO-BOOT DEPLOYMENT
    # -------------------------------------------------------------
    {
        "part": "PART 1: PC MIGRATOR",
        "category": "DEPLOYMENT COMPLETE • AMPLIFIER INITIALIZATION",
        "title": "Amplifier Deployment: Two-Boot Production Verification",
        "subtitle": "Boot 1: Automated partition expansion • Boot 2: Production service on Debian Trixie",
        "image": "tool4_report_hardware.png",
        "caption": "SYSTEM VERIFICATION: 64-BIT DEBIAN TRIXIE KERNEL 6.12 ACTIVE ON AMPLIFIER RASPBERRY PI",
        "narration": "Once flashing finishes on your P C, you insert the new card into your amplifier's Raspberry Pi four or five. On the first boot, automated scripts expand the Linux root partition to fill the full card and configure controller devices. On the second boot, your amplifier enters full production service running pure sixty-four-bit Debian Trixie with the native front panel app and all Web Tools active."
    },
    # -------------------------------------------------------------
    # SLIDE 6: WEB TOOLS INTRO: PORTAL OVERVIEW
    # -------------------------------------------------------------
    {
        "part": "PART 2: ON-AMPLIFIER WEB TOOLS",
        "category": "SUITE PORTAL • BROWSER-BASED MANAGEMENT",
        "title": "JRFK Web Tools: Unified Station Dashboard",
        "subtitle": "Concurrent remote management served directly by the amplifier on port 8088",
        "image": "intro_portal_overview.png",
        "caption": "BLUEPRINT PORTAL ON PORT 8088: ACCESS HEALTH, ANTENNA MATRIX, BACKUPS, LOGS & DOCS",
        "narration": "Now we move to the J R F K Web Tools running live on the amplifier. On screen is the master blueprint portal accessed via any browser on port eighty eighty-eight. It runs simultaneously alongside the native R F kit application using shared memory, giving you direct access to the Health Guard, Antenna Matrix, S D Backup Manager, System Diagnostics, Event Logs, and live Screen Streamer."
    },
    # -------------------------------------------------------------
    # SLIDE 7: WEB TOOL 1 - HEALTH RF METERS & THERMALS
    # -------------------------------------------------------------
    {
        "part": "PART 2: ON-AMPLIFIER WEB TOOLS",
        "category": "TOOL 1: HEALTH MONITOR • LIVE RF & THERMAL STATUS",
        "title": "Health Guard: Real-Time RF Telemetry & Safety Ceiling",
        "subtitle": "Forward power up to 1500 Watts P, E, P, reflected power, and 60°C thermal protection",
        "image": "slide_health_main.png",
        "caption": "HEALTH MONITOR: LIVE RF POWER METERS, 53.5V SUPPLY SHUNTS & 60°C THERMAL SAFETY TRIP",
        "narration": "Examining the Health and Thermal Guard on screen. At the top of the page, the thermal safety banner supervises the P A heatsink temperature against the sixty degree ceiling, unkeying the amplifier into standby if cooling limits are reached. Down below, the instruments display instantaneous forward power up to fifteen hundred Watts, P, E, P, reflected power in Watts, and the fifty-three point five volt D C power supply rail status."
    },
    # -------------------------------------------------------------
    # SLIDE 8: WEB TOOL 2 - ANTENNA MATRIX & TUNER BODE PLOT
    # -------------------------------------------------------------
    {
        "part": "PART 2: ON-AMPLIFIER WEB TOOLS",
        "category": "TOOL 2: ANTENNA MATRIX & ATU • RELAY SWITCHED MATCHING",
        "title": "Antenna Matrix & ATU: Auto Segment Tuning",
        "subtitle": "4-way band routing and B26-ATU switched relay/PIN diode matching network",
        "image": "slide_antenna_main.png",
        "caption": "ANTENNA & ATU MATRIX: 4-WAY SELECTION & B26-ATU SWITCHED COMPONENT TUNING BODE PLOT",
        "narration": "Looking at the Antenna Mapper and Tuner Matrix screen. At the top are the four antenna ports covering one sixty through six meters, which switch automatically via C A T control. Below is the B twenty-six A T U matching network. The R F kit tuner uses relay and P I N diode switching to engage discrete physical inductors and capacitors for each frequency segment. The Bode plot displays S W R across the band and lists the exact physical inductance in nanohenries and capacitance in picofarads selected for that segment."
    },
    # -------------------------------------------------------------
    # SLIDE 9: WEB TOOL 3 - SD BACKUP & DISASTER RECOVERY
    # -------------------------------------------------------------
    {
        "part": "PART 2: ON-AMPLIFIER WEB TOOLS",
        "category": "TOOL 3: SD BACKUP • DUAL-SD RECOVERY PIPELINE",
        "title": "SD Backup Manager: Automated Cloning & Recovery",
        "subtitle": "Three-minute background clone to secondary USB storage while operating",
        "image": "slide_backup_main.png",
        "caption": "SD DISASTER RECOVERY: LIVE CLONING PIPELINE TO SECONDARY STORAGE & SCHEDULER",
        "narration": "Examining the S D Backup and Disaster Recovery tool on screen. The top status panel verifies the active boot card, while the storage selector identifies connected U S B target drives. In under three minutes, this tool writes a complete, bootable clone of your operating system to secondary storage in the background while you remain on the air, keeping a verified standby card ready in case of media failure."
    },
    # -------------------------------------------------------------
    # SLIDE 10: WEB TOOL 4 - SYSTEM REPORT & ENGINEERING ARCHIVE
    # -------------------------------------------------------------
    {
        "part": "PART 2: ON-AMPLIFIER WEB TOOLS",
        "category": "TOOL 4: SYSTEM REPORT • ARCHIVE & HARDWARE",
        "title": "System Report: Complete Calibration Archive",
        "subtitle": "Firmware profile, storage utilization, and downloadable calibration archive",
        "image": "slide_report_main.png",
        "caption": "SYSTEM REPORT: HARDWARE PROFILE, STORAGE UTILIZATION, AND CALIBRATION DATA EXPORT",
        "narration": "On screen is the Complete System Report and Calibration Archive. The upper cards display station identity, operating system version, and storage utilization across the root and U S B partitions. Below, full hardware calibration tables can be reviewed on screen and downloaded as a single compressed archive for off-site backup."
    },
    # -------------------------------------------------------------
    # SLIDE 11: WEB TOOL 5 - DIAGNOSTIC LOG VIEWER
    # -------------------------------------------------------------
    {
        "part": "PART 2: ON-AMPLIFIER WEB TOOLS",
        "category": "TOOL 5: DIAGNOSTIC LOGS • CENTRAL EVENT TERMINAL",
        "title": "Diagnostic Logs: Centralized Event Terminal",
        "subtitle": "Live telemetry logs, GUI events, backup progress, and first-boot migration history",
        "image": "slide_logs_main.png",
        "caption": "DIAGNOSTIC LOGS: REAL-TIME EVENT STREAMING ACROSS SYSTEM SERVICES & CONTROLLER INTERFACES",
        "narration": "Here is the Centralized Diagnostic Log Viewer. On screen, the dropdown allows you to inspect the core R F kit G U I log, the rolling telemetry log, S D backup records, and first-boot migration automation output. System D daemon events and amplifier trip alerts are captured with exact millisecond timestamps for instant diagnosis."
    },
    # -------------------------------------------------------------
    # SLIDE 12: WEB TOOL 6 - REMOTE SCREEN VIEWER & REFERENCE
    # -------------------------------------------------------------
    {
        "part": "PART 2: ON-AMPLIFIER WEB TOOLS",
        "category": "TOOL 6: REMOTE SCREEN • LIVE CONSOLE MIRROR",
        "title": "Remote Screen Viewer: Live 1024x600 Display",
        "subtitle": "Real-time HTTP video mirror of the physical front panel LCD touch screen",
        "image": "slide_screen_main.png",
        "caption": "REMOTE SCREEN: DIRECT FRAMEBUFFER STREAM OF THE 7-INCH FRONT PANEL LCD DISPLAY",
        "narration": "On screen is the Remote Screen Viewer. This web tool grabs the physical X eleven framebuffer of the amplifier's seven-inch front panel display and mirrors it live over H T T P at ten twenty-four by six hundred resolution. You see the physical front panel display update in real time from any browser on your network. Technical documentation and schematics are also stored locally on the Pi for offline reference."
    },
    # -------------------------------------------------------------
    # SLIDE 13: RESOURCES & SUPPORT
    # -------------------------------------------------------------
    {
        "part": "PART 3: RESOURCES & SUPPORT",
        "category": "OPEN SOURCE & COMMUNITY • GETTING STARTED",
        "title": "Resources, Community Support & Project Links",
        "subtitle": "GitHub repository, releases, community group, and station contact info",
        "image": "slide_resources_main.png",
        "caption": "PROJECT RESOURCES: GITHUB REPOSITORY, STANDALONE EXECUTABLE, GROUPS.IO & CONTACT",
        "narration": "In summary, the J R F K Modernization Suite delivers rock-solid operations, comprehensive engineering supervision, and verified disaster recovery for R F kit amplifiers. All source code, pre-compiled Windows migrator executables, and technical releases are available on GitHub at github dot com slash jbirdlebough one slash J R F K Tools. For discussions and technical support, connect with the community on the R F kit groups dot I O reflector. Thank you from K seven B I T."
    }
]

async def generate_slides_and_audio():
    print(f"Starting generation for {len(SLIDES)} slides...")
    total_slides = len(SLIDES)
    
    for idx, s in enumerate(SLIDES):
        s["id"] = idx + 1

    # 1. Generate HTML slides (Zero bullets, full-bleed screen)
    for s in SLIDES:
        slide_id = s["id"]
        slide_num_str = f"{slide_id:02d}"
        
        img_rel_path = f"real_screenshots/{s['image']}"
        html_content = TEMPLATE_FULLSCREEN.replace("{{PART}}", s["part"])
        html_content = html_content.replace("{{CATEGORY}}", s["category"])
        html_content = html_content.replace("{{TITLE}}", s["title"])
        html_content = html_content.replace("{{SUBTITLE}}", s["subtitle"])
        html_content = html_content.replace("{{SLIDE_NUM}}", str(slide_id))
        html_content = html_content.replace("{{TOTAL_SLIDES}}", str(total_slides))
        html_content = html_content.replace("{{IMAGE_SRC}}", img_rel_path)
        html_content = html_content.replace("{{CAPTION}}", s["caption"])
            
        html_path = os.path.join(DECK_DIR, f"slide_{slide_num_str}.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"Wrote {html_path}")

    # 2. Render PNG screenshots with Playwright
    print("\nRendering Slide PNGs via Playwright...")
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1920, "height": 1080})
        
        for s in SLIDES:
            slide_num_str = f"{s['id']:02d}"
            html_file = os.path.abspath(os.path.join(DECK_DIR, f"slide_{slide_num_str}.html"))
            png_file = os.path.join(DECK_DIR, f"slide_{slide_num_str}.png")
            vsdc_png = os.path.join(VSDC_DIR, f"slide_{slide_num_str}.png")
            
            await page.goto(f"file:///{html_file.replace(os.sep, '/')}", wait_until="load")
            await page.wait_for_timeout(300)
            await page.screenshot(path=png_file)
            await page.screenshot(path=vsdc_png)
            print(f"Rendered slide_{slide_num_str}.png")
            
        await browser.close()

    # 3. Generate Audio with edge-tts (Aussie Male William)
    print("\nGenerating Audio via edge-tts (en-AU-WilliamMultilingualNeural)...")
    voice = "en-AU-WilliamMultilingualNeural"
    
    timeline_entries = []
    current_time_ms = 0
    
    for s in SLIDES:
        slide_num_str = f"{s['id']:02d}"
        mp3_file = os.path.join(DECK_DIR, f"slide_{slide_num_str}.mp3")
        vsdc_mp3 = os.path.join(VSDC_DIR, f"slide_{slide_num_str}.mp3")
        
        raw_narration = s["narration"]
        cleaned_narration = clean_for_speech(raw_narration)
        
        comm = edge_tts.Communicate(cleaned_narration, voice)
        await comm.save(mp3_file)
        
        with open(mp3_file, "rb") as f_in, open(vsdc_mp3, "wb") as f_out:
            f_out.write(f_in.read())
            
        audio = mutagen.mp3.MP3(mp3_file)
        duration_sec = audio.info.length
        duration_ms = int(duration_sec * 1000)
        
        start_time_sec = current_time_ms / 1000.0
        end_time_sec = (current_time_ms + duration_ms) / 1000.0
        
        timeline_entries.append({
            "slide": s["id"],
            "title": s["title"],
            "duration_sec": duration_sec,
            "start_time_sec": start_time_sec,
            "end_time_sec": end_time_sec,
            "narration": raw_narration,
            "cleaned": cleaned_narration
        })
        
        current_time_ms += duration_ms + 1000
        print(f"Generated slide_{slide_num_str}.mp3 ({duration_sec:.2f}s)")

    # 4. Generate Responsive Auto-Advancing Presentation Player (preview.html)
    print("\nGenerating Responsive Auto-Advancing Presentation Player (preview.html)...")
    
    slides_json = []
    for e in timeline_entries:
        s_num = f"{e['slide']:02d}"
        slides_json.append({
            "id": e["slide"],
            "num": s_num,
            "title": e["title"],
            "img": f"slide_{s_num}.png",
            "audio": f"slide_{s_num}.mp3",
            "duration": e["duration_sec"],
            "narration": e["narration"]
        })
    
    import json
    slides_json_str = json.dumps(slides_json, indent=2)

    player_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>JRFK Modernization Suite - Auto-Advancing Technical Player - K7BIT</title>
<style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    html, body {{
        width: 100vw;
        height: 100vh;
        overflow: hidden;
        background: #091a2e;
        color: #ffffff;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        display: flex;
        flex-direction: column;
    }}
    .player-header {{
        height: 44px;
        background: #0f2d4f;
        border-bottom: 2px solid #38bdf8;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 16px;
        flex-shrink: 0;
    }}
    .player-title {{ font-size: 15px; font-weight: 800; color: #38bdf8; display: flex; align-items: center; gap: 8px; }}
    .player-callsign {{
        background: #0284c7;
        color: white;
        padding: 2px 10px;
        border-radius: 4px;
        font-family: monospace;
        font-weight: bold;
        font-size: 12px;
    }}
    .player-main {{
        flex: 1 1 auto;
        min-height: 0;
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 4px 8px;
        background: #061524;
        overflow: hidden;
    }}
    .slide-viewport {{
        width: 100%;
        height: 100%;
        display: flex;
        justify-content: center;
        align-items: center;
        overflow: hidden;
    }}
    .slide-img {{
        max-width: 100%;
        max-height: 100%;
        width: auto;
        height: auto;
        object-fit: contain;
        border-radius: 4px;
        box-shadow: 0 6px 25px rgba(0,0,0,0.8);
        border: 2px solid #1e3a5f;
    }}
    .player-footer {{
        height: 64px;
        background: #0f2d4f;
        border-top: 2px solid #38bdf8;
        display: flex;
        flex-direction: column;
        justify-content: center;
        gap: 4px;
        padding: 4px 16px;
        flex-shrink: 0;
    }}
    .controls-row {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 12px;
    }}
    .btn-group {{ display: flex; gap: 8px; align-items: center; }}
    .btn {{
        background: #0284c7;
        color: white;
        border: 1px solid #38bdf8;
        padding: 5px 12px;
        border-radius: 4px;
        font-weight: 700;
        cursor: pointer;
        font-size: 12px;
        transition: background 0.2s;
    }}
    .btn:hover {{ background: #0369a1; }}
    .btn:disabled {{ opacity: 0.4; cursor: not-allowed; }}
    .btn-play {{ background: #059669; border-color: #34d399; font-size: 13px; padding: 5px 18px; }}
    .btn-play:hover {{ background: #047857; }}
    .slide-indicator {{
        font-family: monospace;
        font-size: 13px;
        font-weight: bold;
        color: #7dd3fc;
    }}
    .narration-display {{
        color: #e0f2fe;
        font-size: 12px;
        line-height: 1.3;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        flex: 1;
        max-width: 850px;
        background: rgba(6, 21, 36, 0.7);
        padding: 3px 8px;
        border-radius: 4px;
        border-left: 3px solid #38bdf8;
    }}
    .progress-bar-container {{
        width: 100%;
        height: 4px;
        background: #1e3a5f;
        border-radius: 2px;
        overflow: hidden;
        cursor: pointer;
    }}
    .progress-bar {{
        height: 100%;
        width: 0%;
        background: #38bdf8;
        transition: width 0.1s linear;
    }}
</style>
</head>
<body>
    <div class="player-header">
        <div class="player-title">
            <span>JRFK 64-Bit Modernization Suite • Technical Presentation Player</span>
            <span class="player-callsign">K7BIT</span>
        </div>
        <div class="slide-indicator" id="slideIndicator">Slide 1 of {total_slides}</div>
    </div>

    <div class="player-main">
        <div class="slide-viewport">
            <img id="currentSlideImg" class="slide-img" src="slide_01.png" alt="Current Slide">
        </div>
    </div>

    <div class="player-footer">
        <div class="progress-bar-container" id="progressBarContainer">
            <div class="progress-bar" id="progressBar"></div>
        </div>
        <div class="controls-row">
            <div class="btn-group">
                <button class="btn" id="btnPrev">◀ Previous</button>
                <button class="btn btn-play" id="btnPlayPause">▶ Play</button>
                <button class="btn" id="btnNext">Next ▶</button>
                <button class="btn" id="btnRestart">↺ Restart</button>
            </div>
            <div class="narration-display" id="narrationText">Loading presentation...</div>
            <audio id="slideAudio" preload="auto"></audio>
        </div>
    </div>

    <script>
        const slides = {slides_json_str};
        let currentIndex = 0;
        let isPlaying = false;

        const audio = document.getElementById('slideAudio');
        const img = document.getElementById('currentSlideImg');
        const indicator = document.getElementById('slideIndicator');
        const narration = document.getElementById('narrationText');
        const btnPlayPause = document.getElementById('btnPlayPause');
        const btnPrev = document.getElementById('btnPrev');
        const btnNext = document.getElementById('btnNext');
        const btnRestart = document.getElementById('btnRestart');
        const progressBar = document.getElementById('progressBar');

        function loadSlide(index, autoPlay = false) {{
            if (index < 0) index = 0;
            if (index >= slides.length) index = slides.length - 1;
            currentIndex = index;

            const s = slides[currentIndex];
            img.src = s.img;
            audio.src = s.audio;
            indicator.textContent = `Slide ${{s.id}} of ${{slides.length}}: ${{s.title}}`;
            narration.textContent = s.narration;
            progressBar.style.width = '0%';

            btnPrev.disabled = (currentIndex === 0);
            btnNext.disabled = (currentIndex === slides.length - 1);

            if (autoPlay) {{
                audio.play().then(() => {{
                    isPlaying = true;
                    btnPlayPause.textContent = '❚❚ Pause';
                    btnPlayPause.style.background = '#d97706';
                }}).catch(e => console.log('Autoplay deferred:', e));
            }} else {{
                isPlaying = false;
                btnPlayPause.textContent = '▶ Play';
                btnPlayPause.style.background = '#059669';
            }}
        }}

        audio.addEventListener('ended', () => {{
            if (currentIndex < slides.length - 1) {{
                setTimeout(() => {{
                    loadSlide(currentIndex + 1, true);
                }}, 600);
            }} else {{
                isPlaying = false;
                btnPlayPause.textContent = '▶ Play';
                btnPlayPause.style.background = '#059669';
            }}
        }});

        audio.addEventListener('timeupdate', () => {{
            if (audio.duration) {{
                const pct = (audio.currentTime / audio.duration) * 100;
                progressBar.style.width = pct + '%';
            }}
        }});

        btnPlayPause.addEventListener('click', () => {{
            if (isPlaying) {{
                audio.pause();
                isPlaying = false;
                btnPlayPause.textContent = '▶ Resume';
                btnPlayPause.style.background = '#059669';
            }} else {{
                audio.play();
                isPlaying = true;
                btnPlayPause.textContent = '❚❚ Pause';
                btnPlayPause.style.background = '#d97706';
            }}
        }});

        btnPrev.addEventListener('click', () => {{
            if (currentIndex > 0) loadSlide(currentIndex - 1, isPlaying);
        }});

        btnNext.addEventListener('click', () => {{
            if (currentIndex < slides.length - 1) loadSlide(currentIndex + 1, isPlaying);
        }});

        btnRestart.addEventListener('click', () => {{
            loadSlide(0, true);
        }});

        window.addEventListener('keydown', (e) => {{
            if (e.key === ' ' || e.code === 'Space') {{
                e.preventDefault();
                btnPlayPause.click();
            }} else if (e.key === 'ArrowRight') {{
                btnNext.click();
            }} else if (e.key === 'ArrowLeft') {{
                btnPrev.click();
            }}
        }});

        loadSlide(0, false);
    </script>
</body>
</html>"""

    with open(os.path.join(DECK_DIR, "preview.html"), "w", encoding="utf-8") as f:
        f.write(player_html)

    # 5. Generate Text Document with Transcript & Slide Markers
    print("\nGenerating Presentation Transcript Document (PRESENTATION_TRANSCRIPT.md)...")
    transcript_md = "# JRFK 64-Bit Modernization Suite: Audio Transcript & Slide Synchronization\n\n"
    transcript_md += f"**Voice Model:** Australian English Male (`en-AU-WilliamMultilingualNeural`)\n"
    transcript_md += f"**Callsign:** K7BIT\n"
    transcript_md += f"**Total Slides:** {len(SLIDES)}\n\n"
    transcript_md += "---\n\n"
    
    for e in timeline_entries:
        s_num = f"{e['slide']:02d}"
        transcript_md += f"## [SLIDE {e['slide']:02d}: {e['title'].upper()}]\n"
        transcript_md += f"**File:** `slide_{s_num}.png` | **Audio:** `slide_{s_num}.mp3` ({e['duration_sec']:.2f}s) | **Timestamp:** {e['start_time_sec']:.2f}s - {e['end_time_sec']:.2f}s\n\n"
        transcript_md += f"> \"{e['narration']}\"\n\n"
        transcript_md += "---\n\n"

    with open(os.path.join(DECK_DIR, "PRESENTATION_TRANSCRIPT.md"), "w", encoding="utf-8") as f:
        f.write(transcript_md)

    with open(os.path.join(DECK_DIR, "VSDC_TIMELINE_MAP.md"), "w", encoding="utf-8") as f:
        f.write(transcript_md)

    print(f"\nALL {len(SLIDES)} SLIDES, AUDIO, PLAYER & TRANSCRIPT GENERATED SUCCESSFULLY!")

if __name__ == "__main__":
    asyncio.run(generate_slides_and_audio())
