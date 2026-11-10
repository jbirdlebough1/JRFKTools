import os
import re

MD_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs", "JRFK_EM.md")

with open(MD_PATH, "r", encoding="utf-8") as f:
    content = f.read()

# Marker separating front/Ch1 from Ch2
marker = "# 2. Controller Evolution: Original Mega 2560 vs. Updated Controller"
parts = content.split(marker)
if len(parts) != 2:
    raise ValueError(f"Could not find unique marker in {MD_PATH}")

front = parts[0]
body = marker + parts[1]

# 1. Update the Table of Contents in front
# Find the TOC block between '# Table of Contents' and '# 1. Executive Summary'
toc_pattern = r"(# Table of Contents\s*\n\n)(1\. \[Executive Summary[\s\S]*?)(# 1\. Executive Summary)"
toc_match = re.search(toc_pattern, front)
if not toc_match:
    raise ValueError("Could not find Table of Contents in front")

new_toc = """1. [Executive Summary & Migration Objective](#1-executive-summary--migration-objective)
2. [Hardware Installation, Turnkey 64-Bit SD Deployment & Commissioning Guide](#2-hardware-installation-turnkey-64-bit-sd-deployment--commissioning-guide)
   * 2.1 Pre-Installation Physical Safety & Chassis Preparation
   * 2.2 Turnkey 4-Phase Migration Lifecycle
   * 2.3 Raspberry Pi 4 vs. Raspberry Pi 5 Physical Installation
   * 2.4 First-Boot Autonomous Commissioning Sequence
3. [Controller Evolution: Original Mega 2560 vs. Updated Controller](#3-controller-evolution-original-mega-2560-vs-updated-controller)
   * 3.1 The Original B26 Mega 2560 Backplane Design
   * 3.2 The Updated Proprietary Controller & Documentation Status
   * 3.3 Circuit Parity: Why Operational Theory & Pin Functions Remain Identical
4. [Deep Architectural Analysis: 32-Bit (armhf) vs. 64-Bit (aarch64)](#4-deep-architectural-analysis-32-bit-armhf-vs-64-bit-aarch64)
   * 4.1 Register Pressure, ARMv8-A ISA & Telemetry Throughput
   * 4.2 Shared Object Architecture & The ELF Header Collision
   * 4.3 Compiler Optimization, SIMD Extensions & Memory Overhead
5. [Universal Single-SD Hardware Parity: RPi 4 vs. RPi 5](#5-universal-single-sd-hardware-parity-rpi-4-vs-rpi-5)
   * 5.1 Kernel & Device Tree Discrepancies
   * 5.2 USB Controller Path Fragmentation & Udev Dual-Link Architecture
   * 5.3 DRM Display Pipeline & Pure KMS Resolution Locking
   * 5.4 GPIO Architecture & Driver Pin Parity
6. [RF-KIT Application Execution Flow & Controller Interaction Deep Dive](#6-rf-kit-application-execution-flow--controller-interaction-deep-dive)
   * 6.1 Interface Process Decoupling Architecture
   * 6.2 The SimpleRPC Protocol Wire-Format & Framing Specification
   * 6.3 High-Speed 20ms–50ms Polling Loop & State Machine Dynamics
   * 6.4 The 20-Element Telemetry Return Tuple: Bitfields & Register Mappings
   * 6.5 Exhaustive Catalog of All 71 Remote Procedure Calls (RPCs)
7. [Microcontroller Backplane Hardware Architecture](#7-microcontroller-backplane-hardware-architecture)
   * 7.1 Arduino Mega 2560 R3 vs. Updated Proprietary Controller
   * 7.2 Header Pinout, Bus Routing & Hardware Resource Allocation
   * 7.3 ADC Prescalers, Sampling Windows & Anti-Aliasing Filters
   * 7.4 ULN2803 Relay Drivers, Optoisolators & PTT Sequencing Loops
   * 7.5 Non-Volatile Memory Architecture: FM24CL64 FRAM & MB85RC64 EEPROM
8. [RF Signal Chain, Pallet & Peripheral Circuit Theory (K7BIT B26 Integration)](#8-rf-signal-chain-pallet--peripheral-circuit-theory-k7bit-b26-integration)
   * 8.1 The End-to-End RF Signal Flow
   * 8.2 Step Attenuator Sizing, Transient Surge Protection & TVS Gate Clamping
   * 8.3 Dual Directional Couplers & Stockton/Tandem Match Bridge Architecture
   * 8.4 Low Pass Filter (LPF) Board: Toroidal Band Switching & Harmonic Suppression
   * 8.5 Automatic Antenna Tuner (ATU) Board: Binary Stepped L/C Matching Network
   * 8.6 4-Port Coaxial Antenna Switch Board: Isolation & RF Relay Dynamics
   * 8.7 DC Power Supply Subsystem: Eltek Flatpack2 53.5V Rail & CAN Bus Control
   * 8.8 Thermal Management Subsystem: Front & Rear Fans, Venturi Shroud & Pinouts
   * 8.9 AC Mains Power Switch Wiring & Safety Modifications
9. [Transceiver Interfacing, CAT Control & CI-V Protocols](#9-transceiver-interfacing-cat-control--ci-v-protocols)
   * 9.1 Universal RF Sensing & Hardware Frequency Counter Interfacing
   * 9.2 Icom CI-V Protocol & Open-Collector Wiring
   * 9.3 Yaesu BCD Band Data & CAT Serial Emulation
   * 9.4 Kenwood, Elecraft & FlexRadio Serial Interfacing
10. [Exhaustive 17-Step K7BIT Bench Calibration Procedure](#10-exhaustive-17-step-k7bit-bench-calibration-procedure)
   * 10.1 Calibration Bench Setup, Test Equipment & Prerequisite Coax Bypass Harness
   * 10.2 Step 1: Temporarily Disable Input Protection
   * 10.3 Step 2: Temporarily Disable LPF Forward Power Protection
   * 10.4 Step 3: Preset SPARE Potentiometer
   * 10.5 Step 4: Calibrate 53.5V DC Voltage Display (R1/R2 Trimmers)
   * 10.6 Step 5: PA Pallet Bias Jumper Configuration & Verification
   * 10.7 Step 6: RF Coaxial Wiring Continuity & Port Verification
   * 10.8 Step 7: Frequency Detector Prescaler Calibration (74HC4040/74)
   * 10.9 Step 8: Low Pass Filter (LPF) Automatic Selection & Band Interfacing
   * 10.10 Step 9: SWR Bridge Balance & 2.9V Detector Reference Nulling
   * 10.11 Step 10: Forward (R19) and Reflected (R20) Power Display Alignment
   * 10.12 Step 11: Antenna Tuner Pre-Amplifier Gain Calibration (R15)
   * 10.13 Step 12: LPF Forward Power Protection Trip Calibration (R17)
   * 10.14 Step 13: Input Overdrive Protection Trip Calibration (R1/R2 at 28W)
   * 10.15 Step 14: Relative Input Drive Bar Alignment (R14 Trimmer)
   * 10.16 Step 15: LDMOS Quiescent Bias Current (Idq) Measurement & Calibration (R21)
   * 10.17 Step 16: Hardware Current Limiting Latch Calibration (SPARE Potentiometer)
   * 10.18 Step 17: Final Amplifier Assembly & PA Output Solder Re-Integration
11. [Complete 10-Part Amplifier Characterization & Unit Test Plan](#11-complete-10-part-amplifier-characterization--unit-test-plan)
   * 11.1 Test 1: Power Supply Unit (PSU) DC Rail Stability Under Load
   * 11.2 Test 2: 50V/53.5V Standby / Operate Remote Control Switching
   * 11.3 Test 3: Display & Capacitive Touchscreen Coordinate Alignment
   * 11.4 Test 4: Antenna Relay Board RF Isolation & Port Routing
   * 11.5 Test 5: Manual Antenna Tuner Stepping & Non-Volatile Memory Storage
   * 11.6 Test 6: Minimum Drive RF Characterization Across All Amateur Bands
   * 11.7 Test 7: 25W Drive CW Power Output & Linearity Baseline Matrix
   * 11.8 Test 8: Station Communications, Ethernet, Wi-Fi & VNC Operation
   * 11.9 Test 9: External USB Peripheral Port Verification
   * 11.10 Test 10: Transceiver Peak Turn-On Burst & Keying Sequencing Characterization
12. [Comprehensive Field Troubleshooting Guide & Fault Diagnostic Matrix](#12-comprehensive-field-troubleshooting-guide--fault-diagnostic-matrix)
   * 12.1 Power Supply, Boot & Hardware Startup Faults
   * 12.2 Microcontroller Communication & Serial Link Failures
   * 12.3 RF Drive, Attenuation & Input Overdrive Faults
   * 12.4 SWR Bridge, Directional Coupler & Output Sensing Faults
   * 12.5 Low Pass Filter (LPF) Relay Switching Faults
   * 12.6 Antenna Tuner (ATU) Stepping & Memory Retention Errors
   * 12.7 Thermal, Cooling Fan & Environmental Shutdown Faults
13. [Deep Dive: The RF-KIT Online Update Engine & Self-Healing Architecture](#13-deep-dive-the-rf-kit-online-update-engine--self-healing-architecture)
   * 13.1 The Remote Distribution Architecture & SFTP Synchronization
   * 13.2 Firmware Validation, Integrity Hashing & Flashing Mechanics
   * 13.3 64-Bit Binary Interception & The Self-Healing Injection Hook
   * 13.4 Fault Isolation & Automated Multi-Version Rollback Engine
14. [Storage Media Engineering & Sizing Standards](#14-storage-media-engineering--sizing-standards)
   * 14.1 Storage Sizing Matrix: 16GB, 32GB, and 64GB Deployments
   * 14.2 Application Performance Class (A2) & Endurance Requirements
   * 14.3 Wear-Leveling Mechanics & Filesystem Journal Optimization
15. [Automated Disaster Recovery & Backup Suite (RFK_Backup)](#15-automated-disaster-recovery--backup-suite-rfk_backup)
   * 15.1 Backup Media Topology & Live Hot-Cloning Engine
   * 15.2 Automated Weekly Cron Job Architecture & User Time Selection
   * 15.3 Disaster Recovery Workflow: The "Swap, Boot, Reboot, Run" Paradigm
16. [Integrated Diagnostic Suite Architecture (rfk_tools_suite on Port 8088)](#16-integrated-diagnostic-suite-architecture-rfk_tools_suite-on-port-8088)
   * 16.1 Port Allocation Matrix & Network Architecture
   * 16.2 Antenna Mapper Interface (/antenna)
   * 16.3 Amplifier Health & Thermal Monitor (/health)
   * 16.4 Backup & Disaster Recovery Web Manager (/backup)
17. [System Configuration, Database Engine & Station Personalization](#17-system-configuration-database-engine--station-personalization)
   * 17.1 Display Themes: Cross-Pointer vs Standard Bar Meters
   * 17.2 Station Callsign, Antenna Port Aliasing & Band Allocation
   * 17.3 Automated Weekly OS Maintenance Cron Engine
18. [Complete Step-by-Step Staging & Appliance Build Walkthrough](#18-complete-step-by-step-staging--appliance-build-walkthrough)
19. [Appendix: Complete Register Tables, Schematic References & Pin Mapping](#19-appendix-complete-register-tables-schematic-references--pin-mapping)

---

"""

