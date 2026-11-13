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

# Master Blueprint HTML Template
TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<style>
    * {
        box-sizing: border-box;
        margin: 0;
        padding: 0;
    }
    
    html, body {
        width: 1920px;
        height: 1080px;
        overflow: hidden;
    }

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

    .header-left {
        display: flex;
        flex-direction: column;
        gap: 3px;
    }

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

    .header-subtitle {
        font-size: 16px;
        color: #bfdbfe;
        font-weight: 500;
    }

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

    /* 1/3 WIDTH COLUMN: EXACTLY 600px FIXED WIDTH */
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
        padding: 10px 14px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
    }

    .bullet-title {
        font-size: 15px;
        font-weight: 800;
        color: #ffffff;
        margin-bottom: 2px;
        display: flex;
        align-items: center;
        gap: 6px;
    }

    .bullet-title::before {
        content: "►";
        color: #93c5fd;
        font-size: 12px;
    }

    .bullet-desc {
        font-size: 13px;
        line-height: 1.35;
        color: #e0f2fe;
    }

    /* 2/3 WIDTH COLUMN: EXACTLY 1200px FIXED WIDTH */
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

    .graphic-frame img {
        width: 100%;
        max-height: 780px;
        border-radius: 4px;
        display: block;
        object-fit: contain;
    }

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

    .footer-left {
        color: #93c5fd;
        font-weight: 700;
    }
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

