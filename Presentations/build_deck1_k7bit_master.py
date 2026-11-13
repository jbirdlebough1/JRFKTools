import os
import sys
import asyncio
import mutagen.mp3
import edge_tts
from playwright.async_api import async_playwright

sys.path.insert(0, r"D:\JRFK\Presentations")
from pronunciation_rules import clean_for_speech

DECK_DIR = r"D:\JRFK\Presentations\Deck_1_Intro"
VSDC_DIR = os.path.join(DECK_DIR, "vsdc_media")
SCREENSHOTS_DIR = os.path.join(DECK_DIR, "real_screenshots")

# 13 Master Slides presenting JRFK Modernization Suite with real 8088 / migrator screenshots
# Explicit station callsign: K7BIT (never John, never "the station")
# Authentic Ham Radio RF engineering concepts with Feynman explanation style
SLIDES = [
    {
        "id": 1,
        "part": "PART 1/4",
        "category": "THE JRFK MIGRATION SUITE • 64-BIT ARCHITECTURE",
        "title": "THE JRFK SUITE: MODERNIZING RF CONTROLLERS",
        "subtitle": "Engineering Pure 64-Bit Debian Bookworm Systems for High-Power Amateur Radio Amplifiers",
        "narrative": "Welcome to Part 1 of our technical overview from station K7BIT. When you are managing fifteen hundred watts peak envelope power across one hundred sixty meters through six meters, the controller supervising your R F deck, low-pass relays, and protection sequencing must be completely deterministic. In this briefing, we examine the technical requirement for migrating from legacy thirty-two-bit operating systems to the pure sixty-four-bit Debian Bookworm architecture provided by the JRFK suite.",
        "image": "jrfk_migrator.png",
        "caption": "FIG 1: JRFK STANDALONE MIGRATOR & 64-BIT CONTROLLER PLATFORM",
        "bullets": [
            ("The Embedded Controller Role", "The internal Raspberry Pi manages PTT sequencing, low-pass filter relays, touch display metering, and SimpleRPC communications."),
            ("High-Power Determinism", "Switching 1500W PEP on 160m through 6m requires microsecond determinism and rock-solid controller stability."),
            ("Station Operating Note (K7BIT)", "A deterministic controller is the foundation of amplifier safety—delay or lockup risks devastating LDMOS transistors during keying.")
        ]
    },
    {
        "id": 2,
        "part": "PART 1/4",
        "category": "THE JRFK MIGRATION SUITE • DEPRECATION ANALYSIS",
        "title": "WHY 32-BIT MUST GO: SOFTWARE END-OF-LIFE",
        "subtitle": "Software End-of-Life, Frozen Repositories, and Network Deprecation Risks",
        "narrative": "Let's look at why migration is necessary. The original thirty-two-bit operating system has reached official end-of-life. Upstream package repositories are frozen, and deprecated Python socket implementations prevent the controller from running modern network protocols or security patches. Without upgrading, the amplifier controller becomes an isolated legacy device unable to communicate reliably with modern station automation at K7BIT.",
        "image": "screen_system_report.png",
        "caption": "FIG 2: JRFK 8088 SYSTEM REPORT - KERNEL, SYSTEMD & HARDWARE DIAGNOSTICS",
        "bullets": [
            ("Frozen Upstream Repositories", "Debian and Raspbian 32-bit suites are frozen; critical security and kernel patches are no longer provided."),
            ("Python Socket Deprecation", "Legacy Python 2 and early Python 3 socket models fail on modern TLS/SSL networks and modern RPC layers."),
            ("Station Operating Note (K7BIT)", "An amplifier controller unable to update becomes an unmaintainable technical island in a modern networked shack.")
        ]
    },
    {
        "id": 3,
        "part": "PART 1/4",
        "category": "THE JRFK MIGRATION SUITE • RF STABILITY",
        "title": "WHY 32-BIT MUST GO: DISPLAY DRIVERS & RF LOCKS",
        "subtitle": "User-Space Drivers, Memory Leaks, and High-RF Framebuffer Lockups",
        "narrative": "The second critical driver for migration is display architecture. Legacy thirty-two-bit installations relied on user-space fake-KMS and older X eleven graphics layers. In the presence of strong R F fields during legal-limit keying, memory fragmentation in these user-space drivers frequently caused touchscreen freezes and display blanking. Upgrading to sixty-four-bit Full KMS DRM places the ten twenty-four by six hundred display modelines directly inside the Linux kernel, ensuring rock-solid display stability.",
        "image": "screen_screen_viewer.png",
        "caption": "FIG 3: JRFK 8088 SCREEN VIEWER - LIVE FRAMEBUFFER TELEMETRY STREAM",
        "bullets": [
            ("User-Space Fragility", "Fake-KMS and legacy X11 drivers suffer memory leaks under continuous RF telemetry updates."),
            ("RF Immune Kernel DRM", "Full KMS DRM moves framebuffer timing into kernel space, eliminating display driver lockups during keying."),
            ("Station Operating Note (K7BIT)", "A frozen display leaves the operator blind to VSWR, drain current, and heatsink temperature during high-power operation.")
        ]
    },
    {
        "id": 4,
        "part": "PART 1/4",
        "category": "THE JRFK MIGRATION SUITE • 64-BIT ARCHITECTURE",
        "title": "64-BIT ARCHITECTURE OVERVIEW: TECHNICAL PAYOFF",
        "subtitle": "Memory Protection, Non-Blocking Telemetry, and Native Systemd Daemons",
        "narrative": "The sixty-four-bit architecture delivers an immediate technical payoff. Debian Bookworm provides sixty-four-bit memory protection, modern Linux kernel stability, and a fully non-blocking Simple R P C telemetry loop. Fragile legacy startup scripts are replaced with native system D service units, ensuring that all controller daemons automatically recover in the event of an unexpected fault.",
        "image": "screen_health_monitor.png",
        "caption": "FIG 4: JRFK 8088 HEALTH MONITOR - 64-BIT SYSTEM TELEMETRY & HARDWARE METRICS",
        "bullets": [
            ("Full 64-Bit Memory Protection", "Eliminates address-space fragmentation and prevents daemon crash cascades under heavy I/O loads."),
            ("Non-Blocking SimpleRPC Engine", "Real-time telemetry runs asynchronously, decoupling GUI responsiveness from hardware polling."),
            ("Station Operating Note (K7BIT)", "Native systemd service watchdogs supervise all daemons, guaranteeing automatic self-recovery without operator intervention.")
        ]
    },
    {
        "id": 5,
        "part": "PART 2/4",
        "category": "THE JRFK MIGRATION SUITE • TOOL 1: MIGRATOR",
        "title": "TOOL 1: JRFK STANDALONE MIGRATOR ARCHITECTURE",
        "subtitle": "Zero-Dependency Windows Executable with Native Administrative Launch Guard",
        "narrative": "Now let's examine the first major component of the JRFK suite: the Standalone Migrator. Distributed as a single one hundred sixty-six megabyte Windows executable, J R F K dot E X E requires zero developer tools or Python dependencies. It incorporates a dedicated C sharp launcher that handles administrative elevation, suppresses disruptive Windows 11 format prompts on raw media, and enforces strict physical drive guard locks to prevent accidental drive overwrites.",
        "image": "jrfk_migrator.png",
        "caption": "FIG 5: JRFK.EXE MIGRATOR INTERFACE - PHYSICAL DRIVE GUARD & IMAGE PROVISIONING",
        "bullets": [
            ("Self-Contained Executable", "Pre-packaged with embedded Python runtime, frontend assets, and provisioning scripts in a single 166MB binary."),
            ("Windows 11 Raw Disk Protection", "Active background thread intercepts and suppresses disruptive Windows format disk prompts on raw Linux partitions."),
            ("Station Operating Note (K7BIT)", "Drive Guard strictly filters out system drives, thumbdrives, and network shares to prevent tragic media overwrites.")
        ]
    },
    {
        "id": 6,
        "part": "PART 2/4",
        "category": "THE JRFK MIGRATION SUITE • TOOL 1: MIGRATOR",
        "title": "TOOL 1 IN ACTION: DISCOVERY, FLASHING & CALIBRATION",
        "subtitle": "Automated Network Controller Discovery and Zero-Loss Calibration Restoration",
        "narrative": "In operation, the migrator automates the entire provisioning workflow. It scans your local network to discover the amplifier controller, flashes the verified sixty-four-bit Bookworm base image, injects native ten twenty-four by six hundred display modelines, and extracts your amplifier's unique band tables and S W R calibration offsets from your old S D card so no factory calibration is lost.",
        "image": "screen_backup_manager.png",
        "caption": "FIG 6: JRFK 8088 BACKUP MANAGER - CALIBRATION EXTRACTION & VERIFICATION",
        "bullets": [
            ("Subnet Discovery Engine", "Broadcasts and ARP sweeps detect the controller IP automatically across local Ethernet or Wi-Fi."),
            ("Golden Calibration Preservation", "Mounts raw ext4 partitions to safely pull band tables, ADC offsets, and coupler calibrations before writing."),
            ("Station Operating Note (K7BIT)", "Factory calibration offsets are irreplaceable—the JRFK migrator guarantees zero data loss during modernization.")
        ]
    },
    {
        "id": 7,
        "part": "PART 3/4",
        "category": "THE JRFK MIGRATION SUITE • TOOL 2: 7-SCREEN WEB SUITE",
        "title": "TOOL 2: 7-SCREEN WEB SUITE — RF TELEMETRY & BANDS",
        "subtitle": "Port 8088 Web Operations Cockpit: Low-Pass Filtering and Forward/Reflected Power",
        "narrative": "The second major tool in the suite is the seven-screen operational web cockpit running permanently on port eighty eighty-eight. This tool decouples live operation from P C maintenance. Screen 1 gives you real-time forward peak envelope power, reflected power, and S W R metering from any browser at K7BIT, while Screen 2 provides automatic low-pass filter band switching synchronized to your transceiver via C A T control with active hot-switch prevention.",
        "image": "screen_health_monitor.png",
        "caption": "FIG 7: JRFK 8088 SCREEN 1 - REAL-TIME RF POWER, SWR & LOW-PASS FILTER METRICS",
        "bullets": [
            ("Zero-Install Web Architecture", "Full operational cockpit accessible from any browser on PC, tablet, or smartphone on port 8088."),
            ("CAT Synchronized Band Switching", "Low-pass relays track transceiver VFO frequency instantly with hardware hot-switching interlocks."),
            ("Station Operating Note (K7BIT)", "Directional couplers sample forward and reflected waves directly, rendering precision analog meters in real-time.")
        ]
    },
    {
        "id": 8,
        "part": "PART 3/4",
        "category": "THE JRFK MIGRATION SUITE • TOOL 2: 7-SCREEN WEB SUITE",
        "title": "TOOL 2: PA MONITORING & 4-WAY ANTENNA MATRIX",
        "subtitle": "53.5V Discrete Shunt Telemetry, Dual LDMOS Thermals, and Band-Mapped Relays",
        "narrative": "Screens 3 and 4 handle R F deck health and antenna routing. Screen 3 monitors the fifty-three point five volt D C rail, drain current, and heatsink thermals across the dual Ampleon B L F one eighty-nine L D M O S transistors. Note that the system uses discrete analog shunts rather than C A N bus power supplies, ensuring noise-free D C telemetry. Screen 4 manages a four-way antenna matrix that automatically recalls your selected antenna port for each band.",
        "image": "screen_antenna_mapper.png",
        "caption": "FIG 8: JRFK 8088 SCREEN 4 - 4-WAY ANTENNA MATRIX & PER-BAND ROUTING CONFIGURATOR",
        "bullets": [
            ("Discrete Shunt Current Telemetry", "Avoids digital switching noise by sampling drain current directly across calibrated analog current shunts."),
            ("Dual BLF189 LDMOS Supervision", "Monitors thermal dissipation and balancing across both final amplification stages simultaneously."),
            ("Station Operating Note (K7BIT)", "Antenna mapping eliminates manual coaxial patching—switching bands automatically selects the resonant antenna array.")
        ]
    },
    {
        "id": 9,
        "part": "PART 3/4",
        "category": "THE JRFK MIGRATION SUITE • TOOL 2: 7-SCREEN WEB SUITE",
        "title": "TOOL 2: PROTECTION SYSTEMS, LOGS & TOUCH CALIBRATION",
        "subtitle": "Hardware Protection Interlocks, Event Logging, and 5-Point Coordinate Alignment",
        "narrative": "Screens 5, 6, and 7 deliver comprehensive protection and maintenance. Screen 5 enforces hardware protection limits, clamping drive and dropping into standby within microseconds if S W R exceeds two point five to one or heatsink temperature reaches sixty degrees. Screens 6 and 7 provide real-time controller event logs and a built-in five-point touchscreen calibration utility.",
        "image": "screen_log_viewer.png",
        "caption": "FIG 9: JRFK 8088 SCREEN 6 - REAL-TIME CONTROLLER EVENT LOG & FAULT MONITOR",
        "bullets": [
            ("Microsecond Hardware Trips", "Clamps exciter RF drive and disengages bias if VSWR exceeds 2.5:1 or heatsink temperature reaches 60°C."),
            ("Persistent System Event Logs", "Records high-power trips, band switches, and relay actuations for post-contest diagnostics."),
            ("Station Operating Note (K7BIT)", "A 5-point touch calibration utility ensures accurate fingertip alignment on resistive 7-inch LCD displays.")
        ]
    },
    {
        "id": 10,
        "part": "PART 4/4",
        "category": "THE JRFK MIGRATION SUITE • TOOL 3: DISASTER RECOVERY",
        "title": "TOOL 3: THE 3-MINUTE DISASTER RECOVERY STANDBY CARD",
        "subtitle": "Pre-Cloned Boot Media Strategy for High-Stakes Contest and Field Operations",
        "narrative": "Tool 3 is the Disaster Recovery Engine. During the migration workflow, J R F K provisions an identical secondary S D card containing the complete sixty-four-bit operating system and all current calibration offsets. If an S D card ever suffers hardware failure during contest operations, the operator simply inserts the standby card and powers up, returning K7BIT to full operation in under three minutes.",
        "image": "screen_backup_manager.png",
        "caption": "FIG 10: JRFK 8088 DISASTER RECOVERY - STANDBY MEDIA CLONING & PARTITION AUDIT",
        "bullets": [
            ("Zero-Downtime Resilience", "Dual-card provisioning creates a verified, ready-to-run clone of the operating system and calibration."),
            ("Field Swap Procedure", "Power down, swap the micro-SD card behind the front bezel, and boot directly into service."),
            ("Station Operating Note (K7BIT)", "Contest hours are irreplaceable—having a verified standby card guarantees station availability when it matters most.")
        ]
    },
    {
        "id": 11,
        "part": "PART 4/4",
        "category": "THE JRFK MIGRATION SUITE • TOOL 3: DISASTER RECOVERY",
        "title": "TOOL 3: FIRST-BOOT AUTOMATION & SELF-HEALING SERVICES",
        "subtitle": "Partition Expansion, Modeline Injection, and Systemd Hardware Watchdogs",
        "narrative": "Supporting disaster recovery is our first-boot automation framework. Upon initial startup, the setup script expands the Linux root partition to fill the S D card, applies network configurations, and enables system D service watchdogs. These watchdogs actively supervise all background daemons, automatically restarting them without operator intervention if an abnormal state occurs.",
        "image": "screen_health_manager.png",
        "caption": "FIG 11: JRFK 8088 HEALTH MANAGER - SYSTEMD DAEMON SUPERVISION & AUTO-RECOVERY",
        "bullets": [
            ("Root Partition Expansion", "Automatically resizes ext4 file system to utilize full capacity of 16GB, 32GB, or 64GB micro-SD cards."),
            ("Kernel Watchdog Supervision", "Hardware timer trips controller reset if kernel stalls, preventing unmonitored RF amplification states."),
            ("Station Operating Note (K7BIT)", "Autonomous service self-healing ensures background telemetry daemons restart instantly after transient brownouts.")
        ]
    },
    {
        "id": 12,
        "part": "PART 4/4",
        "category": "THE JRFK MIGRATION SUITE • TOOL 4: ENGINEERING LIBRARY",
        "title": "TOOL 4: MASTER ENGINEERING LIBRARY & COOKBOOK READER",
        "subtitle": "4-Volume Engineering Library and K7BIT's Authentic 193-Page B26 Cookbook",
        "narrative": "Tool 4 is the Master Documentation Portal. The portal hosts our complete four-volume engineering library covering station operation, remote telemetry, and architecture. Furthermore, K seven B I T's authentic one hundred ninety-three page B twenty-six cookbook is integrated directly into the portal, providing operators and builders with instant, searchable access to original schematics and wiring diagrams from any browser.",
        "image": "screen_docs_viewer.png",
        "caption": "FIG 12: JRFK 8088 DOCS VIEWER - K7BIT 193-PAGE B26 COOKBOOK & SCHEMATICS PORTAL",
        "bullets": [
            ("Offline Shack Reference", "Full 4-volume technical documentation served locally on port 8088 without internet connectivity."),
            ("K7BIT B26 Master Cookbook", "Complete 193-page technical reference with searchable schematics, PCB layouts, and calibration procedures."),
            ("Station Operating Note (K7BIT)", "Integrated schematics and wire tables provide immediate on-screen guidance during hardware maintenance and testing.")
        ]
    },
    {
        "id": 13,
        "part": "PART 4/4",
        "category": "THE JRFK MIGRATION SUITE • SUMMARY & RESOURCES",
        "title": "SUMMARY & MASTER RESOURCE DIRECTORY",
        "subtitle": "64-Bit Modernization Ecosystem: Migrator, 7-Screen Cockpit, Recovery & Docs",
        "narrative": "In summary, the JRFK modernization suite delivers a complete sixty-four-bit transformation: automated migration, a seven-screen operational web cockpit, instant disaster recovery, and comprehensive technical documentation. All downloads, source code, and community discussions are accessible at the links displayed on your screen. Thank you for watching, and seventy-three from K seven B I T.",
        "image": "screen_system_report.png",
        "caption": "FIG 13: JRFK SUITE - MASTER ENGINEERING SPECIFICATIONS & REPOSITORY LINKS",
        "bullets": [
            ("The Complete Modernization Suite", "JRFK.exe Standalone Migrator + 7-Screen Web Suite on 8088 + 3-Min Disaster Recovery + Engineering Library."),
            ("Pure 64-Bit Debian Bookworm", "Rock-solid Full KMS display drivers, microsecond protection determinism, and autonomous self-healing daemons."),
            ("Station Operating Note (K7BIT)", "73 from K7BIT—engineering reliable, high-power amateur radio stations for modern contest and DX operations.")
        ]
    }
]

