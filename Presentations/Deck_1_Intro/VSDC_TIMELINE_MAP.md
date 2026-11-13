# JRFK 64-Bit Modernization Suite: Audio Transcript & Slide Synchronization

**Voice Model:** Australian English Male (`en-AU-WilliamMultilingualNeural`)
**Callsign:** K7BIT
**Total Slides:** 13

---

## [SLIDE 01: JRFK 64-BIT APPLIANCE BUILDER & MIGRATOR]
**File:** `slide_01.png` | **Audio:** `slide_01.mp3` (38.69s) | **Timestamp:** 0.00s - 38.69s

> "Thirty-two-bit Raspberry Pi O S is obsolete, leaving R F kit amplifier owners at risk from unmaintained kernels and S D card failures. On screen is the J R F K dot E X E migration tool running on your Windows P C. It launches as a standalone elevated executable that manages Drive Guard protection and local web services. Its purpose is to prepare a complete sixty-four-bit Raspberry Pi operating system containing all original R F kit calibrations, user data, and the J R F K Web Tools suite for your amplifier. Over the next four slides, we look at the P C migration process, and then we will explore each of the on-amplifier web tools."

---

## [SLIDE 02: MIGRATOR OPTION A: GOLD TO PRODUCTION]
**File:** `slide_02.png` | **Audio:** `slide_02.mp3` (32.28s) | **Timestamp:** 39.69s - 71.97s

> "Examining the primary migration path, Option A: Gold to Production. Look at the upper selector tile on screen. In this mode, you take your existing working S D card from the amplifier and plug it into a U S B reader on your P C. The tool reads your card in read-only safety mode, extracting one hundred percent of your calibration files, directional coupler offsets, and station settings. Once extracted, you remove your original card and insert a new card, which the tool flashes with the complete sixty-four-bit Debian Trixie system."

---

## [SLIDE 03: MIGRATOR OPTION B: CLEAN INSTALL TO PRODUCTION]
**File:** `slide_03.png` | **Audio:** `slide_03.mp3` (29.02s) | **Timestamp:** 72.97s - 101.98s

> "Now look at Option B on screen: Clean Install to Production. This option is used when you are starting fresh with a brand new card or building a spare backup without reading an original card first. On this screen, you directly configure your Raspberry Pi username, system password, hostname, and station Wi-Fi credentials. The tool formats the new target card, installs sixty-four-bit Debian Trixie, and provisions the native R F kit controller alongside the J R F K Web Tools suite."

---

## [SLIDE 04: PC MIGRATOR: DIRECTIONAL COUPLER & ADC CALIBRATION]
**File:** `slide_04.png` | **Audio:** `slide_04.mp3` (24.02s) | **Timestamp:** 102.98s - 127.01s

> "This screen shows the exact calibration data recovered by the P C migrator from your original card. Listed here are the factory directional coupler forward and reflected power A D C lookup tables, attenuator step values, and P T T relay timings. The migrator transfers these exact matrices into the new sixty-four-bit operating system, ensuring that your amplifier retains its factory RF metering precision."

---

## [SLIDE 05: AMPLIFIER DEPLOYMENT: TWO-BOOT PRODUCTION VERIFICATION]
**File:** `slide_05.png` | **Audio:** `slide_05.mp3` (22.22s) | **Timestamp:** 128.01s - 150.23s

> "Once flashing finishes on your P C, you insert the new card into your amplifier's Raspberry Pi four or five. On the first boot, automated scripts expand the Linux root partition to fill the full card and configure controller devices. On the second boot, your amplifier enters full production service running pure sixty-four-bit Debian Trixie with the native front panel app and all Web Tools active."

---

## [SLIDE 06: JRFK WEB TOOLS: UNIFIED STATION DASHBOARD]
**File:** `slide_06.png` | **Audio:** `slide_06.mp3` (22.99s) | **Timestamp:** 151.23s - 174.22s

> "Now we move to the J R F K Web Tools running live on the amplifier. On screen is the master blueprint portal accessed via any browser on port eighty eighty-eight. It runs simultaneously alongside the native R F kit application using shared memory, giving you direct access to the Health Guard, Antenna Matrix, S D Backup Manager, System Diagnostics, Event Logs, and live Screen Streamer."

