# Technical Narration Script — System Architecture & 64-Bit Leap

### Slide 1: Modernizing the RF-KIT Linear Amplifier
**Visual:** `slide_1.png`

> **Technical Narration (Spoken Audio):**
> "Welcome to Part 1 of the JRFK technical overview. Today we look at modernizing the RF-KIT B26 and RF2K-plus linear amplifiers. Running 1500 watts PEP through dual LDMOS transistors requires an operating system that is fast, rock-solid, and completely dependable. Today we upgrade our amplifiers to pure 64-bit Debian Bookworm."

---

### Slide 2: Why Legacy 32-Bit OS Must Go
**Visual:** `slide_2.png`

> **Technical Narration (Spoken Audio):**
> "Legacy 32-bit Raspberry Pi OS installs have reached end of life. Deprecated Python 2 sockets, old video drivers, and unmaintained packages lead to display stutter and lockups during heavy RF keying. Debian Bookworm 64-bit provides modern memory management, Full KMS DRM display drivers, and a future-proof foundation."

---

### Slide 3: Dual-Port Architecture: 8089 vs 8088
**Visual:** `slide_3.png`

> **Technical Narration (Spoken Audio):**
> "A critical architectural improvement is port decoupling. The setup tool on your PC runs strictly on port 8089. The operational cockpit on the amplifier runs on port 8088. This clean separation guarantees that PC maintenance or network disconnects never interrupt live amplifier protection or RF transmission."

---

### Slide 4: 4-Volume Documentation & K7BIT Cookbook
**Visual:** `slide_4.png`

> **Technical Narration (Spoken Audio):**
> "For station documentation, we have published a complete 4-volume engineering library covering operations, remote telemetry, and disaster recovery. In addition, John K7BIT's legendary 193-page cookbook is fully preserved in our documentation portal, giving builders complete access to original schematics and wiring layouts."

---

### Slide 5: Master Resources & Downloads
**Visual:** `slide_outro.png`

> **Technical Narration (Spoken Audio):**
> "This concludes our presentation. All project resources—including the turnkey JRFK executable, documentation portal, source code, and community discussions—are available at the links shown on your screen. Thank you for watching, and 73 from the station."

---

