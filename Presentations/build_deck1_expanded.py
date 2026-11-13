"""
JRFK Presentation 1: Master 13-Slide Expanded Deck & Audio Suite
All files located in the SAME flat directory (D:\\JRFK\\Presentations\\Deck_1_Intro)
for direct VSDC / Slideshow sequence import.
Voice: en-US-ChristopherNeural (calm, articulate technical narrator).
Persona: Feynman intuitive physics/engineering style + authentic Ham Radio technical terminology.
Zero CB slang, zero social commentary.
Slide durations precisely equal to audio track lengths.
"""

import os
import sys
import asyncio
import subprocess
import edge_tts
from mutagen.mp3 import MP3

CHROME_BIN = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
BASE_DIR = r"D:\JRFK\Presentations"
DECK_DIR = os.path.join(BASE_DIR, "Deck_1_Intro")
COOKBOOK_MEDIA = r"D:\JRFK\docs\cookbook_media"
PI_SCREEN = r"D:\JRFK\Presentations\rfk_screen_capture_test.png"

VOICE = "en-US-ChristopherNeural"
RATE = "+0%"
PITCH = "+0Hz"

CSS_STYLE = """
:root {
    --bp-bg: #134679;
    --bp-grid: rgba(255, 255, 255, 0.12);
    --bp-line: #ffffff;
    --bp-line-dim: #cbd5e1;
    --bp-card: #0a2544;
    --bp-border: #60a5fa;
    --accent-green: #22c55e;
    --accent-cyan: #38bdf8;
    --accent-amber: #f59e0b;
}
* { box-sizing: border-box; }
body {
    margin: 0;
    padding: 24px 32px;
    width: 1280px;
    height: 720px;
    background-color: var(--bp-bg);
    background-image: 
        linear-gradient(var(--bp-grid) 1px, transparent 1px),
        linear-gradient(90deg, var(--bp-grid) 1px, transparent 1px);
    background-size: 20px 20px;
    color: var(--bp-line);
    font-family: 'Segoe UI', -apple-system, sans-serif;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    overflow: hidden;
}
.header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 2px solid var(--bp-border);
    padding-bottom: 8px;
}
.header-badge {
    background: #0f3460;
    color: var(--accent-cyan);
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    padding: 4px 10px;
    border: 1px solid var(--accent-cyan);
    border-radius: 4px;
}
.header-meta {
    font-size: 13px;
    color: var(--bp-line-dim);
    letter-spacing: 1px;
}
.title-row {
    margin-top: 8px;
}
.title-row h1 {
    font-size: 28px;
    margin: 0;
    font-weight: 800;
    letter-spacing: 0.5px;
    color: #ffffff;
    text-transform: uppercase;
}
.title-row .subtitle {
    font-size: 14px;
    color: var(--accent-cyan);
    margin-top: 3px;
    font-weight: 500;
}
.content {
    flex: 1;
    display: flex;
    gap: 20px;
    margin-top: 12px;
    align-items: stretch;
}
.col-text {
    flex: 1.25;
    display: flex;
    flex-direction: column;
    gap: 10px;
    justify-content: center;
}
.col-media {
    flex: 1;
    background: #06192e;
    border: 2px solid var(--bp-border);
    border-radius: 6px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    overflow: hidden;
    padding: 8px;
    position: relative;
}
.col-media img {
    max-width: 100%;
    max-height: 90%;
    object-fit: contain;
    border-radius: 4px;
}
.media-caption {
    font-size: 11px;
    color: var(--accent-cyan);
    margin-top: 6px;
    text-align: center;
    font-family: monospace;
}
.card {
    background: var(--bp-card);
    border-left: 4px solid var(--accent-cyan);
    padding: 9px 13px;
    border-radius: 0 6px 6px 0;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
}
.card-green {
    border-left-color: var(--accent-green);
}
.card-amber {
    border-left-color: var(--accent-amber);
}
.card-title {
    font-size: 14px;
    font-weight: 700;
    color: #ffffff;
    margin-bottom: 2px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.card-desc {
    font-size: 12.5px;
    color: var(--bp-line-dim);
    line-height: 1.35;
}
.station-note-box {
    background: rgba(15, 23, 42, 0.95);
    border-left: 4px solid var(--accent-amber);
    padding: 8px 12px;
    border-radius: 0 6px 6px 0;
    font-size: 12.5px;
    color: #fef08a;
    line-height: 1.35;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
}
.footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-top: 1px solid rgba(255, 255, 255, 0.2);
    padding-top: 6px;
    font-size: 11.5px;
    color: var(--bp-line-dim);
}
"""