def generate_slide_html(slide):
    bullets_html = ""
    for title, desc in slide["bullets"]:
        bullets_html += f"""
        <div class="bullet-card">
            <div class="bullet-title">{title}</div>
            <div class="bullet-desc">{desc}</div>
        </div>
        """
        
    img_path = f"real_screenshots/{slide['image']}"
    
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
        width: 1920px;
        height: 1080px;
        background: #060d17;
        color: #e2e8f0;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        padding: 50px 70px;
        position: relative;
        overflow: hidden;
    }}
    body::before {{
        content: "";
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        background: 
            radial-gradient(circle at 15% 20%, rgba(14, 165, 233, 0.12) 0%, transparent 45%),
            radial-gradient(circle at 85% 80%, rgba(59, 130, 246, 0.08) 0%, transparent 45%),
            linear-gradient(to right, rgba(255,255,255,0.02) 1px, transparent 1px),
            linear-gradient(to bottom, rgba(255,255,255,0.02) 1px, transparent 1px);
        background-size: 100% 100%, 100% 100%, 60px 60px, 60px 60px;
        pointer-events: none;
    }}
    .header {{
        border-bottom: 2px solid rgba(56, 189, 248, 0.3);
        padding-bottom: 20px;
        display: flex;
        justify-content: space-between;
        align-items: flex-end;
        position: relative;
        z-index: 2;
    }}
    .header-left {{
        display: flex;
        flex-direction: column;
        gap: 6px;
    }}
    .tagline {{
        font-family: "Consolas", monospace;
        font-size: 14px;
        letter-spacing: 2.5px;
        color: #38bdf8;
        text-transform: uppercase;
        font-weight: 700;
    }}
    .title {{
        font-size: 38px;
        font-weight: 800;
        letter-spacing: -0.5px;
        color: #ffffff;
        text-shadow: 0 2px 10px rgba(0,0,0,0.5);
    }}
    .subtitle {{
        font-size: 18px;
        color: #94a3b8;
        font-weight: 400;
    }}
    .header-right {{
        text-align: right;
        font-family: "Consolas", monospace;
        font-size: 14px;
        color: #64748b;
        letter-spacing: 1.5px;
    }}
    .content-grid {{
        display: grid;
        grid-template-columns: 1.05fr 1fr;
        gap: 50px;
        align-items: center;
        margin: 30px 0;
        position: relative;
        z-index: 2;
        flex: 1;
    }}
    .cards-col {{
        display: flex;
        flex-direction: column;
        gap: 16px;
    }}
    .bullet-card {{
        background: rgba(15, 23, 42, 0.75);
        border: 1px solid rgba(56, 189, 248, 0.2);
        border-left: 4px solid #38bdf8;
        border-radius: 8px;
        padding: 18px 22px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    }}
    .bullet-title {{
        font-size: 19px;
        font-weight: 700;
        color: #f1f5f9;
        margin-bottom: 6px;
        display: flex;
        align-items: center;
        gap: 10px;
    }}
    .bullet-title::before {{
        content: "■";
        color: #38bdf8;
        font-size: 12px;
    }}
    .bullet-desc {{
        font-size: 15px;
        line-height: 1.5;
        color: #94a3b8;
    }}
    .image-col {{
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }}
    .image-frame {{
        background: #0f172a;
        padding: 10px;
        border-radius: 10px;
        border: 1px solid rgba(56, 189, 248, 0.3);
        box-shadow: 0 10px 40px rgba(0,0,0,0.6);
        max-width: 100%;
    }}
    .image-frame img {{
        max-width: 100%;
        max-height: 480px;
        border-radius: 6px;
        display: block;
        object-fit: contain;
    }}
    .image-caption {{
        margin-top: 14px;
        font-family: "Consolas", monospace;
        font-size: 13px;
        color: #38bdf8;
        letter-spacing: 1px;
        text-align: center;
    }}
    .footer {{
        border-top: 1px solid rgba(255,255,255,0.1);
        padding-top: 15px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-family: "Consolas", monospace;
        font-size: 13px;
        color: #64748b;
        position: relative;
        z-index: 2;
    }}
    .footer-left {{
        color: #38bdf8;
        font-weight: 600;
    }}