# 20 Complete Slides Structure
SLIDES = [
    # ==========================================
    # SECTION 1: INTRO (SLIDE 1 - EXACT 4 TOPICS)
    # ==========================================
    {
        "id": 1,
        "part": "PART 1: SYSTEM INTRO",
        "category": "JRFK MODERNIZATION SUITE • SYSTEM ARCHITECTURE",
        "title": "JRFK 32-to-64 Bit Migration & Web Tools",
        "subtitle": "Modernizing RFK Linear Amplifiers to Current 64-Bit Debian Trixie on RPi 4 & 5",
        "bullets": [
            ("Topic 1: 32-Bit RPi OS Obsolete", "Thirty-two-bit Raspberry Pi OS is obsolete, unmaintained, and reaches end-of-life."),
            ("Topic 2: RFK Amp Owners at Risk", "Leaves RFK amplifier owners at serious risk from unpatched bugs, security gaps, and SD card failure."),
            ("Topic 3: 64-Bit Trixie Migration", "JRFK 32-bit to 64-bit Migration & Web Tools enable seamless migration to current 64-bit Raspberry Pi 4 or 5 Debian Trixie."),
            ("Topic 4: Concurrent Web Tools", "JRFK Web Tools run concurrently on any web-capable platform with the original RFK application via port 8088.")
        ],
        "image": "tool0_portal_main.png",
        "caption": "JRFK MODERNIZATION SUITE: CONCURRENT 64-BIT ARCHITECTURE & BLUEPRINT WEB TOOLS",
        "narration": "Topic one: thirty-two-bit Raspberry Pi O S is obsolete. Topic two: this leaves R F kit amplifier owners at risk. Topic three: the J R F K thirty-two-bit to sixty-four-bit Migration and J R F K Web Tools enable users to migrate from obsolete systems to current sixty-four-bit Raspberry Pi four or five Debian Trixie. Topic four: J R F K Web Tools run concurrently on any web capable platform with the original R F kit application."
    },

    # ==========================================
    # SECTION 2: MIGRATION TOOL (SLIDES 5 TO 8)
    # ==========================================
    {
        "id": 5,
        "part": "PART 2: MIGRATION TOOL",
        "category": "TOOL 1: JRFK MIGRATOR • CORE CAPABILITIES",
        "title": "What the JRFK Migrator Does",
        "subtitle": "Standalone Windows engineering tool built for seamless amplifier modernization",
        "bullets": [
            ("Standalone Windows Binary", "Portable C# executable requiring no external Linux virtual machines or third-party drivers."),
            ("Automated Card Discovery", "Detects connected MicroSD and USB drives while locking system disks via Drive Guard."),
            ("Multi-Stage Pipeline", "Performs sector backup, calibration extraction, partition flash, and configuration injection."),
            ("One-Click Operation", "Transforms a high-risk manual Linux command line procedure into a verified, automated process.")
        ],
        "image": "migrator_main.png",
        "caption": "JRFK MIGRATOR INTERFACE: DRIVE SELECTION, FLASH ENGINE, AND INJECTION CONTROLS",
        "narration": "Now examining the migration tool. The J R F K Migrator is a standalone Windows executable engineered to modernize R F kit amplifiers. It eliminates the need for manual Linux terminal commands by managing the entire disk discovery, backup, imaging, and calibration injection cycle inside a single utility."
    },
    {
        "id": 6,
        "part": "PART 2: MIGRATION TOOL",
        "category": "TOOL 1: JRFK MIGRATOR • DRIVE GUARD & EXT4 DISCOVERY",
        "title": "How the Migrator Works",
        "subtitle": "Direct raw disk access, partition analysis, and safety-interlocked drive protection",
        "bullets": [
            ("Hardware Drive Guard", "Strict physical drive filtering blocks accidental selection of Windows host system and data disks."),
            ("Raw ext4 Disk Reading", "Directly mounts and reads Linux ext4 filesystem partitions under native Windows environments."),
            ("Controller Identification", "Verifies motherboard revision, EEPROM serials, and existing RFK configuration files."),
            ("Sector-Level Integrity Check", "Computes SHA-256 verification hashes across the target media prior to partition manipulation.")
        ],
        "image": "migrator_main.png",
        "caption": "MIGRATION WORKFLOW: DISK GEOMETRY ANALYSIS AND AUTOMATED EXT4 MOUNTING",
        "narration": "Looking at how the migrator operates under the hood. The utility integrates Drive Guard protection to prevent accidental selection of your computer hard drives. It directly reads the raw ext4 Linux file structure from your MicroSD card to locate existing controller files and verifies controller hardware before proceeding."
    },
    {
        "id": 7,
        "part": "PART 2: MIGRATION TOOL",
        "category": "TOOL 1: JRFK MIGRATOR • CALIBRATION EXTRACTION",
        "title": "Preserving Factory Calibrations",
        "subtitle": "Extracting precision ADC offsets, directional coupler tables, and tuner profiles",
        "bullets": [
            ("RF Power Calibration", "Extracts forward and reflected power directional coupler ADC lookup tables."),
            ("Band Filter Profiles", "Preserves low-pass filter switching logic, relay delays, and PTT timing constants."),
            ("Antenna Port Matrix", "Backs up customized band-to-antenna mapping across all operational bands."),
            ("Lossless Injection", "Injects the extracted calibration files directly into the new sixty-four-bit Debian Trixie filesystem.")
        ],
        "image": "tool4_report_calibration_table.png",
        "caption": "CALIBRATION RECOVERY: ADC LOOKUP MATRICES AND BAND CORRECTION PROFILES",
        "narration": "Preserving amplifier calibration is vital. The migrator automatically locates and extracts the directional coupler forward and reflected power lookup tables, relay timings, and antenna matrix settings. These precise calibration files are preserved and re-injected into the target system with zero data loss."
    },
    {
        "id": 8,
        "part": "PART 2: MIGRATION TOOL",
        "category": "TOOL 1: JRFK MIGRATOR • DEBIAN TRIXIE GOLDEN IMAGE",
        "title": "Flashing 64-Bit Trixie & First-Boot Automation",
        "subtitle": "Writing the verified Debian Trixie golden image and preparing automated initialization",
        "bullets": [
            ("High-Speed Block Flasher", "Streams the pre-configured 64-bit Debian Trixie image to the target storage media."),
            ("First-Boot Provisioning", "Configures systemd services, static network assignments, and SPI controller drivers."),
            ("Automatic Partition Expansion", "Expands the Linux root filesystem automatically on first boot to utilize full card capacity."),
            ("Plug-and-Play Deployment", "Insert the completed card into your Raspberry Pi four or five and power up directly into service.")
        ],
        "image": "tool4_report_hardware.png",
        "caption": "SYSTEM VERIFICATION: CLEAN FIRST BOOT ON 64-BIT LINUX KERNEL 6.12 TRIXIE",
        "narration": "Completing the migration. The migrator writes the verified sixty-four-bit Debian Trixie golden image to the target card. On initial startup in the amplifier, automated provisioning scripts expand the root partition and configure the background daemons, delivering a plug and play upgrade."
    },

    # ==========================================
    # SECTION 3: JRFK WEB TOOLS (SLIDES 9 TO 20)
    # ==========================================
    # Web Tool 1: Health & Thermal Guard (4 slides)
    {
        "id": 9,
        "part": "PART 3: JRFK WEB TOOLS",
        "category": "TOOL 2: HEALTH MONITOR • LIVE TELEMETRY",
        "title": "Health & Thermal Guard: RF Telemetry",
        "subtitle": "Real-time forward power, reflected power, and VSWR live monitoring",
        "bullets": [
            ("Live RF Power Gauges", "Monitors instantaneous forward power up to fifteen hundred Watts, P, E, P, and reflected power."),
            ("Real-Time VSWR Tracking", "Calculates load matching dynamically with instant visual warning bars above one point five to one."),
            ("Low-Latency Updates", "Telemetry streamed via WebSockets directly from the controller hardware at thirty Hertz."),
            ("Peak Hold Memory", "Tracks peak envelope power transients during SSB voice peaks and high-speed CW keying.")
        ],
        "image": "tool1_health_meters.png",
        "caption": "HEALTH MONITOR: HIGH-PRECISION FORWARD POWER AND VSWR DRAFTING GAUGES",
        "narration": "Examining the first web tool, the Health and Thermal Guard. On screen you see the real-time forward and reflected power instruments. The forward power gauge tracks instantaneous output up to fifteen hundred Watts, P, E, P, while the V S W R calculation updates continuously to safeguard the amplifier."
    },
    {
        "id": 10,
        "part": "PART 3: JRFK WEB TOOLS",
        "category": "TOOL 2: HEALTH MONITOR • POWER RAILS & THERMALS",
        "title": "Health Guard: Rail Current & Thermals",
        "subtitle": "53.5V main DC bus monitoring and dual LDMOS heatsink temperature sensing",
        "bullets": [
            ("53.5V DC Rail Metering", "Supervises main switching power supply rail voltage, total current draw, and power dissipation."),
            ("Dual LDMOS Temperature", "Individual thermal probes track L-D moss heatsink temperatures with sixty degree alarm threshold."),
            ("Fan Controller Telemetry", "Monitors pulse-width modulation cooling fan speeds and automatically ramps up airflow."),
            ("Hardware Trip Protection", "Displays real-time lockout states for over-current, thermal runaway, and overdrive events.")
        ],
        "image": "tool1_health_thermals.png",
        "caption": "THERMAL TELEMETRY: 53.5V DC BUS METERS AND INDIVIDUAL LDMOS TEMPERATURE PROBES",
        "narration": "This view highlights the power supply and thermal supervisory pane. The fifty-three point five volt D C rail meters display voltage and current draw during full power transmission. Down below, dual temperature gauges supervise the L-D moss heatsinks with automatic fan speed tracking."
    },
    {
        "id": 11,
        "part": "PART 3: JRFK WEB TOOLS",
        "category": "TOOL 2: HEALTH MONITOR • PROTECTION INTERLOCKS",
        "title": "Health Guard: Protection Interlocks",
        "subtitle": "Sub-millisecond fault detection, alarm latching, and recovery sequencing",
        "bullets": [
            ("Sub-Millisecond Cutoff", "Hardware interlocks isolate bias voltage within microseconds if reflected power exceeds limits."),
            ("Visual Fault Indicators", "Identifies exact trip causes including SWR mismatch, DC overcurrent, and thermal cutoff."),
            ("Fault Reset Controls", "Allows remote alarm inspection and authorized reset directly from the authenticated web interface."),
            ("Alarm History Archive", "Records all trip occurrences with precision timestamps for station engineering review.")
        ],
        "image": "tool1_health_main.png",
        "caption": "HEALTH DASHBOARD: COMPREHENSIVE INTERLOCK AND SAFETY SUPERVISORY OVERVIEW",
        "narration": "Shown here is the complete health and protection dashboard. If load mismatch or thermal thresholds are exceeded, the controller hardware disengages bias within microseconds. The web interface clearly identifies the trip cause and allows operator review before resetting."
    },
    {
        "id": 12,
        "part": "PART 3: JRFK WEB TOOLS",
        "category": "TOOL 2: HEALTH MONITOR • REMOTE COCKPIT",
        "title": "Health Guard: Full Remote Oversight",
        "subtitle": "Complete operational visibility from anywhere on the station network",
        "bullets": [
            ("Remote Operating Ease", "Operate high-power transmission confidently from any remote shack or mobile operating desk."),
            ("Mobile Browser Layout", "Responsive blueprint styling formats perfectly across tablets, laptops, and smartphones."),
            ("Zero Latency Sluggishness", "Efficient lightweight design consumes negligible network bandwidth on local WiFi or Ethernet."),
            ("Fail-Safe Heartbeat", "Automatic disconnect detection ensures remote commands fail safe if network link drops.")
        ],
        "image": "health_overview.png",
        "caption": "REMOTE OVERVIEW: CLEAN RESPONSIVE BLUEPRINT LAYOUT FOR NETWORKED MONITORING",
        "narration": "The complete Health Guard interface provides full remote visibility. Whether operating from the main console or across the home network, you have immediate access to power levels, temperatures, and status flags without sitting in front of the amplifier."
    },

    # Web Tool 2: Antenna Matrix & Tuner Bode Plot (4 slides)
    {
        "id": 13,
        "part": "PART 3: JRFK WEB TOOLS",
        "category": "TOOL 3: ANTENNA MATRIX • 4-WAY ROUTING",
        "title": "Antenna Matrix: 4-Way Routing Grid",
        "subtitle": "Band-by-band antenna selection, safety interlocks, and relay memory",
        "bullets": [
            ("4-Way Output Matrix", "Routes high-power RF cleanly across four individual antenna ports for all amateur bands."),
            ("Per-Band Memory", "Automatically recalls assigned antenna ports as the transceiver changes frequency."),
            ("Hot-Switching Protection", "Interlocks enforce complete PTT unkey before any antenna relay is allowed to switch."),
            ("Manual Override Controls", "Allows instantaneous port reassignment with clear visual relay state indicators.")
        ],
        "image": "tool2_antenna_matrix_grid.png",
        "caption": "ANTENNA MATRIX: 4-WAY SELECTION GRID ACROSS ALL AMATEUR BANDS",
        "narration": "Moving to the second web tool, the Antenna Matrix and Tuner. The upper panel displays the four-way antenna routing grid. Each amateur band from one sixty through six meters has its assigned antenna port with automatic recall when changing bands."
    },
    {
        "id": 14,
        "part": "PART 3: JRFK WEB TOOLS",
        "category": "TOOL 3: ANTENNA MATRIX • TUNER BODE PLOT",
        "title": "Antenna Matrix: Tuner Bode Plot",
        "subtitle": "Graphical VSWR sweep curves and stepper capacitor/inductor positions",
        "bullets": [
            ("Visual Bode Plot", "Plots return loss and SWR curves across the active amateur band in real time."),
            ("Stepper Tuning Coordinates", "Displays precise inductor and capacitor stepper motor positions for rapid LC matching."),
            ("Stored Tuning Memories", "Stores verified LC solutions every ten kilohertz across voice and digital band segments."),
            ("Sub-Second Frequency Agility", "Enables rapid band jumping during contests without manual tuner hunting.")
        ],
        "image": "tool2_antenna_tuner_plot.png",
        "caption": "TUNER BODE PLOT: RETURN LOSS SWEEP AND STEPPER COORDINATE MONITORING",
        "narration": "Examining the lower panel of the antenna tool. Here you see the tuner Bode plot and stepper coordinates. It displays the matched return loss curve across the active band segment alongside exact capacitor and inductor positions for fast recall."
    },
    {
        "id": 15,
        "part": "PART 3: JRFK WEB TOOLS",
        "category": "TOOL 3: ANTENNA MATRIX • RELAY INTERLOCKS",
        "title": "Antenna Matrix: Relay Safety Logic",
        "subtitle": "Protecting relay contacts and feedlines from high-power RF arcing",
        "bullets": [
            ("Cold Switching Enforced", "Firmware blocks relay activation whenever forward RF power exceeds twenty Watts."),
            ("Switching Delay Compensation", "Accounts for mechanical relay transit times before authorizing transmitter RF un-mute."),
            ("Port Isolation Verification", "Ensures unselected antenna ports remain grounded to eliminate cross-talk and RX damage."),
            ("Bypass Mode Support", "Instantly routes transceiver straight through to selected antenna port when amplifier is in standby.")
        ],
        "image": "antenna_tuning_bode.png",
        "caption": "TUNING LOGIC: AUTOMATED CAPACITOR/INDUCTOR RECALL AND COLD-SWITCHING INTERLOCKS",
        "narration": "Safety logic in the antenna matrix prevents high-power RF arcing. The system enforces cold switching by verifying that RF power has ceased before allowing any relay transition, protecting your antenna switches and feedlines."
    },
    {
        "id": 16,
        "part": "PART 3: JRFK WEB TOOLS",
        "category": "TOOL 3: ANTENNA MATRIX • FULL WORKFLOW",
        "title": "Antenna Matrix: Consolidated Interface",
        "subtitle": "Single-pane antenna configuration, tuner status, and band presets",
        "bullets": [
            ("Unified Control Surface", "Combines matrix routing, tuner curves, and relay states on one responsive blueprint screen."),
            ("Real-Time Band Display", "Reflects CAT control frequency data directly from your connected station transceiver."),
            ("Custom Port Labeling", "Configure custom antenna names such as Beam, Wire, Vertical, or Dummy Load."),
            ("Instant Remote Access", "Adjust tuning and antenna selections from any web-connected station terminal.")
        ],
        "image": "tool2_antenna_main.png",
        "caption": "ANTENNA & TUNER SUITE: COMPLETE INTEGRATED MATRIX AND BODE PLOT WORKSPACE",
        "narration": "Here is the full Antenna Matrix interface. It unifies port selection, tuner tracking, and transceiver frequency data onto one clean page, giving you full control of antenna switching from anywhere in the shack."
    },

    # Web Tool 3: SD Backup & Disaster Recovery (2 slides)
    {
        "id": 17,
        "part": "PART 3: JRFK WEB TOOLS",
        "category": "TOOL 4: SD BACKUP • DISASTER RECOVERY",
        "title": "SD Disaster Recovery & Cloning",
        "subtitle": "Three-minute automated live media backup to secondary USB storage",
        "bullets": [
            ("Live Card Cloning", "Creates a fully bootable backup clone of the running MicroSD card without stopping the amplifier."),
            ("Scheduled Automated Backups", "Configures cron pipelines to back up configurations and logs automatically on schedule."),
            ("Secondary Media Target", "Clones directly to an external USB flash drive or secondary card reader mounted on the Pi."),
            ("Zero-Downtime Standby", "Keep a hot-standby boot media ready for immediate physical swap in the event of media failure.")
        ],
        "image": "tool3_backup_status.png",
        "caption": "BACKUP MANAGER: REAL-TIME PIPELINE MONITOR AND SCHEDULED AUTOMATION",
        "narration": "Looking at the SD Backup and Disaster Recovery tool. This tool creates a live, bootable clone of your operating system card to an external USB drive while the amplifier continues running. If a card ever fails, you have an identical bootable spare ready for immediate use."
    },
    {
        "id": 18,
        "part": "PART 3: JRFK WEB TOOLS",
        "category": "TOOL 4: SD BACKUP • LOGGING & RESTORE",
        "title": "SD Backup: Pipeline Logs & Archives",
        "subtitle": "Real-time block streaming verification, integrity audits, and rollback",
        "bullets": [
            ("Live Pipeline Terminal", "Monitors block copying progress, filesystem sync, and partition table generation in real time."),
            ("Configuration Archiving", "Generates lightweight compressed tarball snapshots of all calibration tables for cloud storage."),
            ("Integrity Audit Trail", "Verifies sector hashes to confirm the backup card is completely bootable and error-free."),
            ("Station Peace of Mind", "Eliminates the risk of stranded amplifier hardware due to media degradation.")
        ],
        "image": "tool3_backup_pipeline.png",
        "caption": "PIPELINE LOGS: DETAILED SECTOR COPY AUDIT TRAIL AND BACKUP ENGINE CONSOLE",
        "narration": "The lower portion of the backup tool displays the live cloning pipeline log. You can follow sector replication and filesystem checks in real time, guaranteeing that your backup card is verified and ready for deployment."
    },

    # Web Tool 4: System Report, Diagnostic Logs & Documentation (2 slides)
    {
        "id": 19,
        "part": "PART 3: JRFK WEB TOOLS",
        "category": "TOOL 5: SYSTEM DIAGNOSTICS • OS & LOGS",
        "title": "System Diagnostics & Event Logs",
        "subtitle": "Linux kernel oversight, systemd daemon status, and centralized event viewer",
        "bullets": [
            ("OS & Kernel Health", "Monitors 64-bit Debian Trixie kernel parameters, CPU core load, RAM usage, and storage allocations."),
            ("Systemd Supervisor", "Supervises background controller services with automated restart on fault detection."),
            ("Centralized Event Viewer", "Aggregates hardware controller logs, fault alerts, and web server events into a single terminal."),
            ("Exportable Telemetry", "Exports timestamped diagnostic reports for engineering review and remote assistance.")
        ],
        "image": "tool5_logs_terminal.png",
        "caption": "DIAGNOSTIC LOG VIEWER: SYSTEMD SERVICE SUPERVISION AND EVENT AUDIT TRAIL",
        "narration": "Next is the System Report and Diagnostic Log Viewer. This screen displays comprehensive Linux kernel metrics, hardware storage allocations, and systemd service health. The real-time log viewer captures all controller events and protection alarms for quick review."
    },
    {
        "id": 20,
        "part": "PART 3: JRFK WEB TOOLS",
        "category": "TOOL 6: ENGINEERING LIBRARY • K7BIT REPOSITORIES",
        "title": "Station Reference Library & Documentation",
        "subtitle": "193-page K7BIT technical cookbook, schematics, and interactive screen viewer",
        "bullets": [
            ("193-Page Engineering Manual", "Direct in-browser access to the complete K7BIT RF-KIT technical and operational cookbook."),
            ("Full Schematic Library", "High-resolution board schematics, wiring diagrams, and controller pinouts stored locally on the Pi."),
            ("Live Screen Streamer", "Views the physical front-panel LCD touch display directly over HTTP via the screen streamer."),
            ("Broadcast-Grade Architecture", "Brings professional engineering documentation and remote tools to the amateur radio community.")
        ],
        "image": "tool6_docs_schematics.png",
        "caption": "DOCUMENTATION VIEWER: K7BIT 193-PAGE TECHNICAL COOKBOOK AND OFFLINE SCHEMATICS",
        "narration": "Concluding our overview with the Documentation Library and Screen Viewer. Operators have direct offline access to the complete one hundred ninety-three page K seven B I T engineering cookbook and full schematic library directly from the amplifier, alongside the live front panel screen streamer. Thank you from K seven B I T."
    }
]

