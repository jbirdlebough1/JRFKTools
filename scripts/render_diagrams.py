import urllib.request
import base64
import os
import re
import sys
import textwrap

DIAGRAM_DIR = "/mnt/d/JRFK/docs/images/diagrams"
os.makedirs(DIAGRAM_DIR, exist_ok=True)

diagrams = {
    "arch_migration": """flowchart TD
    subgraph Legacy ["Legacy 32-bit Architecture"]
        A1["Debian 11 Bullseye<br/>(armhf)"]
        A2["Python 3.7<br/>(Deprecated)"]
        A3["Bundled 32-bit ARM<br/>ELF Shared Objects"]
        A4["Hardcoded Pi 4<br/>VL805 PCIe Path"]
    end
    subgraph Target ["Universal 64-bit Appliance Platform"]
        B1["Debian 12/13<br/>Bookworm (aarch64)"]
        B2["Python 3.11/3.13<br/>Runtime Optimized"]
        B3["Native 64-bit<br/>Hamlib Bridge"]
        B4["Universal Udev<br/>Dual-Link Controller"]
        B5["Full KMS 1024x600<br/>60Hz DRM Modeline"]
        B6["RFK Tools Suite<br/>Server (:8088)"]
    end
    Legacy ==>|"JRFK Automated Migration"| Target""",

    "hardware_parity": """sequenceDiagram
    autonumber
    actor MCU as Controller MCU (USB)
    participant Kernel as Linux Kernel (DRM/USB)
    participant Udev as Udev Rule Engine
    participant App as RF-KIT GUI (interface.py)
    MCU->>Kernel: Connects via USB (CDC-ACM / Serial)
    Kernel->>Udev: Matches Subsystem ttyACM* or ttyUSB*
    Udev->>Udev: Creates stable /dev/rfk_controller
    Udev->>Udev: Creates legacy symlink /dev/serial/by-path/platform-fd500000...
    App->>Kernel: Connects to hardcoded legacy path
    Kernel-->>App: Direct Bidirectional Serial Pipe (115200 8-N-1)""",

    "update_pipeline": """flowchart TD
    Start["Operator Initiates<br/>Update in GUI"] --> Connect["Connect to SFTP<br/>(webspace-data.io)"]
    Connect --> FetchManifest["Download & Parse<br/>version.json"]
    FetchManifest --> Compare["Compare controller<br/>& GUI versions"]
    Compare --> Download["Download gui.zip<br/>& firmware.bin"]
    Download --> Verify["Verify SHA256<br/>Integrity Hashes"]
    Verify --> FlashMCU["Flash Controller MCU<br/>via SimpleRPC"]
    FlashMCU --> Unpack["Unpack zip into<br/>rf-kit-gui_v{new}"]
    Unpack --> PatchHook["64-Bit Self-Healing Hook<br/>(Inject aarch64 Hamlib & shims)"]
    PatchHook --> UpdatePtr["Update gui_path.json<br/>(start: v_new, fallback: v_old)"]
    UpdatePtr --> Restart["Execute<br/>gui_starter.py"]
    Restart --> ExecTest{"main.py runtime<br/>> 3 seconds?"}
    ExecTest -- Yes --> Success["Update Successful!<br/>Running New Version"]
    ExecTest -- No --> Fallback["Automatic Rollback<br/>to fallback folder"]""",

    "backup_flow": """flowchart LR
    Active["Active Internal<br/>Boot SD Card<br/>(/dev/mmcblk0)"] -->|"Live Block Stream &<br/>PARTUUID Regeneration"| Target["External USB<br/>SD Card Reader<br/>(/dev/sda)"]
    Target --> Emergency["100% Plug-and-Play<br/>Disaster Recovery Spare"]""",

    "diagnostics_arch": """flowchart TD
    subgraph DataSources ["Telemetry & Data Plane"]
        CAN["SocketCAN (can0)<br/>53.5V Rail & Current"]
        MCU["Controller MCU<br/>Tuner L/C/K EEPROM"]
        RFK["RF-KIT GUI Core<br/>REST API (:8080)"]
    end
    subgraph ToolsServer ["RFK Tools Suite Server (Port 8088)"]
        Daemon["Telemetry Polling Daemon<br/>(Every 5 Seconds)"]
        RingBuf["1-Hour High-Res RAM Buffer<br/>(720 Data Points)"]
        SQLite["24-Hour Rolling SQLite DB<br/>(telemetry_history.db)"]
    end
    subgraph UserInterface ["Operator Diagnostic Tools"]
        Mapper["Antenna Mapper<br/>SWR Matrix & Segment Inspection"]
        Health["Amplifier Health Monitor<br/>Power, Sag, Thermal Profile"]
        Print["Standard CUPS / IP Network Printing<br/>(@media print Vector Sheet)"]
    end
    DataSources --> Daemon
    Daemon --> RingBuf
    Daemon --> SQLite
    RingBuf --> Health
    SQLite --> Health
    MCU --> Mapper
    Mapper --> Print
    Health --> Print""",

    "controller_comm_flow": """sequenceDiagram
    autonumber
    participant GUI as Python RFK GUI (thread_controller.py)
    participant Pipe as Serial Interface (/dev/rfk_controller 115200 8N1)
    participant MCU as Controller MCU (Mega 2560 / Updated Controller)
    participant HW as Hardware Sensors, Relays & Bias
    loop Every 20ms to 50ms High-Speed Telemetry Poll
        GUI->>Pipe: SimpleRPC: get_all_values()
        Pipe->>MCU: Packed Frame: Method ID 0x14
        MCU->>HW: Sample Fast ADC Channels (FWD, REF, Idq, 53V, Temp)
        HW-->>MCU: Raw Analog Voltages
        MCU-->>Pipe: SimpleRPC Return 20-Tuple (FWD, REF, SWR, V, I, T, Flags)
        Pipe-->>GUI: Deserialized Tuple & Dynamic GUI Strip Refresh
    end
    Note over GUI,HW: Transmit (PTT) Event Triggered
    GUI->>Pipe: SimpleRPC: set_operate_mode(1)
    Pipe->>MCU: Method ID 0x07 (Operate State = ON)
    MCU->>HW: Assert LPF / Antenna Relays & Enable LDMOS Gate Bias
    HW-->>MCU: Status Verified
    MCU-->>GUI: Return OK
    Note over HW,GUI: Hardware Overdrive / SWR Fault Exception
    HW->>MCU: Fast Analog Comparator Trip (Input > 30W / SWR > 3.0:1)
    MCU->>HW: Instant Hardware Cutoff (< 5ms) Disables Bias & Drops TX Relay
    MCU-->>Pipe: Sets Error Flag in get_all_values() Tuple
    Pipe-->>GUI: GUI Pops "Input Power Too High! Press Reset" Modal""",

    "backup_restore_sequence": """sequenceDiagram
    autonumber
    actor Admin as Station Operator
    participant UI as RFK Tools Web UI (:8088/backup)
    participant Cron as Cron Service (/etc/cron.d/jrfk_weekly_backup)
    participant Script as rfk_backup.sh Cloner
    participant BootSD as Primary Boot SD (/dev/mmcblk0)
    participant SpareSD as External USB SD Reader (/dev/sda)
    Admin->>UI: Selects Backup Schedule (e.g., Sunday 03:00 AM)
    UI->>Cron: Writes Automated Cron Job Entry
    Note over Cron,Script: Automated Weekly Trigger Fired
    Cron->>Script: Execute rfk_backup.sh --auto
    Script->>SpareSD: Scans and Validates External Target Media
    Script->>BootSD: Performs Live Partition Stream & File Sync
    Script->>SpareSD: Writes New Partition UUIDs (Prevents UUID Collisions)
    Script->>SpareSD: Copies Calibration, Configs & SQLite Databases
    Script-->>Cron: Backup Completed Cleanly (/var/log/rfk_backup.log)
    Note over BootSD,Admin: Catastrophic Boot Media Failure Scenario
    Admin->>BootSD: Removes Corrupted Primary SD from Amplifier Slot
    Admin->>SpareSD: Inserts Cloned Spare SD Directly into Internal Slot
    Admin->>SpareSD: Powers On Amplifier (BOOT 1: Disaster Recovery)
    SpareSD->>SpareSD: First-boot script verifies filesystem & regenerates machine-id
    SpareSD->>SpareSD: Clean Automatic Reboot
    SpareSD->>Admin: BOOT 2: Direct Launch into RFKGUI with All User Data Intact!""",

    # Modular Staging Panels (Chapter 17)
    "lifecycle_stage1_extract": """sequenceDiagram
    autonumber
    actor User as Operator
    participant PC as Windows 11 PC (Host)
    participant OrigSD as Original Working SD (from Amp)
    participant Store as PC Local Storage (C:\\RFK_Backups)
    User->>PC: Insert Original SD into USB Card Reader
    PC->>OrigSD: Mount ext4 Linux Partition (Read-Only)
    PC->>OrigSD: Extract /home/pi/PA-Files/ (calibration.json, touch, offsets)
    PC->>OrigSD: Extract WiFi credentials & network settings
    PC->>Store: Archive Golden Master (RFK_Golden_Master.tar.gz)
    PC-->>User: Prompt: Safely Remove & Store Original SD as Untouched Master""",

    "lifecycle_stage2_target_sd": """sequenceDiagram
    autonumber
    actor User as Operator
    participant PC as Windows 11 PC (Host)
    participant NewSD as Brand New 32GB SD (A2 / V30 / U3)
    participant Web as Debian / Raspberry Pi Repositories
    User->>PC: Insert New 32GB High-Endurance SD Card
    PC->>Web: Fetch Official 64-Bit Bookworm OS & Kernel 6.6+ Patches
    PC->>NewSD: Flash 64-Bit OS & Provision Multi-Arch Runtime
    PC->>NewSD: Configure Weekly Maintenance Cron (Sun 4:00 AM Upgrade)
    PC->>NewSD: Inject Extracted User Calibrations & rfk_tools_suite
    PC->>NewSD: Validate Filesystem Structure & Permissions (pi:pi 755)
    PC-->>User: Prompt: Eject Card & Install in RF-KIT Amplifier""",

    "lifecycle_stage3_boot1": """sequenceDiagram
    autonumber
    actor User as Operator
    participant Amp as RF-KIT Amplifier (RPi 4 or RPi 5)
    participant Kernel as 64-Bit Linux Kernel & Systemd
    User->>Amp: Insert New 64-Bit SD & Turn On Main AC Power
    Amp->>Kernel: Boot 1 Initial Hardware Discovery
    Kernel->>Kernel: Auto-expand root filesystem to fill full 32GB
    Kernel->>Kernel: Generate unique machine-id & D-Bus UUIDs
    Kernel->>Kernel: Configure DSI / HDMI Display Timing (800x480 / 1024x600)
    Kernel->>Kernel: Verify USB / Serial UART (/dev/rfk_controller)
    Kernel->>Amp: Trigger Automatic Clean Soft Reboot (reboot)""",

    "lifecycle_stage4_boot2": """sequenceDiagram
    autonumber
    actor User as Operator
    participant Kernel as Linux 64-Bit OS
    participant GUI as RFKGUI Fullscreen Touch Interface
    participant Suite as RFK Tools Suite (:8088)
    participant MCU as Controller MCU (SimpleRPC)
    Kernel->>GUI: Launch RFKGUI via Pure KMS / X11 Session
    GUI->>MCU: Handshake SimpleRPC (115200 8N1)
    MCU-->>GUI: Return Operational Status & Sensor Array
    GUI->>GUI: Load Injected User Calibrations & Band Mappings
    Kernel->>Suite: Start rfk_tools_suite (:8088) & Backup Watcher
    GUI-->>User: Amplifier Fully Operational! 100% Calibrations Active""",

    # Modular Calibration Panels (Chapter 9)
    "calibration_phase1": """flowchart TD
    Start["Phase 1: Bench Safety & DC Setup"] --> Step1["Step 1-3: Disable Protections & Preset SPARE Pot"]
    Step1 --> Step4["Step 4: Calibrate 53.5V DC Display<br/>(R1/R2 Trimmers to match DMM)"]
    Step4 --> Step5["Step 5: Verify PA Bias Jumpers<br/>(Remove jumpers, verify 0V bias)"]
    Step5 --> Step6["Step 6: Verify RF Coax Continuity<br/>(Inject 5W into bypass harness)"]""",

    "calibration_phase2": """flowchart TD
    Start["Phase 2: Frequency & Filter Integration"] --> Step7["Step 7: Calibrate Prescaler Counter<br/>(74HC4040/74 counter bus)"]
    Step7 --> Step8["Step 8: Verify LPF Auto-Band Select<br/>(Cycle 160m - 6m across toroid relays)"]""",

    "calibration_phase3": """flowchart TD
    Start["Phase 3: SWR Bridge & RF Power Alignment"] --> Step9["Step 9: Null SWR Bridge Balance<br/>(C_null trimmers into 50Ω & 25Ω)"]
    Step9 --> Step10["Step 10: Calibrate FWD (R19) & REF (R20)<br/>(Align display to 50W into calibrated load)"]
    Step10 --> Step11["Step 11: Calibrate Tuner Pre-Amp Gain<br/>(R15 to 600 ADC @ 10W into 25Ω)"]""",

    "calibration_phase4": """flowchart TD
    Start["Phase 4: Protection Trips & PA Reassembly"] --> Step12["Step 12: Calibrate LPF Protection Trip<br/>(R17 trimmer to 93 ADC @ 50W)"]
    Step12 --> Step13["Step 13: Calibrate Input Overdrive Trip<br/>(R1/R2 trimmer trip @ 28W limit)"]
    Step13 --> Step14["Step 14: Align Drive Yellow Warning Bar<br/>(R14 trimmer @ 27W drive)"]
    Step14 --> Step15["Step 15: Calibrate Idq Quiescent Current<br/>(R21 trimmer for BLF189XR to match DMM)"]
    Step15 --> Step16["Step 16: Calibrate Current Limiter Latch<br/>(SPARE pot to 1000 ADC)"]
    Step16 --> Step17["Step 17: Final Amplifier Reassembly<br/>(Resolder PA pads, remove test harness)"]""",

    # Modular RF Signal Chain Panels (Chapter 7)
    "rf_stage1_input": """flowchart LR
    TRX["Transceiver RF Input<br/>(SO-239 TRX Jack)"] --> ATT["Chassis Step Attenuator<br/>(13 dB / 16 dB Flange Mount)"]
    ATT --> TVS["TVS Diode Gate Clamp<br/>(1.5KE8.2A Clamps @ 11V)"]
    TVS --> DET["Fast RF Peak Detector<br/>(Schottky Comparator Loop)"]""",

    "rf_stage2_pallet": """flowchart LR
    DET["Phase Splitter Balun<br/>(Input Matching)"] --> LDMOS["Push-Pull Ampleon BLF189XR<br/>(1500W+ PEP, 53.5V @ 38A)"]
    PSU["53.5V / 55A DC Bus<br/>(Eltek Flatpack2)"] --> LDMOS
    BIAS["Quiescent Bias Trimmers<br/>(Vgs = 1.8V - 2.6V, Idq = 1.5A - 2.0A)"] --> LDMOS
    LDMOS --> BALUN["Output Combining Balun<br/>(50Ω Coaxial Line)"]""",

    "rf_stage3_lpf_swr": """flowchart LR
    BALUN["50Ω PA Output"] --> LPF["Toroidal Low-Pass Filter<br/>(7 Bands: 160m to 6m)"]
    LPF --> SWR["Tandem Match SWR Bridge<br/>(FT50-43 Cores & 2.9V Ref)"]
    SWR --> ATU["Switched L/C Matching Matrix<br/>(Binary Relays K1 - K16)"]""",

    "rf_stage4_output": """flowchart LR
    ATU["ATU Output"] --> TR["High-Speed Vacuum / PIN T/R Relay<br/>(Sequenced < 5ms)"]
    TR --> SW["4-Port Coax Switch Matrix<br/>(4 x High-Isolation Relays)"]
    SW --> ANT["Antenna Ports 1 to 4<br/>(Ant 1 = Default Dummy Load)"]"""
}