front = front[:toc_match.start(2)] + new_toc + front[toc_match.end(2):]

# 2. Renumber chapters in body from 18 down to 2 -> 19 down to 3
for n in range(18, 1, -1):
    old_h1 = f"# {n}. "
    new_h1 = f"# {n+1}. "
    body = re.sub(r"^" + re.escape(old_h1), new_h1, body, flags=re.MULTILINE)
    body = re.sub(r"^(#{2,4} )" + str(n) + r"\.", r"\g<1>" + str(n+1) + ".", body, flags=re.MULTILINE)

# 3. New Chapter 2 text
chapter_2_text = """# 2. Hardware Installation, Turnkey 64-Bit SD Deployment & Commissioning Guide

### 2.1 Pre-Installation Physical Safety, Chassis Preparation & High-Voltage Discharge
Operating inside high-power solid-state RF power amplifiers requires rigorous adherence to high-voltage and high-current electrical safety protocols. The RF2K-S and RF2K+ amplifiers employ an internal **Eltek Flatpack2 HE 53.5 VDC power supply subsystem capable of delivering continuous currents up to 55 A (over 2,900 Watts of direct current energy)**.

> [!CAUTION]
> ### 53.5 VDC / 55 A BUS ENERGY & HIGH CAPACITANCE DISCHARGE HAZARD
> Before opening the amplifier chassis or touching the internal Raspberry Pi computer:
> * **Complete AC Mains Disconnection:** Switch off the front and rear AC mains switches and physically disconnect both AC power cords from the wall receptacles.
> * **Mandatory 60-Second Capacitor Bleed-Down Period:** The main 53.5V DC distribution bus contains an extensive low-ESR electrolytic filter capacitor bank. Even after AC power is removed, these capacitors store lethal energy levels. Allow a minimum of **60 full seconds** for the internal bleeder resistors to discharge the bus voltage below 2.0 VDC before removing chassis fasteners.
> * **Electrostatic Discharge (ESD) Protection:** Wear an ESD wrist strap connected to unpainted chassis ground. CMOS integrated circuits on the Raspberry Pi 4/5 and controller board are highly susceptible to ESD damage from body charge accumulations.

#### Chassis Access Mechanics
* **RF2K+ Chassis:** Access to the internal Raspberry Pi 4 is achieved by removing the 8 perimeter countersunk screws securing the ventilated top aluminum enclosure plate. Once lifted, the Raspberry Pi board is positioned on the left internal mounting bracket behind the front LCD bezel.
* **RF2K-S Chassis:** The RF2K-S utilizes an integrated modular sub-chassis. The compute module or Raspberry Pi is accessible by removing the top maintenance cowl or via the designated service port on the rear-left chassis quadrant.

#### MicroSD Card Slot Mechanics & Retention
* **Raspberry Pi 4 Model B:** The MicroSD slot is located on the underside of the PCB opposite the display ribbon connector. It features a **friction-fit push-pull** receptacle. When removing or inserting an SD card, grasp the edge firmly with tweezers or non-magnetic needle-nose pliers and pull directly outward in line with the PCB. Never bend or twist the card.
* **Raspberry Pi 5:** The MicroSD slot on the Raspberry Pi 5 also employs a high-retention push-pull connector. Ensure the card is inserted with the copper contacts facing downward toward the circuit board until seated flush against the internal stop.

---

### 2.2 Turnkey 4-Phase Migration Lifecycle

The JRFK 64-Bit Migration environment provides a zero-friction, automated 4-phase deployment lifecycle that guarantees 100% preservation of operator calibrations, touchscreen matrices, and transceiver CAT configurations:

```mermaid
sequenceDiagram
    autonumber
    actor User as Operator / Admin
    participant PC as Windows 11 PC (Host)
    participant SD as Target SD Card
    participant Pi as RF-KIT Amplifier (RPi)

    Note over User,PC: Phase 1: Golden Master Extraction & Verification
    User->>PC: Insert Original 32-bit SD Card (Reader E:)
    PC->>PC: Extract calibration.json, touch matrices & wifi
    PC->>PC: Create Golden Master Backup Archive (C:\\RFK_Backups)
    
    Note over User,SD: Phase 2: Safe SD Ejection & Hardware Labeling
    User->>PC: Click 'Safely Eject SD' in Stage 1 UI
    PC->>PC: Windows Shell flushes buffers & unmounts E:
    User->>User: Remove original card & label 'GOLDEN MASTER'
    
    Note over User,SD: Phase 3: Zero-Friction Target 64-Bit Provisioning
    User->>PC: Insert New Blank 16GB/32GB+ SD Card
    PC->>SD: Flash Debian 12 Bookworm 64-Bit (Dual Partition)
    PC->>SD: Inject JRFK Bits, User Calibrations & Credentials
    PC->>PC: Validate Partition 1 (FAT32) & Partition 2 (ext4)
    User->>PC: Click 'Safely Eject' in Stage 2 UI
    
    Note over User,Pi: Phase 4: In-Amplifier Deployment & Turnkey Autostart
    User->>Pi: Insert SD into Amplifier & Power On
    Pi->>Pi: Auto-expands rootfs across entire SD card
    Pi->>Pi: Loads touch.cal & locks KMS 1024x600 60Hz display
    Pi->>Pi: Binds /dev/rfk_controller via Universal Udev Dual-Link
    Pi->>Pi: Launches RFKGUI fullscreen & initializes Diagnostic Suite (:8088)
```

| Deployment Phase | Hardware Action | Automated Software Process | Operator Safety Rule |
| :--- | :--- | :--- | :--- |
| **Phase 1: Extraction** | Insert working 32-bit SD card into Windows USB reader. | Migrator interrogates SD card, extracts `/home/pi/PA-Files/` (`calibration.json`, `touch.cal`, attenuator offsets, WiFi). Packages into `RFK_Golden_Master.tar.gz`. | **Read-Only Safety:** Original SD card is never modified or partitioned. |
| **Phase 2: Safe Ejection** | Click **⏏️ Safely Eject SD** in Stage 1 UI. | Migrator triggers Windows COM `Shell.Application.Namespace(17).InvokeVerb('Eject')`, flushing filesystem buffers. | Remove card and write **"GOLDEN MASTER"** on adhesive label. Place safely in station drawer. |
| **Phase 3: Provisioning** | Insert blank 16GB/32GB+ SD card into reader. | Automated pipeline writes 64-bit Bookworm image, provisions FAT32 bootfs + ext4 rootfs, injects user calibrations and station credentials. | Select verified target disk (e.g. `Disk 2`). Never target system boot drives. |
| **Phase 4: Commissioning** | Eject target SD, install into amplifier RPi, power on. | First boot auto-expands rootfs, activates udev dual-link rule `/dev/rfk_controller`, boots directly into full-screen RFKGUI. | Turnkey appliance operation: Zero keyboard or mouse required. |

---

### 2.3 Raspberry Pi 4 vs. Raspberry Pi 5 Physical Installation

The JRFK 64-bit appliance architecture is universally backward- and forward-compatible across both the **Raspberry Pi 4 Model B** and the **Raspberry Pi 5**. Operators upgrading an existing amplifier or replacing a damaged single board computer must observe specific mechanical and thermal requirements:

#### Raspberry Pi 4 Model B Deployment
1. **Mechanical Mounting:** The Raspberry Pi 4 mounts to the internal aluminum chassis bracket via four M2.5 brass standoffs. Ensure the nylon or brass spacers maintain at least 3mm clearance above the chassis plate.
2. **HDMI Display Interface:** Connect the micro-HDMI display adapter cable to **Micro-HDMI Port 0** (the connector immediately adjacent to the USB-C power input port). Connecting to Port 1 will disable DRM framebuffer rendering on the front LCD.
3. **Internal USB Backplane Interconnection:** Connect the USB cable from the controller backplane to one of the **black USB 2.0 ports** (or blue USB 3.0 ports). The JRFK udev rule dynamically recognizes the controller regardless of port assignment.
4. **DC Power Harness:** Power is supplied via the 5V/3A DC buck converter harness connected to the 40-pin GPIO header (`Pin 2 / Pin 4: +5VDC`, `Pin 6: Ground`) or via the USB-C power port.

#### Raspberry Pi 5 Deployment & Upgrading
Upgrading an RF2K+ or RF2K-S to a Raspberry Pi 5 delivers a 2.5x to 3x increase in CPU throughput, instantaneous touchscreen response, and reduced latency across the SimpleRPC telemetry loop. When installing a Raspberry Pi 5:
1. **Active Cooler Thermal Clearance:** The Raspberry Pi 5 requires the official **Raspberry Pi Active Cooler** (an integrated extruded aluminum heatsink with a thermostatically controlled blower fan). Verify that the cooler fins do not contact the RF-KIT front panel ribbon harness or LCD housing.
2. **Power Delivery Considerations:** The Raspberry Pi 5 requires up to 5.0A at +5.1VDC during peak multi-core processing bursts. Ensure your amplifier's internal 5V auxiliary buck regulator is rated for **5A continuous output**. If an older 3A regulator is installed, replace it with a 5V/5A step-down switching converter to prevent low-voltage throttling.
3. **RP1 Southbridge & USB Serial Routing:** The Raspberry Pi 5 routes all external USB ports through the dedicated RP1 southbridge chip. While legacy 32-bit software failed to detect the controller on the Pi 5, the JRFK **Universal Udev Dual-Link Rule** automatically detects the RP1 USB bus topology and binds `/dev/rfk_controller` instantly.

---

### 2.4 First-Boot Autonomous Commissioning Sequence

When the newly provisioned 64-bit MicroSD card is powered on inside the amplifier for the first time, the system executes an autonomous 5-stage staging sequence without requiring any external monitor, keyboard, or mouse:

1. **Autonomous Filesystem Expansion (Stage 1):**
   * The Linux kernel boots and detects the secondary Linux partition (`/dev/mmcblk0p2`).
   * The automated `jrfk-init` service executes `resize2fs` to dynamically expand the ext4 root filesystem across the entire remaining storage boundary of your 16GB, 32GB, or 64GB card.
2. **KMS Display & Touchscreen Coordinate Alignment (Stage 2):**
   * The modern Linux Direct Rendering Manager (DRM) driver locks the HDMI output to pure **1024x600 resolution at 60 Hz**.
   * The injected 4-wire resistive touch matrix file (`/etc/pointercal` and `/home/pi/PA-Files/touch.cal`) is loaded into the evdev input subsystem, ensuring instant, pinpoint touch tracking without recalibration.
3. **Controller Communication Synchronization (Stage 3):**
   * The udev dual-link rule `/etc/udev/rules.d/99-rfk-controller.rules` fires immediately upon USB bus enumeration:
     ```bash
     KERNEL=="ttyACM*|ttyUSB*", ATTRS{idVendor}=="2341|1a86|0403", SYMLINK+="rfk_controller", MODE="0666"
     ```
   * The SimpleRPC daemon opens `/dev/rfk_controller` at 115,200 baud, executes the STK500v2 handshake, and interrogates the 20-element real-time telemetry stream.
4. **RFKGUI Touchscreen Interface Launch (Stage 4):**
   * The graphical display manager launches the RF-KIT GUI in full-screen mode on the 7-inch LCD.
   * All restored operator parameters—including station callsign, transceiver CAT baud rate, antenna switch matrix, and SWR power polynomials—are applied immediately.
5. **Integrated Diagnostic Suite & Disaster Recovery Server (Stage 5):**
   * The lightweight Python Bottle diagnostic server (`rfk_tools_suite`) initializes in the background on **Port 8088**.
   * Operators can navigate to `http://<amplifier-ip>:8088/` from any PC, tablet, or smartphone on the station Wi-Fi network to monitor real-time thermal curves, inspect forward/reflected power RF waveforms, and configure automated weekly SD card disaster recovery backups.

---

"""

# Combine front + Chapter 2 + body
full_content = front + chapter_2_text + body

with open(MD_PATH, "w", encoding="utf-8") as f:
    f.write(full_content)

print(f"Successfully updated {MD_PATH} with Chapter 2 and renumbered chapters!")