async def generate_slides_and_audio():
    # Renumber slides 1..N sequentially
    for idx, s in enumerate(SLIDES):
        s["id"] = idx + 1
        
    print(f"Starting generation for {len(SLIDES)} slides...")
    total_slides = len(SLIDES)
    
    # 1. Generate HTML slides
    for s in SLIDES:
        slide_id = s["id"]
        slide_num_str = f"{slide_id:02d}"
        
        # Build Bullets HTML (Left 1/3: 600px)
        bullets_html = ""
        for b_title, b_desc in s["bullets"]:
            bullets_html += f"""
            <div class="bullet-card">
                <div class="bullet-title">{b_title}</div>
                <div class="bullet-desc">{b_desc}</div>
            </div>"""
        
        # Build Graphics HTML (Right 2/3: 1200px)
        img_rel_path = f"real_screenshots/{s['image']}"
        graphics_html = f"""
        <div class="graphic-frame">
            <img src="{img_rel_path}" alt="{s['title']}">
        </div>
        <div class="graphic-caption">{s['caption']}</div>"""
        
        html_content = TEMPLATE.replace("{{PART}}", s["part"])
        html_content = html_content.replace("{{CATEGORY}}", s["category"])
        html_content = html_content.replace("{{TITLE}}", s["title"])
        html_content = html_content.replace("{{SUBTITLE}}", s["subtitle"])
        html_content = html_content.replace("{{SLIDE_NUM}}", str(slide_id))
        html_content = html_content.replace("{{TOTAL_SLIDES}}", str(total_slides))
        html_content = html_content.replace("{{BULLETS_HTML}}", bullets_html)
        html_content = html_content.replace("{{GRAPHICS_HTML}}", graphics_html)
        
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

    # 3. Generate Audio with edge-tts (Aussie Male William, phonetically cleaned)
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
        
        # Generate MP3
        comm = edge_tts.Communicate(cleaned_narration, voice)
        await comm.save(mp3_file)
        
        # Copy to vsdc_media
        with open(mp3_file, "rb") as f_in, open(vsdc_mp3, "wb") as f_out:
            f_out.write(f_in.read())
            
        # Get duration
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
        
        current_time_ms += duration_ms + 1000  # 1-second pause between slides
        print(f"Generated slide_{slide_num_str}.mp3 ({duration_sec:.2f}s)")

    # 4. Generate Master Preview HTML & Timeline Document
    print("\nUpdating preview.html and VSDC_TIMELINE_MAP.md...")
    
    preview_cards = ""
    for entry in timeline_entries:
        s_id = entry["slide"]
        s_num = f"{s_id:02d}"
        preview_cards += f"""
        <div class="slide-card">
            <div class="slide-header">
                <h3>Slide {s_id}: {entry['title']}</h3>
                <span class="badge">{entry['duration_sec']:.2f}s</span>
            </div>
            <img src="slide_{s_num}.png" alt="Slide {s_num}">
            <div class="audio-box">
                <audio controls src="slide_{s_num}.mp3"></audio>
                <div class="narration-text"><strong>Narration:</strong> {entry['narration']}</div>
                <div class="phonetic-text"><strong>TTS Input:</strong> {entry['cleaned']}</div>
            </div>
        </div>"""
        
    preview_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Deck 1 Blueprint Master Review - K7BIT</title>
