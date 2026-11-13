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

# Master Blueprint Layout Template
# For Slide 1 & 2: Bullets layout
# For Slides 3+: Screen-focused layout (Full width 1830px screen with overlay control panel, zero bullets)

TEMPLATE_BULLETS = """<!DOCTYPE html>
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
        padding: 30px 45px;
        border: 4px solid #93c5fd;
    }
    .master-header {
        width: 1830px;
        border-bottom: 3px solid #93c5fd;
        padding-bottom: 12px;
        display: flex;
        justify-content: space-between;
        align-items: flex-end;
        background: rgba(26, 86, 149, 0.90);
        padding-left: 10px;
        padding-right: 10px;
    }
    .header-left { display: flex; flex-direction: column; gap: 3px; }
    .header-tagline {
        font-family: "Consolas", monospace;
        font-size: 14px;
        letter-spacing: 2px;
        color: #93c5fd;
        text-transform: uppercase;
        font-weight: 700;
    }
    .header-title {
        font-size: 34px;
        font-weight: 900;
        letter-spacing: -0.5px;
        color: #ffffff;
        text-shadow: 0 2px 8px rgba(0, 0, 0, 0.6);
    }
    .header-subtitle { font-size: 16px; color: #bfdbfe; font-weight: 500; }
    .header-right {
        text-align: right;
        font-family: "Consolas", monospace;
        font-size: 15px;
        color: #ffffff;
        letter-spacing: 1.5px;
        font-weight: bold;
        background: #0284c7;
        padding: 8px 18px;
        border-radius: 4px;
        border: 1px solid #93c5fd;
    }
    .master-body {
        width: 1830px;
        height: 870px;
        display: flex;
        gap: 20px;
        margin: 12px 0;
    }
    .col-one-third {
        width: 600px;
        flex-shrink: 0;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        gap: 8px;
    }
    .bullet-card {
        background: rgba(15, 45, 85, 0.95);
        border: 2px solid #93c5fd;
        border-left: 6px solid #60a5fa;
        border-radius: 6px;
        padding: 12px 16px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
    }
    .bullet-title {
        font-size: 16px;
        font-weight: 800;
        color: #ffffff;
        margin-bottom: 4px;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .bullet-title::before { content: "►"; color: #93c5fd; font-size: 12px; }
    .bullet-desc { font-size: 14px; line-height: 1.4; color: #e0f2fe; }
    .col-two-thirds {
        width: 1210px;
        flex-shrink: 0;
        display: flex;
        flex-direction: column;
        justify-content: center;
        gap: 10px;
    }
    .graphic-frame {
        width: 1210px;
        background: rgba(10, 30, 60, 0.95);
        border: 3px solid #93c5fd;
        border-radius: 8px;
        padding: 8px;
        display: flex;
        justify-content: center;
        align-items: center;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.6);
        max-height: 820px;
        overflow: hidden;
    }
    .graphic-frame img { width: 100%; max-height: 780px; border-radius: 4px; display: block; object-fit: contain; }
    .graphic-caption {
        font-family: "Consolas", monospace;
        font-size: 13px;
        color: #93c5fd;
        text-align: center;
        font-weight: 700;
        letter-spacing: 1px;
        background: rgba(15, 45, 85, 0.95);
        padding: 4px 8px;
        border-radius: 4px;
        border: 1px solid rgba(147, 197, 253, 0.5);
    }
    .master-footer {
        width: 1830px;
        border-top: 2px solid #93c5fd;
        padding-top: 8px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-family: "Consolas", monospace;
        font-size: 12px;
        color: #bfdbfe;
        background: rgba(26, 86, 149, 0.90);
        padding-left: 10px;
        padding-right: 10px;
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
            <div>CALLSIGN: K7BIT</div>
            <div>SLIDE {{SLIDE_NUM}} OF {{TOTAL_SLIDES}}</div>
        </div>
    </div>
    <div class="master-body">
        <div class="col-one-third">
            {{BULLETS_HTML}}
        </div>
        <div class="col-two-thirds">
            {{GRAPHICS_HTML}}
        </div>
    </div>
    <div class="master-footer">
        <div class="footer-left">JRFK 64-BIT MODERNIZATION SUITE • HIGH-POWER AMATEUR RADIO • K7BIT</div>
        <div class="footer-right">GITHUB.COM/BIRDIEBOUGHT/JRFKTOOLS</div>
    </div>
</body>
</html>
"""

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
        padding: 24px 35px;
        border: 4px solid #93c5fd;
    }
    .master-header {
        width: 1850px;
        border-bottom: 3px solid #93c5fd;
        padding-bottom: 10px;
        display: flex;
        justify-content: space-between;
        align-items: flex-end;
        background: rgba(26, 86, 149, 0.92);
        padding-left: 10px;
        padding-right: 10px;
    }
    .header-left { display: flex; flex-direction: column; gap: 2px; }
    .header-tagline {
        font-family: "Consolas", monospace;
        font-size: 13px;
        letter-spacing: 2px;
        color: #93c5fd;
        text-transform: uppercase;
        font-weight: 700;
    }
    .header-title {
        font-size: 32px;
        font-weight: 900;
        letter-spacing: -0.5px;
        color: #ffffff;
        text-shadow: 0 2px 8px rgba(0, 0, 0, 0.6);
    }
    .header-subtitle { font-size: 15px; color: #bfdbfe; font-weight: 500; }
    .header-right {
        text-align: right;
        font-family: "Consolas", monospace;
        font-size: 14px;
        color: #ffffff;
        letter-spacing: 1.5px;
        font-weight: bold;
        background: #0284c7;
        padding: 6px 16px;
        border-radius: 4px;
        border: 1px solid #93c5fd;
    }
    .master-body-fullscreen {
        width: 1850px;
        height: 890px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        gap: 8px;
        margin: 8px 0;
    }
    .graphic-frame-full {
        width: 1850px;
        height: 840px;
        background: rgba(10, 30, 60, 0.95);
        border: 3px solid #93c5fd;
        border-radius: 8px;
        padding: 6px;
        display: flex;
        justify-content: center;
        align-items: center;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.6);
        overflow: hidden;
    }
    .graphic-frame-full img {
        width: 100%;
        height: 100%;
        border-radius: 4px;
        display: block;
        object-fit: contain;
    }
    .graphic-caption-full {
        width: 1850px;
        font-family: "Consolas", monospace;
        font-size: 14px;
        color: #93c5fd;
        text-align: center;
        font-weight: 700;
        letter-spacing: 1px;
        background: rgba(15, 45, 85, 0.95);
        padding: 6px 12px;
        border-radius: 4px;
        border: 1px solid rgba(147, 197, 253, 0.5);
    }
    .master-footer {
        width: 1850px;
        border-top: 2px solid #93c5fd;
        padding-top: 8px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-family: "Consolas", monospace;
        font-size: 12px;
        color: #bfdbfe;
        background: rgba(26, 86, 149, 0.90);
        padding-left: 10px;
        padding-right: 10px;
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
            <div>CALLSIGN: K7BIT</div>
            <div>SLIDE {{SLIDE_NUM}} OF {{TOTAL_SLIDES}}</div>
        </div>
    </div>
    <div class="master-body-fullscreen">
        <div class="graphic-frame-full">
            <img src="{{IMAGE_SRC}}" alt="{{TITLE}}">
        </div>
        <div class="graphic-caption-full">{{CAPTION}}</div>
    </div>
    <div class="master-footer">
        <div class="footer-left">JRFK 64-BIT MODERNIZATION SUITE • HIGH-POWER AMATEUR RADIO • K7BIT</div>
        <div class="footer-right">GITHUB.COM/BIRDIEBOUGHT/JRFKTOOLS</div>
    </div>
</body>
</html>
"""

# Complete 20 Slide Definition
# Slide 1 & 2: Intro & Architecture Overview
# Slides 3 to 7: Migration in 5 deep-dive slides (Zero bullets, full screen graphics, technical discussion of controls)
# Slides 8 to 20: JRFK Web Tools deep-dive slides (Zero bullets, full screen graphics, discussion of each page's controls)
SLIDES = [
    # -------------------------------------------------------------
    # SLIDE 1: INTRO (THE 4 CORE TOPICS)
    # -------------------------------------------------------------
    {
        "type": "bullets",
        "part": "PART 1: SYSTEM INTRO",
        "category": "JRFK MODERNIZATION SUITE • ARCHITECTURAL OVERVIEW",
        "title": "JRFK 32-to-64 Bit Migration & Web Tools",
        "subtitle": "Modernizing RFK Linear Amplifiers to Current 64-Bit Debian Trixie on RPi 4 & 5",
        "bullets": [
            ("32-Bit RPi OS Obsolete", "Thirty-two-bit Raspberry Pi OS is obsolete, unmaintained, and reaches end-of-life across Linux distributions."),
            ("RFK Amp Owners at Risk", "Leaves RFK amplifier owners at serious risk from unpatched kernel bugs, security gaps, and SD card failure."),
            ("64-Bit Trixie Migration", "The JRFK 32-bit to 64-bit Migration and Web Tools enable seamless migration to current 64-bit Raspberry Pi 4 or 5 Debian Trixie."),
            ("Concurrent Web Tools", "JRFK Web Tools run concurrently on any web-capable platform with the original RFK application via port 8088.")
        ],
        "image": "tool0_portal_main.png",
        "caption": "JRFK MODERNIZATION SUITE: CONCURRENT 64-BIT ARCHITECTURE & BLUEPRINT WEB TOOLS",
        "narration": "Thirty-two-bit Raspberry Pi O S is obsolete. This leaves R F kit amplifier owners at risk. The J R F K thirty-two-bit to sixty-four-bit Migration and J R F K Web Tools enable users to migrate from obsolete systems to current sixty-four-bit Raspberry Pi four or five Debian Trixie. J R F K Web Tools run concurrently on any web capable platform with the original R F kit application."
    },
    # -------------------------------------------------------------
    # SLIDE 2: SUITE ARCHITECTURE & WEB PORTAL
    # -------------------------------------------------------------
    {
        "type": "fullscreen",
        "part": "PART 1: SYSTEM INTRO",
        "category": "WEB TOOLS PORTAL • PORT 8088 BLUEPRINT DASHBOARD",
        "title": "JRFK Web Tools: Unified Station Portal",
        "subtitle": "Access all amplifier telemetry, matrix routing, and diagnostics simultaneously over port 8088",
        "image": "intro_portal_overview.png",
        "caption": "PORT 8088 BLUEPRINT PORTAL: DIRECT ACCESS TO HEALTH, ANTENNA MATRIX, BACKUPS, LOGS & DOCS",
        "narration": "Here is the master blueprint portal running live on port eighty eighty-eight. It displays the complete J R F K Web Tools suite, providing direct tiles to the Health Guard, Antenna Matrix, S D Backup Manager, System Report, Diagnostic Logs, Documentation Library, and live front panel screen streamer. Everything runs simultaneously in the background without disturbing the amplifier front display."
    },
    # -------------------------------------------------------------
    # SLIDE 3: MIGRATION 1 - DISCOVERY & DRIVE GUARD
    # -------------------------------------------------------------
    {
        "type": "fullscreen",
        "part": "PART 2: MIGRATION TOOL",
        "category": "MIGRATION DEEP-DIVE 1 OF 5 • DISK DISCOVERY & DRIVE GUARD",
        "title": "Migrator: Original SD Discovery & Drive Guard",
        "subtitle": "Automated disk enumeration, safe drive locking, and raw ext4 partition mounting",
        "image": "migrator_step1_discovery.png",
        "caption": "MIGRATOR STEP 1: PHYSICAL DRIVE ENUMERATION, DRIVE GUARD PROTECTION, AND EXT4 DISCOVERY",
        "narration": "Covering the migration suite starting with step one of the J R F K Migrator console. On the upper left, the Drive Guard engine scans connected storage buses and locks out your primary Windows system disks to eliminate any risk of accidental drive wiping. It directly mounts the raw ext four Linux partitions from your original thirty-two-bit S D card, identifies the controller firmware version, and verifies card health."
    },
    # -------------------------------------------------------------
    # SLIDE 4: MIGRATION 2 - CALIBRATION EXTRACTION
    # -------------------------------------------------------------
    {
        "type": "fullscreen",
        "part": "PART 2: MIGRATION TOOL",
        "category": "MIGRATION DEEP-DIVE 2 OF 5 • CALIBRATION EXTRACTION",
        "title": "Migrator: Factory Calibration Extraction",
        "subtitle": "Reading factory ADC lookup tables, forward/reflected coupler constants, and relay profiles",
        "image": "report_calibrations.png",
        "caption": "CALIBRATION RECOVERY: DIRECTIONAL COUPLER ADC MATRICES, RELAY TIMINGS, AND BAND CALIBRATION",
        "narration": "Examining calibration recovery. On screen you see the directional coupler forward and reflected power A D C lookup tables and band calibration matrices extracted directly from the original card. The migrator extracts every factory calibration coefficient, P T T relay timing constant, and antenna matrix preset, packaging them into an encrypted gold archive so no manual recalibration is required."
    },
    # -------------------------------------------------------------
    # SLIDE 5: MIGRATION 3 - TARGET CARD PROVISIONING
    # -------------------------------------------------------------
    {
        "type": "fullscreen",
        "part": "PART 2: MIGRATION TOOL",
        "category": "MIGRATION DEEP-DIVE 3 OF 5 • TARGET CARD PROVISIONING",
        "title": "Migrator: 64-Bit Target Provisioning",
        "subtitle": "Writing verified Debian Trixie golden image, setting network credentials, and partition creation",
        "image": "migrator_step2_provisioning.png",
        "caption": "MIGRATOR STEP 2: CREDENTIAL SETUP, TARGET DISK SELECTION, AND BLOCK-LEVEL IMAGE FLASHING",
        "narration": "Moving to step two of the migrator: target card provisioning. Here the operator configures network hostnames and station Wi-Fi credentials before selecting the high-speed target Micro S D card or U S B boot media. The flasher writes the pure sixty-four-bit Debian Trixie golden image with automatic sector verification and hash checking to ensure flawless boot integrity."
    },
    # -------------------------------------------------------------
    # SLIDE 6: MIGRATION 4 - CALIBRATION INJECTION & BUILD
    # -------------------------------------------------------------
    {
        "type": "fullscreen",
        "part": "PART 2: MIGRATION TOOL",
        "category": "MIGRATION DEEP-DIVE 4 OF 5 • CALIBRATION INJECTION",
        "title": "Migrator: Automated Configuration Injection",
        "subtitle": "Direct ext4 configuration injection, driver binding, and systemd service initialization",
        "image": "migrator_tab_utils.png",
        "caption": "MIGRATOR UTILITIES: CALIBRATION INJECTION ENGINE, CARD REPAIR, AND SECTOR FORMAT TOOLS",
        "narration": "This view shows the migrator utilities tab. Once the base operating system is written, the injection pipeline directly writes your extracted calibration files, controller configurations, and network settings into the target ext four filesystem. It provisions system D service supervisors and binds low-level hardware drivers before ejecting the completed card."
    },
    # -------------------------------------------------------------
    # SLIDE 7: MIGRATION 5 - FIRST BOOT & TRIXIE KERNEL
    # -------------------------------------------------------------
    {
        "type": "fullscreen",
        "part": "PART 2: MIGRATION TOOL",
        "category": "MIGRATION DEEP-DIVE 5 OF 5 • DEBIAN TRIXIE FIRST BOOT",
        "title": "Migrator: 64-Bit Debian Trixie Verification",
        "subtitle": "Automated root partition expansion, 64-bit kernel 6.12 initialization, and hardware verification",
        "image": "tool4_report_hardware.png",
        "caption": "SYSTEM VERIFICATION: DEBIAN TRIXIE 64-BIT LINUX 6.12 KERNEL AND RASPBERRY PI HARDWARE REPORT",
        "narration": "Concluding the migration on the amplifier itself. When the card boots on your Raspberry Pi four or five, first-boot automation scripts automatically expand the Linux root partition to fill the entire card capacity and initialize the sixty-four-bit kernel six point twelve. The amplifier launches directly into service with all factory calibrations intact and verified."
    },
    # -------------------------------------------------------------
    # SLIDE 8: WEB TOOL 1 - HEALTH OVERVIEW
    # -------------------------------------------------------------
    {
        "type": "fullscreen",
        "part": "PART 3: JRFK WEB TOOLS",
        "category": "TOOL 1: HEALTH MONITOR • LIVE RF METERS",
        "title": "Health Guard: Real-Time RF Telemetry",
        "subtitle": "Precision forward power up to 1500 Watts P, E, P, reflected power, and continuous VSWR",
        "image": "tool1_health_meters.png",
        "caption": "HEALTH MONITOR: HIGH-SPEED FORWARD POWER, REFLECTED POWER, AND DYNAMIC SWR BARS",
        "narration": "Examining the first web tool, the Health and Thermal Guard. The prominent upper instruments display instantaneous forward power up to fifteen hundred Watts, P, E, P, alongside reflected power in Watts. The central V S W R indicator updates at thirty Hertz, giving you precise, low-latency visual feedback on antenna loading during transmission."
    },
    # -------------------------------------------------------------
    # SLIDE 9: WEB TOOL 1 - THERMALS & POWER RAILS
    # -------------------------------------------------------------
    {
        "type": "fullscreen",
        "part": "PART 3: JRFK WEB TOOLS",
        "category": "TOOL 1: HEALTH MONITOR • POWER RAILS & THERMALS",
        "title": "Health Guard: 53.5V Rail & LDMOS Thermals",
        "subtitle": "Main switching supply rail shunt monitoring and individual LDMOS heatsink probes",
        "image": "tool1_health_thermals.png",
        "caption": "THERMAL SUPERVISION: 53.5V DC BUS METERS, AMMETERS, AND INDIVIDUAL LDMOS HEATSINK SENSORS",
        "narration": "Looking at the lower pane of the health tool. On the left are the fifty-three point five volt D C rail voltage and current meters, showing exact power supply draw under heavy carrier. To the right, individual temperature sensors monitor the dual L-D moss heatsinks with a sixty degree threshold and automatic cooling fan regulation."
    },
    # -------------------------------------------------------------
    # SLIDE 10: WEB TOOL 1 - PROTECTION INTERLOCKS
    # -------------------------------------------------------------
    {
        "type": "fullscreen",
        "part": "PART 3: JRFK WEB TOOLS",
        "category": "TOOL 1: HEALTH MONITOR • PROTECTION INTERLOCKS",
        "title": "Health Guard: Protection Alarms & Reset",
        "subtitle": "Microsecond hardware fault detection, alarm latching, and authorized remote reset",
        "image": "tool1_health_main.png",
        "caption": "PROTECTION DASHBOARD: LATCHED FAULT INDICATORS, HARDWARE INTERLOCKS, AND REMOTE RESET",
        "narration": "On screen is the protection interlock supervisory pane. In the event of excessive reflected power or overcurrent, hardware interlocks disengage bias within microseconds. The web interface identifies the specific fault, latches the alarm for operator inspection, and allows an authorized remote reset once antenna conditions are safe."
    },
    # -------------------------------------------------------------
    # SLIDE 11: WEB TOOL 1 - CONSOLIDATED REMOTE VIEW
    # -------------------------------------------------------------
    {
        "type": "fullscreen",
        "part": "PART 3: JRFK WEB TOOLS",
        "category": "TOOL 1: HEALTH MONITOR • CONSOLIDATED REMOTE VIEW",
        "title": "Health Guard: Responsive Operations Cockpit",
        "subtitle": "Complete single-pane amplifier health, power rails, and interlocks from any browser",
        "image": "health_overview.png",
        "caption": "REMOTE OVERVIEW: CLEAN BLUEPRINT DISPLAY OPTIMIZED FOR PC, TABLET, AND PHONE BROWSERS",
        "narration": "Here is the full Health Guard overview. It organizes power meters, thermal gauges, voltage shunts, and protection alarms onto a clean blueprint canvas. You can monitor high-power transmissions remotely from anywhere in the home or operating shack with complete peace of mind."
    },
    # -------------------------------------------------------------
    # SLIDE 12: WEB TOOL 2 - ANTENNA MATRIX ROUTING
    # -------------------------------------------------------------
    {
        "type": "fullscreen",
        "part": "PART 3: JRFK WEB TOOLS",
        "category": "TOOL 2: ANTENNA MATRIX • 4-WAY ROUTING",
        "title": "Antenna Matrix: 4-Way Routing Grid",
        "subtitle": "Band-by-band antenna selection, frequency memory recall, and manual overrides",
        "image": "tool2_antenna_matrix_grid.png",
        "caption": "ANTENNA MATRIX: 4-WAY OUTPUT SELECTION GRID ACROSS ALL AMATEUR BANDS",
        "narration": "Moving to the second web tool, the Antenna Matrix. The upper grid provides four-way antenna port routing for every amateur band from one sixty through six meters. As you tune your transceiver, C A T control automatically recalls the programmed antenna port with zero manual intervention."
    },
    # -------------------------------------------------------------
    # SLIDE 13: WEB TOOL 2 - TUNER BODE PLOT
    # -------------------------------------------------------------
    {
        "type": "fullscreen",
        "part": "PART 3: JRFK WEB TOOLS",
        "category": "TOOL 2: ANTENNA MATRIX • TUNER BODE PLOT",
        "title": "Antenna Matrix: Tuner Bode Plot & Steppers",
        "subtitle": "Real-time return loss curves, stepper motor coordinates, and LC memory solutions",
        "image": "tool2_antenna_tuner_plot.png",
        "caption": "TUNER BODE PLOT: GRAPHICAL SWR SWEEP AND PRECISION STEPPER TUNING COORDINATES",
        "narration": "Looking at the lower section of the antenna tool. On the left is the real-time tuner Bode plot, showing S W R across the active band. On the right are precision stepper motor coordinates for the roller inductor and tuning capacitors, recalling stored match solutions every ten kilohertz."
    },
    # -------------------------------------------------------------
    # SLIDE 14: WEB TOOL 2 - RELAY SAFETY LOGIC
    # -------------------------------------------------------------
    {
        "type": "fullscreen",
        "part": "PART 3: JRFK WEB TOOLS",
        "category": "TOOL 2: ANTENNA MATRIX • RELAY SAFETY LOGIC",
        "title": "Antenna Matrix: Cold-Switching Interlocks",
        "subtitle": "PTT sensing, RF power threshold detection, and mechanical contact arc protection",
        "image": "antenna_tuning_bode.png",
        "caption": "TUNER LOGIC: RELAY TRANSIT COMPENSATION, RF POWER INTERLOCKS, AND STEPPER TRACKING",
        "narration": "This view highlights the antenna matrix relay safety logic. Firmware enforces cold switching by blocking relay movement whenever forward power exceeds twenty Watts. It factors in mechanical relay transit delays before allowing the transceiver to un-mute, preventing contact arcing and relay destruction."
    },
    # -------------------------------------------------------------
    # SLIDE 15: WEB TOOL 2 - CONSOLIDATED WORKSPACE
    # -------------------------------------------------------------
    {
        "type": "fullscreen",
        "part": "PART 3: JRFK WEB TOOLS",
        "category": "TOOL 2: ANTENNA MATRIX • CONSOLIDATED WORKSPACE",
        "title": "Antenna Matrix: Complete Control Surface",
        "subtitle": "Single-pane antenna configuration, tuner status, and live transceiver tracking",
        "image": "tool2_antenna_main.png",
        "caption": "ANTENNA & TUNER SUITE: CONSOLIDATED BLUEPRINT DASHBOARD ACROSS 160 TO 6 METERS",
        "narration": "Shown here is the consolidated Antenna Matrix workspace. It integrates port configuration, tuner tracking, and transceiver frequency data into a single responsive screen, allowing operators to change antennas or adjust matches directly from their computer or tablet."
    },
    # -------------------------------------------------------------
    # SLIDE 16: WEB TOOL 3 - SD BACKUP & CLONING
    # -------------------------------------------------------------
    {
        "type": "fullscreen",
        "part": "PART 3: JRFK WEB TOOLS",
        "category": "TOOL 3: SD BACKUP • LIVE DISASTER RECOVERY",
        "title": "SD Backup Manager: 3-Minute Live Media Cloning",
        "subtitle": "Creating live bootable MicroSD/USB clones while the amplifier remains in active service",
        "image": "tool3_backup_status.png",
        "caption": "BACKUP MANAGER: AUTOMATED DISASTER RECOVERY CLONING ENGINE AND SCHEDULE MANAGER",
        "narration": "Examining the third web tool, the S D Backup and Disaster Recovery Manager. This tool creates an exact, fully bootable duplicate of your active operating card to an external U S B flash drive or spare reader. Cloning takes under three minutes and runs in the background while the amplifier continues normal operation."
    },
    # -------------------------------------------------------------
    # SLIDE 17: WEB TOOL 3 - PIPELINE LOGS & VERIFICATION
    # -------------------------------------------------------------
    {
        "type": "fullscreen",
        "part": "PART 3: JRFK WEB TOOLS",
        "category": "TOOL 3: SD BACKUP • PIPELINE LOGS",
        "title": "SD Backup: Pipeline Console & Hash Verification",
        "subtitle": "Real-time block copying audit, sector hash checks, and standby media generation",
        "image": "tool3_backup_pipeline.png",
        "caption": "BACKUP PIPELINE CONSOLE: REAL-TIME SECTOR STREAMING AND INTEGRITY AUDIT TRAIL",
        "narration": "The lower panel provides the live backup pipeline log. You can follow sector replication, filesystem synchronizations, and integrity hash checks line by line. With a verified standby card always available, card corruption will never take your amplifier off the air."
    },
    # -------------------------------------------------------------
    # SLIDE 18: WEB TOOL 4 - SYSTEM REPORT & CALIBRATIONS
    # -------------------------------------------------------------
    {
        "type": "fullscreen",
        "part": "PART 3: JRFK WEB TOOLS",
        "category": "TOOL 4: SYSTEM REPORT • ARCHIVE & HARDWARE",
        "title": "System Report: Hardware Profile & Calibrations",
        "subtitle": "Operating system parameters, storage utilization, and complete calibration tables",
        "image": "report_system_overview.png",
        "caption": "SYSTEM REPORT: HARDWARE ARCHITECTURE, STORAGE UTILIZATION, AND CALIBRATION DATA",
        "narration": "Next is the System Report and Calibration Archive. This screen presents an exhaustive profile of the amplifier hardware, Linux kernel status, memory usage, and storage allocations. It also provides an instant downloadable archive of all factory calibration parameters for off-site backup."
    },
    # -------------------------------------------------------------
    # SLIDE 19: WEB TOOL 5 - DIAGNOSTIC LOGS
    # -------------------------------------------------------------
    {
        "type": "fullscreen",
        "part": "PART 3: JRFK WEB TOOLS",
        "category": "TOOL 5: DIAGNOSTIC LOGS • CENTRAL EVENT VIEWER",
        "title": "Diagnostic Logs: Centralized Event Terminal",
        "subtitle": "Systemd daemon monitoring, controller fault logging, and timestamped audit logs",
        "image": "tool5_logs_terminal.png",
        "caption": "DIAGNOSTIC LOGS: REAL-TIME EVENT STREAMING, SYSTEMD LOGS, AND CONTROLLER TELEMETRY",
        "narration": "Here is the Centralized Diagnostic Log Viewer. It streams live system D daemon logs, hardware serial communications, and amplifier controller events in real time. Timestamped warnings and trip events are captured for troubleshooting and engineering review."
    },
    # -------------------------------------------------------------
    # SLIDE 20: WEB TOOL 6 & 7 - DOCS & SCREEN STREAMER
    # -------------------------------------------------------------
    {
        "type": "fullscreen",
        "part": "PART 3: JRFK WEB TOOLS",
        "category": "TOOL 6 & 7: REFERENCE LIBRARY & SCREEN STREAMER",
        "title": "Documentation Library & Screen Streamer",
        "subtitle": "193-page K7BIT technical cookbook, offline schematics, and live front panel LCD stream",
        "image": "tool6_docs_schematics.png",
        "caption": "TECHNICAL LIBRARY: 193-PAGE K7BIT COOKBOOK, BOARD SCHEMATICS, AND LIVE LCD STREAMER",
        "narration": "Concluding with the Documentation Library and live Screen Streamer. Operators have instant offline access to the complete one hundred ninety-three page K seven B I T technical cookbook, high-resolution schematics, and wiring diagrams stored directly on the Raspberry Pi. The companion screen viewer streams the front panel touch display live over H T T P. Thank you from K seven B I T."
    }
]

async def generate_slides_and_audio():
    print(f"Starting generation for {len(SLIDES)} slides...")
    total_slides = len(SLIDES)
    
    # Renumber sequentially 1..N
    for idx, s in enumerate(SLIDES):
        s["id"] = idx + 1

    # 1. Generate HTML slides
    for s in SLIDES:
        slide_id = s["id"]
        slide_num_str = f"{slide_id:02d}"
        
        if s["type"] == "bullets":
            bullets_html = ""
            for b_title, b_desc in s["bullets"]:
                bullets_html += f"""
                <div class="bullet-card">
                    <div class="bullet-title">{b_title}</div>
                    <div class="bullet-desc">{b_desc}</div>
                </div>"""
            
            img_rel_path = f"real_screenshots/{s['image']}"
            graphics_html = f"""
            <div class="graphic-frame">
                <img src="{img_rel_path}" alt="{s['title']}">
            </div>
            <div class="graphic-caption">{s['caption']}</div>"""
            
            html_content = TEMPLATE_BULLETS.replace("{{PART}}", s["part"])
            html_content = html_content.replace("{{CATEGORY}}", s["category"])
            html_content = html_content.replace("{{TITLE}}", s["title"])
            html_content = html_content.replace("{{SUBTITLE}}", s["subtitle"])
            html_content = html_content.replace("{{SLIDE_NUM}}", str(slide_id))
            html_content = html_content.replace("{{TOTAL_SLIDES}}", str(total_slides))
            html_content = html_content.replace("{{BULLETS_HTML}}", bullets_html)
            html_content = html_content.replace("{{GRAPHICS_HTML}}", graphics_html)
        else:
            # Fullscreen layout
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

    # 4. Generate Interactive Auto-Advancing Presentation Player (preview.html)
    print("\nGenerating Auto-Advancing Presentation Player (preview.html)...")
    
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
        height: 48px;
        background: #0f2d4f;
        border-bottom: 2px solid #38bdf8;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 20px;
        flex-shrink: 0;
    }}
    .player-title {{ font-size: 16px; font-weight: 800; color: #38bdf8; display: flex; align-items: center; gap: 8px; }}
    .player-callsign {{
        background: #0284c7;
        color: white;
        padding: 3px 10px;
        border-radius: 4px;
        font-family: monospace;
        font-weight: bold;
        font-size: 13px;
    }}
    .player-main {{
        flex: 1 1 auto;
        min-height: 0;
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 8px 12px;
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
        border-radius: 6px;
        box-shadow: 0 8px 30px rgba(0,0,0,0.8);
        border: 2px solid #1e3a5f;
    }}
    .player-footer {{
        height: 72px;
        background: #0f2d4f;
        border-top: 2px solid #38bdf8;
        display: flex;
        flex-direction: column;
        justify-content: center;
        gap: 6px;
        padding: 6px 20px;
        flex-shrink: 0;
    }}
    .controls-row {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 16px;
    }}
    .btn-group {{ display: flex; gap: 8px; align-items: center; }}
    .btn {{
        background: #0284c7;
        color: white;
        border: 1px solid #38bdf8;
        padding: 6px 14px;
        border-radius: 5px;
        font-weight: 700;
        cursor: pointer;
        font-size: 13px;
        transition: background 0.2s;
    }}
    .btn:hover {{ background: #0369a1; }}
    .btn:disabled {{ opacity: 0.4; cursor: not-allowed; }}
    .btn-play {{ background: #059669; border-color: #34d399; font-size: 14px; padding: 6px 20px; }}
    .btn-play:hover {{ background: #047857; }}
    .slide-indicator {{
        font-family: monospace;
        font-size: 14px;
        font-weight: bold;
        color: #7dd3fc;
    }}
    .narration-display {{
        color: #e0f2fe;
        font-size: 13px;
        line-height: 1.35;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        flex: 1;
        max-width: 800px;
        background: rgba(6, 21, 36, 0.7);
        padding: 4px 10px;
        border-radius: 4px;
        border-left: 3px solid #38bdf8;
    }}
    .progress-bar-container {{
        width: 100%;
        height: 5px;
        background: #1e3a5f;
        border-radius: 3px;
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
            <span>JRFK 64-Bit Modernization Suite • Auto-Advancing Technical Player</span>
            <span class="player-callsign">K7BIT</span>
        </div>
        <div class="slide-indicator" id="slideIndicator">Slide 1 of 20</div>
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

        // When audio ends: Automatically advance to next slide and start playback immediately!
        audio.addEventListener('ended', () => {{
            if (currentIndex < slides.length - 1) {{
                setTimeout(() => {{
                    loadSlide(currentIndex + 1, true);
                }}, 600); // 600ms natural breathing room between slides
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

        // Keyboard arrow navigation
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

        // Initial slide load
        loadSlide(0, false);
    </script>
</body>
</html>"""

    with open(os.path.join(DECK_DIR, "preview.html"), "w", encoding="utf-8") as f:
        f.write(player_html)

    # 5. Update VSDC timeline markdown
    timeline_rows = ""
    for e in timeline_entries:
        s_num = f"{e['slide']:02d}"
        timeline_rows += f"| {e['slide']} | slide_{s_num}.png | slide_{s_num}.mp3 | {e['duration_sec']:.2f}s | {e['start_time_sec']:.2f}s | {e['end_time_sec']:.2f}s | {e['title']} |\n"

    total_duration_sec = current_time_ms / 1000.0
    timeline_md = f"""# Deck 1 Intro: Master Timeline Map (Auto-Advancing Player Sync)

**Total Slides:** {len(SLIDES)}  
**Total Timeline Duration:** {total_duration_sec:.2f} seconds ({total_duration_sec/60:.2f} minutes)  
**Layout:** Fullscreen Blueprint Screens (Slides 3-20) with verbal walkthrough of controls  
**Voice Engine:** `en-AU-WilliamMultilingualNeural` (Aussie Male)  
**Callsign:** K7BIT  
**Operating System:** 64-Bit Raspberry Pi OS Debian Trixie  

## Slide-by-Slide Synchronization Map

| Slide # | Image File | Audio File | Duration | Start Time | End Time | Title |
| :---: | :--- | :--- | :---: | :---: | :---: | :--- |
{timeline_rows}
"""

    with open(os.path.join(DECK_DIR, "VSDC_TIMELINE_MAP.md"), "w", encoding="utf-8") as f:
        f.write(timeline_md)

    print(f"\nALL 20 SLIDES, AUDIO, AND AUTO-ADVANCING PLAYER GENERATED SUCCESSFULLY!")

if __name__ == "__main__":
    asyncio.run(generate_slides_and_audio())
