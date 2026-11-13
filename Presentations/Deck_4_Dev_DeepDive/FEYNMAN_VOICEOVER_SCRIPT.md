# Richard Feynman Voiceover Script — Development Deep Dive & Build Automation

### Slide 1: JRFK Engineering Deep Dive
**Visual:** `slide_1.png`

> **Feynman Avatar (Spoken Audio):**
> "Welcome to Part 4, our technical deep dive! As I always used to say, what I cannot create, I do not understand! Today we look at every engineering layer: video modelines, Python deprecation patches, electrical characteristics, and Gemini Pro automation."

---

### Slide 2: Full KMS DRM Video & SimpleRPC Patches
**Visual:** `slide_2.png`

> **Feynman Avatar (Spoken Audio):**
> "In the old days, video was handled by clunky user-space drivers that would choke under RF interference. We moved to Linux Full KMS DRM with custom 1024 by 600 kernel modelines. And we eliminated deprecated Python sockets, giving us a non-blocking SimpleRPC pipeline."

---

### Slide 3: RF Deck & Standard DC Architecture
**Visual:** `slide_3.png`

> **Feynman Avatar (Spoken Audio):**
> "Let's be crystal clear on hardware: the amplifier runs dual Ampleon BLF189 LDMOS devices. And the RF-KIT does NOT use CAN bus power supplies! Voltage and current are read directly through clean, discrete analog shunts. No CAN bus crashes, no firmware handshakes—just pure, reliable DC physics."

---

### Slide 4: Gemini Pro Automation & 18/18 Testing
**Visual:** `slide_4.png`

> **Feynman Avatar (Spoken Audio):**
> "How was this built? Through modern AI automation! Using Google Gemini Pro and Antigravity, we automated the entire build and verification pipeline. Every release passes all 18 automated unit tests before a single byte touches production."

---

### Slide 5: Local Git & Complete Session Logging
**Visual:** `slide_5.png`

> **Feynman Avatar (Spoken Audio):**
> "In real science, you keep a laboratory notebook! Every step, command, and test result in this project is recorded in structured JSONL session logs and committed directly to Git. It's completely transparent, fully auditable, and reproducible."

---

### Slide 6: Master Resources & Downloads
**Visual:** `slide_outro.png`

> **Feynman Avatar (Spoken Audio):**
> "And that wraps up this briefing! Every link you need—the turnkey JRFK.exe download, the live web documentation portal on GitHub Pages, the full source repository, and the community forum—is right on your screen. Go ahead and grab the files, have fun experimenting, and 73 from the shack!"

---

