"""
JRFK Master Presentation Engine
Builds 720p (1280x720) Slide Decks and Richard Feynman Voiceover Scripts
for All 5 Video Presentations.
"""

import os
import subprocess
import json

CHROME_BIN = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
BASE_DIR = r"D:\JRFK\Presentations"
COOKBOOK_MEDIA = r"D:\JRFK\docs\cookbook_media"
PI_SCREEN = r"D:\JRFK\Presentations\rfk_screen_capture_test.png"

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
    font-size: 30px;
    margin: 0;
    font-weight: 800;
    letter-spacing: 0.5px;
    color: #ffffff;
    text-transform: uppercase;
}
.title-row .subtitle {
    font-size: 15px;
    color: var(--accent-cyan);
    margin-top: 3px;
    font-weight: 500;
}
.content {
    flex: 1;
    display: flex;
    gap: 20px;
    margin-top: 14px;
    align-items: stretch;
}
.col-text {
    flex: 1.2;
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
    padding: 10px 14px;
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
    font-size: 15px;
    font-weight: 700;
    color: #ffffff;
    margin-bottom: 3px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.card-desc {
    font-size: 13px;
    color: var(--bp-line-dim);
    line-height: 1.4;
}
.feynman-box {
    background: rgba(15, 23, 42, 0.9);
    border: 1px dashed var(--accent-amber);
    padding: 8px 12px;
    border-radius: 6px;
    font-style: italic;
    font-size: 12.5px;
    color: #fef08a;
    line-height: 1.35;
}
.footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-top: 1px solid rgba(255, 255, 255, 0.2);
    padding-top: 8px;
    font-size: 12px;
    color: var(--bp-line-dim);
}
table.clean-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 12px;
    background: #081d33;
    border: 1px solid var(--bp-border);
}
table.clean-table th {
    background: #0f3460;
    color: var(--accent-cyan);
    padding: 6px 8px;
    text-align: left;
    border-bottom: 2px solid var(--bp-border);
}
table.clean-table td {
    padding: 6px 8px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    color: var(--bp-line-dim);
}
table.clean-table tr:hover td {
    background: #0c2d54;
    color: #ffffff;
}
"""

def render_slide_html(series_badge, meta_text, title, subtitle, content_html, footer_text="JRFK 64-BIT STATION SUITE"):
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
        <div>{footer_text}</div>
        <div>GITHUB.COM/JBIRDLEBOUGH1/JRFKTOOLS</div>
    </div>
</body>
</html>"""

def capture_slide(html_path, png_path):
    cmd = [
        CHROME_BIN,
        "--headless=new",
        "--disable-gpu",
        "--window-size=1280,720",
        f"--screenshot={png_path}",
        f"file:///{html_path.replace(os.sep, '/')}"
    ]
    subprocess.run(cmd, check=True)


def get_outro_slide(deck_name):
    content_html = """
    <div class="col-text" style="flex:1;">
        <div class="card card-green">
            <div class="card-title">⚡ Fast Download (No Developer Tools Required)</div>
            <div class="card-desc">
                Direct Windows Executable: <b>JRFK.exe (Beta 1.0)</b><br>
                <code>https://github.com/jbirdlebough1/JRFKTools/releases/download/v01.00.00-beta/JRFK.exe</code>
            </div>
        </div>
        <div class="card">
            <div class="card-title">🌐 Live Web Documentation Portal (GitHub Pages)</div>
            <div class="card-desc">
                Read all manuals in your browser (desktop, tablet, or shack mobile):<br>
                <code>https://jbirdlebough1.github.io/JRFKTools/</code>
            </div>
        </div>
        <div class="card">
            <div class="card-title">📂 Open Source GitHub Repository</div>
            <div class="card-desc">
                Source code, migrator tools, and full session audit logs:<br>
                <code>https://github.com/jbirdlebough1/JRFKTools</code>
            </div>
        </div>
        <div class="card card-amber">
            <div class="card-title">💬 Community & Discussion Forum</div>
            <div class="card-desc">
                RF-KIT / B26-PA Worldwide Community:<br>
                <code>https://b26-pa.groups.io/g/main</code>
            </div>
        </div>
    </div>
    <div class="col-media" style="flex:0.8;">
        <div style="font-size:24px; font-weight:800; color:#ffffff; text-align:center; margin-bottom:12px;">73 & GOOD DX</div>
        <div style="font-size:14px; color:var(--accent-cyan); text-align:center; line-height:1.6;">
            RF-KIT RF2K+ / RF2K-S Linear Amplifier Modernization<br>
            Designed & Maintained for the Global Amateur Radio Community<br><br>
            <span style="color:#22c55e; font-weight:700;">Zero LaTeX Defects • Pure 64-Bit Bookworm • 7-Screen Telemetry</span>
        </div>
    </div>
    """
    return render_slide_html(
        series_badge=deck_name,
        meta_text="MASTER STATION RESOURCES & LINKS",
        title="Resources & Project Downloads",
        subtitle="Turnkey Links for Software, Documentation, Firmware & Community Support",
        content_html=content_html
    )