---

## [SLIDE 07: HEALTH GUARD: REAL-TIME RF TELEMETRY & SAFETY CEILING]
**File:** `slide_07.png` | **Audio:** `slide_07.mp3` (25.42s) | **Timestamp:** 175.22s - 200.64s

> "Examining the Health and Thermal Guard on screen. At the top of the page, the thermal safety banner supervises the P A heatsink temperature against the sixty degree ceiling, unkeying the amplifier into standby if cooling limits are reached. Down below, the instruments display instantaneous forward power up to fifteen hundred Watts, P, E, P, reflected power in Watts, and the fifty-three point five volt D C power supply rail status."

---

## [SLIDE 08: ANTENNA MATRIX & ATU: AUTO SEGMENT TUNING]
**File:** `slide_08.png` | **Audio:** `slide_08.mp3` (31.42s) | **Timestamp:** 201.64s - 233.06s

> "Looking at the Antenna Mapper and Tuner Matrix screen. At the top are the four antenna ports covering one sixty through six meters, which switch automatically via C A T control. Below is the B twenty-six A T U matching network. The R F kit tuner uses relay and P I N diode switching to engage discrete physical inductors and capacitors for each frequency segment. The Bode plot displays S W R across the band and lists the exact physical inductance in nanohenries and capacitance in picofarads selected for that segment."

---

## [SLIDE 09: SD BACKUP MANAGER: AUTOMATED CLONING & RECOVERY]
**File:** `slide_09.png` | **Audio:** `slide_09.mp3` (22.73s) | **Timestamp:** 234.06s - 256.78s

> "Examining the S D Backup and Disaster Recovery tool on screen. The top status panel verifies the active boot card, while the storage selector identifies connected U S B target drives. In under three minutes, this tool writes a complete, bootable clone of your operating system to secondary storage in the background while you remain on the air, keeping a verified standby card ready in case of media failure."

---

## [SLIDE 10: SYSTEM REPORT: COMPLETE CALIBRATION ARCHIVE]
**File:** `slide_10.png` | **Audio:** `slide_10.mp3` (19.94s) | **Timestamp:** 257.78s - 277.73s

> "On screen is the Complete System Report and Calibration Archive. The upper cards display station identity, operating system version, and storage utilization across the root and U S B partitions. Below, full hardware calibration tables can be reviewed on screen and downloaded as a single compressed archive for off-site backup."

---

## [SLIDE 11: DIAGNOSTIC LOGS: CENTRALIZED EVENT TERMINAL]
**File:** `slide_11.png` | **Audio:** `slide_11.mp3` (20.18s) | **Timestamp:** 278.73s - 298.91s

> "Here is the Centralized Diagnostic Log Viewer. On screen, the dropdown allows you to inspect the core R F kit G U I log, the rolling telemetry log, S D backup records, and first-boot migration automation output. System D daemon events and amplifier trip alerts are captured with exact millisecond timestamps for instant diagnosis."

---

## [SLIDE 12: REMOTE SCREEN VIEWER: LIVE 1024X600 DISPLAY]
**File:** `slide_12.png` | **Audio:** `slide_12.mp3` (23.54s) | **Timestamp:** 299.91s - 323.46s

> "On screen is the Remote Screen Viewer. This web tool grabs the physical X eleven framebuffer of the amplifier's seven-inch front panel display and mirrors it live over H T T P at ten twenty-four by six hundred resolution. You see the physical front panel display update in real time from any browser on your network. Technical documentation and schematics are also stored locally on the Pi for offline reference."

---

## [SLIDE 13: RESOURCES, COMMUNITY SUPPORT & PROJECT LINKS]
**File:** `slide_13.png` | **Audio:** `slide_13.mp3` (29.71s) | **Timestamp:** 324.46s - 354.17s

> "In summary, the J R F K Modernization Suite delivers rock-solid operations, comprehensive engineering supervision, and verified disaster recovery for R F kit amplifiers. All source code, pre-compiled Windows migrator executables, and technical releases are available on GitHub at github dot com slash jbirdlebough one slash J R F K Tools. For discussions and technical support, connect with the community on the R F kit groups dot I O reflector. Thank you from K seven B I T."

---

