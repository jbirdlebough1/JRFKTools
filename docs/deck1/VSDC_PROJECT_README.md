# VSDC Import & Timeline Mapping Guide
**Presentation 1: The Migration Requirement & RF-KIT Controller Architecture**
**Target Software:** VSDC Free / Pro Video Editor
**Dedicated Clean Media Folder:** `D:\JRFK\Presentations\Deck_1_Intro\vsdc_media\`

---

## 1. VSDC Architecture & File Handling

According to official VSDC documentation:
1. **`.vproj` File Nature:** A VSDC project (`.vproj`) is an OLE Structured Storage compound document containing serialized binary property streams and proprietary GUID blocks. It is not an XML text file and cannot be manually written from scratch without risk of binary corruption.
2. **Media Loading:** VSDC loads media by file paths. To ensure VSDC loads **only** the slides and audio tracks (and does not see or attempt to parse markdown, HTML, or build scripts), all 13 slide images and 13 audio files have been isolated into a dedicated folder:
   ```
   D:\JRFK\Presentations\Deck_1_Intro\vsdc_media\
   ```
   This folder contains strictly supported media: 13 `.png` slide images and 13 `.mp3` narration tracks.

---

## 2. 60-Second Import Workflow in VSDC

### Option A: The Slideshow Wizard (Fastest)
1. Open **VSDC Video Editor**.
2. On the start screen, click **"Create Slideshow"** (or in an empty project, click **Editor > Run Wizard**).
3. Set Project Name: `Deck_1_Intro_Migration_Architecture`.
4. In the Wizard window, click **"Add files"** (or open Windows File Explorer to `D:\JRFK\Presentations\Deck_1_Intro\vsdc_media\` and drag all 13 `slide_*.png` files into the window).
5. The slides will arrange automatically from `slide_01.png` to `slide_13.png`.
6. Click **"Apply Settings"** to place the sprite onto Timeline Track 1.
7. Click **Editor > Add Object > Audio** (or drag all 13 `slide_*.mp3` files from `vsdc_media`) onto Timeline Track 2.

### Option B: Direct Multi-Select Timeline Drag
1. In VSDC, create a **Blank Project** (`1920x1080`, `30 fps`).
2. Open Windows File Explorer to:
   ```
   D:\JRFK\Presentations\Deck_1_Intro\vsdc_media\
   ```
3. Multi-select all 13 `.png` files (`slide_01.png` through `slide_13.png`) and drop them onto **Track 1**.
4. Multi-select all 13 `.mp3` files (`slide_01.mp3` through `slide_13.mp3`) and drop them onto **Track 2**.

---

## 3. Exact Slide & Audio Timing Map (05:58.34 Total)

Every slide duration in VSDC should be set to match its narration track. In VSDC's **Properties Window** on the right, set the duration for each slide as follows:

| Index | Slide Asset | Audio Asset | Duration (s) | Milliseconds | Timeline Start | Timeline End | Content Topic |
|---|---|---|---|---|---|---|---|
| **01** | `slide_01.png` | `slide_01.mp3` | **28.104s** | 28,104 ms | `00:00.000` | `00:28.104` | Migration Requirement: RF-KIT Controller & 64-Bit Bookworm |
| **02** | `slide_02.png` | `slide_02.mp3` | **27.264s** | 27,264 ms | `00:28.104` | `00:55.368` | Why 32-Bit Must Go: Software EOL & Python Deprecation |
| **03** | `slide_03.png` | `slide_03.mp3` | **33.480s** | 33,480 ms | `00:55.368` | `01:28.848` | Display Driver Architecture & Framebuffer Lock Risks |
| **04** | `slide_04.png` | `slide_04.mp3` | **24.792s** | 24,792 ms | `01:28.848` | `01:53.640` | 64-Bit Architecture Overview: The Technical Payoff |
| **05** | `slide_05.png` | `slide_05.mp3` | **30.288s** | 30,288 ms | `01:53.640` | `02:23.928` | Tool 1: JRFK Standalone Migrator Architecture |
| **06** | `slide_06.png` | `slide_06.mp3` | **25.080s** | 25,080 ms | `02:23.928` | `02:49.008` | Tool 1: Automated Discovery, Flashing & Calibration Backup |
| **07** | `slide_07.png` | `slide_07.mp3` | **27.120s** | 27,120 ms | `02:49.008` | `03:16.128` | Tool 2: 7-Screen Web Suite — RF Telemetry & Band Switching |
| **08** | `slide_08.png` | `slide_08.mp3` | **32.352s** | 32,352 ms | `03:16.128` | `03:48.480` | Tool 2: PA Thermal Monitoring & 4-Way Antenna Matrix |
| **09** | `slide_09.png` | `slide_09.mp3` | **26.376s** | 26,376 ms | `03:48.480` | `04:14.856` | Tool 2: Protection Systems, Error Tripping & Touch Cal |
| **10** | `slide_10.png` | `slide_10.mp3` | **26.400s** | 26,400 ms | `04:14.856` | `04:41.256` | Tool 3: The 3-Minute Disaster Recovery Standby Card |
| **11** | `slide_11.png` | `slide_11.mp3` | **24.768s** | 24,768 ms | `04:41.256` | `05:06.024` | Tool 3: First-Boot Automation & Self-Healing Services |
| **12** | `slide_12.png` | `slide_12.mp3` | **27.144s** | 27,144 ms | `05:06.024` | `05:33.168` | Tool 4: Master Engineering Library & Cookbook Portal |
| **13** | `slide_13.png` | `slide_13.mp3` | **25.176s** | 25,176 ms | `05:33.168` | `05:58.344` | Summary & Master Resource Directory |

---

## 4. Saving & Packaging Your Project in VSDC

Once the files are positioned on your timeline:
1. Click the **Projects** tab in the top ribbon and select **"Save Project"** to save `Deck_1_Intro.vproj` directly into `D:\JRFK\Presentations\Deck_1_Intro\`.
2. (Optional) To create a completely self-contained portable package, select **Projects > Pack project**. VSDC will bundle the `.vproj` and all referenced media assets into a single portable zip archive.