SLIDES = [
    # ---------------- PART A: MIGRATION REQUIREMENT & 32-TO-64B OVERVIEW (4 SLIDES) ----------------
    {
        "id": "slide_01",
        "badge": "JRFK PRESENTATION 1 • PART 1/4",
        "meta": "THE MIGRATION REQUIREMENT • RF2K+ & B26 PLATFORMS",
        "title": "Modernizing the RF-KIT Linear Amplifier",
        "subtitle": "The Architectural Need for 64-Bit Operating Systems on High-Power RF Amplifiers",
        "media_path": os.path.join(COOKBOOK_MEDIA, "img_001.jpeg"),
        "caption": "FIG 1: RF-KIT RF2K+ 1500W PEP LINEAR AMPLIFIER PLATFORM",
        "cards": [
            ("The Embedded Controller Role", "The internal Raspberry Pi manages PTT sequencing, low-pass filter relays, touch display metering, and SimpleRPC communications.", "cyan"),
            ("High-Power RF Demands", "Switching 1500W PEP on 160m through 6m requires microsecond determinism and rock-solid controller stability.", "green"),
            ("Station Operating Note", "A stable controller is the foundation of amplifier safety—delay or lockup risks devastating LDMOS transistors during keying.", "amber", True)
        ],
        "narration": (
            "Welcome to Part 1 of our technical overview. When you are managing fifteen hundred watts PEP across 160 meters "
            "through 6 meters, the micro-controller supervising your RF deck, low-pass relays, and protection sequencing must be "
            "completely deterministic. In this briefing, we examine the technical requirement for migrating the RF-KIT platform "
            "from legacy 32-bit operating systems to pure 64-bit Debian Bookworm architecture."
        )
    },
    {
        "id": "slide_02",
        "badge": "JRFK PRESENTATION 1 • PART 2/4",
        "meta": "SOFTWARE ARCHITECTURE • END-OF-LIFE OS STACK",
        "title": "Why 32-Bit Must Go: Software End-of-Life",
        "subtitle": "Frozen Repositories, Deprecated Python Sockets & Security Dead-Ends",
        "media_path": os.path.join(COOKBOOK_MEDIA, "img_102.jpeg"),
        "caption": "FIG 2: LEGACY 32-BIT CONTROLLER & DEPRECATED SOCKET STACK",
        "cards": [
            ("Frozen Upstream Repositories", "Debian and Raspberry Pi OS have discontinued security and utility updates for legacy 32-bit releases.", "cyan"),
            ("Python Runtime Deprecations", "Legacy Python 2 and early Python 3 asynchronous socket implementations suffer protocol deprecations, blocking modern TLS and SSH.", "amber"),
            ("Station Automation Dead-End", "Old network stacks prevent seamless integration with modern shack automation, remote station controllers, and current web standards.", "green")
        ],
        "narration": (
            "Let's look at why migration is necessary. The original 32-bit operating system has reached official end-of-life. "
            "Upstream package repositories are frozen, and deprecated Python socket implementations prevent the controller from running "
            "modern network protocols or security patches. Without upgrading, the amplifier controller becomes an isolated legacy device "
            "unable to communicate reliably with modern station automation."
        )
    },
    {
        "id": "slide_03",
        "badge": "JRFK PRESENTATION 1 • PART 3/4",
        "meta": "DISPLAY DRIVER SUBSYSTEM • RF IMMUNITY",
        "title": "Why 32-Bit Must Go: Display Architecture & RF Locks",
        "subtitle": "Eliminating User-Space Fake-KMS Latency and Touchscreen Freezes",
        "media_path": os.path.join(COOKBOOK_MEDIA, "img_135.jpeg"),
        "caption": "FIG 3: FULL KMS DIRECT RENDERING MANAGER KERNEL TESTING",
        "cards": [
            ("Legacy Fake-KMS Bottlenecks", "Old 32-bit graphics ran through user-space fake-KMS and legacy X11 layers, creating high display latency and frame stutter.", "cyan"),
            ("RF-Induced Touch Freezes", "Under high circulating RF fields, memory fragmentation in the legacy display pipeline caused the touchscreen driver to lock up during transmission.", "amber"),
            ("Kernel-Level Full KMS DRM", "64-bit Debian Bookworm moves display modelines directly into the Linux kernel DRM subsystem, restoring complete touchscreen stability.", "green")
        ],
        "narration": (
            "The second critical driver for migration is display architecture. Legacy 32-bit installations relied on user-space "
            "fake-KMS and older X11 graphics layers. In the presence of strong RF fields during legal-limit keying, memory fragmentation "
            "in these user-space drivers frequently caused touchscreen freezes and display blanking. Upgrading to 64-bit Full KMS DRM "
            "places the 1024 by 600 display modelines directly inside the Linux kernel, ensuring rock-solid display stability."
        )
    },
    {
        "id": "slide_04",
        "badge": "JRFK PRESENTATION 1 • PART 4/4",
        "meta": "64-BIT TECHNICAL OVERVIEW • THE ARCHITECTURAL PAYOFF",
        "title": "64-Bit Architecture Overview: The Technical Payoff",
        "subtitle": "Debian Bookworm 64-Bit Kernel, SimpleRPC Non-Blocking Bus & Systemd Watchdogs",
        "media_path": os.path.join(COOKBOOK_MEDIA, "img_148.jpeg"),
        "caption": "FIG 4: MODERNISED 64-BIT SYSTEMD & ASYNCHRONOUS SIMPLERPC BUS",
        "cards": [
            ("64-Bit Memory Addressing", "Eliminates 32-bit memory boundaries, providing clean memory protection and long-term Linux kernel 6.x stability.", "green"),
            ("Non-Blocking SimpleRPC Engine", "Rebuilt asynchronous socket pipeline delivers sub-millisecond polling between the Raspberry Pi and the Arduino controller.", "cyan"),
            ("Supervised Systemd Daemons", "Native systemd unit files replace fragile background scripts, providing automatic process supervision and instant watchdog recovery.", "amber")
        ],
        "narration": (
            "The 64-bit architecture delivers an immediate technical payoff. Debian Bookworm provides 64-bit memory protection, "
            "modern Linux kernel stability, and a fully non-blocking SimpleRPC telemetry loop. Fragile legacy startup scripts are replaced "
            "with native systemd service units, ensuring that all controller daemons automatically recover in the event of an unexpected fault."
        )
    },

    # ---------------- PART B: TWO TO THREE SLIDES PER JRFK TOOL (8 SLIDES) ----------------
    # TOOL 1: JRFK STANDALONE MIGRATOR (2 SLIDES)
    {
        "id": "slide_05",
        "badge": "JRFK TOOL 1 • SLIDE 1/2",
        "meta": "TOOL 1: STANDALONE MIGRATION ENGINE (JRFK.EXE)",
        "title": "Tool 1: JRFK Standalone Migrator Architecture",
        "subtitle": "Zero-Dependency Windows Executable, Automated UAC & Physical Drive Guard",
        "media_path": os.path.join(COOKBOOK_MEDIA, "img_110.jpeg"),
        "caption": "FIG 5: JRFK STANDALONE WINDOWS MIGRATOR & ELEVATION ENGINE",
        "cards": [
            ("Zero-Dependency Windows App", "A self-contained 166MB executable (JRFK.exe) requiring no Python install, developer toolchains, or command line hassle.", "cyan"),
            ("Windows 11 Dialog Suppressor", "Integrated C# launcher automatically requests administrative rights and suppresses Windows 11 unformatted disk prompts.", "green"),
            ("Physical Drive Guard (sd_guard.py)", "Enforces strict raw physical drive isolation, preventing accidental writes to host hard drives or USB storage.", "amber")
        ],
        "narration": (
            "Now let's examine the first major component of the JRFK suite: the Standalone Migrator. Distributed as a single 166-megabyte "
            "Windows executable, JRFK.exe requires zero developer tools or Python dependencies. It incorporates a dedicated C-sharp launcher "
            "that handles administrative elevation, suppresses disruptive Windows 11 format prompts on raw media, and enforces strict "
            "physical drive guard locks to prevent accidental drive overwrites."
        )
    },
    {
        "id": "slide_06",
        "badge": "JRFK TOOL 1 • SLIDE 2/2",
        "meta": "TOOL 1: DISCOVERY & CALIBRATION MIGRATION",
        "title": "Tool 1 in Action: Discovery, Flashing & Calibration",
        "subtitle": "Network Subnet Scanning, Block-Level Imaging & Factory Calibration Preservation",
        "media_path": os.path.join(COOKBOOK_MEDIA, "img_126.jpeg"),
        "caption": "FIG 6: BLOCK-LEVEL FLASHING & SWR CALIBRATION EXTRACTION",
        "cards": [
            ("Subnet Discovery Protocol", "Scans local subnets via ARP and MAC tables to locate the amplifier controller without manual IP entry.", "cyan"),
            ("Verified Block-Level Imaging", "Flashes clean 64-bit Debian Bookworm images with SHA-256 integrity verification and automated partition alignment.", "green"),
            ("Preserving Amplifier Calibration", "Extracts existing band tables, SWR directional coupler offsets, and user configurations from the old 32-bit card and restores them into Bookworm.", "amber")
        ],
        "narration": (
            "In operation, the migrator automates the entire provisioning workflow. It scans your local network to discover the amplifier "
            "controller, flashes the verified 64-bit Bookworm base image, injects native 1024 by 600 display modelines, and extracts your "
            "amplifier's unique band tables and SWR calibration offsets from your old SD card so no factory calibration is lost."
        )
    },

    # TOOL 2: 7-SCREEN AMPLIFIER WEB COCKPIT (3 SLIDES)
    {
        "id": "slide_07",
        "badge": "JRFK TOOL 2 • SLIDE 1/3",
        "meta": "TOOL 2: 7-SCREEN COCKPIT • PORT 8088",
        "title": "Tool 2: 7-Screen Web Suite — RF Telemetry & Bands",
        "subtitle": "Port Decoupling, Real-Time Power Telemetry & Automated CAT Band Tracking",
        "media_path": PI_SCREEN,
        "caption": "FIG 7: 7-SCREEN COCKPIT — MAIN RF DASHBOARD & BAND MATRIX (PORT 8088)",
        "cards": [
            ("Strict Port Decoupling", "PC provisioning runs on port 8089; the permanent operational amplifier suite runs on port 8088 on the Raspberry Pi.", "cyan"),
            ("Screen 1: Main RF Dashboard", "Displays real-time forward PEP power, reflected power, and responsive SWR bar graphs accessible from any shack browser.", "green"),
            ("Screen 2: Band Switching Matrix", "Tracks transceiver frequency automatically via CAT and CI-V protocols, with active hardware lockout against hot-switching.", "amber")
        ],
        "narration": (
            "The second major tool in the suite is the 7-screen operational web cockpit running permanently on port 8088. This tool decouples "
            "live operation from PC maintenance. Screen 1 gives you real-time forward PEP, reflected power, and SWR metering from any browser "
            "in your shack, while Screen 2 provides automatic low-pass filter band switching synchronized to your transceiver via CAT control "
            "with active hot-switch prevention."
        )
    },
    {
        "id": "slide_08",
        "badge": "JRFK TOOL 2 • SLIDE 2/3",
        "meta": "TOOL 2: PA HEALTH & ANTENNAS",
        "title": "Tool 2: PA Monitoring & 4-Way Antenna Matrix",
        "subtitle": "LDMOS Voltage/Current Shunt Sensing and Non-Volatile Antenna Routing",
        "media_path": os.path.join(COOKBOOK_MEDIA, "img_055.jpeg"),
        "caption": "FIG 8: LDMOS VOLTAGE/CURRENT SHUNT SENSING & 4-WAY ANTENNA MATRIX",
        "cards": [
            ("Screen 3: LDMOS PA Telemetry", "Direct continuous monitoring of the 53.5V DC rail, total drain current, and heatsink thermal sensors across dual BLF189 transistors.", "green"),
            ("Discrete DC Sensing (No CAN Bus)", "Relies entirely on clean analog discrete shunts feeding controller ADCs, eliminating CAN bus communication failures.", "amber"),
            ("Screen 4: 4-Way Antenna Matrix", "Provides 4-port coaxial antenna routing with independent, non-volatile antenna memory for every amateur band.", "cyan")
        ],
        "narration": (
            "Screens 3 and 4 handle RF deck health and antenna routing. Screen 3 monitors the 53.5-volt DC rail, drain current, and heatsink "
            "thermals across the dual Ampleon BLF189 LDMOS transistors. Note that the RF-KIT uses discrete analog shunts rather than CAN bus "
            "power supplies, ensuring noise-free DC telemetry. Screen 4 manages a 4-way antenna matrix that automatically recalls your selected "
            "antenna port for each band."
        )
    },
    {
        "id": "slide_09",
        "badge": "JRFK TOOL 2 • SLIDE 3/3",
        "meta": "TOOL 2: PROTECTION & CALIBRATION",
        "title": "Tool 2: Protection Systems, Logs & Touch Calibration",
        "subtitle": "Microsecond Trip Hardware Comparators, Event Traces & 5-Point Calibration",
        "media_path": os.path.join(COOKBOOK_MEDIA, "img_049.jpeg"),
        "caption": "FIG 9: HARDWARE PROTECTION COMPARATORS & 5-POINT TOUCH CALIBRATION",
        "cards": [
            ("Screen 5: Multi-Stage Protection", "Hardware comparator trip curves execute in microseconds for SWR exceeding 2.5:1, input overdrive, and 60°C thermal thresholds.", "amber"),
            ("Screen 6: Real-Time Event Logging", "Continuous diagnostic trace of SimpleRPC bus messages, thermal history, and operating state transitions.", "cyan"),
            ("Screen 7: Touch Calibration", "Interactive 5-point touch alignment utility ensuring sub-millimeter precision for the physical front-panel display.", "green")
        ],
        "narration": (
            "Screens 5, 6, and 7 deliver comprehensive protection and maintenance. Screen 5 enforces hardware protection limits, clamping "
            "drive and dropping into standby within microseconds if SWR exceeds 2.5 to 1 or heatsink temperature reaches 60 degrees. "
            "Screens 6 and 7 provide real-time controller event logs and a built-in 5-point touchscreen calibration utility."
        )
    },

    # TOOL 3: DISASTER RECOVERY & AUTOMATION ENGINE (2 SLIDES)
    {
        "id": "slide_10",
        "badge": "JRFK TOOL 3 • SLIDE 1/2",
        "meta": "TOOL 3: REDUNDANCY & DISASTER RECOVERY",
        "title": "Tool 3: The 3-Minute Disaster Recovery Standby Card",
        "subtitle": "Pre-Provisioned Hot-Swap Backup SD Card for Zero Contest Downtime",
        "media_path": os.path.join(COOKBOOK_MEDIA, "img_002.png"),
        "caption": "FIG 10: HOT-SWAP DISASTER RECOVERY SD CARD COMPARTMENT",
        "cards": [
            ("Pre-Provisioned Standby Storage", "During initial migration, JRFK automatically provisions an identical secondary SD card containing your full 64-bit OS and calibration files.", "green"),
            ("Contest-Ready Hot-Swap Recovery", "In the event of an SD card failure during contest operations, swapping cards restores the amplifier to service in under 3 minutes.", "cyan"),
            ("Zero Shack Downtime", "Network addresses, touch calibration parameters, and band tables are pre-configured on the backup card with zero setup required.", "amber")
        ],
        "narration": (
            "Tool 3 is the Disaster Recovery Engine. During the migration workflow, JRFK provisions an identical secondary SD card containing "
            "the complete 64-bit operating system and all current calibration offsets. If an SD card ever suffers hardware failure during "
            "contest operations, the operator simply inserts the standby card and powers up, returning the station to full operation in "
            "under three minutes."
        )
    },
    {
        "id": "slide_11",
        "badge": "JRFK TOOL 3 • SLIDE 2/2",
        "meta": "TOOL 3: FIRST-BOOT AUTOMATION",
        "title": "Tool 3: First-Boot Automation & Self-Healing Services",
        "subtitle": "Automated Partition Expansion, Kernel Modeline Lock & Systemd Watchdogs",
        "media_path": os.path.join(COOKBOOK_MEDIA, "img_092.jpeg"),
        "caption": "FIG 11: AUTOMATED FIRST-BOOT SYSTEM EXPANSION & DAEMON SUPERVISION",
        "cards": [
            ("Automated First-Boot Setup", "Expands the Linux root filesystem to fill available card capacity, configures network interfaces, and sets host permissions automatically.", "cyan"),
            ("Systemd Service Watchdogs", "Supervises the RF-KIT GUI and SimpleRPC background daemons with automatic restart on abnormal exit.", "green"),
            ("Display Modeline Persistence", "Permanently injects custom kernel video modelines into /boot/firmware/cmdline.txt during initial partition expansion.", "amber")
        ],
        "narration": (
            "Supporting disaster recovery is our first-boot automation framework. Upon initial startup, the setup script expands the Linux "
            "root partition to fill the SD card, applies network configurations, and enables systemd service watchdogs. These watchdogs actively "
            "supervise all background daemons, automatically restarting them without operator intervention if an abnormal state occurs."
        )
    },

    # TOOL 4: MASTER ENGINEERING LIBRARY & COOKBOOK READER (1 SLIDE)
    {
        "id": "slide_12",
        "badge": "JRFK TOOL 4 • SLIDE 1/1",
        "meta": "TOOL 4: STATION DOCUMENTATION PORTAL",
        "title": "Tool 4: Master Engineering Library & Cookbook Reader",
        "subtitle": "Complete 4-Volume Engineering Library + Integrated John K7BIT 193-Page Manual",
        "media_path": os.path.join(COOKBOOK_MEDIA, "img_007.jpeg"),
        "caption": "FIG 12: MASTER DOCUMENTATION PORTAL & K7BIT COOKBOOK VIEWER",
        "cards": [
            ("Complete 4-Volume Station Library", "Includes the full Operations Manual, 7-Screen User Guide, Engineering Architecture Manual, and Disaster Recovery Card.", "green"),
            ("John K7BIT's Authentic Cookbook (Rev 1.05)", "The complete 193-page historical cookbook is fully indexed in the portal, providing direct access to original pallet schematics and wiring.", "cyan"),
            ("Responsive Web Reader", "Hosted on GitHub Pages for instant viewing across tablets, laptops, and smartphones with full search capability.", "amber")
        ],
        "narration": (
            "Tool 4 is the Master Documentation Portal. The portal hosts our complete 4-volume engineering library covering station operation, "
            "remote telemetry, and architecture. Furthermore, John K7BIT's authentic 193-page B26 cookbook is integrated directly into the "
            "portal, providing operators and builders with instant, searchable access to original schematics and wiring diagrams from any browser."
        )
    },

    # OUTRO / MASTER SUMMARY SLIDE (1 SLIDE)
    {
        "id": "slide_13",
        "badge": "JRFK PRESENTATION 1 • SUMMARY",
        "meta": "TURNKEY RESOURCES & REPOSITORIES",
        "title": "Summary & Master Resource Directory",
        "subtitle": "Complete Executable Downloads, Online Documentation & Community Support",
        "media_path": None,
        "is_outro": True,
        "cards": [],
        "narration": (
            "In summary, the JRFK modernization suite delivers a complete 64-bit transformation: automated migration, a 7-screen "
            "operational web cockpit, instant disaster recovery, and comprehensive technical documentation. All downloads, source code, "
            "and community discussions are accessible at the links displayed on your screen. Thank you for watching, and 73 from the station."
        )
    }
]

