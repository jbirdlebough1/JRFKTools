"""
JRFK Master Presentation Engine
Builds 720p (1280x720) Slide Decks and Technical Narration Scripts for Ham Radio Operators
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
.station-note-box {
    background: rgba(15, 23, 42, 0.95);
    border-left: 4px solid var(--accent-amber);
    padding: 9px 13px;
    border-radius: 0 6px 6px 0;
    font-size: 13px;
    color: #fef08a;
    line-height: 1.4;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
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

def get_outro_slide(deck_name):
    content_html = """
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
            <b>Ham Radio Station Notice:</b> All software and documentation are provided free and open source for the amateur radio community. 73 and good DX!
        </div>
    </div>
    """
    return render_slide_html(
        series_badge="JRFK STATION SUITE",
        meta_text="RESOURCES & COMMUNITY REPOSITORY",
        title="Project Resources & Reference Links",
        subtitle=f"Complete Downloads, Documentation, and Links for {deck_name}",
        content_html=content_html
    )

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


# Master Slide Deck Definitions
DECKS = {
    "Deck_1_Intro": {
        "title": "System Architecture & 64-Bit Leap",
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
                    ("Station Operating Note", "When delivering 1500W PEP on HF/6m, rock-solid controller stability and real-time protection loops are mandatory.", "amber", True)
                ],
                "narration": "Welcome to Part 1 of the JRFK technical overview. Today we look at modernizing the RF-KIT B26 and RF2K-plus linear amplifiers. Running 1500 watts PEP through dual LDMOS transistors requires an operating system that is fast, rock-solid, and completely dependable. Today we upgrade our amplifiers to pure 64-bit Debian Bookworm."
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
                "narration": "Legacy 32-bit Raspberry Pi OS installs have reached end of life. Deprecated Python 2 sockets, old video drivers, and unmaintained packages lead to display stutter and lockups during heavy RF keying. Debian Bookworm 64-bit provides modern memory management, Full KMS DRM display drivers, and a future-proof foundation."
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
                "narration": "A critical architectural improvement is port decoupling. The setup tool on your PC runs strictly on port 8089. The operational cockpit on the amplifier runs on port 8088. This clean separation guarantees that PC maintenance or network disconnects never interrupt live amplifier protection or RF transmission."
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
                "narration": "For station documentation, we have published a complete 4-volume engineering library covering operations, remote telemetry, and disaster recovery. In addition, John K7BIT's legendary 193-page cookbook is fully preserved in our documentation portal, giving builders complete access to original schematics and wiring layouts."
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
                    ("Station Operating Note", "The migrator runs deterministically with physical drive safety locks to eliminate any chance of corrupting system disks.", "amber", True)
                ],
                "narration": "Welcome to Part 2. In this guide, we walk step-by-step through the migration process. You do not need to install developer tools or manage Linux commands. A single turnkey executable, JRFK.exe, automates the entire migration while keeping your amplifier calibration data completely secure."
            },
            {
                "id": "slide_2",
                "badge": "JRFK SERIES • PART 2",
                "meta": "STEP 1: INSTALLATION & LAUNCH",
                "title": "Download & Run JRFK.exe",
                "subtitle": "Self-Contained Executable with Integrated Windows Safety & Elevation",
                "media_path": os.path.join(COOKBOOK_MEDIA, "img_110.jpeg"),
                "caption": "FIG 2: JRFK DESKTOP CONTROLLER INITIALIZATION",
                "cards": [
                    ("Single File Executable", "Contains embedded web dashboard, flash engine, discovery tools, and recovery scripts in one 166MB package.", "cyan"),
                    ("Windows 11 Suppressor", "Automatically bypasses annoying Windows 11 format prompts when unpartitioned raw SD cards are inserted.", "green"),
                    ("One-Click Access", "Automatically launches your default browser to http://127.0.0.1:8089 with Administrator rights.", "amber")
                ],
                "narration": "Step 1 is downloading and launching JRFK.exe. Our launcher manages Windows UAC elevation, suppresses Windows unformatted drive prompts, and opens your browser directly to the migration dashboard on port 8089."
            },
            {
                "id": "slide_3",
                "badge": "JRFK SERIES • PART 2",
                "meta": "STEP 2: PRE-FLIGHT VERIFICATION",
                "title": "Pre-Flight Checks & Safety Isolation",
                "subtitle": "Automatic Network Discovery, Target Validation, and Flash Protection",
                "media_path": os.path.join(COOKBOOK_MEDIA, "img_105.jpeg"),
                "caption": "FIG 3: NETWORK CONTROLLER SCANNING & PRE-FLIGHT CHECKS",
                "cards": [
                    ("Subnet Discovery", "Scans your local LAN to locate the RF-KIT controller by MAC address and hostname.", "cyan"),
                    ("Firmware Validation", "Validates the existing configuration, band settings, and custom calibration constants.", "green"),
                    ("Strict Drive Locking", "Requires explicit multi-factor confirmation before writing to physical target cards.", "amber")
                ],
                "narration": "Before writing any data, the migrator performs pre-flight verification. It scans your local subnet, locates the amplifier controller, verifies communication, and validates your target SD card with physical drive safety locks."
            },
            {
                "id": "slide_4",
                "badge": "JRFK SERIES • PART 2",
                "meta": "STEP 3: IMAGE FLASH & CONFIG",
                "title": "Flashing 64-Bit OS & Injecting Drivers",
                "subtitle": "Writing Debian Bookworm, 1024x600 Video Modeline, and SimpleRPC",
                "media_path": os.path.join(COOKBOOK_MEDIA, "img_126.jpeg"),
                "caption": "FIG 4: HARDWARE-ACCELERATED FULL KMS VIDEO DRIVER INJECTION",
                "cards": [
                    ("Automated OS Flashing", "Writes clean 64-bit Debian Bookworm base image directly to the target SD card with SHA-256 integrity verification.", "green"),
                    ("Driver & Modeline Injection", "Injects native 1024x600 video modelines directly into /boot/firmware/cmdline.txt for touch precision.", "cyan"),
                    ("Calibration Migration", "Transfers all your existing band tables and SWR calibration offsets automatically.", "amber")
                ],
                "narration": "During the flash step, the migrator writes 64-bit Debian Bookworm, injects the exact 1024 by 600 video modelines for the built-in touchscreen, and automatically migrates your existing band tables and calibration constants."
            },
            {
                "id": "slide_5",
                "badge": "JRFK SERIES • PART 2",
                "meta": "STEP 4: DISASTER RECOVERY",
                "title": "The 3-Minute Disaster Recovery Card",
                "subtitle": "Pre-Provisioned Hot-Swap Backup SD Card for Zero Shack Downtime",
                "media_path": os.path.join(COOKBOOK_MEDIA, "img_002.jpeg"),
                "caption": "FIG 5: RF-KIT INTERNAL CONTROLLER COMPARTMENT & SD CARD SLOT",
                "cards": [
                    ("Redundant Standby Card", "The migrator provisions an identical secondary SD card containing your full 64-bit OS and calibration files.", "green"),
                    ("Hot-Swap Simplicity", "If your primary SD card ever fails during a contest, swap in the backup card and boot in under three minutes.", "cyan"),
                    ("Zero Re-Configuration", "All IP addresses, touch calibration, and amplifier constants are pre-baked into the standby card.", "amber")
                ],
                "narration": "To ensure maximum station uptime, JRFK provisions a secondary disaster recovery SD card. If an SD card ever fails during a major contest, simply swap in the backup card and your amplifier is back on the air in under three minutes."
            }
        ]
    },
    "Deck_3_Operations": {
        "title": "7-Screen Operational Web Suite",
        "slides": [
            {
                "id": "slide_1",
                "badge": "JRFK SERIES • PART 3",
                "meta": "OPERATIONAL COCKPIT OVERVIEW",
                "title": "The 7-Screen Amplifier Web Cockpit",
                "subtitle": "Complete Browser Telemetry: Why, What, and How to Operate",
                "media_path": PI_SCREEN,
                "caption": "FIG 1: MAIN RF DASHBOARD LIVE TELEMETRY DISPLAY (1024x600)",
                "cards": [
                    ("Shack-Wide Accessibility", "Access every single amplifier control and meter from any PC, tablet, or smartphone on your home network.", "cyan"),
                    ("Sub-Millisecond Polling", "Real-time Forward Power, Reflected Power, Peak Envelope Power (PEP), and instant SWR arc response.", "green"),
                    ("Station Operating Note", "Continuous forward and reflected power telemetry gives you instant insight into antenna match and transmission line health.", "amber", True)
                ],
                "narration": "Welcome to Part 3. In this video, we review the 7-screen operational web suite running on port 8088. This cockpit gives you complete real-time telemetry, meter monitoring, and control from any browser in your shack."
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
                "narration": "Screen 1 is your main operational dashboard, displaying real-time forward power, reflected power, and SWR. Screen 2 displays the low-pass filter band matrix, tracking transceiver frequency via CAT control with active hot-switch lockout."
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
                "narration": "Screen 3 monitors power amplifier telemetry: 53.5V rail voltage, drain current, and heatsink temperature. Screen 4 controls the 4-port antenna matrix, automatically selecting your preferred antenna port for each band."
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
                "narration": "Screen 5 manages amplifier protection. If high SWR exceeds 2.5 to 1 or excessive drive power is detected, the hardware protection loop trips into standby in microseconds, protecting your LDMOS transistors from damage."
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
                "narration": "Screens 6 and 7 provide system diagnostics and touchscreen alignment. Screen 6 displays real-time SimpleRPC controller logs, while Screen 7 provides a 5-point touch calibration utility for the 1024 by 600 front-panel display."
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
                "subtitle": "Architectural Solution, Kernel Modelines, and Build Automation",
                "media_path": os.path.join(COOKBOOK_MEDIA, "img_148.jpeg"),
                "caption": "FIG 1: CONTROLLER HARDWARE & ARDUINO/RPI BUS ARCHITECTURE",
                "cards": [
                    ("Slide-Only Technical Briefing", "An exhaustive master briefing for builders, developers, and software engineers modernizing RF-KIT linear amplifiers.", "cyan"),
                    ("Under the Hood", "Video DRM KMS drivers, SimpleRPC asynchronous patches, discrete sensing DC rails, and full build automation.", "green"),
                    ("Station Operating Note", "A transparent, modular software architecture ensures that kit maintainers can audit and maintain their station software long term.", "amber", True)
                ],
                "narration": "Welcome to Part 4, our technical engineering briefing. In this session, we examine the underlying software architecture: Linux Full KMS display drivers, Python SimpleRPC deprecation patches, discrete DC sensing, and automated build verification."
            },
            {
                "id": "slide_2",
                "badge": "JRFK SERIES • PART 4",
                "meta": "DRIVER & KERNEL LAYER",
                "title": "Full KMS DRM Video & SimpleRPC Patches",
                "subtitle": "Resolving 1024x600 Display Modelines and Python 3.13 Deprecations",
                "media_path": os.path.join(COOKBOOK_MEDIA, "img_135.jpeg"),
                "caption": "FIG 2: FULL KMS KERNEL VIDEO DRIVER TESTING",
                "cards": [
                    ("Video Modeline Fix", "Injected kernel command line video=HDMI-A-1:1024x600M@60D to permanently resolve display blanking.", "green"),
                    ("Python SimpleRPC Modernization", "Patched legacy async socket handlers to comply with modern Python 3.11 through 3.13 standards.", "cyan"),
                    ("Systemd Services", "Native systemd unit files replace fragile rc.local background scripts for robust automatic recovery.", "amber")
                ],
                "narration": "On the driver layer, we resolved legacy display blanking by injecting custom 1024 by 600 kernel modelines into Full KMS DRM. We also modernized SimpleRPC socket communications and replaced fragile background scripts with systemd service units."
            },
            {
                "id": "slide_3",
                "badge": "JRFK SERIES • PART 4",
                "meta": "ELECTRICAL CHARACTERISTICS",
                "title": "Hardware Truth: Dual BLF189 & Discrete DC",
                "subtitle": "The True Architecture: RF-KIT Does NOT Use CAN Bus Power Supplies",
                "media_path": os.path.join(COOKBOOK_MEDIA, "img_006.jpeg"),
                "caption": "FIG 3: DISCRETE ANALOG VOLTAGE SHUNT & SENSOR WIRING",
                "cards": [
                    ("Dual Ampleon BLF189 LDMOS", "Provides 1500W PEP output across 160m through 6m with massive linearity headroom.", "green"),
                    ("NO CAN Bus Power Supplies", "Voltage and current telemetry use direct discrete analog sensing—no complex CAN bus handshakes or crashes.", "amber"),
                    ("Rugged Reliability", "Analog shunts feed directly into the Arduino controller ADC with hardware comparator interrupts.", "cyan")
                ],
                "narration": "For clarity on hardware architecture: the RF-KIT amplifier utilizes dual Ampleon BLF189 LDMOS devices and does NOT use CAN bus power supplies. Voltage and current telemetry are read via discrete analog shunts directly into the controller ADC, delivering rugged and crash-free DC monitoring."
            },
            {
                "id": "slide_4",
                "badge": "JRFK SERIES • PART 4",
                "meta": "DEVELOPMENT AUTOMATION",
                "title": "Automated Build & Test Pipeline",
                "subtitle": "Continuous Integration, 18 Unit Tests, and Regression Prevention",
                "media_path": os.path.join(COOKBOOK_MEDIA, "img_153.jpeg"),
                "caption": "FIG 4: JRFK AUTOMATED UNIT TEST RUNNER PASSING 18/18 SUITES",
                "cards": [
                    ("18-Point Test Suite", "Every commit is verified against 18 automated unit tests covering port safety, disk guard, and modeline syntax.", "green"),
                    ("Zero Developer Workstation", "All builds and tests execute headlessly on Windows with complete end-to-end regression prevention.", "cyan"),
                    ("Production Grade", "Guarantees zero regressions in SimpleRPC communication, network scanning, or SD image formatting.", "amber")
                ],
                "narration": "To guarantee reliable operation, every build passes an 18-point automated test suite covering network discovery, physical disk guard safety locks, video modeline syntax, and SimpleRPC protocol handlers before release."
            },
            {
                "id": "slide_5",
                "badge": "JRFK SERIES • PART 4",
                "meta": "STATION AUDITABILITY",
                "title": "Local Version Control & Session Logging",
                "subtitle": "Deterministic Reproducibility and Complete Session History",
                "media_path": os.path.join(COOKBOOK_MEDIA, "img_150.jpeg"),
                "caption": "FIG 5: LOCAL GIT HISTORY & STRUCTURED SESSION LOG ARCHIVE",
                "cards": [
                    ("Local Git Tracking", "All source changes, scripts, and documentation updates are committed locally for total revision control.", "green"),
                    ("Session Transcript Archive", "Complete prompt and execution history preserved in structured JSONL session records.", "cyan"),
                    ("Offline Autonomy", "No cloud dependencies required—the entire station toolchain runs 100% locally.", "amber")
                ],
                "narration": "All changes and development sessions are tracked in local Git repositories and structured session logs. The entire build, testing, and migration suite is 100% local with zero cloud dependencies."
            }
        ]
    },
    "Deck_5_Community_Mods": {
        "title": "Hardware Modifications & Station Hardening",
        "slides": [
            {
                "id": "slide_1",
                "badge": "JRFK SERIES • PART 5",
                "meta": "COMMUNITY BEST PRACTICES",
                "title": "Essential Hardware Modifications",
                "subtitle": "Field-Tested Enhancements for Maximum Reliability & Longevity",
                "media_path": os.path.join(COOKBOOK_MEDIA, "img_005.jpeg"),
                "caption": "FIG 1: RF PALLET ASSEMBLY WITH COMMUNITY THERMAL CLAMPS",
                "cards": [
                    ("Community Experience", "Consolidating years of real-world operational experience from thousands of active RF-KIT builders worldwide.", "cyan"),
                    ("Thermal & RF Protection", "Proven modifications addressing thermal transfer, input overdrive, harmonic filtering, and RFI hardening.", "green"),
                    ("Station Operating Note", "Field-proven thermal and RFI modifications significantly increase operating reliability during continuous high-duty-cycle operation.", "amber", True)
                ],
                "narration": "Welcome to Part 5. In this presentation, we cover the top hardware modifications and hardening techniques proven by the worldwide amateur radio community to maximize the reliability of the B26 and RF2K-plus amplifiers."
            },
            {
                "id": "slide_2",
                "badge": "JRFK SERIES • PART 5",
                "meta": "THERMAL MODIFICATIONS",
                "title": "Thermal Clamps & Indium Foil",
                "subtitle": "Eliminating Transistor Flange Warping and Grease Pump-Out",
                "media_path": os.path.join(COOKBOOK_MEDIA, "img_008.jpeg"),
                "caption": "FIG 2: CNC SOLID CLAMP BAR & INDIUM HEAT SINK INTERFACE",
                "cards": [
                    ("CNC Solid Clamp Bar", "Replaces individual screw tension with uniform pressure across the entire transistor flange to prevent warping.", "green"),
                    ("0.1mm Indium Metal Foil", "Replaces silicone thermal grease. Eliminates thermal pump-out forever with pure metallic heat conduction.", "cyan"),
                    ("Thermal Results", "Reduces full-load junction temperature by 8°C to 12°C during high-duty-cycle digital modes (FT8/RTTY).", "amber")
                ],
                "narration": "Modification 1 covers thermal dissipation. Installing a CNC solid clamp bar provides uniform pressure across the transistor flange, while replacing silicone grease with 0.1 millimeter Indium foil eliminates thermal pump-out and lowers operating temperatures by up to 12 degrees Celsius."
            },
            {
                "id": "slide_3",
                "badge": "JRFK SERIES • PART 5",
                "meta": "RF DRIVE PROTECTION",
                "title": "16 dB Input Attenuator Upgrade",
                "subtitle": "Protecting LDMOS Gates from Modern Transceiver ALC Power Spikes",
                "media_path": os.path.join(COOKBOOK_MEDIA, "img_023.jpeg"),
                "caption": "FIG 3: 16 DB INPUT ATTENUATOR PAD ON RF DRIVER BOARD",
                "cards": [
                    ("The Problem: ALC Overshoot", "Modern 100W transceivers produce brief 80W power spikes before ALC loops settle, overdriving LDMOS gates.", "amber"),
                    ("The Solution: 16 dB Pad", "Increases drive requirement to a comfortable 50W, placing transceivers in their cleanest, most linear power zone.", "green"),
                    ("Purity & Linearity", "Eliminates input clipping, lowers transmitter phase noise, and ensures clean IMD3 performance.", "cyan")
                ],
                "narration": "Modification 2 is the 16 dB input attenuator. Modern 100-watt transceivers can produce brief power spikes before internal ALC loops settle. A 16 dB pad allows your transceiver to drive at 50 watts in its cleanest linear operating range while protecting the amplifier input."
            },
            {
                "id": "slide_4",
                "badge": "JRFK SERIES • PART 5",
                "meta": "LPF & COUPLER HARDENING",
                "title": "LPF ATC Capacitors & Coupler Shielding",
                "subtitle": "Handling Circulating RF Currents and Eliminating 6m SWR Trips",
                "media_path": os.path.join(COOKBOOK_MEDIA, "img_077.jpeg"),
                "caption": "FIG 4: LOW PASS FILTER BOARD WITH UPGRADED ATC CAPACITORS",
                "cards": [
                    ("High-Q ATC Porcelain Caps", "Replaces standard mica capacitors on 10m/12m filter sections to handle severe circulating RF currents.", "green"),
                    ("Directional Coupler Shield", "Adds grounded copper foil shielding over the SWR bridge to eliminate stray RF pickup on 6 meters.", "cyan"),
                    ("Reliability Benefit", "Prevents dielectric breakdown, eliminates filter detuning, and stops nuisance SWR fault trips.", "amber")
                ],
                "narration": "Modifications 3 and 4 harden the low-pass filter and SWR coupler. Upgrading to high-Q ATC porcelain capacitors handles high circulating RF currents on 10 and 12 meters, while copper foil shielding over the directional coupler prevents stray RF pickup on 6 meters."
            },
            {
                "id": "slide_5",
                "badge": "JRFK SERIES • PART 5",
                "meta": "STATION RFI HARDENING",
                "title": "Ferrite Decoupling & RFI Hardening",
                "subtitle": "Suppressing RF Ground Loops and Protecting Ribbon Cable Buses",
                "media_path": os.path.join(COOKBOOK_MEDIA, "img_104.jpeg"),
                "caption": "FIG 5: MIX 31 & MIX 43 FERRITE CORES APPLIED TO CABLES",
                "cards": [
                    ("Display Ribbon Protection", "Mix 31 ferrite clamp chokes on the HDMI and touch controller ribbon cables eliminate touchscreen lockups.", "green"),
                    ("I2C & Serial Line Chokes", "Mix 43 beads on telemetry buses block stray common-mode RF from entering the Raspberry Pi and Arduino.", "cyan"),
                    ("Chassis Bonding", "Star-ground bonding between the controller chassis, RF deck, and power supply minimizes RF loops.", "amber")
                ],
                "narration": "Modification 5 addresses station RFI hardening. Installing Mix 31 and Mix 43 ferrite beads on HDMI and sensor ribbon cables prevents common-mode RF currents from locking up the touchscreen or disrupting telemetry during legal-limit transmission."
            },
            {
                "id": "slide_6",
                "badge": "JRFK SERIES • PART 5",
                "meta": "PARTS & MODIFICATION DIRECTORY",
                "title": "Community Hardware Modifications Directory",
                "subtitle": "Summary Table of Proven Enhancements, Components, and Benefits",
                "is_table": True,
                "table_html": """
                <table class="clean-table">
                    <thead>
                        <tr>
                            <th>Modification Name</th>
                            <th>Target Area</th>
                            <th>Recommended Components</th>
                            <th>Primary Benefit</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td><b>Solid Thermal Clamp</b></td>
                            <td>LDMOS Pallet</td>
                            <td>CNC Aluminum Clamp Bar + Indium Foil (0.1mm)</td>
                            <td>Uniform flange pressure; eliminates grease pump-out</td>
                        </tr>
                        <tr>
                            <td><b>16 dB Input Pad</b></td>
                            <td>RF Input Stage</td>
                            <td>High-power 16 dB attenuator pad</td>
                            <td>Transceiver ALC overshoot protection; cleaner IMD3</td>
                        </tr>
                        <tr>
                            <td><b>ATC Filter Caps</b></td>
                            <td>LPF Board</td>
                            <td>High-Q ATC 100B / 800B porcelain capacitors</td>
                            <td>Handles high circulating RF current on 10m/12m</td>
                        </tr>
                        <tr>
                            <td><b>Coupler Shielding</b></td>
                            <td>SWR Bridge</td>
                            <td>Adhesive copper foil shield, bonded to chassis</td>
                            <td>Stops stray 6m RF pickup & false SWR trips</td>
                        </tr>
                        <tr>
                            <td><b>Ferrite Chokes</b></td>
                            <td>Data / Video Cables</td>
                            <td>Fair-Rite Mix 31 & Mix 43 snap-on cores</td>
                            <td>Eliminates touchscreen lockups & common-mode RFI</td>
                        </tr>
                    </tbody>
                </table>
                """,
                "cards": [
                    ("Field-Tested Solutions", "Every modification listed here has been validated by active amateur radio operators in high-power station environments.", "green"),
                    ("Full Documentation", "Detailed installation schematics and component suppliers are indexed in the JRFK Documentation Portal.", "cyan")
                ],
                "narration": "This reference table summarizes all five community modifications: solid thermal clamping, 16 dB input padding, ATC porcelain capacitors, coupler shielding, and ferrite decoupling. Full installation details and component sources are available in our documentation portal."
            }
        ]
    }
}

def main():
    print("Compiling all 5 presentation decks with Ham Radio technical narration...")

    for deck_key, deck_data in DECKS.items():
        deck_dir = os.path.join(BASE_DIR, deck_key)
        os.makedirs(deck_dir, exist_ok=True)
        deck_title = deck_data["title"]
        
        script_lines = [f"# Technical Narration Script — {deck_title}\n\n"]
        
        slide_count = len(deck_data["slides"]) + 1 # +1 for outro
        
        for idx, slide in enumerate(deck_data["slides"], 1):
            slide_id = slide["id"]
            html_filename = f"{slide_id}.html"
            png_filename = f"{slide_id}.png"
            html_path = os.path.join(deck_dir, html_filename)
            png_path = os.path.join(deck_dir, png_filename)
            
            cards_html = ""
            for card_data in slide.get("cards", []):
                if len(card_data) == 4 and card_data[3]: # station operating note
                    cards_html += f"""
                    <div class="station-note-box">
                        <b>Station Operating Note:</b> {card_data[1]}
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
            
            narration_text = slide.get("narration", "")
            script_lines.append(f"### Slide {idx}: {slide['title']}\n")
            script_lines.append(f"**Visual:** `{png_filename}`\n\n")
            script_lines.append(f"> **Technical Narration (Spoken Audio):**\n> \"{narration_text}\"\n\n---\n\n")
        
        # Add standardized Outro slide to each deck
        outro_idx = len(deck_data["slides"]) + 1
        outro_html_path = os.path.join(deck_dir, "slide_outro.html")
        outro_png_path = os.path.join(deck_dir, "slide_outro.png")
        
        with open(outro_html_path, "w", encoding="utf-8") as f:
            f.write(get_outro_slide(deck_data["title"].upper()))
        
        print(f"[{deck_key}] Rendering slide_outro.png...")
        capture_slide(outro_html_path, outro_png_path)
        
        outro_narration = "This concludes our presentation. All project resources—including the turnkey JRFK executable, documentation portal, source code, and community discussions—are available at the links shown on your screen. Thank you for watching, and 73 from the station."
        script_lines.append(f"### Slide {outro_idx}: Master Resources & Downloads\n")
        script_lines.append(f"**Visual:** `slide_outro.png`\n\n")
        script_lines.append(f"> **Technical Narration (Spoken Audio):**\n> \"{outro_narration}\"\n\n---\n\n")
        
        # Write updated narration script file
        script_path = os.path.join(deck_dir, "TECHNICAL_NARRATION_SCRIPT.md")
        with open(script_path, "w", encoding="utf-8") as f:
            f.writelines(script_lines)
        
        # Remove old Feynman script file if present
        old_feynman_file = os.path.join(deck_dir, "FEYNMAN_VOICEOVER_SCRIPT.md")
        if os.path.exists(old_feynman_file):
            os.remove(old_feynman_file)
            
        print(f"[{deck_key}] Wrote {script_path}")

    print("All 5 presentation decks compiled successfully with Ham Radio narration!")

if __name__ == "__main__":
    main()