DECKS = {
    "Deck_1_Intro": {
        "title": "Series Introduction & Overview",
        "slides": [
            {
                "id": "slide_1",
                "badge": "JRFK SERIES • PART 1",
                "meta": "EXECUTIVE OVERVIEW • RF-KIT RF2K+ & B26-PA",
                "title": "Modernizing the RF-KIT Linear Amplifier",
                "subtitle": "Turnkey 64-Bit OS Migration, 7-Screen Web Suite & Community Hardening",
                "media_path": os.path.join(COOKBOOK_MEDIA, "img_001.jpeg"),
                "caption": "FIG 1: RF-KIT RF2K+ 1500W HF/6M LINEAR AMPLIFIER",
                "cards": [
                    ("The Modernization Leap", "Upgrading legacy 32-bit Raspberry Pi OS installs to pure 64-bit Debian Bookworm with modern Full KMS DRM display drivers and Python 3.13 deprecation patches.", "cyan"),
                    ("Strict Port Decoupling", "Independent separation: PC Migrator runs on Port 8089, while the Amplifier Operational Web Suite lives on Port 8088.", "green"),
                    ("Feynman Note", "Nature cannot be fooled! When a kilowatt amplifier is switching in milliseconds, your software stack must be rock solid.", "amber", True)
                ],
                "feynman": "Look, nature cannot be fooled! When you've got fifteen hundred watts of RF power cruising through a pair of LDMOS transistors, the computer controlling it has to be fast, stable, and completely dependable. Today we take the great leap into pure 64-bit architecture!"
            },
            {
                "id": "slide_2",
                "badge": "JRFK SERIES • PART 1",
                "meta": "THE ARCHITECTURAL PROBLEM",
                "title": "Why Legacy 32-Bit OS Must Go",
                "subtitle": "End-of-Life Python Runtimes, Display Driver Freezes, and Fragile Scripts",
                "media_path": os.path.join(COOKBOOK_MEDIA, "img_102.jpeg"),
                "caption": "FIG 2: LEGACY 32-BIT CONTROLLER SYSTEM ON THE AIR VIA CAT",
                "cards": [
                    ("End of Support Life", "The old 32-bit OS foundation is frozen in time. Modern security patches, network tools, and Python 3 libraries are completely locked out.", "cyan"),
                    ("Touchscreen & Video Latency", "Legacy fake-KMS and legacy X11 display stacks cause occasional frame stutter and unrecoverable touchscreen lockups during RF keying.", "amber"),
                    ("Turnkey Solution", "JRFK brings an automated migrator: zero-touch imaging, automatic recovery, and clean modern services in under three minutes.", "green")
                ],
                "feynman": "Think about it like this: running an ancient 32-bit operating system on a modern linear amplifier is like bolting a high-performance jet engine onto a wooden wagon! It works until the wheels fall off. Bookworm gives us 64-bit precision and rock-solid DRM display drivers."
            },
            {
                "id": "slide_3",
                "badge": "JRFK SERIES • PART 1",
                "meta": "DECOUPLED ARCHITECTURE",
                "title": "Dual-Port Architecture: 8089 vs 8088",
                "subtitle": "Strict Separation Between the PC Migrator and the Amplifier Web Suite",
                "media_path": PI_SCREEN,
                "caption": "FIG 3: NATIVE 1024x600 TOUCHSCREEN FRAME BUFFER (PORT 8088)",
                "cards": [
                    ("Port 8089 (PC Migrator)", "Runs locally on your Windows PC via JRFK.exe. Handles image downloading, pre-flight discovery, SSH flashing, and disaster recovery.", "cyan"),
                    ("Port 8088 (Amplifier Suite)", "Runs permanently on the Raspberry Pi inside the RF-KIT. Hosts all 7 operational touch screens, real-time power meters, and antenna routing.", "green"),
                    ("Why Decoupling Matters", "Your amplifier never crashes if a PC disconnects, and PC maintenance never interferes with active RF operations.", "cyan")
                ],
                "feynman": "Here's the secret to reliable engineering: isolation! The tool that sets up the system on your PC lives on port 8089. The actual amplifier cockpit lives on port 8088 on the Pi itself. They never get in each other's way. Brilliant and clean!"
            },
            {
                "id": "slide_4",
                "badge": "JRFK SERIES • PART 1",
                "meta": "DOCUMENTATION REFERENCE",
                "title": "4-Volume Documentation & K7BIT Cookbook",
                "subtitle": "Complete Engineering Manuals + Historical Master Cookbook Reference",
                "media_path": os.path.join(COOKBOOK_MEDIA, "img_007.jpeg"),
                "caption": "FIG 4: RF PALLET WITH LDMOS CLAMPS (FROM K7BIT COOKBOOK REV 1.05)",
                "cards": [
                    ("Complete 4-Volume Station Library", "Includes Operations Manual, 7-Screen User Guide, Engineering Architecture Manual, and Disaster Recovery Card.", "green"),
                    ("The K7BIT Master Cookbook (Rev 1.05)", "For kit builders and maintainers, John K7BIT's authentic 193-page cookbook is fully preserved in the docs portal—an older historical reference, but packed with irreplaceable schematics and wiring diagrams.", "cyan"),
                    ("Live In-Browser Reader", "All manuals are instantly readable on any tablet, phone, or shack PC via GitHub Pages with zero downloads required.", "amber")
                ],
                "feynman": "Now, for the builders who love getting solder on their fingers: we've included John K7BIT's legendary 193-page cookbook in the portal. It's an older reference now, but it has every wire, bolt, and schematic diagram you'll ever need. Plus our complete modern 4-volume engineering manuals!"
            }
        ]
    },
    "Deck_2_Migration": {
        "title": "32-to-64 Bit Migration Walkthrough",
        "slides": [
            {
                "id": "slide_1",
                "badge": "JRFK SERIES • PART 2",
                "meta": "STEP-BY-STEP MIGRATION GUIDE",
                "title": "Automated 32-to-64 Bit Migration",
                "subtitle": "Step-by-Step From JRFK.exe Download to Production Operation",
                "media_path": os.path.join(COOKBOOK_MEDIA, "img_129.jpeg"),
                "caption": "FIG 1: ZERO-TOUCH FLASHING & PARTITION RESTORATION",
                "cards": [
                    ("Zero Developer Tools Needed", "No Python setup, no compiler toolchains, no command-line hassle. One standalone executable does everything.", "cyan"),
                    ("Automated Safety Pipeline", "Automatic backup verification, network target discovery, and elevated privilege handling.", "green"),
                    ("Feynman Note", "Don't guess what the software is doing—know it! The migrator executes an exact, deterministic pipeline.", "amber", True)
                ],
                "feynman": "Welcome to Part 2! Today we walk step-by-step through the migration. You don't need to be a Linux guru, and you don't need developer tools. One clean executable does the whole job with surgical precision."
            },
            {
                "id": "slide_2",
                "badge": "JRFK SERIES • PART 2",
                "meta": "STEP 1: DOWNLOAD & LAUNCH",
                "title": "Step 1: Download & Elevated Launch",
                "subtitle": "Running JRFK.exe with Windows Defender & UAC Handled Automatically",
                "media_path": os.path.join(COOKBOOK_MEDIA, "img_104.jpeg"),
                "caption": "FIG 2: SECURE ELEVATION & NETWORK INTERFACE HANDSHAKE",
                "cards": [
                    ("Download Standalone JRFK.exe", "Grab the pre-compiled binary directly from GitHub releases (~162 MB, includes embedded Python runtime and migrator).", "cyan"),
                    ("C# Elevated Launcher", "JRFK.exe automatically requests Administrator rights to configure local networking and suppress Windows 11 notification traps.", "green"),
                    ("Port 8089 Live Console", "Automatically launches your browser to http://127.0.0.1:8089 where the visual migration cockpit guides your progress.", "cyan")
                ],
                "feynman": "Step one: download JRFK.exe and run it! Our custom C# wrapper handles Windows UAC elevation, suppresses annoying popups, and immediately opens your browser to the local migration dashboard on port 8089."
            },
            {
                "id": "slide_3",
                "badge": "JRFK SERIES • PART 2",
                "meta": "STEP 2: PRE-FLIGHT CHECKS",
                "title": "Step 2: Pre-Flight Hardware Checks",
                "subtitle": "Network Discovery, SSH Key Verification, and Disk Health Inspection",
                "media_path": os.path.join(COOKBOOK_MEDIA, "img_103.jpeg"),
                "caption": "FIG 3: TARGET RASPBERRY PI NETWORK DISCOVERY & TERMINAL HANDSHAKE",
                "cards": [
                    ("Automated IP Discovery", "The migrator scans your shack subnet and locks onto the amplifier IP (e.g. 192.168.12.193).", "cyan"),
                    ("SSH Key Handshake", "Establishes a secure remote channel to test storage integrity and check current operating parameters.", "green"),
                    ("Backup Card Detection", "Verifies the secondary USB backup card is present before proceeding with any flash operations.", "amber")
                ],
                "feynman": "Before you take off, you check the instruments! The migrator scans your network, finds the amplifier, verifies SSH communication, and makes sure your secondary backup storage is ready before touching a single byte."
            },
            {
                "id": "slide_4",
                "badge": "JRFK SERIES • PART 2",
                "meta": "STEP 3: 64-BIT BOOKWORM FLASH",
                "title": "Step 3: Automated Bookworm Flashing",
                "subtitle": "Writing the 64-Bit OS Image, Video Modelines & Deprecation Patches",
                "media_path": os.path.join(COOKBOOK_MEDIA, "img_130.jpeg"),
                "caption": "FIG 4: DIRECT SECTOR-BY-SECTOR FLASHING PROCESS",
                "cards": [
                    ("Pure 64-Bit Debian Bookworm", "Installs the official Debian aarch64 kernel with optimized ARM64 compiler optimizations.", "green"),
                    ("1024x600 Full KMS Modelines", "Configures direct hardware DRM modelines for the 7-inch HDMI touchscreen with zero display flickering.", "cyan"),
                    ("Python 3.13 Patches Applied", "Patches SimpleRPC to eliminate all deprecated asynchronous socket calls, guaranteeing continuous 24/7 uptime.", "cyan")
                ],
                "feynman": "Now the magic happens: the migrator flashes pure 64-bit Debian Bookworm. It injects the custom 1024 by 600 video modelines so the physical touch screen is crisp and stable, and patches the Python runtime for smooth SimpleRPC telemetry."
            },
            {
                "id": "slide_5",
                "badge": "JRFK SERIES • PART 2",
                "meta": "STEP 4: DISASTER RECOVERY",
                "title": "Step 4: The 3-Minute Recovery Card",
                "subtitle": "Emergency 'Swap, Boot, Reboot, Run' Card Eliminates Shack Downtime",
                "media_path": os.path.join(COOKBOOK_MEDIA, "img_131.jpeg"),
                "caption": "FIG 5: AUTOMATED SECONDARY SD CARD MIRRORING",
                "cards": [
                    ("Automated Mirroring", "The migrator mirrors the entire production system to a secondary USB MicroSD card.", "cyan"),
                    ("Under 3 Minutes Target Recovery", "If the primary MicroSD ever suffers corruption during a contest, swap the cards and power on.", "green"),
                    ("Zero Configuration Re-Entry", "All callsign settings, calibration coefficients, and antenna matrices are mirrored automatically.", "amber")
                ],
                "feynman": "Here is the ultimate peace of mind: the 3-minute disaster recovery card. If a power spike ever kills your primary SD card in the middle of a DX contest, you simply swap in the secondary backup card, boot up, and you're back on the air!"
            }
        ]
    },
    "Deck_3_Operations": {
        "title": "JRFK Operations Suite (The 7 Web Screens)",
        "slides": [
            {
                "id": "slide_1",
                "badge": "JRFK SERIES • PART 3",
                "meta": "AMPLIFIER WEB COCKPIT • PORT 8088",
                "title": "The 7-Screen Web Suite on Port 8088",
                "subtitle": "Complete Browser Telemetry: Why, What, and How to Operate",
                "media_path": PI_SCREEN,
                "caption": "FIG 1: MAIN RF DASHBOARD LIVE TELEMETRY DISPLAY (1024x600)",
                "cards": [
                    ("Shack-Wide Accessibility", "Access every single amplifier control and meter from any PC, tablet, or smartphone on your home network.", "cyan"),
                    ("Sub-Millisecond Polling", "Real-time Forward Power, Reflected Power, Peak Envelope Power (PEP), and instant SWR arc response.", "green"),
                    ("Feynman Note", "A meter isn't just a dial—it's a direct window into electromagnetic field transfer in your transmission line!", "amber", True)
                ],
                "feynman": "Welcome to Part 3! Today we explore the cockpit. Why should you have to bend down and squint at the front panel when you can have all seven amplifier screens running smoothly in your web browser? Let's break down each screen: why it exists, what it measures, and how to use it."
            },
            {
                "id": "slide_2",
                "badge": "JRFK SERIES • PART 3",
                "meta": "SCREENS 1 & 2: RF & BANDS",
                "title": "Screen 1 & 2: RF Dashboard & Band Matrix",
                "subtitle": "Real-Time Power Telemetry and Automated Relay Sequencing",
                "media_path": os.path.join(COOKBOOK_MEDIA, "img_063.jpeg"),
                "caption": "FIG 2: BAND MATRIX & LPF RELAY SELECTION DISPLAY",
                "cards": [
                    ("Screen 1: Main RF Dashboard", "WHY: Continuous visual verification of legal-limit output. WHAT: Forward/Reflected PEP, SWR bar, and active status. HOW: Instant operate/standby toggle.", "green"),
                    ("Screen 2: Band Switching", "WHY: Pre-selector filter selection. WHAT: Active low-pass filter relay state. HOW: Automatic tracking via CAT/CI-V, with one-click manual band override.", "cyan"),
                    ("Sequence Protection", "Hardware lockout prevents band changes while the transmitter is actively keyed.", "amber")
                ],
                "feynman": "Screen one is your primary cockpit: real-time forward power, reflected power, and SWR. Screen two is the band switching matrix. When you turn the VFO on your transceiver, CAT commands automatically switch the low-pass filter relays with zero hot-switching."
            },
            {
                "id": "slide_3",
                "badge": "JRFK SERIES • PART 3",
                "meta": "SCREENS 3 & 4: PA & ANTENNAS",
                "title": "Screen 3 & 4: PA Telemetry & Antenna Matrix",
                "subtitle": "LDMOS Voltage/Current Monitoring and 4x Antenna Routing",
                "media_path": os.path.join(COOKBOOK_MEDIA, "img_055.jpeg"),
                "caption": "FIG 3: DISCRETE VOLTAGE & BIAS TELEMETRY ALIGNMENT",
                "cards": [
                    ("Screen 3: PA Telemetry", "WHY: Ensure LDMOS transistors operate within safe electrical envelope. WHAT: 53.5V rail voltage, drain current, and heatsink temperature. HOW: Continuous health monitoring.", "green"),
                    ("Screen 4: 4x Antenna Matrix", "WHY: Route RF to the correct beam or wire. WHAT: 4-way antenna matrix with per-band memory. HOW: Click antenna 1 through 4, saved per band.", "cyan"),
                    ("Discrete DC Sensing", "Utilizes clean analog discrete sensing across the DC bus—simple, rugged, and free of bus communication crashes.", "amber")
                ],
                "feynman": "Screen three watches your amplifier's heart: the dual LDMOS transistors. You get continuous readouts of the 53.5 volt DC rail, drain current, and temperature. Screen four gives you a four-way antenna matrix with memory for every band."
            },
            {
                "id": "slide_4",
                "badge": "JRFK SERIES • PART 3",
                "meta": "SCREEN 5: PROTECTION LIMITS",
                "title": "Screen 5: Protection Limits & Thermal Guard",
                "subtitle": "SWR Trip Curves, Overdrive Clamps, and 60°C Safety Thresholds",
                "media_path": os.path.join(COOKBOOK_MEDIA, "img_049.jpeg"),
                "caption": "FIG 4: SWR BRIDGE TEST JIG & COUPLER CALIBRATION",
                "cards": [
                    ("Why Protection Matters", "LDMOS devices are rugged, but severe reflected power or extreme overdrive can destroy a transistor in microseconds.", "amber"),
                    ("What It Protects", "SWR > 2.5:1 instant trip, RF overdrive clamp, and multi-stage 60°C heatsink thermal guard shutdown.", "green"),
                    ("How to Use", "Inspect peak hold metrics, view trip event logs, and reset safety states after clearing an antenna fault.", "cyan")
                ],
                "feynman": "Transistors are fast, but high SWR spikes are just as fast! Screen five shows your active protection thresholds. If your antenna blows down in a windstorm, the software clamps the drive and trips standby in microseconds, saving your amplifier from destruction."
            },
            {
                "id": "slide_5",
                "badge": "JRFK SERIES • PART 3",
                "meta": "SCREENS 6 & 7: CONFIG & TOUCH",
                "title": "Screen 6 & 7: Config, Logs & Touch Calibration",
                "subtitle": "SimpleRPC Diagnostic Logs and DRM Full KMS Screen Alignment",
                "media_path": os.path.join(COOKBOOK_MEDIA, "img_092.jpeg"),
                "caption": "FIG 5: RASPBERRY PI SYSTEM CONFIGURATION & EVENT LOGS",
                "cards": [
                    ("Screen 6: System Config & Logs", "WHY: Station troubleshooting. WHAT: Live SimpleRPC communication traces, temperature logs, and service status. HOW: One-click service restart.", "cyan"),
                    ("Screen 7: Touch Calibration", "WHY: Precise touch accuracy. WHAT: 5-point touch alignment routine for the 1024x600 display. HOW: Tap on-screen crosshairs to calibrate.", "green"),
                    ("Direct Web Access", "All features are also completely operable from your desktop web browser on port 8088.", "cyan")
                ],
                "feynman": "Finally, screens six and seven: diagnostic event logs showing exactly what the SimpleRPC controller is doing, and a five-point touch calibration screen that aligns your physical touchscreen with sub-millimeter precision!"
            }
        ]
    },
    "Deck_4_Dev_DeepDive": {
        "title": "Development Deep Dive & Build Automation",
        "slides": [
            {
                "id": "slide_1",
                "badge": "JRFK SERIES • PART 4",
                "meta": "ENGINEERING ARCHITECTURE BRIEFING",
                "title": "JRFK Engineering Deep Dive",
                "subtitle": "Architectural Solution, Kernel Modelines, and Gemini Pro Automation",
                "media_path": os.path.join(COOKBOOK_MEDIA, "img_148.jpeg"),
                "caption": "FIG 1: CONTROLLER HARDWARE & ARDUINO/RPI BUS ARCHITECTURE",
                "cards": [
                    ("Slide-Only Technical Briefing", "An exhaustive master briefing for builders, developers, and software engineers modernizing RF-KIT linear amplifiers.", "cyan"),
                    ("Under the Hood", "Video DRM KMS drivers, SimpleRPC asynchronous patches, discrete sensing DC rails, and full build automation.", "green"),
                    ("Feynman Principle", "What I cannot create, I do not understand! Today we tear down the software and hardware architecture to first principles.", "amber", True)
                ],
                "feynman": "Welcome to Part 4, our technical deep dive! As I always used to say, what I cannot create, I do not understand! Today we look at every engineering layer: video modelines, Python deprecation patches, electrical characteristics, and Gemini Pro automation."
            },
            {
                "id": "slide_2",
                "badge": "JRFK SERIES • PART 4",
                "meta": "DRIVER & KERNEL LAYER",
                "title": "Full KMS DRM Video & SimpleRPC Patches",
                "subtitle": "Resolving 1024x600 Display Modelines and Python 3.13 Deprecations",
                "media_path": os.path.join(COOKBOOK_MEDIA, "img_018.jpeg"),
                "caption": "FIG 2: CONTROLLER BACKPLANE & 7-INCH DISPLAY INTERFACE",
                "cards": [
                    ("Full KMS DRM Driver", "Transitioned from legacy fake-KMS to native Linux Full KMS DRM. Injected custom 1024x600 @ 60Hz video modeline directly into kernel boot parameters.", "green"),
                    ("SimpleRPC Deprecation Patches", "Replaced obsolete asynchronous socket schemas with clean non-blocking JSON-RPC schemas compatible with modern Python 3.13.", "cyan"),
                    ("Zero Lockup Architecture", "Isolates hardware polling loops so UI rendering stalls never interrupt amplifier protection watchdogs.", "amber")
                ],
                "feynman": "In the old days, video was handled by clunky user-space drivers that would choke under RF interference. We moved to Linux Full KMS DRM with custom 1024 by 600 kernel modelines. And we eliminated deprecated Python sockets, giving us a non-blocking SimpleRPC pipeline."
            },
            {
                "id": "slide_3",
                "badge": "JRFK SERIES • PART 4",
                "meta": "ELECTRICAL & HARDWARE SPECIFICATIONS",
                "title": "RF Deck & Standard DC Architecture",
                "subtitle": "Ampleon BLF189 LDMOS Envelope & Standard Discrete DC Rail Sensing",
                "media_path": os.path.join(COOKBOOK_MEDIA, "img_151.jpeg"),
                "caption": "FIG 3: RF POWER PALLET SCHEMATIC & TRANSISTOR MOUNTING",
                "cards": [
                    ("Ampleon BLF189 / BLF189XR LDMOS", "Optimized electrical curves for dual 50V LDMOS devices capable of 1500W PEP output across 1.8 MHz through 54 MHz with >65% efficiency.", "green"),
                    ("No CAN BUS PSU Dependency", "The RF-KIT does not use CAN bus power supplies. Voltage and current are monitored cleanly via precision discrete resistive shunts and ADCs.", "cyan"),
                    ("Robust Reliability", "Eliminating CAN bus communications eliminates software handshake timeouts, transceiver faults, and PSU lockouts.", "amber")
                ],
                "feynman": "Let's be crystal clear on hardware: the amplifier runs dual Ampleon BLF189 LDMOS devices. And the RF-KIT does NOT use CAN bus power supplies! Voltage and current are read directly through clean, discrete analog shunts. No CAN bus crashes, no firmware handshakes—just pure, reliable DC physics."
            },
            {
                "id": "slide_4",
                "badge": "JRFK SERIES • PART 4",
                "meta": "AI AUTOMATION & CI/CD",
                "title": "Gemini Pro Automation & 18/18 Testing",
                "subtitle": "Full Build Automation, Regression Testing, and Self-Contained Deployment",
                "media_path": os.path.join(COOKBOOK_MEDIA, "img_149.jpeg"),
                "caption": "FIG 4: PIN MAPPING & CONTROLLER LOGIC TIMING DIAGRAMS",
                "cards": [
                    ("Gemini Pro Driven Engineering", "Used Google Gemini Pro and Antigravity tooling to drive automated codebase analysis, C# launcher compilation, and HTML UI builds.", "cyan"),
                    ("Automated Unit Test Suite", "Full test suite validates 18/18 unit tests (migrator pipeline, socket RPC, network discovery, and file I/O) with 100% pass rate in under 2 seconds.", "green"),
                    ("Git LFS Binary Distribution", "Large binaries like JRFK.exe (162 MB) are tracked cleanly via Git LFS, keeping repository clones lightweight.", "amber")
                ],
                "feynman": "How was this built? Through modern AI automation! Using Google Gemini Pro and Antigravity, we automated the entire build and verification pipeline. Every release passes all 18 automated unit tests before a single byte touches production."
            },
            {
                "id": "slide_5",
                "badge": "JRFK SERIES • PART 4",
                "meta": "DEVELOPMENT AUDITING",
                "title": "Local Git & Complete Session Logging",
                "subtitle": "Saving and Synchronizing Every .jsonl Transcript for Full Auditability",
                "media_path": os.path.join(COOKBOOK_MEDIA, "img_042.jpeg"),
                "caption": "FIG 5: COMPLETE CONTROLLER ASSEMBLY & AUDIT CHECKPOINT",
                "cards": [
                    ("Permanent Session Audit Trails", "Every AI development turn, command execution, and test output is captured in structured .jsonl session logs.", "green"),
                    ("Committed to Git Repository", "Sanitized transcripts are checked directly into the git tree under session_logs/ for total transparency.", "cyan"),
                    ("Reproducible Engineering", "Any ham radio developer can clone the repository, review the exact steps taken, and build upon the work with zero guesswork.", "amber")
                ],
                "feynman": "In real science, you keep a laboratory notebook! Every step, command, and test result in this project is recorded in structured JSONL session logs and committed directly to Git. It's completely transparent, fully auditable, and reproducible."
            }
        ]
    },
    "Deck_5_Community_Mods": {
        "title": "Community-Proven B26 & RF2K-S Modifications",
        "slides": [
            {
                "id": "slide_1",
                "badge": "JRFK SERIES • PART 5",
                "meta": "COMMUNITY HARDENING GUIDE",
                "title": "Community-Proven B26 & RF2K-S Mods",
                "subtitle": "Consolidating What Actually Works: Thermal, RF Drive, and RFI Hardening",
                "media_path": os.path.join(COOKBOOK_MEDIA, "img_008.jpeg"),
                "caption": "FIG 1: RF PALLET WITH MACHINED LDMOS CLAMP BARS",
                "cards": [
                    ("Consolidating Community Wisdom", "Over years of contest and DX operation on groups.io, builders discovered crucial tweaks that dramatically increase reliability.", "cyan"),
                    ("Uncluttered & Proven", "Focusing on field-proven mechanical and electrical improvements with zero clutter.", "green"),
                    ("Master Table of Links", "Includes direct references and forum links so you can find parts and discussion threads instantly.", "amber")
                ],
                "feynman": "Welcome to Part 5! When thousands of ham radio operators build and run an amplifier, the collective community discovers what truly works. Today we consolidate the most critical, field-proven modifications for the B26 and RF2K-S—proven improvements that give you massive reliability headroom."
            },
            {
                "id": "slide_2",
                "badge": "JRFK SERIES • PART 5",
                "meta": "MOD 1: THERMAL MANAGEMENT",
                "title": "Mod 1: LDMOS Clamp Bars & Indium Foil",
                "subtitle": "Uniform Clamping Pressure and Permanent, Non-Degrading Heat Transfer",
                "media_path": os.path.join(COOKBOOK_MEDIA, "img_007.jpeg"),
                "caption": "FIG 2: CLOSE-UP OF CNC MACHINED LDMOS CLAMP BARS",
                "cards": [
                    ("CNC Machined Clamp Bars", "Replaces individual corner screws with solid clamp bars across the transistor flanges, eliminating package warping and localized hot-spots.", "green"),
                    ("0.1 mm Indium Metal Foil", "Replaces silicone thermal grease. Silicone grease dries and pumps out under repeated 50°C thermal cycles. Indium foil never degrades.", "cyan"),
                    ("Performance Impact", "Dramatically lower thermal resistance between LDMOS die and copper spreader; perfect for digital RTTY/FT8 contest duty.", "amber")
                ],
                "feynman": "Modification number one: thermal clamping! Individual screws can warp transistor flanges. A solid CNC clamp bar applies perfectly uniform pressure. And replacing silicone grease with 0.1 millimeter Indium foil stops grease pump-out forever—solid metal heat transfer that never degrades!"
            },
            {
                "id": "slide_3",
                "badge": "JRFK SERIES • PART 5",
                "meta": "MOD 2: RF INPUT OPTIMIZATION",
                "title": "Mod 2: The 16 dB Input Attenuator Pad",
                "subtitle": "Matching Modern 100W Transceivers to the LDMOS Linear Sweet Spot",
                "media_path": os.path.join(COOKBOOK_MEDIA, "img_141.jpeg"),
                "caption": "FIG 3: 16 DB ATTENUATOR UPGRADE BOARD AND RESISTOR NETWORK",
                "cards": [
                    ("The 13 dB vs 16 dB Problem", "Stock 13 dB attenuator requires very low drive (~20-25W) where modern 100W radios experience ALC overshoot, causing SWR trip spikes.", "amber"),
                    ("The 16 dB Solution", "Upgrading to a 16 dB pad lets your exciter run comfortably in its linear sweet spot: 45W to 55W drive for full 1500W PEP output.", "green"),
                    ("Transceiver Protection", "Provides an ideal 50-ohm broadband load back to the radio, completely eliminating input SWR trips during keying.", "cyan")
                ],
                "feynman": "Modification number two: the 16 dB input attenuator. Modern 100-watt transceivers hate putting out only twenty watts—their ALC circuits overshoot and spike the input! Swapping to a 16 dB pad lets your radio drive comfortably at fifty watts, right in its linear sweet spot."
            },
            {
                "id": "slide_4",
                "badge": "JRFK SERIES • PART 5",
                "meta": "MOD 3 & 4: FILTERS & COUPLERS",
                "title": "Mod 3 & 4: ATC Capacitors & Coupler Shielding",
                "subtitle": "Porcelain Dielectrics on 10/12/15m and Stray RF Coupler Isolation",
                "media_path": os.path.join(COOKBOOK_MEDIA, "img_010.jpeg"),
                "caption": "FIG 4: DIRECTIONAL COUPLER SWR BRIDGE & SENSING DIODES",
                "cards": [
                    ("ATC 100B / 100E Porcelain Caps", "Replace dipped mica capacitors on high-frequency LPF boards (10m, 12m, 15m) with high-voltage porcelain caps to prevent RF current breakdown.", "green"),
                    ("Directional Coupler Foil Shielding", "Adding copper/brass foil shielding partitions over the SWR coupler bridge stops stray magnetic fields from adjacent LPF coils.", "cyan"),
                    ("Eliminates False Trips", "Completely stops mysterious false high-SWR protection trips on 6m and 10m during full-power transmissions.", "amber")
                ],
                "feynman": "Mods three and four: low-pass filters and couplers! High RF circulating currents can crack standard mica capacitors on ten meters. Upgrading to ATC porcelain caps handles extreme RF current. And adding copper foil shielding over the SWR bridge stops false SWR trips on six meters!"
            },
            {
                "id": "slide_5",
                "badge": "JRFK SERIES • PART 5",
                "meta": "MOD 5: RFI HARDENING",
                "title": "Mod 5: Ferrite Choking on Display & Buses",
                "subtitle": "Suppressing Common-Mode RF Ingress on HDMI, USB, and I2C Lines",
                "media_path": os.path.join(COOKBOOK_MEDIA, "img_039.jpeg"),
                "caption": "FIG 5: 7-INCH DISPLAY HDMI & USB TOUCH INTERFACE CABLING",
                "cards": [
                    ("Mix 31 & Mix 43 Snap-On Ferrites", "Clamp split-bead ferrite chokes on the 7-inch HDMI display ribbon, USB touchscreen cable, and controller I2C wiring.", "green"),
                    ("Why It Works", "High-power legal-limit RF fields inside the shack can induce stray voltages on digital lines, causing touchscreen freezes.", "cyan"),
                    ("Shielded Pi Housing", "Mounting the Raspberry Pi in an all-aluminum shielded enclosure provides a solid RF Faraday cage.", "amber")
                ],
                "feynman": "Mod five: RFI hardening! When you have fifteen hundred watts radiating nearby, digital ribbon cables act like little antennas. Snapping Mix 31 and 43 ferrite beads onto the display and I2C cables keeps the RF out and prevents your touchscreen from ever freezing up."
            },
            {
                "id": "slide_6",
                "badge": "JRFK SERIES • PART 5",
                "meta": "MODIFICATION LINKS DIRECTORY",
                "title": "Master Table of Links for Every Mod",
                "subtitle": "Direct References, Part Sources, and Community Forum Threads",
                "media_path": None,
                "is_table": True,
                "table_html": """
                <table class="clean-table">
                    <thead>
                        <tr>
                            <th>Modification Name</th>
                            <th>Primary Purpose & Benefit</th>
                            <th>Forum / Discussion Link</th>
                            <th>Part / Material Source</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td><b>LDMOS Clamp Bar</b></td>
                            <td>Uniform clamping, stops flange warp</td>
                            <td>b26-pa.groups.io/g/main</td>
                            <td>CNC Machined Clamp Kit</td>
                        </tr>
                        <tr>
                            <td><b>0.1mm Indium Foil</b></td>
                            <td>Zero thermal pump-out @ >50°C</td>
                            <td>b26-pa.groups.io/g/main</td>
                            <td>Indium Corp 99.99% foil</td>
                        </tr>
                        <tr>
                            <td><b>16 dB Input Attenuator</b></td>
                            <td>50W linear drive sweet spot for 100W rigs</td>
                            <td>b26-pa.groups.io/g/main</td>
                            <td>High-power RF flange pad</td>
                        </tr>
                        <tr>
                            <td><b>ATC Porcelain LPF Caps</b></td>
                            <td>Prevents dielectric breakdown on 10/12/15m</td>
                            <td>b26-pa.groups.io/g/main</td>
                            <td>ATC 100B / 100E Capacitors</td>
                        </tr>
                        <tr>
                            <td><b>Coupler RF Shielding</b></td>
                            <td>Stops false 6m/10m high-SWR trips</td>
                            <td>b26-pa.groups.io/g/main</td>
                            <td>Copper foil partition / shield</td>
                        </tr>
                        <tr>
                            <td><b>Mix 31/43 Ferrite Chokes</b></td>
                            <td>Touchscreen / I2C RFI immunity</td>
                            <td>b26-pa.groups.io/g/main</td>
                            <td>Fair-Rite split snap-on beads</td>
                        </tr>
                        <tr>
                            <td><b>K7BIT Master Cookbook</b></td>
                            <td>193-page historical assembly reference</td>
                            <td>jbirdlebough1.github.io/JRFKTools</td>
                            <td>Vol 1 Reference (Preserved)</td>
                        </tr>
                    </tbody>
                </table>
                """,
                "cards": [
                    ("Quick Jump Directory", "Every modification is fully documented with direct links to groups.io forum threads and part sources.", "cyan"),
                    ("Cookbook Reference", "All underlying original circuit schematics and board layouts are indexed in the K7BIT Master Cookbook in the docs portal.", "green")
                ],
                "feynman": "Here is your master table of links! Every single modification we just covered—from the clamp bars and Indium foil to the 16 dB attenuator and ATC caps—is listed right here with direct references so you can find the parts and forum discussions instantly."
            }
        ]
    }
}