def convert_foreign_object_to_native_text(svg):
    def replacer(match):
        w_str = match.group(1)
        h_str = match.group(2)
        inner = match.group(3)
        try:
            w = float(w_str)
            h = float(h_str)
        except ValueError:
            w = 120.0
            h = 40.0

        s = re.sub(r'</p>\s*<p>', '\n', inner)
        s = re.sub(r'<br\s*/?>', '\n', s, flags=re.IGNORECASE)
        s = re.sub(r'<[^>]+>', '', s)
        raw_lines = [line.strip() for line in s.split('\n') if line.strip()]

        if not raw_lines:
            return ""

        max_chars = max(12, int(w / 7.2))
        wrapped_lines = []
        for rl in raw_lines:
            sub = textwrap.wrap(rl, width=max_chars)
            if sub:
                wrapped_lines.extend(sub)
            else:
                wrapped_lines.append(rl)

        cx = w / 2.0
        font_size = 10.5
        line_height = 13.0
        total_text_h = len(wrapped_lines) * line_height
        start_y = (h - total_text_h) / 2.0 + (font_size * 0.85)

        tspans = []
        for idx, line in enumerate(wrapped_lines):
            y_pos = start_y + (idx * line_height)
            esc_line = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            tspans.append(f'<tspan x="{cx:.1f}" y="{y_pos:.1f}">{esc_line}</tspan>')

        return f'<text x="{cx:.1f}" text-anchor="middle" font-family="-apple-system, BlinkMacSystemFont, \'Segoe UI\', Roboto, \'Helvetica Neue\', Arial, sans-serif" font-size="{font_size}px" font-weight="600" fill="#1a202c">{"".join(tspans)}</text>'

    cleaned = re.sub(r'<foreignObject[^>]*width="([^"]+)"[^>]*height="([^"]+)"[^>]*>(.*?)</foreignObject>', replacer, svg, flags=re.DOTALL)
    return cleaned

for name, code in diagrams.items():
    svg_path = os.path.join(DIAGRAM_DIR, f"{name}.svg")
    print(f"[*] Rendering diagram {name}...")
    encoded = base64.b64encode(code.encode('utf-8')).decode('ascii')
    url = f"https://mermaid.ink/svg/{encoded}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            svg_content = resp.read().decode('utf-8')
            svg_content = convert_foreign_object_to_native_text(svg_content)
            with open(svg_path, 'w', encoding='utf-8') as f:
                f.write(svg_content)
            print(f" [+] Saved with native wrapped text: {svg_path} ({len(svg_content)} bytes)")
    except Exception as e:
        print(f" [-] Failed to render {name}: {e}")

print("[*] All diagram SVG renderings processed.")
