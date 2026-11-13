# Presentation 1: Master 13-Slide Narration Script

### Slide 1: Modernizing the RF-KIT Linear Amplifier
**Visual:** `slide_01.png` | **Audio:** `slide_01.mp3` | **Duration:** `28.10s`

> **Technical Narration:**
> "Welcome to Part 1 of our technical overview. When you are managing fifteen hundred watts PEP across 160 meters through 6 meters, the micro-controller supervising your RF deck, low-pass relays, and protection sequencing must be completely deterministic. In this briefing, we examine the technical requirement for migrating the RF-KIT platform from legacy 32-bit operating systems to pure 64-bit Debian Bookworm architecture."

---

### Slide 2: Why 32-Bit Must Go: Software End-of-Life
**Visual:** `slide_02.png` | **Audio:** `slide_02.mp3` | **Duration:** `27.26s`

> **Technical Narration:**
> "Let's look at why migration is necessary. The original 32-bit operating system has reached official end-of-life. Upstream package repositories are frozen, and deprecated Python socket implementations prevent the controller from running modern network protocols or security patches. Without upgrading, the amplifier controller becomes an isolated legacy device unable to communicate reliably with modern station automation."

---

### Slide 3: Why 32-Bit Must Go: Display Architecture & RF Locks
**Visual:** `slide_03.png` | **Audio:** `slide_03.mp3` | **Duration:** `33.48s`

> **Technical Narration:**
> "The second critical driver for migration is display architecture. Legacy 32-bit installations relied on user-space fake-KMS and older X11 graphics layers. In the presence of strong RF fields during legal-limit keying, memory fragmentation in these user-space drivers frequently caused touchscreen freezes and display blanking. Upgrading to 64-bit Full KMS DRM places the 1024 by 600 display modelines directly inside the Linux kernel, ensuring rock-solid display stability."

---

### Slide 4: 64-Bit Architecture Overview: The Technical Payoff
**Visual:** `slide_04.png` | **Audio:** `slide_04.mp3` | **Duration:** `24.79s`

> **Technical Narration:**
> "The 64-bit architecture delivers an immediate technical payoff. Debian Bookworm provides 64-bit memory protection, modern Linux kernel stability, and a fully non-blocking SimpleRPC telemetry loop. Fragile legacy startup scripts are replaced with native systemd service units, ensuring that all controller daemons automatically recover in the event of an unexpected fault."

---

### Slide 5: Tool 1: JRFK Standalone Migrator Architecture
**Visual:** `slide_05.png` | **Audio:** `slide_05.mp3` | **Duration:** `30.29s`

> **Technical Narration:**
> "Now let's examine the first major component of the JRFK suite: the Standalone Migrator. Distributed as a single 166-megabyte Windows executable, JRFK.exe requires zero developer tools or Python dependencies. It incorporates a dedicated C-sharp launcher that handles administrative elevation, suppresses disruptive Windows 11 format prompts on raw media, and enforces strict physical drive guard locks to prevent accidental drive overwrites."

---

### Slide 6: Tool 1 in Action: Discovery, Flashing & Calibration
**Visual:** `slide_06.png` | **Audio:** `slide_06.mp3` | **Duration:** `25.08s`

> **Technical Narration:**
> "In operation, the migrator automates the entire provisioning workflow. It scans your local network to discover the amplifier controller, flashes the verified 64-bit Bookworm base image, injects native 1024 by 600 display modelines, and extracts your amplifier's unique band tables and SWR calibration offsets from your old SD card so no factory calibration is lost."

---

### Slide 7: Tool 2: 7-Screen Web Suite — RF Telemetry & Bands
**Visual:** `slide_07.png` | **Audio:** `slide_07.mp3` | **Duration:** `27.12s`

> **Technical Narration:**
> "The second major tool in the suite is the 7-screen operational web cockpit running permanently on port 8088. This tool decouples live operation from PC maintenance. Screen 1 gives you real-time forward PEP, reflected power, and SWR metering from any browser in your shack, while Screen 2 provides automatic low-pass filter band switching synchronized to your transceiver via CAT control with active hot-switch prevention."

---

### Slide 8: Tool 2: PA Monitoring & 4-Way Antenna Matrix
**Visual:** `slide_08.png` | **Audio:** `slide_08.mp3` | **Duration:** `32.35s`

> **Technical Narration:**
> "Screens 3 and 4 handle RF deck health and antenna routing. Screen 3 monitors the 53.5-volt DC rail, drain current, and heatsink thermals across the dual Ampleon BLF189 LDMOS transistors. Note that the RF-KIT uses discrete analog shunts rather than CAN bus power supplies, ensuring noise-free DC telemetry. Screen 4 manages a 4-way antenna matrix that automatically recalls your selected antenna port for each band."

---

### Slide 9: Tool 2: Protection Systems, Logs & Touch Calibration
**Visual:** `slide_09.png` | **Audio:** `slide_09.mp3` | **Duration:** `26.38s`

> **Technical Narration:**
> "Screens 5, 6, and 7 deliver comprehensive protection and maintenance. Screen 5 enforces hardware protection limits, clamping drive and dropping into standby within microseconds if SWR exceeds 2.5 to 1 or heatsink temperature reaches 60 degrees. Screens 6 and 7 provide real-time controller event logs and a built-in 5-point touchscreen calibration utility."

---

### Slide 10: Tool 3: The 3-Minute Disaster Recovery Standby Card
**Visual:** `slide_10.png` | **Audio:** `slide_10.mp3` | **Duration:** `26.40s`

> **Technical Narration:**
> "Tool 3 is the Disaster Recovery Engine. During the migration workflow, JRFK provisions an identical secondary SD card containing the complete 64-bit operating system and all current calibration offsets. If an SD card ever suffers hardware failure during contest operations, the operator simply inserts the standby card and powers up, returning the station to full operation in under three minutes."

---

### Slide 11: Tool 3: First-Boot Automation & Self-Healing Services
**Visual:** `slide_11.png` | **Audio:** `slide_11.mp3` | **Duration:** `24.77s`

> **Technical Narration:**
> "Supporting disaster recovery is our first-boot automation framework. Upon initial startup, the setup script expands the Linux root partition to fill the SD card, applies network configurations, and enables systemd service watchdogs. These watchdogs actively supervise all background daemons, automatically restarting them without operator intervention if an abnormal state occurs."

---

### Slide 12: Tool 4: Master Engineering Library & Cookbook Reader
**Visual:** `slide_12.png` | **Audio:** `slide_12.mp3` | **Duration:** `27.14s`

> **Technical Narration:**
> "Tool 4 is the Master Documentation Portal. The portal hosts our complete 4-volume engineering library covering station operation, remote telemetry, and architecture. Furthermore, John K7BIT's authentic 193-page B26 cookbook is integrated directly into the portal, providing operators and builders with instant, searchable access to original schematics and wiring diagrams from any browser."

---

### Slide 13: Summary & Master Resource Directory
**Visual:** `slide_13.png` | **Audio:** `slide_13.mp3` | **Duration:** `25.18s`

> **Technical Narration:**
> "In summary, the JRFK modernization suite delivers a complete 64-bit transformation: automated migration, a 7-screen operational web cockpit, instant disaster recovery, and comprehensive technical documentation. All downloads, source code, and community discussions are accessible at the links displayed on your screen. Thank you for watching, and 73 from the station."

---