</style>
</head>
<body>
    <div class="header">
        <div class="header-left">
            <div class="tagline">{slide['part']} • {slide['category']}</div>
            <div class="title">{slide['title']}</div>
            <div class="subtitle">{slide['subtitle']}</div>
        </div>
        <div class="header-right">
            <div>STATION: K7BIT</div>
            <div>SLIDE {slide['id']:02d} OF 13</div>
        </div>
    </div>
    
    <div class="content-grid">
        <div class="cards-col">
            {bullets_html}
        </div>
        <div class="image-col">
            <div class="image-frame">
                <img src="{img_path}" alt="{slide['title']}">
            </div>
            <div class="image-caption">{slide['caption']}</div>
        </div>
    </div>
    
    <div class="footer">
        <div class="footer-left">JRFK 64-BIT MODERNIZATION SUITE • AMATEUR RADIO HIGH-POWER STATIONS (K7BIT)</div>
        <div class="footer-right">GITHUB.COM/BIRDIEBOUGHT/JRFKTOOLS</div>
    </div>
</body>
</html>
"""

async def build_all():
    print("=== REBUILDING DECK 1 WITH AUTHENTIC 8088 / MIGRATOR SCREENSHOTS & K7BIT CALLSIGN ===")
    
    # 1. Generate HTML slides
    for slide in SLIDES:
        html_path = os.path.join(DECK_DIR, f"slide_{slide['id']:02d}.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(generate_slide_html(slide))
        print(f"Generated HTML: {html_path}")
        
    # 2. Render 1080p PNGs using Playwright
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1920, "height": 1080})
        
        for slide in SLIDES:
            sid = slide['id']
            html_path = os.path.join(DECK_DIR, f"slide_{sid:02d}.html")
            png_deck = os.path.join(DECK_DIR, f"slide_{sid:02d}.png")
            png_vsdc = os.path.join(VSDC_DIR, f"slide_{sid:02d}.png")
            
            url = f"file:///{html_path.replace(os.sep, '/')}"
            await page.goto(url, wait_until="networkidle")
            await page.screenshot(path=png_deck)
            
            # Copy to vsdc_media
            with open(png_deck, "rb") as src, open(png_vsdc, "wb") as dst:
                dst.write(src.read())
            print(f"Rendered PNG: slide_{sid:02d}.png -> Deck & VSDC media")
            
        await browser.close()
        
    # 3. Generate Audio with clean pronunciation and K7BIT callsign
    voice = "en-US-ChristopherNeural"
    timing_map = []
    
    for slide in SLIDES:
        sid = slide['id']
        raw_text = slide['narrative']
        clean_text = clean_for_speech(raw_text)
        
        deck_mp3 = os.path.join(DECK_DIR, f"slide_{sid:02d}.mp3")
        vsdc_mp3 = os.path.join(VSDC_DIR, f"slide_{sid:02d}.mp3")
        
        print(f"Synthesizing Audio for Slide {sid:02d} ({voice})...")
        communicate = edge_tts.Communicate(clean_text, voice)
        await communicate.save(deck_mp3)
        
        try:
            with open(deck_mp3, "rb") as src, open(vsdc_mp3, "wb") as dst:
                dst.write(src.read())
        except Exception as e:
            print(f"Warning writing to vsdc_media: {e}")
            
        duration = mutagen.mp3.MP3(deck_mp3).info.length
        frames = round(duration * 30)
        timing_map.append((sid, slide['title'], duration, frames))
        
    print("\n=== COMPLETE DECK 1 TIMING REFERENCE (K7BIT) ===")
    total_sec = sum(t[2] for t in timing_map)
    m, s = divmod(total_sec, 60)
    print(f"Total Run Time: {int(m):02d}:{s:05.2f}")
    for sid, title, dur, fr in timing_map:
        print(f"Slide {sid:02d} | {dur:5.2f}s | {fr:4d} frames | {title}")

if __name__ == "__main__":
    asyncio.run(build_all())
