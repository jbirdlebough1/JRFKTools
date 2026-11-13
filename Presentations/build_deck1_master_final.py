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

# Presentation Structure:
# Topic 1: The Migration Requirement & 32-to-64 Bit Overview (Slides 1-4)
# Topic 2: JRFK Migrator Tool (Slides 5-6)
# Topic 3: JRFK Web Tools - 7 Screens (Slides 7-9)
# Topic 4: Disaster Recovery & Docs Portal (Slides 10-13)
# Explicit Rules:
# - NEVER use word "station" -> use "K7BIT"
# - NEVER use "John" -> use "K7BIT"
# - NEVER use "web cockpit" -> use "JRFK Web Tools"
# - LDMOS pronounced "LD MOS"
# - 1500W PEP pronounced "fifteen hundred watts, P-E-P,"
# - Up to 6 left-side bullet cards
# - Right side: real screenshots of JRFK tools & 8088 screens
SLIDES = [
    {
        "id": 1,
        "part": "TOPIC 1: ARCHITECTURAL OVERVIEW",
        "category": "THE JRFK MIGRATION SUITE • 64-BIT REQUIREMENT",
        "title": "MODERNIZING RF AMPLIFIER CONTROLLERS",
        "subtitle": "Engineering Pure 64-Bit Debian Bookworm Systems for High-Power Amateur Radio Amplifiers",
        "narrative": "Welcome to Part 1 of our technical overview from K7BIT. When you are managing fifteen hundred watts, P-E-P, across one sixty through six meters, the controller supervising your R F deck, low-pass relays, and protection sequencing must be completely deterministic. In this briefing, we examine the technical requirement for migrating from legacy thirty-two-bit operating systems to the pure sixty-four-bit Debian Bookworm architecture provided by the JRFK suite.",
        "graphics": [
            ("jrfk_migrator.png", "FIG 1: JRFK STANDALONE MIGRATOR INTERFACE & PHYSICAL DRIVE GUARD"),
            ("screen_health_monitor.png", "FIG 2: JRFK WEB TOOLS (PORT 8088) - REAL-TIME RF TELEMETRY & METRICS")
        ],
        "bullets": [
            ("High-Power RF Determinism", "Managing 1500W PEP on 160m through 6m requires microsecond determinism and rock-solid controller stability."),
            ("Embedded Raspberry Pi Controller", "Supervises PTT sequencing, directional couplers, low-pass relays, touch metering, and SimpleRPC."),
            ("Pure 64-Bit Debian Bookworm", "Modern 64-bit kernel guarantees address-space isolation, preemption stability, and active patch streams."),
            ("Hardware Protection Interlocks", "Hardware watchdogs immediately disengage bias and clamp exciter drive during abnormal RF events."),
            ("Operating Note (K7BIT)", "A deterministic controller is the foundation of amplifier safety—delay or lockup risks devastating LD MOS transistors during keying.")
        ]
    },
    {
        "id": 2,
        "part": "TOPIC 1: ARCHITECTURAL OVERVIEW",
        "category": "THE JRFK MIGRATION SUITE • DEPRECATION ANALYSIS",
        "title": "WHY 32-BIT MUST GO: SOFTWARE END-OF-LIFE",
        "subtitle": "Software End-of-Life, Frozen Repositories, and Network Deprecation Risks",
        "narrative": "Let's look at why migration is necessary. The original thirty-two-bit operating system has reached official end-of-life. Upstream package repositories are frozen, and deprecated Python socket implementations prevent the controller from running modern network protocols or security patches. Without upgrading, the amplifier controller becomes an isolated legacy device unable to communicate reliably with modern automation at K7BIT.",
        "graphics": [
            ("screen_system_report.png", "FIG 3: JRFK WEB TOOLS SYSTEM REPORT - KERNEL & RUNTIME AUDIT"),
            ("screen_log_viewer.png", "FIG 4: JRFK WEB TOOLS REAL-TIME EVENT LOGGING & DIAGNOSTICS")
        ],
        "bullets": [
            ("Frozen Upstream Repositories", "Debian and Raspbian 32-bit suites are frozen; critical security and kernel patches are permanently discontinued."),
            ("Python Socket Deprecation", "Legacy Python 2 and early Python 3 socket implementations fail on modern TLS/SSL encrypted networks."),
            ("Broken Package Dependencies", "Attempting to install modern utilities or compilers triggers circular dependency failures on legacy 32-bit rootfs."),
            ("Network Automation Failure", "Obsolete networking stacks cannot integrate cleanly with modern orchestrators or CAT daemons."),
            ("Operating Note (K7BIT)", "An amplifier controller unable to update becomes an unmaintainable technical island in a modern networked shack.")
        ]
    },
    {
        "id": 3,
        "part": "TOPIC 1: ARCHITECTURAL OVERVIEW",
        "category": "THE JRFK MIGRATION SUITE • RF STABILITY",
        "title": "WHY 32-BIT MUST GO: DISPLAY DRIVERS & RF LOCKS",
        "subtitle": "User-Space Drivers, Memory Leaks, and High-RF Framebuffer Lockups",
        "narrative": "The second critical driver for migration is display architecture. Legacy thirty-two-bit installations relied on user-space fake-KMS and older X eleven graphics layers. In the presence of strong R F fields during legal-limit keying, memory fragmentation in these user-space drivers frequently caused touchscreen freezes and display blanking. Upgrading to sixty-four-bit Full KMS DRM places the ten twenty-four by six hundred display modelines directly inside the Linux kernel, ensuring rock-solid display stability.",
        "graphics": [
            ("screen_screen_viewer.png", "FIG 5: JRFK WEB TOOLS SCREEN VIEWER - LIVE RESISTIVE TOUCH STREAM")
        ],
        "bullets": [
            ("User-Space Fake-KMS Fragility", "Legacy 32-bit fake-KMS graphics layers suffer continuous memory fragmentation under high-speed telemetry polling."),
            ("High-RF Field Interference", "Strong local electromagnetic fields during 1500W keying trigger X11 client-server socket disconnects."),
            ("Full KMS Direct-to-Kernel DRM", "64-bit Full KMS places 1024x600 display modelines directly inside the Linux kernel DRM subsystem."),
            ("Hardware Touch Layer Isolation", "Direct kernel touchscreen coordinate handling eliminates lag, ghost taps, and driver hangs."),
            ("Operating Note (K7BIT)", "A frozen display leaves the operator blind to VSWR, drain current, and heatsink temperature during high-power operation.")
        ]
    },
    {
        "id": 4,
        "part": "TOPIC 1: ARCHITECTURAL OVERVIEW",
        "category": "THE JRFK MIGRATION SUITE • 64-BIT ARCHITECTURE",
        "title": "64-BIT ARCHITECTURE OVERVIEW: TECHNICAL PAYOFF",
        "subtitle": "Memory Protection, Non-Blocking Telemetry, and Native Systemd Daemons",
        "narrative": "The sixty-four-bit architecture delivers an immediate technical payoff. Debian Bookworm provides sixty-four-bit memory protection, modern Linux kernel stability, and a fully non-blocking Simple R P C telemetry loop. Fragile legacy startup scripts are replaced with native system D service units, ensuring that all controller daemons automatically recover in the event of an unexpected fault.",
        "graphics": [
            ("screen_health_monitor.png", "FIG 6: JRFK WEB TOOLS HEALTH MONITOR - ASYNCHRONOUS DAEMON TELEMETRY"),
            ("screen_health_manager.png", "FIG 7: JRFK WEB TOOLS HEALTH MANAGER - SYSTEMD DAEMON ACTIVE WATCHDOGS")
        ],
        "bullets": [
            ("64-Bit Virtual Memory Isolation", "Complete address space isolation prevents daemon crash cascades under sustained I/O or network bursts."),
            ("Asynchronous SimpleRPC Engine", "Decouples the real-time hardware telemetry loop from web serving, guaranteeing zero GUI stalling."),
            ("Native Systemd Supervision", "Replaces brittle rc.local shell scripts with robust systemd units configured for automatic restart on failure."),
            ("Modern Kernel I/O Determinism", "Debian Bookworm 64-bit provides deterministic scheduler latency for serial, I2C, and SPI controller buses."),
            ("Operating Note (K7BIT)", "Native systemd service watchdogs supervise all daemons, guaranteeing automatic self-recovery without operator intervention.")
        ]
    },
    {
        "id": 5,
        "part": "TOPIC 2: JRFK MIGRATOR TOOL",
        "category": "THE JRFK MIGRATION SUITE • TOOL 1: MIGRATOR",
        "title": "TOOL 1: JRFK STANDALONE MIGRATOR ARCHITECTURE",
        "subtitle": "Zero-Dependency Windows Executable with Native Administrative Launch Guard",
        "narrative": "Now let's examine topic two: the JRFK Standalone Migrator. Distributed as a single one hundred sixty-six megabyte Windows executable, J R F K dot E X E requires zero developer tools or Python dependencies. It incorporates a dedicated C sharp launcher that handles administrative elevation, suppresses disruptive Windows 11 format prompts on raw media, and enforces strict physical drive guard locks to prevent accidental drive overwrites.",
        "graphics": [
            ("jrfk_migrator.png", "FIG 8: JRFK.EXE MIGRATOR INTERFACE - PHYSICAL DRIVE GUARD & PROVISIONING")
        ],
        "bullets": [
            ("Zero Developer Dependencies", "Packaged as a standalone 166MB Windows executable with internal Python runtime and embedded frontend assets."),
            ("C# Elevation Launcher", "Automates UAC administrative elevation and configures runtime environment without manual command line setup."),
            ("Windows 11 Disk Prompt Suppressor", "Background worker intercepts and dismisses Windows 11 format drive dialogs when raw ext4 media is inserted."),
            ("Physical Drive Guard Protection", "Strict physical drive inspection locks out system volumes, USB flash sticks, and network mapped drives."),
            ("Operating Note (K7BIT)", "Drive Guard strictly filters out system drives, thumbdrives, and network shares to prevent tragic media overwrites.")
        ]
    },
    {
        "id": 6,
        "part": "TOPIC 2: JRFK MIGRATOR TOOL",
        "category": "THE JRFK MIGRATION SUITE • TOOL 1: MIGRATOR",
        "title": "TOOL 1 IN ACTION: DISCOVERY, FLASHING & CALIBRATION",
        "subtitle": "Automated Network Controller Discovery and Zero-Loss Calibration Restoration",
        "narrative": "In operation, the migrator automates the entire provisioning workflow. It scans your local network to discover the amplifier controller, flashes the verified sixty-four-bit Bookworm base image, injects native ten twenty-four by six hundred display modelines, and extracts your amplifier's unique band tables and S W R calibration offsets from your old S D card so no factory calibration is lost.",
        "graphics": [
            ("screen_backup_manager.png", "FIG 9: JRFK WEB TOOLS BACKUP MANAGER - CALIBRATION EXTRACTION & RESTORATION"),
            ("jrfk_migrator.png", "FIG 10: JRFK SUBNET CONTROLLER DISCOVERY & FLASH PROGRESS")
        ],
        "bullets": [
            ("Automated Subnet Discovery", "Scans local IPv4 subnets via broadcast sweeps to pinpoint controller IP address without router inspection."),
            ("Raw ext4 Calibration Harvesting", "Directly mounts and reads legacy ext4 partitions on Windows to extract unique band data and coupler offsets."),
            ("Verified 64-Bit Base Flashing", "Writes verified Debian Bookworm golden image with SHA-256 integrity verification across all written sectors."),
            ("Zero-Touch Display Modeline Injection", "Injects native 1024x600 Full KMS timings into bootloader configuration prior to first controller startup."),
            ("Operating Note (K7BIT)", "Factory calibration offsets are irreplaceable—the JRFK migrator guarantees zero data loss during modernization.")
        ]
    },
    {
        "id": 7,
        "part": "TOPIC 3: JRFK WEB TOOLS",
        "category": "THE JRFK MIGRATION SUITE • TOOL 2: JRFK WEB TOOLS",
        "title": "TOOL 2: JRFK WEB TOOLS — RF TELEMETRY & BANDS",
        "subtitle": "Port 8088 Operations: Low-Pass Filtering and Forward/Reflected Power Metering",
        "narrative": "Following migration, topic three presents the seven-screen JRFK Web Tools running permanently on port eighty eighty-eight. This tool decouples live operation from P C maintenance. Screen 1 gives you real-time forward peak envelope power, reflected power, and S W R metering from any browser at K7BIT, while Screen 2 provides automatic low-pass filter band switching synchronized to your transceiver via C A T control with active hot-switch prevention.",
        "graphics": [
            ("screen_health_monitor.png", "FIG 11: JRFK WEB TOOLS SCREEN 1 - PRECISION RF POWER, VSWR & LPF METERING")
        ],
        "bullets": [
            ("Zero-Install JRFK Web Tools", "Runs on local port 8088, delivering an interactive operational tool suite to any browser, PC, or tablet at K7BIT."),
            ("Directional Coupler Telemetry", "Samples forward and reflected RF voltage across dual directional couplers, rendering real-time peak meters."),
            ("CAT Synchronized Band Tracking", "Low-pass filter relay banks track transceiver VFO frequency changes automatically over serial or IP."),
            ("Hardware Hot-Switching Interlock", "Blocks relay state transitions while exciter RF drive is present, protecting relay contacts from arcing."),
            ("Operating Note (K7BIT)", "Directional couplers sample forward and reflected waves directly, rendering precision analog meters in real-time.")
        ]
    },
    {
        "id": 8,
        "part": "TOPIC 3: JRFK WEB TOOLS",
        "category": "THE JRFK MIGRATION SUITE • TOOL 2: JRFK WEB TOOLS",
        "title": "TOOL 2: PA MONITORING & 4-WAY ANTENNA MATRIX",
        "subtitle": "53.5V Discrete Shunt Telemetry, Dual LD MOS Thermals, and Band-Mapped Relays",
        "narrative": "Screens 3 and 4 of the JRFK Web Tools handle R F deck health and antenna routing. Screen 3 monitors the fifty-three point five volt D C rail, drain current, and heatsink thermals across the dual Ampleon B L F one eighty-nine LD MOS transistors. Note that the system uses discrete analog shunts rather than C A N bus power supplies, ensuring noise-free D C telemetry. Screen 4 manages a four-way antenna matrix that automatically recalls your selected antenna port for each band.",
        "graphics": [
            ("screen_antenna_mapper.png", "FIG 12: JRFK WEB TOOLS SCREEN 4 - 4-WAY ANTENNA MATRIX & PER-BAND ROUTING"),
            ("screen_health_monitor.png", "FIG 13: JRFK WEB TOOLS SCREEN 3 - 53.5V DC RAIL & PA THERMAL MONITORING")
        ],
        "bullets": [
            ("Discrete Shunt Current Measurement", "Uses precision analog current shunts on the 53.5V rail, avoiding high-frequency digital CAN bus hash."),
            ("Dual BLF189 LD MOS Monitoring", "Monitors current symmetry and heatsink temperature distribution across both final amplifier transistors."),
            ("4-Way Coaxial Matrix Controller", "Automates 4-port antenna matrix switching with per-band memory recall for multi-antenna arrays."),
            ("Cross-Band Interlock Rules", "Prevents erroneous relay energization outside valid amateur bands, preserving amplifier match."),
            ("Operating Note (K7BIT)", "Antenna mapping eliminates manual coaxial patching—switching bands automatically selects the resonant antenna array.")
        ]
    },
    {
        "id": 9,
        "part": "TOPIC 3: JRFK WEB TOOLS",
        "category": "THE JRFK MIGRATION SUITE • TOOL 2: JRFK WEB TOOLS",
        "title": "TOOL 2: PROTECTION SYSTEMS, LOGS & TOUCH CALIBRATION",
        "subtitle": "Hardware Protection Interlocks, Event Logging, and 5-Point Coordinate Alignment",
        "narrative": "Screens 5, 6, and 7 deliver comprehensive protection and maintenance. Screen 5 enforces hardware protection limits, clamping drive and dropping into standby within microseconds if S W R exceeds two point five to one or heatsink temperature reaches sixty degrees. Screens 6 and 7 provide real-time controller event logs and a built-in five-point touchscreen calibration utility.",
        "graphics": [
            ("screen_log_viewer.png", "FIG 14: JRFK WEB TOOLS SCREEN 6 - REAL-TIME FAULT LOG & TRIP MONITOR"),
            ("screen_screen_viewer.png", "FIG 15: JRFK WEB TOOLS SCREEN 7 - 5-POINT TOUCHSCREEN ALIGNMENT")
        ],
        "bullets": [
            ("Microsecond Protection Response", "Clamps exciter RF drive and disengages gate bias in under 5 microseconds when thresholds trip."),
            ("Trip Limits: VSWR 2.5:1 / Temp 60°C", "Enforces strict upper limits to safeguard LD MOS semiconductors against load mismatch or thermal runaway."),
            ("Persistent High-Power Event Log", "Logs trips, peak reflected events, and operating hours to persistent storage for post-event analysis."),
            ("5-Point Coordinate Matrix", "Recalibrates 7-inch resistive touchscreen digitizer coordinates directly from the web interface."),
            ("Operating Note (K7BIT)", "A 5-point touch calibration utility ensures accurate fingertip alignment on resistive 7-inch LCD displays.")
        ]
    },
    {
        "id": 10,
        "part": "TOPIC 4: RECOVERY & DOCUMENTATION",
        "category": "THE JRFK MIGRATION SUITE • TOOL 3: DISASTER RECOVERY",
        "title": "TOOL 3: THE 3-MINUTE DISASTER RECOVERY STANDBY CARD",
        "subtitle": "Pre-Cloned Boot Media Strategy for High-Stakes Contest and Field Operations",
        "narrative": "Tool 3 is the Disaster Recovery Engine. During the migration workflow, J R F K provisions an identical secondary S D card containing the complete sixty-four-bit operating system and all current calibration offsets. If an S D card ever suffers hardware failure during contest operations, the operator simply inserts the standby card and powers up, returning K7BIT to full operation in under three minutes.",
        "graphics": [
            ("screen_backup_manager.png", "FIG 16: JRFK WEB TOOLS DISASTER RECOVERY - STANDBY MEDIA CLONING")
        ],
        "bullets": [
            ("Contest-Ready Cold Standby", "Generates an exact bootable twin SD card during provisioning, ready for instant emergency swap."),
            ("Mirrored Calibration & Band Offsets", "All coupler corrections, band parameters, and antenna routing tables reside permanently on the clone."),
            ("Sub-3-Minute Mean Time to Restore", "Power off, swap the front-panel micro-SD card, and power up directly into fully calibrated operation."),
            ("Offline Readiness", "Requires zero internet access, zero laptop connections, and zero terminal commands during field recovery."),
            ("Operating Note (K7BIT)", "Contest hours are irreplaceable—having a verified standby card guarantees station availability when it matters most.")
        ]
    },
    {
        "id": 11,
        "part": "TOPIC 4: RECOVERY & DOCUMENTATION",
        "category": "THE JRFK MIGRATION SUITE • TOOL 3: DISASTER RECOVERY",
        "title": "TOOL 3: FIRST-BOOT AUTOMATION & SELF-HEALING SERVICES",
        "subtitle": "Partition Expansion, Modeline Injection, and Systemd Hardware Watchdogs",
        "narrative": "Supporting disaster recovery is our first-boot automation framework. Upon initial startup, the setup script expands the Linux root partition to fill the S D card, applies network configurations, and enables system D service watchdogs. These watchdogs actively supervise all background daemons, automatically restarting them without operator intervention if an abnormal state occurs.",
        "graphics": [
            ("screen_health_manager.png", "FIG 17: JRFK WEB TOOLS HEALTH MANAGER - SYSTEMD DAEMON ACTIVE WATCHDOGS"),
            ("screen_system_report.png", "FIG 18: JRFK WEB TOOLS FIRST-BOOT PARTITION EXPANSION & KERNEL STATUS")
        ],
        "bullets": [
            ("Dynamic ext4 Partition Expansion", "Automatically resizes root partition on first boot to utilize 100% of 16GB, 32GB, or 64GB media capacity."),
            ("Automated Network Re-Binding", "Configures fallback static IP (192.168.1.189) alongside DHCP, ensuring access even without a local router."),
            ("Hardware Kernel Watchdog", "Integrates with internal Broadcom watchdog timer to reboot controller if kernel hangs during transmission."),
            ("Daemon Restart Watchdogs", "Systemd supervises all 7 backend daemons with automatic restart on unexpected exit."),
            ("Operating Note (K7BIT)", "Autonomous service self-healing ensures background telemetry daemons restart instantly after transient brownouts.")
        ]
    },
    {
        "id": 12,
        "part": "TOPIC 4: RECOVERY & DOCUMENTATION",
        "category": "THE JRFK MIGRATION SUITE • TOOL 4: ENGINEERING LIBRARY",
        "title": "TOOL 4: MASTER ENGINEERING LIBRARY & COOKBOOK READER",
        "subtitle": "4-Volume Engineering Library and K7BIT's Authentic 193-Page B26 Cookbook",
        "narrative": "Tool 4 is the Master Documentation Portal. The portal hosts our complete four-volume engineering library covering operation, remote telemetry, and architecture. Furthermore, K seven B I T's authentic one hundred ninety-three page B twenty-six cookbook is integrated directly into the portal, providing operators and builders with instant, searchable access to original schematics and wiring diagrams from any browser.",
        "graphics": [
            ("screen_docs_viewer.png", "FIG 19: JRFK WEB TOOLS DOCS VIEWER - K7BIT 193-PAGE B26 COOKBOOK & SCHEMATICS")
        ],
        "bullets": [
            ("Integrated Technical Portal", "Served locally on port 8088, providing full documentation access completely offline at K7BIT."),
            ("Complete 4-Volume Library", "Includes User Guide, Remote Operations, Emergency Recovery, and Controller Architecture manuals."),
            ("K7BIT 193-Page Master B26 Cookbook", "Authentic engineering reference with complete schematics, relay tables, coupler specs, and wiring."),
            ("Interactive Searchable PDF Viewer", "Embedded JavaScript document viewer allows instant keyword searching, zooming, and schematic tracing."),
            ("Operating Note (K7BIT)", "Integrated schematics and wire tables provide immediate on-screen guidance during hardware maintenance and testing.")
        ]
    },
    {
        "id": 13,
        "part": "TOPIC 4: RECOVERY & DOCUMENTATION",
        "category": "THE JRFK MIGRATION SUITE • SUMMARY & RESOURCES",
        "title": "SUMMARY & MASTER RESOURCE DIRECTORY",
        "subtitle": "64-Bit Modernization Ecosystem: Migrator, JRFK Web Tools, Recovery & Docs",
        "narrative": "In summary, the JRFK modernization suite delivers a complete sixty-four-bit transformation: automated migration, the seven-screen JRFK Web Tools, instant disaster recovery, and comprehensive technical documentation. All downloads, source code, and community discussions are accessible at the links displayed on your screen. Thank you for watching, and seventy-three from K seven B I T.",
        "graphics": [
            ("jrfk_migrator.png", "FIG 20: JRFK.EXE MIGRATOR SUITE - WINDOWS STANDALONE EXECUTABLE"),
            ("screen_health_monitor.png", "FIG 21: JRFK WEB TOOLS - 64-BIT CONTROLLER PLATFORM (PORT 8088)")
        ],
        "bullets": [
            ("JRFK Standalone Migrator", "Single 166MB Windows executable with elevation launcher, format prompt suppressor, and Drive Guard."),
            ("7-Screen JRFK Web Tools", "Runs on port 8088 for RF metering, CAT band switching, 53.5V DC rail telemetry, and antenna matrix."),
            ("3-Minute Disaster Recovery", "Pre-cloned standby SD media strategy delivers instant sub-3-minute recovery during contested operation."),
            ("Master Engineering Library", "Local port 8088 docs portal featuring K7BIT's authentic 193-page B26 cookbook and schematics."),
            ("Operating Note (K7BIT)", "73 from K7BIT—engineering reliable, high-power amateur radio stations for modern contest and DX operations.")
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
        
    graphics_html = ""
    num_graphics = len(slide["graphics"])
    img_max_h = "360px" if num_graphics > 1 else "740px"
    
    for img_file, caption in slide["graphics"]:
        img_rel_path = f"real_screenshots/{img_file}"
        graphics_html += f"""
        <div class="graphic-item">
            <div class="image-frame">
                <img src="{img_rel_path}" style="max-height: {img_max_h};" alt="{caption}">
            </div>
            <div class="image-caption">{caption}</div>
        </div>
        """
    
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
        width: 1920px;
        height: 1080px;
        background: #050b14;
        color: #e2e8f0;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        padding: 40px 60px;
        position: relative;
        overflow: hidden;
    }}
    body::before {{
        content: "";
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        background: 
            radial-gradient(circle at 10% 15%, rgba(14, 165, 233, 0.15) 0%, transparent 40%),
            radial-gradient(circle at 90% 85%, rgba(59, 130, 246, 0.10) 0%, transparent 40%),
            linear-gradient(to right, rgba(56, 189, 248, 0.03) 1px, transparent 1px),
            linear-gradient(to bottom, rgba(56, 189, 248, 0.03) 1px, transparent 1px);
        background-size: 100% 100%, 100% 100%, 50px 50px, 50px 50px;
        pointer-events: none;
    }}
    .header {{
        border-bottom: 2px solid rgba(56, 189, 248, 0.35);
        padding-bottom: 16px;
        display: flex;
        justify-content: space-between;
        align-items: flex-end;
        position: relative;
        z-index: 2;
    }}
    .header-left {{
        display: flex;
        flex-direction: column;
        gap: 4px;
    }}
    .tagline {{
        font-family: "Consolas", monospace;
        font-size: 13px;
        letter-spacing: 2px;
        color: #38bdf8;
        text-transform: uppercase;
        font-weight: 700;
    }}
    .title {{
        font-size: 34px;
        font-weight: 800;
        letter-spacing: -0.5px;
        color: #ffffff;
        text-shadow: 0 2px 8px rgba(0,0,0,0.6);
    }}
    .subtitle {{
        font-size: 16px;
        color: #94a3b8;
        font-weight: 400;
    }}
    .header-right {{
        text-align: right;
        font-family: "Consolas", monospace;
        font-size: 13px;
        color: #64748b;
        letter-spacing: 1.5px;
    }}
    .content-grid {{
        display: grid;
        grid-template-columns: 1fr 2fr;
        gap: 36px;
        align-items: stretch;
        margin: 20px 0;
        position: relative;
        z-index: 2;
        flex: 1;
    }}
    .cards-col {{
        display: flex;
        flex-direction: column;
        gap: 10px;
        justify-content: center;
    }}
    .bullet-card {{
        background: rgba(15, 23, 42, 0.85);
        border: 1px solid rgba(56, 189, 248, 0.2);
        border-left: 4px solid #38bdf8;
        border-radius: 6px;
        padding: 12px 18px;
        box-shadow: 0 3px 12px rgba(0,0,0,0.35);
    }}
    .bullet-title {{
        font-size: 16px;
        font-weight: 700;
        color: #f1f5f9;
        margin-bottom: 3px;
        display: flex;
        align-items: center;
        gap: 8px;
    }}
    .bullet-title::before {{
        content: "■";
        color: #38bdf8;
        font-size: 11px;
    }}
    .bullet-desc {{
        font-size: 13.5px;
        line-height: 1.4;
        color: #94a3b8;
    }}
    .image-col {{
        display: flex;
        flex-direction: column;
        justify-content: center;
        gap: 16px;
    }}
    .graphic-item {{
        display: flex;
        flex-direction: column;
        align-items: center;
    }}
    .image-frame {{
        background: #0b1322;
        padding: 8px;
        border-radius: 8px;
        border: 1px solid rgba(56, 189, 248, 0.35);
        box-shadow: 0 8px 30px rgba(0,0,0,0.6);
        width: 100%;
        display: flex;
        justify-content: center;
        align-items: center;
    }}
    .image-frame img {{
        max-width: 100%;
        border-radius: 4px;
        display: block;
        object-fit: contain;
    }}
    .image-caption {{
        margin-top: 6px;
        font-family: "Consolas", monospace;
        font-size: 11.5px;
        color: #38bdf8;
        letter-spacing: 1px;
        text-align: center;
    }}
    .footer {{
        border-top: 1px solid rgba(255,255,255,0.1);
        padding-top: 12px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-family: "Consolas", monospace;
        font-size: 12px;
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
            <div>K7BIT</div>
            <div>SLIDE {slide['id']:02d} OF 13</div>
        </div>
    </div>
    
    <div class="content-grid">
        <div class="cards-col">
            {bullets_html}
        </div>
        <div class="image-col">
            {graphics_html}
        </div>
    </div>
    
    <div class="footer">
        <div class="footer-left">JRFK 64-BIT MODERNIZATION SUITE • HIGH-POWER AMATEUR RADIO • K7BIT</div>
        <div class="footer-right">GITHUB.COM/BIRDIEBOUGHT/JRFKTOOLS</div>
    </div>
</body>
</html>
"""

async def build_deck1_master():
    print("=== BUILDING DECK 1 MASTER (MIGRATION TOPIC 2, JRFK WEB TOOLS, ZERO STATION, BRIAN VOICE) ===")
    
    # 1. Write HTML slides
    for slide in SLIDES:
        html_file = os.path.join(DECK_DIR, f"slide_{slide['id']:02d}.html")
        with open(html_file, "w", encoding="utf-8") as f:
            f.write(generate_slide_html(slide))
        print(f"Generated HTML: {html_file}")
        
    # 2. Render 1080p PNG slides via Playwright
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1920, "height": 1080})
        
        for slide in SLIDES:
            sid = slide['id']
            html_file = os.path.join(DECK_DIR, f"slide_{sid:02d}.html")
            deck_png = os.path.join(DECK_DIR, f"slide_{sid:02d}.png")
            
            url = f"file:///{html_file.replace(os.sep, '/')}"
            await page.goto(url, wait_until="networkidle")
            await page.screenshot(path=deck_png)
            print(f"Rendered PNG: slide_{sid:02d}.png (1920x1080)")
            
        await browser.close()
        
    # 3. Synthesize Speech with BrianNeural voice, natural terms, zero "station", zero "John"
    voice = "en-US-BrianNeural"
    timing_table = []
    
    for slide in SLIDES:
        sid = slide['id']
        raw_text = slide['narrative']
        clean_text = clean_for_speech(raw_text)
        
        deck_mp3 = os.path.join(DECK_DIR, f"slide_{sid:02d}.mp3")
        
        print(f"Synthesizing Audio for Slide {sid:02d} ({voice})...")
        communicate = edge_tts.Communicate(clean_text, voice)
        await communicate.save(deck_mp3)
            
        length = mutagen.mp3.MP3(deck_mp3).info.length
        frames = round(length * 30)
        timing_table.append((sid, slide['title'], length, frames))
        
    print("\n=== FINAL VSDC TIMING MAP (DECK 1 - K7BIT) ===")
    total_sec = sum(t[2] for t in timing_table)
    m, s = divmod(total_sec, 60)
    print(f"Total Duration: {int(m):02d}:{s:05.2f}")
    for sid, title, length, frames in timing_table:
        print(f"Slide {sid:02d} | {length:5.2f}s | {frames:4d} frames | {title}")

if __name__ == "__main__":
    asyncio.run(build_deck1_master())