<style>
    body {{
        background: #0f172a;
        color: #f8fafc;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        padding: 40px;
        margin: 0;
    }}
    h1 {{ color: #38bdf8; margin-bottom: 8px; }}
    .subtitle {{ color: #94a3b8; margin-bottom: 30px; font-size: 16px; }}
    .grid {{ display: flex; flex-direction: column; gap: 40px; max-width: 1400px; margin: 0 auto; }}
    .slide-card {{
        background: #1e293b;
        border: 2px solid #38bdf8;
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.5);
    }}
    .slide-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }}
    .slide-header h3 {{ margin: 0; color: #ffffff; font-size: 22px; }}
    .badge {{ background: #0284c7; color: white; padding: 4px 12px; border-radius: 9999px; font-weight: bold; font-family: monospace; }}
    img {{ width: 100%; border-radius: 8px; border: 1px solid #475569; margin-bottom: 16px; }}
    .audio-box {{ background: #0f172a; padding: 16px; border-radius: 8px; border: 1px solid #334155; }}
    audio {{ width: 100%; margin-bottom: 12px; }}
    .narration-text {{ color: #e2e8f0; font-size: 14px; margin-bottom: 8px; line-height: 1.4; }}
    .phonetic-text {{ color: #38bdf8; font-family: monospace; font-size: 12px; line-height: 1.4; }}
</style>
</head>
<body>
    <div style="max-width: 1400px; margin: 0 auto;">
        <h1>JRFK Modernization Suite - Deck 1 Blueprint Master</h1>
        <div class="subtitle">Enforced 1/3 Bullets vs 2/3 Live Screens • Aussie Male William • Pure 64-Bit Trixie • Callsign K7BIT • P, E, P, Enforced</div>
        <div class="grid">
            {preview_cards}
        </div>
    </div>
</body>
</html>"""

    with open(os.path.join(DECK_DIR, "preview.html"), "w", encoding="utf-8") as f:
        f.write(preview_html)

    # VSDC Timeline Map
    timeline_rows = ""
    for e in timeline_entries:
        s_num = f"{e['slide']:02d}"
        timeline_rows += f"| {e['slide']} | slide_{s_num}.png | slide_{s_num}.mp3 | {e['duration_sec']:.2f}s | {e['start_time_sec']:.2f}s | {e['end_time_sec']:.2f}s | {e['title']} |\n"

    total_duration_sec = current_time_ms / 1000.0
    timeline_md = f"""# Deck 1 Intro: Master Timeline Map (VSDC Video Editor)

**Total Slides:** {len(SLIDES)}  
**Total Timeline Duration:** {total_duration_sec:.2f} seconds ({total_duration_sec/60:.2f} minutes)  
**Layout:** 1/3 (600px) Bullets vs 2/3 (1200px) High-Resolution Screens  
**Slide Master:** Blueprint Blue (`#1a5695`) with Technical Drafting Grid  
**Voice Engine:** `en-AU-WilliamMultilingualNeural` (Aussie Male)  
**Callsign:** K7BIT  
**Operating System:** 64-Bit Raspberry Pi OS Debian Trixie  

## Slide-by-Slide Synchronization Map

| Slide # | Image File | Audio File | Duration | Start Time | End Time | Topic / Title |
| :---: | :--- | :--- | :---: | :---: | :---: | :--- |
{timeline_rows}

## VSDC Import Instructions
1. Open VSDC Video Editor.
2. Set Project Resolution to **1920x1080** at **30 fps**.
3. Import all images and MP3 files from `D:\\JRFK\\Presentations\\Deck_1_Intro\\vsdc_media`.
4. Align each slide PNG to its corresponding audio track using the start/end timestamps above.
"""

    with open(os.path.join(DECK_DIR, "VSDC_TIMELINE_MAP.md"), "w", encoding="utf-8") as f:
        f.write(timeline_md)
        
    print(f"\nALL 20 SLIDES, AUDIO, AND TIMELINE MAP GENERATED SUCCESSFULLY!")

if __name__ == "__main__":
    asyncio.run(generate_slides_and_audio())