def render_slide_html(series_badge, meta_text, title, subtitle, content_html):
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
{CSS_STYLE}
</style>
</head>
<body>
    <div class="header">
        <div class="header-badge">{series_badge}</div>
        <div class="header-meta">{meta_text}</div>
    </div>
    <div class="title-row">
        <h1>{title}</h1>
        <div class="subtitle">{subtitle}</div>
    </div>
    <div class="content">
        {content_html}
    </div>
    <div class="footer">
        <div>JRFK 64-BIT STATION SUITE • AMATEUR RADIO HIGH-POWER LINEAR AMPLIFIERS</div>
        <div>GITHUB.COM/JBIRDLEBOUGH1/JRFKTOOLS</div>
    </div>
</body>
</html>"""

def get_outro_content():
    return """
    <div style="flex:1; display:flex; flex-direction:column; justify-content:center; gap:16px;">
        <div style="text-align:center; margin-bottom:8px;">
            <div style="font-size:24px; font-weight:800; color:#38bdf8; letter-spacing:1px; text-transform:uppercase;">
                Turnkey Resources & Community Links
            </div>
            <div style="font-size:14px; color:#cbd5e1; margin-top:4px;">
                Open-Source Tools, Engineering Documentation, and Ham Radio Community Support
            </div>
        </div>
        
        <div style="display:grid; grid-template-columns: 1fr 1fr; gap:14px;">
            <div class="card card-green">
                <div class="card-title">📦 JRFK Migration Executable (Windows)</div>
                <div class="card-desc">
                    <b>Direct Executable:</b> Standalone turnkey migrator with automated safety locks.<br>
                    <code style="color:#38bdf8;">github.com/jbirdlebough1/JRFKtools/releases</code>
                </div>
            </div>
            
            <div class="card">
                <div class="card-title">📖 Master Documentation Portal</div>
                <div class="card-desc">
                    <b>Live In-Browser Reader:</b> Complete 4-Volume manuals and K7BIT Cookbook.<br>
                    <code style="color:#38bdf8;">jbirdlebough1.github.io/JRFKtools/</code>
                </div>
            </div>
            
            <div class="card">
                <div class="card-title">💻 Full Source Repository</div>
                <div class="card-desc">
                    <b>Source Code & Scripts:</b> Migration server, first-boot scripts, and systemd units.<br>
                    <code style="color:#38bdf8;">github.com/jbirdlebough1/JRFKtools</code>
                </div>
            </div>
            
            <div class="card card-amber">
                <div class="card-title">📻 RF-KIT Community Discussion</div>
                <div class="card-desc">
                    <b>Operator Forum:</b> Technical exchange, mod sharing, and live operating support.<br>
                    <code style="color:#38bdf8;">groups.io/g/rf-kit</code>
                </div>
            </div>
        </div>
        
        <div class="station-note-box" style="text-align:center;">
            <b>Amateur Radio Station Notice:</b> All software and documentation are provided free and open-source for the amateur radio community. 73 and good DX!
        </div>
    </div>
    """

def capture_slide(html_path, output_png):
    file_url = "file:///" + os.path.abspath(html_path).replace(os.sep, "/")
    cmd = [
        CHROME_BIN,
        "--headless=new",
        "--disable-gpu",
        "--hide-scrollbars",
        "--window-size=1280,720",
        "--force-device-scale-factor=1",
        f"--screenshot={output_png}",
        file_url
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

async def generate_audio(text, output_mp3):
    comm = edge_tts.Communicate(text, voice=VOICE, rate=RATE, pitch=PITCH)
    await comm.save(output_mp3)

def format_time(seconds):
    mins = int(seconds // 60)
    secs = seconds % 60
    return f"{mins:02d}:{secs:05.2f}"

async def main():
    os.makedirs(DECK_DIR, exist_ok=True)
    print("==================================================================")
    print("Building Expanded 13-Slide Presentation 1 & Generating Audio Suite")
    print("Voice: en-US-ChristopherNeural | Rate: +0% | Output: Single Flat Folder")
    print("==================================================================")
    
    script_lines = ["# Presentation 1: Master 13-Slide Narration Script\n\n"]
    timeline_rows = []
    current_time = 0.0
    
    for idx, slide in enumerate(SLIDES, 1):
        slide_id = slide["id"]
        title = slide["title"]
        html_file = f"{slide_id}.html"
        png_file = f"{slide_id}.png"
        mp3_file = f"{slide_id}.mp3"
        
        html_path = os.path.join(DECK_DIR, html_file)
        png_path = os.path.join(DECK_DIR, png_file)
        mp3_path = os.path.join(DECK_DIR, mp3_file)
        
        # Build HTML content
        if slide.get("is_outro"):
            content_html = get_outro_content()
        else:
            cards_html = ""
            for card_data in slide.get("cards", []):
                if len(card_data) == 4 and card_data[3]: # station note
                    cards_html += f"""
                    <div class="station-note-box">
                        <b>Station Operating Note:</b> {card_data[1]}
                    </div>
                    """
                else:
                    c_title, c_desc, c_color = card_data[:3]
                    color_class = "card-green" if c_color == "green" else ("card-amber" if c_color == "amber" else "")
                    cards_html += f"""
                    <div class="card {color_class}">
                        <div class="card-title">{c_title}</div>
                        <div class="card-desc">{c_desc}</div>
                    </div>
                    """
            
            media_html = ""
            if slide.get("media_path") and os.path.exists(slide["media_path"]):
                rel_media = os.path.abspath(slide["media_path"]).replace(os.sep, "/")
                media_html = f"""
                <div class="col-media">
                    <img src="file:///{rel_media}">
                    <div class="media-caption">{slide.get('caption', '')}</div>
                </div>
                """
            
            content_html = f"""
            <div class="col-text">
                {cards_html}
            </div>
            {media_html}
            """
        
        full_html = render_slide_html(
            series_badge=slide["badge"],
            meta_text=slide["meta"],
            title=slide["title"],
            subtitle=slide["subtitle"],
            content_html=content_html
        )
        
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(full_html)
            
        print(f"[{slide_id}] Rendering 720p PNG ({png_file})...")
        capture_slide(html_path, png_path)
        
        # Generate Audio
        narration = slide["narration"]
        print(f"[{slide_id}] Generating Audio ({mp3_file})...")
        await generate_audio(narration, mp3_path)
        
        # Measure audio duration
        audio = MP3(mp3_path)
        duration = audio.info.length
        
        start_str = format_time(current_time)
        end_time = current_time + duration
        end_str = format_time(end_time)
        dur_str = f"{duration:.2f}s"
        
        timeline_rows.append({
            "idx": idx,
            "id": slide_id,
            "title": title,
            "png": png_file,
            "mp3": mp3_file,
            "duration": duration,
            "dur_str": dur_str,
            "start_str": start_str,
            "end_str": end_str
        })
        
        script_lines.append(f"### Slide {idx}: {title}\n")
        script_lines.append(f"**Visual:** `{png_file}` | **Audio:** `{mp3_file}` | **Duration:** `{dur_str}`\n\n")
        script_lines.append(f"> **Technical Narration:**\n> \"{narration}\"\n\n---\n\n")
        
        # Set slide length equal to audio length on timeline
        current_time = end_time
    
    total_duration_str = format_time(current_time)
    
    # Write VSDC_TIMELINE_MAP.md
    map_path = os.path.join(DECK_DIR, "VSDC_TIMELINE_MAP.md")
    with open(map_path, "w", encoding="utf-8") as f:
        f.write("# VSDC Pro Timeline Alignment Map — Presentation 1 (Expanded 13 Slides)\n\n")
        f.write(f"**Total Video Duration:** `{total_duration_str}` ({current_time:.2f} seconds)\n")
        f.write(f"**Voice:** Microsoft Christopher Online (Natural) — `en-US-ChristopherNeural`\n")
        f.write("**Audio/Slide Duration Rule:** Each slide's display duration is set **EXACTLY equal to its audio track duration**.\n")
        f.write("**Directory:** All `.png` and `.mp3` files are located in the **same directory** for direct sequence import.\n\n")
        f.write("| Slide # | Title | Visual Track (PNG) | Audio Track (MP3) | Duration (Slide = Audio) | Timeline Start | Timeline End |\n")
        f.write("| :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n")
        for r in timeline_rows:
            f.write(f"| **Slide {r['idx']:02d}** | {r['title']} | `{r['png']}` | `{r['mp3']}` | **{r['dur_str']}** | `{r['start_str']}` | `{r['end_str']}` |\n")
        f.write("\n\n### How to Open / Import in VSDC Pro:\n")
        f.write("1. Create New Project in VSDC: **1280x720, 30 fps**.\n")
        f.write(f"2. In File Explorer, select all files in `{DECK_DIR}`.\n")
        f.write("3. Drag all `slide_*.png` onto Video Track 1.\n")
        f.write("4. Drag all `slide_*.mp3` onto Audio Track 2.\n")
        f.write("5. Set each slide's duration property to match the corresponding audio duration shown in the table above.\n")
    
    # Write script file
    script_path = os.path.join(DECK_DIR, "TECHNICAL_NARRATION_SCRIPT.md")
    with open(script_path, "w", encoding="utf-8") as f:
        f.writelines(script_lines)
    
    # Write interactive preview.html with visible player and duration matching
    write_preview_html(timeline_rows)
    print("\n[+] All 13 slides, audio tracks, timeline maps, and browser preview generated successfully!")

def write_preview_html(timeline_rows):
    slides_js = []
    for r in timeline_rows:
        slides_js.append(f"""{{
            id: "{r['id']}",
            title: "{r['title']}",
            png: "{r['png']}",
            audio: "{r['mp3']}",
            duration: "{r['dur_str']}",
            start: "{r['start_str']}"
        }}""")
    slides_js_str = ",\n            ".join(slides_js)
    
    preview_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>JRFK Presentation 1: 13-Slide Complete Master Preview</title>
    <style>
        body {{
            margin: 0;
            padding: 16px;
            background: #06152b;
            color: #ffffff;
            font-family: 'Segoe UI', -apple-system, sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            box-sizing: border-box;
        }}
        .player-container {{
            width: 1080px;
            background: #0c2340;
            border: 2px solid #38bdf8;
            border-radius: 10px;
            box-shadow: 0 12px 35px rgba(0,0,0,0.75);
            overflow: hidden;
            display: flex;
            flex-direction: column;
        }}
        .slide-frame {{
            width: 1080px;
            height: 608px;
            border: none;
            background: #000;
            display: block;
        }}
        .control-panel {{
            padding: 14px 20px;
            background: #081a33;
            border-top: 2px solid #1e3a5f;
            display: flex;
            flex-direction: column;
            gap: 10px;
        }}
        .top-row {{
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .nav-group {{
            display: flex;
            gap: 10px;
            align-items: center;
        }}
        .btn {{
            background: #0284c7;
            color: #ffffff;
            border: none;
            padding: 8px 16px;
            border-radius: 5px;
            cursor: pointer;
            font-weight: 700;
            font-size: 13px;
            letter-spacing: 0.5px;
            transition: background 0.15s ease;
        }}
        .btn:hover {{ background: #0369a1; }}
        .btn-green {{ background: #16a34a; }}
        .btn-green:hover {{ background: #15803d; }}
        .slide-indicator {{
            font-size: 13.5px;
            font-weight: 600;
            color: #38bdf8;
            letter-spacing: 0.5px;
        }}
        .audio-wrapper {{
            display: flex;
            align-items: center;
            gap: 14px;
            background: #051329;
            padding: 8px 14px;
            border-radius: 6px;
            border: 1px solid #1e3a5f;
        }}
        .audio-label {{
            font-size: 12px;
            color: #94a3b8;
            font-family: monospace;
            white-space: nowrap;
        }}
        audio {{
            flex: 1;
            height: 36px;
            outline: none;
        }}
        .timeline-guide {{
            display: flex;
            justify-content: space-between;
            font-size: 11.5px;
            color: #64748b;
            font-family: monospace;
            padding: 0 4px;
        }}
        .slide-selector {{
            background: #0f2744;
            color: #ffffff;
            border: 1px solid #38bdf8;
            padding: 6px 10px;
            border-radius: 4px;
            font-size: 12px;
            cursor: pointer;
        }}
    </style>
</head>
<body>
    <div class="player-container">
        <!-- 720p Clean Slide Frame -->
        <iframe id="slideFrame" class="slide-frame" src="slide_01.html"></iframe>
        
        <!-- Controls & Visible Audio Player -->
        <div class="control-panel">
            <div class="top-row">
                <div class="nav-group">
                    <button class="btn" onclick="prevSlide()">◀ Previous</button>
                    <button class="btn" onclick="nextSlide()">Next ▶</button>
                    <button class="btn btn-green" onclick="restartAudio()">▶ Play Narration</button>
                    <select id="jumpSelect" class="slide-selector" onchange="jumpToSlide(this.value)">
                        <option value="0">Slide 1: The Migration Requirement</option>
                        <option value="1">Slide 2: Why 32-Bit Must Go (Software EOL)</option>
                        <option value="2">Slide 3: Display Architecture & RF Locks</option>
                        <option value="3">Slide 4: 64-Bit Architecture Payoff</option>
                        <option value="4">Slide 5: Tool 1 - JRFK Migrator Engine</option>
                        <option value="5">Slide 6: Tool 1 - Discovery & Calibration</option>
                        <option value="6">Slide 7: Tool 2 - 7-Screen Cockpit RF Metering</option>
                        <option value="7">Slide 8: Tool 2 - PA Health & 4-Way Antennas</option>
                        <option value="8">Slide 9: Tool 2 - Protection & Calibration</option>
                        <option value="9">Slide 10: Tool 3 - 3-Min Disaster Recovery</option>
                        <option value="10">Slide 11: Tool 3 - First-Boot Automation</option>
                        <option value="11">Slide 12: Tool 4 - Documentation & Cookbook</option>
                        <option value="12">Slide 13: Summary & Resources</option>
                    </select>
                </div>
                <div class="slide-indicator" id="slideMeta">
                    Slide 1 of 13: Modernizing the RF-KIT Linear Amplifier
                </div>
            </div>
            
            <!-- Visible Audio Track with Scrubber -->
            <div class="audio-wrapper">
                <span class="audio-label" id="audioLabel">🔊 TRACK: slide_01.mp3 (Christopher Natural)</span>
                <audio id="audioPlayer" controls preload="auto"></audio>
            </div>
            
            <div class="timeline-guide">
                <span id="timingStart">Timeline Offset: 00:00.00</span>
                <span>Voice: en-US-ChristopherNeural • Slide Duration = Audio Duration</span>
                <span id="timingDur">Duration: Loading...</span>
            </div>
        </div>
    </div>

    <script>
        const slides = [
            {slides_js_str}
        ];
        
        let currentIdx = 0;
        const player = document.getElementById('audioPlayer');

        function loadSlide(idx) {{
            currentIdx = idx;
            const s = slides[currentIdx];
            document.getElementById('slideFrame').src = s.id + '.html';
            document.getElementById('slideMeta').innerText = `Slide ${{currentIdx + 1}} of ${{slides.length}}: ${{s.title}}`;
            document.getElementById('audioLabel').innerText = `🔊 TRACK: ${{s.audio}} (Christopher Natural)`;
            document.getElementById('timingStart').innerText = `Timeline Offset: ${{s.start}}`;
            document.getElementById('timingDur').innerText = `Duration: ${{s.duration}} (Exact Match)`;
            document.getElementById('jumpSelect').value = currentIdx;
            
            player.src = s.audio;
            player.play().catch(() => {{
                // Handled user gesture requirements
            }});
        }}

        function restartAudio() {{
            player.currentTime = 0;
            player.play();
        }}

        function nextSlide() {{
            if (currentIdx < slides.length - 1) {{
                loadSlide(currentIdx + 1);
            }}
        }}

        function prevSlide() {{
            if (currentIdx > 0) {{
                loadSlide(currentIdx - 1);
            }}
        }}

        function jumpToSlide(val) {{
            loadSlide(parseInt(val));
        }}

        // Auto-advance slide when audio finishes
        player.addEventListener('ended', () => {{
            if (currentIdx < slides.length - 1) {{
                loadSlide(currentIdx + 1);
            }}
        }});

        window.addEventListener('DOMContentLoaded', () => {{
            loadSlide(0);
        }});
    </script>
</body>
</html>
"""
    preview_path = os.path.join(DECK_DIR, "preview.html")
    with open(preview_path, "w", encoding="utf-8") as f:
        f.write(preview_content)

if __name__ == "__main__":
    asyncio.run(main())
