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
        height: 42px;
        border-bottom: 2px solid #93c5fd;
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: rgba(26, 86, 149, 0.96);
        padding: 0 10px;
        flex-shrink: 0;
    }
    .header-left {
        display: flex;
        align-items: baseline;
        gap: 10px;
        overflow: hidden;
        white-space: nowrap;
        flex: 1;
        min-width: 0;
    }
    .header-tagline {
        font-family: "Consolas", monospace;
        font-size: 11px;
        letter-spacing: 1.2px;
        color: #93c5fd;
        text-transform: uppercase;
        font-weight: 700;
        white-space: nowrap;
        flex-shrink: 0;
    }
    .header-title {
        font-size: 18px;
        font-weight: 800;
        letter-spacing: -0.3px;
        color: #ffffff;
        text-shadow: 0 2px 6px rgba(0, 0, 0, 0.6);
        white-space: nowrap;
        flex-shrink: 0;
    }
    .header-subtitle {
        font-size: 12px;
        color: #bfdbfe;
        font-weight: 500;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .header-right {
        display: flex;
        gap: 8px;
        align-items: center;
        font-family: "Consolas", monospace;
        font-size: 11.5px;
        color: #ffffff;
        letter-spacing: 1px;
        font-weight: bold;
        flex-shrink: 0;
    }
    .badge-callsign {
        background: #0284c7;
        padding: 2px 7px;
        border-radius: 4px;
        border: 1px solid #93c5fd;
    }
    .badge-slide {
        background: rgba(15, 45, 85, 0.95);
        padding: 2px 7px;
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
        position: relative;
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
        height: 22px;
        border-top: 1px solid #93c5fd;
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-family: "Consolas", monospace;
        font-size: 10.5px;
        color: #bfdbfe;
        background: rgba(26, 86, 149, 0.96);
        padding: 0 10px;
        flex-shrink: 0;
    }
    .footer-left { color: #93c5fd; font-weight: 700; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 80%; }
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
            <img id="mainSlideImg" src="{{IMAGE_SRC}}" alt="{{TITLE}}" {{IMG_EXTRA_STYLE}}>
        </div>
    </div>
    <div class="master-footer">
        <div class="footer-left">{{CAPTION}}</div>
        <div class="footer-right">JRFK 64-BIT MODERNIZATION SUITE • K7BIT</div>
    </div>
    {{EXTRA_SCRIPT}}
</body>
</html>
"""

# EXACT 14 TECHNICAL SLIDES
# Remote Screen added directly behind Health Monitor
# Strictly Raspberry Pi OS (zero Debian references)
# Field/object names used for visual controls (no K7BIT overuse)
# PEP pronounced Peak Envelope Power
# Backup takes 15 minutes + scheduled cron updates/upgrades/backups
# Zero schematics references
# Row scrolling on Slides 4, 9, 11
SLIDES = [
    # -------------------------------------------------------------
    # SLIDE 1: INTRO (PC MIGRATION OVERVIEW & JRFK.EXE WINDOW)
    # -------------------------------------------------------------
    {
        "part": "PART 1: ARCHITECTURE",
        "category": "SUITE OVERVIEW • WINDOWS PC APP",
        "title": "Modernizing the RF-KIT Linear Amplifier",
        "subtitle": "The 64-Bit Leap: Standalone PC Migrator & On-Amplifier Web Tools Suite",
        "image": "slide_jrfk_exe_window.png",
        "caption": "JRFK MODERNIZATION SUITE: STANDALONE PC MIGRATOR WITH DRIVE GUARD & ON-AMPLIFIER WEB TOOLS",
        "scroll": False,
        "narration": "Thirty-two-bit Raspberry Pi O S is obsolete, leaving R F kit amplifier owners at risk from unmaintained kernels and S D card failures. On screen is the J R F K dot E X E modernization suite running on your Windows P C. It launches as a standalone elevated executable that manages Drive Guard protection and local web services. Over the first four slides, we examine why upgrading to sixty-four-bit Raspberry Pi O S is essential, and then beginning on slide five, we dive into the P C migration process, followed by the on-amplifier web tools."
    },
    # -------------------------------------------------------------
    # SLIDE 2: WHY 32-BIT MUST GO (VULNERABILITIES & RISKS)
    # -------------------------------------------------------------
    {
        "part": "PART 1: ARCHITECTURE",
        "category": "OBSOLESCENCE AUDIT • 32-BIT RISKS",
        "title": "Why Legacy 32-Bit Raspberry Pi OS Must Go",
        "subtitle": "End-of-life kernel maintenance, flash storage vulnerabilities, and amplifier protection risks",
        "image": "slide_02_32bit_risks.png",
        "caption": "LEGACY VULNERABILITIES: FROZEN SECURITY REPOSITORIES, UNBUFFERED MEDIA CORRUPTION & SOCKET DRIFT",
        "scroll": False,
        "narration": "Examining why the legacy thirty-two-bit operating system must be retired. Upstream Raspberry Pi O S has completely deprecated thirty-two-bit builds, freezing security fixes and controller patches. Furthermore, unbuffered S D card operations leave your station vulnerable to permanent file corruption during dirty shutdowns or power drops. Socket starvation on the controller interface introduces latency, and the legacy stack cannot run modern concurrent telemetry daemons."
    },
    # -------------------------------------------------------------
    # SLIDE 3: 64-BIT MODERNIZATION ARCHITECTURE & BENEFITS
    # -------------------------------------------------------------
    {
        "part": "PART 1: ARCHITECTURE",
        "category": "MODERN PLATFORM • 64-BIT TECHNICAL PAYOFF",
        "title": "64-Bit Modernization Architecture & Benefits",
        "subtitle": "64-Bit Raspberry Pi OS kernel, Full KMS direct rendering, and dual-service pipeline",
        "image": "slide_03_64bit_arch.png",
        "caption": "64-BIT ADVANTAGES: MODERN RASPBERRY PI OS KERNEL, FULL KMS DISPLAY, AND CONCURRENT WEB DAEMON",
        "scroll": False,
        "narration": "Now looking at the sixty-four-bit architecture payoff. By moving to pure sixty-four-bit Raspberry Pi O S on kernel six point twelve, your amplifier gains modern sixty-four-bit memory addressing and long-term security maintenance. Hardware-accelerated Full K M S direct rendering eliminates touch latency and coordinate drift on the front panel L C D. At the same time, high-priority Simple R P C communications run on dev rfk controller with zero socket warnings, enabling concurrent web daemons."
    },
    # -------------------------------------------------------------
    # SLIDE 4: SYSTEM DIAGNOSTICS & CALIBRATION MATRIX (SCROLLING)
    # -------------------------------------------------------------
    {
        "part": "PART 1: ARCHITECTURE",
        "category": "SYSTEM REPORT • CALIBRATION ARCHIVE",
        "title": "System Diagnostics: Calibration Archive & ATU Matrix",
        "subtitle": "Full ext4 audit: forward/reflected power nulls, 1500W scaling factor, and 11-band ATU presets",
        "image": "report_full_scroll.png",
        "caption": "SYSTEM CALIBRATION REPORT: SCROLLING FROM STATION PROFILE DOWN THROUGH FULL 11-BAND ATU MATRIX",
        "scroll": True,
        "max_scroll": 380,
        "narration": "Examining the complete System Report and Calibration Archive. Starting across the top row, the Station Identity panel displays the station callsign, operating system version, and C A T decoding link to the transceiver. Beside it, the Storage Utilization card tracks root partition capacity and A2 high-endurance wear-leveling health. Scrolling down to the middle row, the RF Detector Calibration card lists the factory forward and reflected null voltages, power scaling calibrated to fifteen hundred Watts Peak Envelope Power, and the fifty-ohm bridge balance, while the Shack Network card confirms the IP address and full KMS ten twenty-four by six hundred display modeline. Scrolling down to the end of the report, the ATU Band Segments table maps all eleven amateur bands from one sixty through six meters, showing assigned antenna ports, segment counts, and the exact discrete physical inductance in nanohenries and capacitance in picofarads engaged by the switched relays."
    },
    # -------------------------------------------------------------
    # SLIDE 5: MIGRATION STARTS - OPTION A (GOLD TO PROD)
    # -------------------------------------------------------------
    {
        "part": "PART 2: PC MIGRATOR",
        "category": "OPTION A • GOLDEN MASTER EXTRACTION",
        "title": "Migrator Option A: Gold to Production",
        "subtitle": "Extracts 100% of calibration.json, ADC offsets & Wi-Fi from your existing working card",
        "image": "migrator_optA_gold_to_prod.png",
        "caption": "OPTION A: EXTRACTS 100% OF CALIBRATIONS FROM WORKING AMPLIFIER CARD, THEN WRITES 64-BIT RPI OS",
        "scroll": False,
        "narration": "Slide five marks the start of the migration process. Examining the primary migration path, Option A: Gold to Production. Look at the upper selector tile on screen. In this mode, you take your existing working S D card from the amplifier and plug it into a U S B reader on your P C. The tool reads your card in read-only safety mode, extracting one hundred percent of your calibration files, directional coupler offsets, and station settings. Once extracted, you remove your original card and insert a new card, which the tool flashes with the complete sixty-four-bit Raspberry Pi O S system."
    },
    # -------------------------------------------------------------
    # SLIDE 6: MIGRATOR OPTION B (CLEAN PRODUCTION INSTALL)
    # -------------------------------------------------------------
    {
        "part": "PART 2: PC MIGRATOR",
        "category": "OPTION B • CLEAN PRODUCTION INSTALL",
        "title": "Migrator Option B: Clean Install to Production",
        "subtitle": "Builds a fresh 64-bit card with user credentials, station Wi-Fi, and default profiles",
        "image": "migrator_optB_new_to_prod.png",
        "caption": "OPTION B: CONFIGURES NEW SYSTEM CREDENTIALS, WI-FI SSID, AND PARTITIONS FRESH 64-BIT SD CARD",
        "scroll": False,
        "narration": "Now look at Option B on screen: Clean Install to Production. This option is used when you are starting fresh with a brand new card or building a spare backup without reading an original card first. On this screen, you directly configure your Raspberry Pi username, system password, hostname, and station Wi-Fi credentials. The tool formats the new target card, installs sixty-four-bit Raspberry Pi O S, and provisions the native R F kit controller alongside the J R F K Web Tools suite."
    },
    # -------------------------------------------------------------
    # SLIDE 7: TWO-BOOT PRODUCTION VERIFICATION PROCESS
    # -------------------------------------------------------------
    {
        "part": "PART 2: PC MIGRATOR",
        "category": "DEPLOYMENT • AMPLIFIER INITIALIZATION",
        "title": "Two-Boot Production Verification Process",
        "subtitle": "Automated partition expansion on Boot 1 followed by production launch on Boot 2",
        "image": "slide_two_boot_process.png",
        "caption": "TWO-BOOT VERIFICATION: FIRST INITIALIZATION EXPANDS PARTITIONS; SECOND BOOT ENTERS PRODUCTION",
        "scroll": False,
        "narration": "Once flashing finishes on your P C, you insert the new card into your amplifier's Raspberry Pi four or five. Look at the two-boot verification process on screen. On Boot One, automated scripts detect the hardware, expand the Linux root partition to fill the full media capacity, apply the native full KMS display timings for the front panel, and execute an automated soft reboot in under twenty seconds. On Boot Two, the amplifier performs a fast cold start in under twelve seconds, opens the Simple R P C controller link on dev rfk controller, reconnects to your station Wi-Fi, and brings all JRFK Web Tools live on port eighty eighty-eight."
    },
    # -------------------------------------------------------------
    # SLIDE 8: WEB TOOLS INTRO: UNIFIED STATION DASHBOARD
    # -------------------------------------------------------------
    {
        "part": "PART 3: WEB TOOLS",
        "category": "PORTAL OVERVIEW • PORT 8088",
        "title": "JRFK Web Tools: Unified Station Dashboard",
        "subtitle": "Concurrent remote management served directly by the amplifier on port 8088",
        "image": "intro_portal_overview.png",
        "caption": "STATION DASHBOARD ON PORT 8088: HEALTH GUARD, ANTENNA MATRIX, SD BACKUP, LOGS & DOCS",
        "scroll": False,
        "narration": "Now we move to the J R F K Web Tools running live on the amplifier. On screen is the master station dashboard accessed via any browser on port eighty eighty-eight. It runs simultaneously alongside the native R F kit application using shared memory, giving you direct access to the Health Guard, Antenna Matrix, S D Backup Manager, System Diagnostics, Event Logs, and live Screen Streamer."
    },
    # -------------------------------------------------------------
    # SLIDE 9: WEB TOOL 1 - HEALTH RF METERS & THERMALS (SCROLLING)
    # -------------------------------------------------------------
    {
        "part": "PART 3: WEB TOOLS",
        "category": "TOOL 1: HEALTH • RF & THERMAL GUARD",
        "title": "Health Guard: Real-Time RF Telemetry & Safety Ceiling",
        "subtitle": "Forward power up to 1500 Watts Peak Envelope Power, reflected power, and 60°C thermal protection",
        "image": "health_full_scroll.png",
        "caption": "HEALTH MONITOR: LIVE RF POWER METERS, 53.5V SUPPLY SHUNTS & 60°C THERMAL SAFETY TRIP",
        "scroll": True,
        "max_scroll": 320,
        "narration": "Examining the Health and Thermal Guard on screen. Starting at the top of the page, the thermal safety banner supervises the P A heatsink temperature against the sixty degree ceiling, unkeying the amplifier into standby if cooling limits are reached. Scrolling down into the instrument cluster, the meters display instantaneous forward power up to fifteen hundred Watts Peak Envelope Power and reflected power in Watts. Scrolling further down to the electrical status panel, the instruments monitor the fifty-three point five volt D C power supply rail and L-D moss current consumption in real time."
    },
    # -------------------------------------------------------------
    # SLIDE 10: WEB TOOL 2 - REMOTE SCREEN VIEWER (BEHIND HEALTH MONITOR)
    # -------------------------------------------------------------
    {
        "part": "PART 3: WEB TOOLS",
        "category": "TOOL 2: REMOTE CONSOLE • LIVE LCD MIRROR",
        "title": "Remote Screen Viewer: Live 1024x600 Display",
        "subtitle": "Real-time HTTP video mirror of the physical front panel LCD touch screen",
        "image": "web_screen_viewer.png",
        "caption": "REMOTE SCREEN: DIRECT FRAMEBUFFER STREAM OF THE 7-INCH FRONT PANEL LCD DISPLAY",
        "scroll": False,
        "narration": "Directly behind the Health Monitor, look at the Remote Screen Viewer on screen. This tool grabs the physical framebuffer of the amplifier's seven-inch front panel display and mirrors it live over H T T P at ten twenty-four by six hundred resolution. You see the physical front panel touchscreen update in real time from any browser across your station network, allowing complete remote control without sitting in front of the amplifier."
    },
    # -------------------------------------------------------------
    # SLIDE 11: WEB TOOL 3 - ANTENNA MATRIX & TUNER BODE PLOT (SCROLLING)
    # -------------------------------------------------------------
    {
        "part": "PART 3: WEB TOOLS",
        "category": "TOOL 3: ANTENNA MATRIX & B26-ATU",
        "title": "Antenna Matrix & ATU: Auto Segment Tuning",
        "subtitle": "4-way band routing and B26-ATU switched relay/PIN diode matching network",
        "image": "antenna_full_scroll.png",
        "caption": "ANTENNA & ATU MATRIX: 4-WAY SELECTION & B26-ATU SWITCHED COMPONENT TUNING BODE PLOT",
        "scroll": True,
        "max_scroll": 460,
        "narration": "Looking at the Antenna Mapper and Tuner Matrix screen. Across the top are the four antenna ports covering one sixty through six meters, which switch automatically via C A T control. Scrolling down into the B twenty-six A T U matching network, the R F kit tuner uses relay and P I N diode switching to engage discrete physical inductors and capacitors for each frequency segment. Down below, the Bode plot displays S W R across the band and lists the exact physical inductance in nanohenries and capacitance in picofarads selected for that segment."
    },
    # -------------------------------------------------------------
    # SLIDE 12: WEB TOOL 4 - SD BACKUP & DISASTER RECOVERY
    # -------------------------------------------------------------
    {
        "part": "PART 3: WEB TOOLS",
        "category": "TOOL 4: SD BACKUP • RECOVERY PIPELINE",
        "title": "SD Backup Manager: Automated Media Cloning & Cron",
        "subtitle": "USB SD reader setup, 15-minute background clone, and scheduled maintenance cron",
        "image": "slide_backup_main.png",
        "caption": "SD DISASTER RECOVERY: USB CARD CLONING IN 15 MINUTES WITH SCHEDULED AUTO-MAINTENANCE CRON",
        "scroll": False,
        "narration": "Examining the S D Backup and Disaster Recovery tool on screen. To establish disaster recovery, you simply plug a standard U S B S D card reader with a spare card into an available Raspberry Pi U S B port on the amplifier. When initiated, the tool performs a complete block-level clone in approximately fifteen minutes while you continue operating on the air. In addition, an automated cron job runs in the background on schedule to perform system updates, software upgrades, and automated standby backups, ensuring a highly available amplifier that never suffers unrecoverable media failure."
    },
    # -------------------------------------------------------------
    # SLIDE 13: WEB TOOL 5 - DIAGNOSTIC LOG VIEWER
    # -------------------------------------------------------------
    {
        "part": "PART 3: WEB TOOLS",
        "category": "TOOL 5: DIAGNOSTICS • EVENT LOGS",
        "title": "Diagnostic Logs: Centralized Event Terminal",
        "subtitle": "Real-time event streaming across system services, controller interfaces & trip alerts",
        "image": "slide_logs_main.png",
        "caption": "CENTRAL LOG TERMINAL: MONITORS CONTROLLER EVENTS, DAEMONS & FAULT TRIPS WITH TIMESTAMPS",
        "scroll": False,
        "narration": "Here is the Centralized Diagnostic Log Viewer. On screen, the dropdown allows you to inspect the core R F kit G U I log, the rolling telemetry log, S D backup records, and first-boot migration history with millisecond timestamps. Fault alerts and trip triggers are logged with exact system time, while technical documentation and operating manuals are stored locally for instant offline reference."
    },
    # -------------------------------------------------------------
    # SLIDE 14: RESOURCES, SUPPORT & LIABILITY DISCLAIMER
    # -------------------------------------------------------------
    {
        "part": "PART 4: RESOURCES",
        "category": "OPEN SOURCE & COMMUNITY • GETTING STARTED",
        "title": "Resources, Community Support & Project Links",
        "subtitle": "GitHub repository, releases, community group, and station contact info",
        "image": "slide_resources_main.png",
        "caption": "PROJECT RESOURCES: GITHUB REPOSITORY, STANDALONE EXECUTABLE, GROUPS.IO & 73's K7BIT",
        "scroll": False,
        "narration": "In summary, the J R F K Modernization Suite delivers rock-solid operations, comprehensive engineering supervision, and verified disaster recovery for R F kit amplifiers. All source code, pre-compiled Windows migrator executables, and technical releases are available on GitHub at github dot com slash jbirdlebough one slash J R F K Tools. For discussions and technical support, connect with the community on the R F kit groups dot I O reflector. Please note the experimental research disclaimer: all software is provided as-is with all risks accepted by the user. Seventy-three's K seven B I T."
    }
]

async def generate_slides_and_audio():
    print(f"Starting generation for {len(SLIDES)} slides...")
    total_slides = len(SLIDES)
    
    for idx, s in enumerate(SLIDES):
        s["id"] = idx + 1

    # 1. Generate HTML slides
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
        
        # If slide supports vertical scroll
        if s.get("scroll"):
            max_scroll = s.get("max_scroll", 360)
            html_content = html_content.replace("{{IMG_EXTRA_STYLE}}", 'style="width: 100%; height: auto; position: absolute; top: 0; left: 0; object-fit: fill; transition: transform 0.1s linear;"')
            extra_script = f"""<script>
            window.addEventListener('message', (e) => {{
                if (e.data && e.data.type === 'scroll') {{
                    const norm = e.data.norm;
                    const maxScroll = {max_scroll};
                    let scrollY = 0;
                    if (norm <= 0.16) {{
                        scrollY = 0;
                    }} else if (norm >= 0.88) {{
                        scrollY = maxScroll;
                    }} else {{
                        scrollY = ((norm - 0.16) / (0.88 - 0.16)) * maxScroll;
                    }}
                    const img = document.getElementById('mainSlideImg');
                    if (img) img.style.transform = `translateY(-${{scrollY}}px)`;
                }}
            }});
            </script>"""
            html_content = html_content.replace("{{EXTRA_SCRIPT}}", extra_script)
        else:
            html_content = html_content.replace("{{IMG_EXTRA_STYLE}}", '')
            html_content = html_content.replace("{{EXTRA_SCRIPT}}", '')
            
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
        s_obj = SLIDES[e['slide'] - 1]
        slides_json.append({
            "id": e["slide"],
            "num": s_num,
            "title": e["title"],
            "img": f"slide_{s_num}.png",
            "html": f"slide_{s_num}.html",
            "audio": f"slide_{s_num}.mp3",
            "duration": e["duration_sec"],
            "scroll": s_obj.get("scroll", False),
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
        background: #0c2340;
        border-bottom: 2px solid #38bdf8;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 16px;
        flex-shrink: 0;
    }}
    .player-title {{
        font-weight: 800;
        font-size: 14px;
        color: #e0f2fe;
        display: flex;
        align-items: center;
        gap: 10px;
    }}
    .player-callsign {{
        background: #0284c7;
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        font-family: monospace;
        font-size: 12px;
        font-weight: bold;
    }}
    .player-main {{
        flex: 1 1 auto;
        min-height: 0;
        width: 100%;
        display: flex;
        justify-content: center;
        align-items: center;
        background: #000000;
        padding: 4px;
        overflow: hidden;
    }}
    .slide-viewport {{
        width: 100%;
        height: 100%;
        display: flex;
        justify-content: center;
        align-items: center;
        position: relative;
    }}
    .slide-img {{
        width: 100%;
        height: 100%;
        object-fit: contain;
        display: block;
    }}
    .slide-iframe {{
        width: 100%;
        height: 100%;
        border: none;
        display: none;
    }}
    .player-footer {{
        height: 60px;
        background: #0c2340;
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
            <iframe id="slideIframe" class="slide-iframe" src="about:blank"></iframe>
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
        const iframe = document.getElementById('slideIframe');
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
            audio.src = s.audio;
            indicator.textContent = `Slide ${{s.id}} of ${{slides.length}}: ${{s.title}}`;
            narration.textContent = s.narration;
            progressBar.style.width = '0%';

            btnPrev.disabled = (currentIndex === 0);
            btnNext.disabled = (currentIndex === slides.length - 1);

            // Use interactive iframe for smooth vertical scrolling on slides with scroll: true
            if (s.scroll) {{
                img.style.display = 'none';
                iframe.style.display = 'block';
                iframe.src = s.html;
            }} else {{
                iframe.style.display = 'none';
                img.style.display = 'block';
                img.src = s.img;
            }}

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
                const norm = audio.currentTime / audio.duration;
                progressBar.style.width = (norm * 100) + '%';
                
                // Communicate scroll progress to iframe
                if (slides[currentIndex].scroll && iframe.contentWindow) {{
                    iframe.contentWindow.postMessage({{ type: 'scroll', norm: norm }}, '*');
                }}
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
