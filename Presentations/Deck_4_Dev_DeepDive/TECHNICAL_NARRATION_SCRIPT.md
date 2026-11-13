# Technical Narration Script — Development Deep Dive & Build Automation

### Slide 1: JRFK Engineering Deep Dive
**Visual:** `slide_1.png`

> **Technical Narration (Spoken Audio):**
> "Welcome to Part 4, our technical engineering briefing. In this session, we examine the underlying software architecture: Linux Full KMS display drivers, Python SimpleRPC deprecation patches, discrete DC sensing, and automated build verification."

---

### Slide 2: Full KMS DRM Video & SimpleRPC Patches
**Visual:** `slide_2.png`

> **Technical Narration (Spoken Audio):**
> "On the driver layer, we resolved legacy display blanking by injecting custom 1024 by 600 kernel modelines into Full KMS DRM. We also modernized SimpleRPC socket communications and replaced fragile background scripts with systemd service units."

---

### Slide 3: Hardware Truth: Dual BLF189 & Discrete DC
**Visual:** `slide_3.png`

> **Technical Narration (Spoken Audio):**
> "For clarity on hardware architecture: the RF-KIT amplifier utilizes dual Ampleon BLF189 LDMOS devices and does NOT use CAN bus power supplies. Voltage and current telemetry are read via discrete analog shunts directly into the controller ADC, delivering rugged and crash-free DC monitoring."

---

### Slide 4: Automated Build & Test Pipeline
**Visual:** `slide_4.png`

> **Technical Narration (Spoken Audio):**
> "To guarantee reliable operation, every build passes an 18-point automated test suite covering network discovery, physical disk guard safety locks, video modeline syntax, and SimpleRPC protocol handlers before release."

---

### Slide 5: Local Version Control & Session Logging
**Visual:** `slide_5.png`

> **Technical Narration (Spoken Audio):**
> "All changes and development sessions are tracked in local Git repositories and structured session logs. The entire build, testing, and migration suite is 100% local with zero cloud dependencies."

---

### Slide 6: Master Resources & Downloads
**Visual:** `slide_outro.png`

> **Technical Narration (Spoken Audio):**
> "This concludes our presentation. All project resources—including the turnkey JRFK executable, documentation portal, source code, and community discussions—are available at the links shown on your screen. Thank you for watching, and 73 from the station."

---

