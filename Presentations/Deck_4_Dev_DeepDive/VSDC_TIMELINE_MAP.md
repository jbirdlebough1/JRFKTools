# VSDC Pro Timeline Alignment Map — Development Deep Dive & Build Automation

**Total Video Duration:** `01:39.15`

Use this exact table to position each image and audio track in VSDC Video Editor Pro:

| Slide / Segment | Visual Track (PNG) | Audio Track (MP3) | Timeline Start | Duration | Timeline End |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Slide 1: JRFK Engineering Deep Dive** | `slide_1.png` | `audio/slide_1.mp3` | `00:00.00` | `16.25s` | `00:16.25` |
| **Slide 2: Full KMS DRM Video & SimpleRPC Patches** | `slide_2.png` | `audio/slide_2.mp3` | `00:17.25` | `16.37s` | `00:33.62` |
| **Slide 3: Hardware Truth: Dual BLF189 & Discrete DC** | `slide_3.png` | `audio/slide_3.mp3` | `00:34.62` | `18.77s` | `00:53.38` |
| **Slide 4: Automated Build & Test Pipeline** | `slide_4.png` | `audio/slide_4.mp3` | `00:54.38` | `13.30s` | `01:07.68` |
| **Slide 5: Local Version Control & Session Logging** | `slide_5.png` | `audio/slide_5.mp3` | `01:08.68` | `12.48s` | `01:21.16` |
| **Outro: Master Resources** | `slide_outro.png` | `audio/slide_outro.mp3` | `01:22.16` | `16.99s` | `01:39.15` |


### VSDC Setup Instructions:
1. Set Project Resolution: **1280 x 720 (16:9)** at **30 fps**.
2. Drag the `.png` slides in order onto Layer 1.
3. Drag the matching `audio/*.mp3` tracks onto Layer 2, aligning each start time to the `Timeline Start` column above.
4. Export video via `Export Project` -> `To MP4` (H.264/AAC).
