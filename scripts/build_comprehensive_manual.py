import os

MANUAL_PATH = "/mnt/d/JRFK/docs/JRFK_EM.md"
DIAGRAM_DIR = "/mnt/d/JRFK/docs/images/diagrams"

content = """# JRFK_EM — Master RFK 64-Bit Architecture, Controller Interface & Diagnostics Manual

> **Document Class:** Master System Engineering Architecture, Controller Protocol Reference & Diagnostics Manual  
> **Target Equipment:** RF-KIT Linear Power Amplifier (RF2K-S / RF2K+ Series)  
> **Embedded SBC Host:** Raspberry Pi 4 Model B (4 GB / 8 GB) & Raspberry Pi 5 (8 GB) Universal Parity  
> **Controller Architecture:** Arduino Mega 2560 R3 / Arduino Due (SAM3X8E ARM Cortex-M3) PA Backplane  
> **Source Platform:** Legacy 32-bit Raspbian 11 Bullseye (`armhf`, Python 3.7)  
> **Target Platform:** 64-bit Raspberry Pi OS Debian Bookworm / Trixie (`aarch64`, Python 3.11 / 3.13)  
> **Network Services:** RF-KIT Core REST API (`:8080`), RFK Tools Diagnostic Suite (`:8088`), TCI (`:50002`), UDP (`:50001`)  
> **Primary References:** B26 RF01 PA Controller V4, K7BIT B26 Cookbook Vol 1 R1.5 (John Birdlebough K7BIT/AE & John Stafford)  
> **Version Control Policy:** Strictly Local Git (`D:\\JRFK` on branch `JCF`) — Zero Remote Push  

---

## 1. Executive Summary & Migration Objective

The RF-KIT RF2K-S and RF2K+ amateur radio linear amplifiers represent premier solid-state RF power amplification technology, combining an advanced LDMOS RF power block (capable of 1500W+ PEP output across 160m through 6m) with a dedicated dual-tier control architecture:
1. **Tier 1 (Real-Time Hardware Controller):** An embedded microcontroller (Arduino Mega 2560 R3 or Arduino Due SAM3X8E backplane) managing sub-millisecond PTT interlocks, high-speed peak/reflected power detection, Low Pass Filter (LPF) relay switching, bias gating, and stepper-switched Automatic Antenna Tuner (ATU) relay matrices.
2. **Tier 2 (Supervisory SBC & Human-Machine Interface):** A Raspberry Pi running Linux, providing the 7-inch 1024x600 capacitive touchscreen display, transceiver CAT/TCI integration, network control, SocketCAN power supply telemetry, and high-level system supervision.

```mermaid
flowchart TD
    subgraph Legacy ["Legacy 32-bit Architecture"]
        A1["Debian 11 Bullseye (armhf)"]
        A2["Python 3.7 (Deprecated)"]
        A3["Bundled 32-bit ARM ELF Shared Objects"]
        A4["Hardcoded Pi 4 VL805 PCIe USB Path"]
    end
    subgraph Target ["Universal 64-bit Appliance Platform"]
        B1["Debian Bookworm/Trixie (aarch64)"]
        B2["Python 3.11/3.13 Runtime Optimized"]
        B3["Native 64-bit Hamlib Bridge"]
        B4["Universal Udev Dual-Link (/dev/rfk_controller)"]
        B5["Full KMS 1024x600 60Hz DRM Modeline"]
        B6["RFK Tools Suite Server (:8088)"]
    end
    Legacy ==>|"JRFK Automated Migration"| Target
```

---

## 2. Deep Architectural Analysis: 32-Bit (`armhf`) vs. 64-Bit (`aarch64`)

The transition from 32-bit to 64-bit Linux on ARM represents a complete architectural overhaul of CPU register usage, dynamic memory addressing, system calls, and Python C-extensions:

| Subsystem Component | Legacy 32-bit Architecture (`armhf`) | Universal 64-bit Platform (`aarch64`) | Architectural Impact |
|---|---|---|---|
| **CPU Architecture** | ARMv7-A / ARMv8 32-bit execution mode | ARMv8.2-A / ARMv8.5-A 64-bit native | Native 64-bit wide math registers |
| **CPU Registers** | 16 Core Registers (`r0`–`r15`) | 31 Core Registers (`x0`–`x30`) | Eliminates CPU register spilling to RAM |
| **Virtual Address Space** | 4 GB limit per process (32-bit pointers) | 256 TB virtual space (64-bit pointers) | Eliminates shared library address fragmentation |
| **System Time (`time_t`)**| Signed 32-bit (overflows Jan 19, 2038) | Signed 64-bit (`t64` Debian transition) | Complete temporal stability beyond 2038 |
| **Kernel Page Size** | 4 KB Hardcoded | 4 KB (RPi 4) and 16 KB (RPi 5) | Dynamic memory alignment across SBCs |
| **Dynamic Libraries** | `/lib/arm-linux-gnueabihf` | `/lib/aarch64-linux-gnu` | 64-bit clean shared object resolution |
| **Hamlib C-Bindings** | 32-bit ARM ELF (`ELFCLASS32`) | Native 64-bit `aarch64` (`ELFCLASS64`) | Zero dynamic linker collision |
| **Python Runtime** | Python 3.7 (Deprecated upstream) | Python 3.11 / Python 3.13 (Active LTS) | 20%–30% faster AST execution loop |

### 2.1 Register Pressure and Telemetry Throughput
In 32-bit mode, the ARM core is limited to 16 registers. Several registers are reserved for the Program Counter (`r15`), Link Register (`r14`), Stack Pointer (`r13`), and Platform pointer (`r9`), leaving fewer than 12 usable registers. During fast SWR calculations, floating-point peak power envelope decays, and SimpleRPC packet serialization, the processor is forced to spill intermediate calculations to stack RAM. In 64-bit `aarch64` mode, 31 general-purpose registers (`x0`–`x30`) allow complex math, CAN-bus polling, and GUI event handling to remain entirely within CPU registers.

### 2.2 Shared Object Architecture & The ELF Header Collision
The stock RF-KIT release packages (`gui200.zip`) bundle pre-compiled shared libraries (`_Hamlib.so`) compiled for 32-bit ARM:
```bash
$ file hamlib/v4_6_5_bindings_backport/lib/python3_7/site_packages/_Hamlib.so
ELF 32-bit LSB shared object, ARM, EABI5 version 1 (SYSV), dynamically linked
```
Attempting to load this under a 64-bit Python interpreter results in an immediate failure:
```text
ImportError: .../_Hamlib.so: wrong ELF class: ELFCLASS32
```
The JRFK platform shims native Debian 64-bit libraries (`_Hamlib.cpython-313-aarch64-linux-gnu.so`), resolving transceiver CAT control transparently.

---

## 3. Universal Single-SD Hardware Parity: RPi 4 vs. RPi 5

```mermaid
sequenceDiagram
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
    Kernel-->>App: Direct Bidirectional Serial Pipe (115200 8-N-1)
```

1. **Microcontroller USB Topology:**
   * *Raspberry Pi 4:* The USB controller is a VIA Labs VL805 PCIe host chip (`/dev/serial/by-path/platform-fd500000.pcie-pci-0000:01:00.0-usb-0:1.3:1.0-port0`).
   * *Raspberry Pi 5:* USB routing is handled by the Raspberry Pi RP1 Southbridge ASIC (`platform-1f00000000.pcie...`).
   * *Universal Solution:* `/etc/udev/rules.d/99-rfk-controller.rules` maps any connected controller MCU to `/dev/rfk_controller` and aliases the legacy Pi 4 path.
2. **Display Modeline:** The Pi 5 eliminated firmware `hdmi_cvt` parameters. DRM parameter `video=HDMI-A-1:1024x600M@60D` in `cmdline.txt` enforces 1024x600 60Hz Full KMS operation across both boards.
3. **Kernel Memory Pages:** Pi 5 uses 16 KB memory pages (`PAGE_SIZE=16384`). Native 64-bit binaries dynamically align to 4 KB (Pi 4) and 16 KB (Pi 5).

---

## 4. Execution Flow: RF-KIT App <──> Controller Deep Dive

The core operational stability of the RF-KIT amplifier relies on constant, tightly synchronized communication between the Raspberry Pi Python supervisory layer (`interface.py`, `data.py`) and the Controller Microcontroller (Arduino Mega 2560 R3 / Arduino Due SAM3X8E backplane).

```
┌────────────────────────────────────────────────────────────────────────┐
│                   RF-KIT BI-DIRECTIONAL CONTROL BUS                    │
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│   [Raspberry Pi 4/5 (Tier 2: Linux HMI)]                               │
│      ├── interface.py (InterfaceWrapper / InterfaceProcess)            │
│      ├── simple_rpc Protocol Encoder / Decoder                         │
│      └── Baud Rate: 115200 bps | 8 Data Bits | No Parity | 1 Stop Bit  │
│                                │                                       │
│                                ▼ Bidirectional USB-Serial CDC-ACM      │
│   [B26 RF01 PA Controller Backplane (Tier 1: MCU Engine)]              │
│      ├── Arduino Due / SAM3X8E 84MHz ARM Cortex-M3 (or Mega 2560 R3)   │
│      ├── Direct RF Peak/Reflected Detector ADC Interface               │
│      ├── 8:1 Frequency Prescaler Counter Input                         │
│      ├── LPF Relays & Antenna Matrix Control Latches                   │
│      ├── Stepper-Driven ATU L/C/K Relay Drivers                        │
│      └── Non-Volatile EEPROM / Flash Calibration Tables                │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
```

### 4.1 Interface Process Decoupling Architecture
In `interface.py`, RF-KIT isolates the serial communication into a dedicated background worker process (`InterfaceProcess` extending `multiprocessing.Process`):
* **Why Multi-Process?** Python's Global Interpreter Lock (GIL) and Tkinter GUI drawing operations would introduce jitter into serial communication. By executing the SimpleRPC loop inside an isolated process communicating via `multiprocessing.Queue`, communication timing is preserved.
* **Handshake Watchdog:** On startup, the GUI initializes `InterfaceWrapper` with a 5-second `start_timeout_seconds` and a 30-second `timeout_seconds`. If the microcontroller fails to respond within the timeout window, the supervisory thread calls `_replace_process()`, terminates the unresponsive worker, and restarts the serial pipe.

### 4.2 Comprehensive 71-Method RPC Register Catalog

The table below documents all 71 remote procedure calls implemented between the Raspberry Pi and the controller microcontroller:

| # | RPC Method Name | Parameters | Return Type | Subsystem / Functional Role |
|---|---|---|---|---|
| 1 | `get_generation` | *None* | `int` (1 or 2) | Identifies hardware tier (1 = Legacy RF2K, 2 = Modern RF2K-S) |
| 2 | `get_company` | *None* | `str` | Identifies manufacturer branding string ("RF-KIT") |
| 3 | `get_all_values` | *None* | `tuple[15+]` | Master telemetry acquisition (Firmware Rev, Volt, Current, P_F, P_R, etc.) |
| 4 | `get_frequency` | *None* | `int` (Hz) | Current frequency measured by the hardware 8:1 prescaler counter |
| 5 | `get_frq_count` | *None* | `int` | Raw frequency prescaler register accumulator |
| 6 | `incr_frq_count` | `int` (delta) | `bool` | Incremental fine-tuning calibration of prescaler counter |
| 7 | `decr_frq_count` | `int` (delta) | `bool` | Decremental fine-tuning calibration of prescaler counter |
| 8 | `set_cat_frq` | `int` (Hz) | `bool` | Injects transceiver frequency obtained via CAT/TCI into controller |
| 9 | `set_operate` | *None* | `bool` | Engages amplifier Operate mode (enables bias & RF switching) |
| 10 | `set_standby` | *None* | `bool` | Forces amplifier Standby mode (RF bypass, bias grounded) |
| 11 | `setHighLowPower` | `int` (0=High, 1=Low) | `bool` | Toggles amplifier output attenuation / drive level limit |
| 12 | `getHighLowPower` | *None* | `int` | Queries active output power limit profile |
| 13 | `set_antenna` | `int` (0–3) | `bool` | Switches the physical RF antenna relay matrix (ANT 1 through ANT 4) |
| 14 | `get_default_antennas`| *None* | `list[int]` | Reads 11-band default antenna assignments from MCU EEPROM |
| 15 | `set_default_antenna`| `int` (band), `int` (ant)| `bool` | Commits default band antenna selection into MCU non-volatile memory |
| 16 | `set_use_ext_antenna` | `bool` | `bool` | Engages external relay controller bus (X22 interface) |
| 17 | `get_ext_antenna_high_low_active` | *None* | `int` | Reads external antenna active logic level (active-high vs low) |
| 18 | `set_ext_antenna_high_low_active` | `int` (logic) | `bool` | Configures external antenna relay polarity |
| 19 | `delete_tuner_antenna` | `int` (ant_idx) | `bool` | Purges tuner calibration table for specified local antenna |
| 20 | `delete_tuner_ext_antenna` | `int` (ext_idx) | `bool` | Purges tuner calibration table for specified external antenna |
| 21 | `autotune` | *None* | `bool` | Triggers hardware ATU automatic impedance search routine |
| 22 | `store_tuner` | `int` (sub_band), `int` (L), `int` (C), `int` (K) | `bool` | Stores tuner calibration solution in controller EEPROM |
| 23 | `reset_tuner` | *None* | `bool` | Resets ATU inductors and capacitors to zero baseline |
| 24 | `set_tuner_auto` | *None* | `bool` | Places ATU in Automatic Tracking mode based on frequency |
| 25 | `set_tuner_bypass`| *None* | `bool` | Bypasses all ATU L/C matching elements (straight-through 50 ohm) |
| 26 | `increment_L` | *None* | `int` (new L) | Steps ATU series inductance upward (+1 step) |
| 27 | `decrement_L` | *None* | `int` (new L) | Steps ATU series inductance downward (-1 step) |
| 28 | `increment_C` | *None* | `int` (new C) | Steps ATU shunt capacitance upward (+1 step) |
| 29 | `decrement_C` | *None* | `int` (new C) | Steps ATU shunt capacitance downward (-1 step) |
| 30 | `set_K` | `int` (relay_state) | `bool` | Switches ATU configuration relay (C-input vs C-output side) |
| 31 | `set_tunermode` | `bool` | `bool` | Enters interactive manual tuning calibration mode |
| 32 | `get_tuner_on_off_per_band` | *None* | `list[bool]` | Returns 11-element array of ATU bypass/active state per band |
| 33 | `set_tuner_on_off_for_band` | `int` (band), `bool` | `bool` | Toggles ATU active engagement for a specific amateur band |
| 34 | `isTunerAtSixMeterEnabled` | *None* | `bool` | Queries whether 50 MHz (6m) ATU matching is permitted |
| 35 | `setTunerAtSixMeterEnabled` | `bool` | `bool` | Sets 50 MHz (6m) ATU matching permission |
| 36 | `get_autotune_return_loss_threshold` | *None* | `float` (dB) | Reads target return loss threshold for autotune completion |
| 37 | `set_autotune_return_loss_threshold` | `float` (dB) | `bool` | Sets target return loss threshold (typically 14dB = ~1.5:1 SWR) |
| 38 | `set_fan_threshold_temperatures` | `int` (on), `int` (off) | `bool` | Sets PA cooling fan trip points (Standard: 42°C on, 38°C off) |
| 39 | `reset_error_state` | *None* | `bool` | Clears latched hardware protection faults (High SWR, Over-current) |
| 40 | `get_high_current_threshold` | *None* | `int` (ADC raw) | Reads PA DC drain over-current trip point from MCU |
| 41 | `set_power_supply_voltage` | `float` (volts) | `bool` | Sets target nominal DC power supply rail voltage (53.5V) |
| 42 | `set_power_supply_current` | `float` (amps) | `bool` | Sets maximum DC power supply current limit (e.g. 35.0A) |
| 43 | `set_nominal_power_supply_voltage` | `float` (volts) | `bool` | Calibrates baseline DC rail sensing voltage factor |
| 44 | `get_power_supply_data_source` | *None* | `int` | Queries telemetry bus source (0 = Internal ADC, 1 = SocketCAN) |
| 45 | `initialize_power_supply_current_limits`| *None* | `bool` | Programs initial safe current ramp into CAN-bus supply |
| 46 | `get_dac_alc_output` | *None* | `int` (0–4095) | Reads current hardware Automatic Level Control (ALC) DAC voltage |
| 47 | `set_dac_alc_output` | `int` (dac_val) | `bool` | Programs ALC output voltage to reduce exciter drive |
| 48 | `get_dac_offset` | *None* | `int` | Reads ALC DAC zero-calibration offset |
| 49 | `increment_dac_offset` | *None* | `int` | Calibrates ALC DAC output upward |
| 50 | `decrement_dac_offset` | *None* | `int` | Calibrates ALC DAC output downward |
| 51 | `save_dac_value_input_offsets` | *None* | `bool` | Commits ALC offset adjustments into EEPROM |
| 52 | `increment_offset_F` | *None* | `int` | Calibrates Forward Power directional coupler ADC scaling upward |
| 53 | `decrement_offset_F` | *None* | `int` | Calibrates Forward Power directional coupler ADC scaling downward |
| 54 | `increment_offset_R` | *None* | `int` | Calibrates Reflected Power directional coupler ADC scaling upward |
| 55 | `decrement_offset_R` | *None* | `int` | Calibrates Reflected Power directional coupler ADC scaling downward |
| 56 | `increment_offset_BIAS` | *None* | `int` | Fine-adjusts LDMOS gate quiescent bias voltage upward |
| 57 | `decrement_offset_BIAS` | *None* | `int` | Fine-adjusts LDMOS gate quiescent bias voltage downward |
| 58 | `get_offset_BIAS` | *None* | `int` | Queries active LDMOS gate quiescent bias DAC offset |
| 59 | `save_offset_values` | *None* | `bool` | Flushes coupler calibration factors (F, R, BIAS) to EEPROM |
| 60 | `set_10_12_15_m_gap_power_allowed` | `int` (0/1) | `bool` | Configures power limits on cross-band frequency gaps (WARC) |
| 61 | `get_storage_bank` | *None* | `int` | Reads active non-volatile configuration memory bank index |
| 62 | `set_storage_bank` | `int` (bank_id) | `bool` | Switches non-volatile memory profile bank |
| 63 | `delete_storage` | `int` (bank_id) | `bool` | Purges stored settings in selected memory bank |
| 64 | `zeroFRAM` | *None* | `bool` | Completely clears non-volatile Ferroelectric RAM (FRAM/EEPROM) |
| 65 | `set_operational_interface` | `int` (mode) | `bool` | Configures CAT link mode (Universal, CI-V, Kenwood, Yaesu) |
| 66 | `display_on` | *None* | `bool` | Enables touchscreen display backlight control pin |
| 67 | `display_off` | *None* | `bool` | Shuts down touchscreen display backlight (Sleep Timer) |
| 68 | `go_sleep` | *None* | `bool` | Places controller MCU into low-power quiescent sleep mode |
| 69 | `wake_up` | *None* | `bool` | Wakes controller MCU from low-power sleep mode |
| 70 | `update` | `str` (firmware_bin_path) | `bool` | Initiates SimpleRPC microcontroller firmware flash sequence |
| 71 | `close` | *None* | `bool` | Cleanly shuts down serial thread and releases hardware descriptors |

---

## 5. Hardware Interfacing & K7BIT B26 Cookbook Integration

The **K7BIT B26 Cookbook Vol 1 R1.5** (by John Birdlebough K7BIT/AE & John Stafford) provides foundational technical details on the physical construction and calibration of the amplifier backplane:

```
┌────────────────────────────────────────────────────────────────────────┐
│                   B26 RF01 CONTROLLER & RF HARDWARE                     │
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│   [RF Input] ──> [Relay Board] ──> [Teflon Coax] ──> [LPF Board]       │
│                        │                                   │           │
│                        ├── Prescaler Tap (SMA)             ├── Relays  │
│                        ▼                                   ▼           │
│   [B26 Controller Backplane (Arduino Mega 2560 R3 / Due)]              │
│      ├── Connector X1: RF Prescaler Input (8:1 divider)                │
│      ├── Connector X9/X99: Directional Coupler FWD/REF DC Voltages     │
│      ├── Connector X22: External Antenna Control Bus                   │
│      └── Driver ICs: ULN2803 Relay Drivers for LPF & ATU Matrix        │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
```

### 5.1 Step 7 Frequency Prescaler Counter Calibration
* **Theory of Operation:** The amplifier controller features an onboard hardware frequency detector circuit. RF energy sampled at the input relay board is routed via miniature Teflon coax to connector **`X1`** on the B26 Controller Board. An onboard high-speed divider divides the frequency by 8:1 before feeding it to the microcontroller timer/counter pin.
* **Calibration Protocol:** As documented in the Cookbook, if the frequency calibration register is offset, the controller misidentifies amateur bands (e.g., misclassifying 1.983 MHz as 80m instead of 160m). The SimpleRPC methods `incr_frq_count()` and `decr_frq_count()` adjust this multiplier until the hardware frequency detector matches the transceiver CAT frequency within 1 kHz.

### 5.2 Directional Coupler & Peak RF Detection
* The directional coupler samples forward and reflected RF voltages, rectifies them via zero-bias Schottky diodes, and applies temperature-compensated scaling before routing DC voltages to analog ADC inputs on the controller.
* Software calibration offsets are managed via `increment_offset_F()` / `decrement_offset_F()` for forward power and `increment_offset_R()` / `decrement_offset_R()` for reflected power, and committed to controller EEPROM via `save_offset_values()`.

### 5.3 LPF and Tuner Relay Driver Architecture
* Relay switching across the Low Pass Filter (160m to 6m banks) and the Automatic Antenna Tuner matrix is buffered using **ULN2803 Darlington transistor arrays**.
* Safety Interlock: The controller enforces a **PTT Break-Before-Make delay**. When a frequency change is detected via CAT, the controller de-asserts the PTT bias interlock, switches the LPF and ATU relays, waits 15 milliseconds for relay contact settling, and re-enables PTT gating.

---

## 6. Deep Dive: The RF-KIT Online Update Engine

```mermaid
flowchart TD
    Start["Operator Initiates Update in GUI"] --> Connect["Connect to SFTP (access816807157.webspace-data.io)"]
    Connect --> FetchManifest["Download & Parse version.json"]
    FetchManifest --> Compare["Compare controller and GUI version numbers"]
    Compare --> Download["Download gui{ver}.zip & firmware{ver}.bin"]
    Download --> Verify["Verify SHA256 Integrity Checksums"]
    Verify --> FlashMCU["Flash Controller MCU via SimpleRPC"]
    FlashMCU --> Unpack["Unpack zip into /home/pi/rf-kit-gui_v{new}"]
    Unpack --> PatchHook["64-Bit Self-Healing Hook (Injects aarch64 Hamlib & shims)"]
    PatchHook --> UpdatePtr["Update gui_path.json (start: v{new}, fallback: v{old})"]
    UpdatePtr --> Restart["Execute gui_starter.py"]
    Restart --> ExecTest{"main.py runtime > 3 seconds?"}
    ExecTest -- Yes --> Success["Update Successful! Running New Version"]
    ExecTest -- No --> Fallback["Automatic Rollback to fallback folder"]
```

1. **Remote SFTP Authentication:** The amplifier authenticates via SSH/SFTP to `access816807157.webspace-data.io` using credentials stored in `config.json` (`u100014070-F-rf2ksf` / `flash-RF2Ks`).
2. **Manifest Verification:** Evaluates `version.json` against current active versions (`gui200.zip` / `firmware267.bin`).
3. **Flashing Firmware:** The new firmware binary is pushed across the SimpleRPC link via `InterfaceWrapper.getInstance().update(filepath)`. The controller enters its bootloader, writes flash memory, and restarts.
4. **Crash Supervisor (`gui_starter.py`):** Monitors GUI execution duration. If `main.py` crashes in under 3 seconds, the supervisor rolls back execution to the previous release in `gui_path.json`.
5. **64-Bit Self-Healing Hook:** Automatically re-links native 64-bit `Hamlib.py` and `_Hamlib*.so` bindings into newly unzipped release directories.

---

## 7. Storage Media Engineering & Sizing Standards

```mermaid
flowchart LR
    Active["Active Internal Boot SD<br/>(/dev/mmcblk0)"] -->|"Live Block Stream & UUID Regen"| Target["USB SD Reader<br/>(/dev/sda)"]
    Target --> Emergency["100% Plug-and-Play Spare SD Card"]
```

### 7.1 Card Sizing Specifications
* **Minimum Required Size: 16 GB:** The 64-bit OS, desktop, RF-KIT suite, dependencies, Cookbook, and diagnostic suite consume ~7.2 GB to 8.5 GB.
* **Recommended Production Standard: 32 GB (A2 / V30):** Provides critical unallocated flash space (over-provisioning) allowing flash memory controllers to rotate write cycles, significantly extending lifespan under continuous telemetry logging.

### 7.2 Application & Video Speed Classes
* **Class A2:** Requires minimum **4,000 Read IOPS** and **2,000 Write IOPS** with Command Queuing (CQ).
* **Class V30:** Guarantees minimum sustained sequential write speed of **30 MB/s**.
* **Recommended Models:**
  1. *SanDisk High Endurance / MAX Endurance*
  2. *SanDisk Extreme / Extreme PRO (A2, V30, U3)*
  3. *Kingston Canvas Go! Plus (A2, V30)*
  4. *Samsung PRO Endurance*

---

## 8. Integrated Diagnostic Suite: Architecture & Implementation

```mermaid
flowchart TD
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
    Health --> Print
```

### 8.1 Port Allocation Matrix
* **UDP 50001:** Active Radio Broadcast
* **UDP 50002:** TCI Transceiver Interface
* **TCP 8080:** RF-KIT Internal REST API
* **TCP 8088:** **RFK Tools Suite Diagnostic Server** *(Conflict-Free)*
* **TCP 22:** SSH / SFTP Upstream Repository Link

### 8.2 Antenna Mapper Interface (`/antenna`)
* **Band Spinner:** Rapid cycling across 160m through 6m amateur bands.
* **Interactive Frequency Slider:** Smooth horizontal pan and zoom across wide bands.
* **Segment Inspector:** Clicking any segment displays the exact hardware tuning solution: **Inductance (L steps), Capacitance (C steps), Transformer Relay (K status), and calibrated SWR**.
* **IP Network Printing:** Formats an engineering report with vector curves and prints to any CUPS/AirPrint IP printer on the shack network.

### 8.3 Amplifier Health & Thermal Monitor (`/health`)
* **Dual Time Windows:** High-resolution 1-Hour Zoom (5s intervals) vs. 24-Hour Session Accumulation.
* **Pane 1 (RF Envelope):** Forward Power (0–2000 W) and Reflected Power (W).
* **Pane 2 (DC Power Supply Health):** 53.5 V rail regulation and drain current (0–40 A) tracking voltage sag under heavy key-down.
* **Pane 3 (Thermal Profiling):** PA Heatsink temperature curves overlaid with the 42°C fan-activation and 38°C fan-deactivation thresholds.

---

## 9. Complete Step-by-Step Staging & Dual-Boot Walkthrough

```mermaid
sequenceDiagram
    autonumber
    actor User as Operator / Admin
    participant PC as Windows 11 PC (Host)
    participant SD as Target SD Card
    participant Pi as RF-KIT Amplifier (RPi)
    User->>PC: Launch Raspberry Pi Imager v2
    PC->>SD: Flash Official RPi OS 64-bit (User: pi, Hostname: K7BIT)
    User->>PC: Attach SD via usbipd to WSL2
    PC->>SD: Execute finalize_sd.sh (Offline chroot)
    Note over PC,SD: Pre-installs all packages, bridges Hamlib,<br/>patches Pillow/Bottle, installs RFK Tools
    User->>Pi: Insert SD into Amplifier & Power On (BOOT 1)
    Pi->>Pi: Auto-expands rootfs, autologins to pure X11 (rpd-x)
    Pi->>Pi: Launches RF-KIT GUI fullscreen at 1024x600 Full KMS
    Note over Pi: Amplifier fully operational with Callsign K7BIT
    User->>Pi: Power Cycle Amplifier (BOOT 2)
    Pi->>Pi: Cold boots directly into fullscreen GUI in < 12 seconds
```

---

## 10. User Configuration & Database Engine Reference

The software settings plane is governed by `JsonFileStorageABC` storing atomically synced JSON records:
* **Station Configuration (`config.json`):** Preserves station callsign `K7BIT`, ICOM IC-7610 transceiver link (9600 baud), 53.5 V rail limit, and the full 11-band $\times$ 4-antenna routing matrix.
* **Tuner EEPROM Independence:** Antenna tuner calibration solutions (L, C, K steps per segment) reside inside the **non-volatile memory of the amplifier microcontroller**, guaranteeing 100% zero data loss of tuner calibration during OS upgrades.
"""

with open(MANUAL_PATH, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"JRFK_EM.md updated cleanly: {len(content)} characters.")