print("Generating all HTML slides and Feynman scripts...")

for deck_key, deck_data in DECKS.items():
    deck_dir = os.path.join(BASE_DIR, deck_key)
    os.makedirs(deck_dir, exist_ok=True)
    deck_title = deck_data["title"]
    
    script_lines = [f"# Richard Feynman Voiceover Script — {deck_title}\n\n"]
    
    slide_count = len(deck_data["slides"]) + 1 # +1 for outro
    
    for idx, slide in enumerate(deck_data["slides"], 1):
        slide_id = slide["id"]
        html_filename = f"{slide_id}.html"
        png_filename = f"{slide_id}.png"
        html_path = os.path.join(deck_dir, html_filename)
        png_path = os.path.join(deck_dir, png_filename)
        
        cards_html = ""
        for card_data in slide.get("cards", []):
            if len(card_data) == 4 and card_data[3]: # feynman note
                cards_html += f"""
                <div class="feynman-box">
                    <b>Feynman Insight:</b> {card_data[1]}
                </div>
                """
            else:
                title, desc, color = card_data[:3]
                color_class = "card-green" if color == "green" else ("card-amber" if color == "amber" else "")
                cards_html += f"""
                <div class="card {color_class}">
                    <div class="card-title">{title}</div>
                    <div class="card-desc">{desc}</div>
                </div>
                """
        
        if slide.get("is_table"):
            content_html = f"""
            <div style="flex:1; display:flex; flex-direction:column; gap:12px;">
                {slide.get('table_html', '')}
                <div style="display:flex; gap:16px;">
                    {cards_html}
                </div>
            </div>
            """
        else:
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
        
        print(f"[{deck_key}] Rendering {png_filename}...")
        capture_slide(html_path, png_path)
        
        feynman_narration = slide.get("feynman", "")
        script_lines.append(f"### Slide {idx}: {slide['title']}\n")
        script_lines.append(f"**Visual:** `{png_filename}`\n\n")
        script_lines.append(f"> **Feynman Avatar (Spoken Audio):**\n> \"{feynman_narration}\"\n\n---\n\n")
    
    # Add standardized Outro slide to each deck
    outro_idx = len(deck_data["slides"]) + 1
    outro_html_path = os.path.join(deck_dir, "slide_outro.html")
    outro_png_path = os.path.join(deck_dir, "slide_outro.png")
    
    with open(outro_html_path, "w", encoding="utf-8") as f:
        f.write(get_outro_slide(deck_data["title"].upper()))
    
    print(f"[{deck_key}] Rendering slide_outro.png...")
    capture_slide(outro_html_path, outro_png_path)
    
    script_lines.append(f"### Slide {outro_idx}: Master Resources & Downloads\n")
    script_lines.append(f"**Visual:** `slide_outro.png`\n\n")
    script_lines.append(f"> **Feynman Avatar (Spoken Audio):**\n> \"And that wraps up this briefing! Every link you need—the turnkey JRFK.exe download, the live web documentation portal on GitHub Pages, the full source repository, and the community forum—is right on your screen. Go ahead and grab the files, have fun experimenting, and 73 from the shack!\"\n\n---\n\n")
    
    # Write Feynman voiceover script file
    script_path = os.path.join(deck_dir, "FEYNMAN_VOICEOVER_SCRIPT.md")
    with open(script_path, "w", encoding="utf-8") as f:
        f.writelines(script_lines)
    print(f"[{deck_key}] Wrote {script_path}")

print("All 5 presentation decks and Feynman voiceover scripts compiled successfully!")
