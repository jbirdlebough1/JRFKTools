"""
JRFK Audio Voiceover & VSDC Timeline Generator
Generates clean, professional technical narration audio tracks for amateur radio operators
using open-source Edge-TTS and outputs timeline synchronization maps for VSDC Pro.
"""

import os
import sys
import asyncio
import edge_tts
from mutagen.mp3 import MP3

sys.path.append(r"D:\JRFK\Presentations")
from build_all_presentations import DECKS, BASE_DIR

VOICE = "en-US-GuyNeural"
RATE = "+0%"
PITCH = "+0Hz"

OUTRO_TEXT = (
    "This concludes our presentation. All project resources—including the turnkey JRFK "
    "executable, documentation portal, source code, and community discussions—are available "
    "at the links shown on your screen. Thank you for watching, and 73 from the station."
)

async def generate_track(text, output_path):
    communicate = edge_tts.Communicate(text, VOICE, rate=RATE, pitch=PITCH)
    await communicate.save(output_path)

def format_time(seconds):
    mins = int(seconds // 60)
    secs = seconds % 60
    return f"{mins:02d}:{secs:05.2f}"

async def main():
    print(f"Generating technical narration audio using {VOICE} ({RATE} rate)...")
    
    for deck_key, deck_data in DECKS.items():
        deck_dir = os.path.join(BASE_DIR, deck_key)
        audio_dir = os.path.join(deck_dir, "audio")
        os.makedirs(audio_dir, exist_ok=True)
        
        timeline_rows = []
        current_time = 0.0
        
        # Slides narration
        for idx, slide in enumerate(deck_data["slides"], 1):
            slide_id = slide["id"]
            title = slide["title"]
            narration = slide.get("narration", "")
            mp3_path = os.path.join(audio_dir, f"{slide_id}.mp3")
            
            print(f"[{deck_key}] Generating {slide_id}.mp3...")
            await generate_track(narration, mp3_path)
            
            # Read duration
            audio = MP3(mp3_path)
            duration = audio.info.length
            
            start_str = format_time(current_time)
            end_time = current_time + duration
            end_str = format_time(end_time)
            dur_str = f"{duration:.2f}s"
            
            timeline_rows.append((f"Slide {idx}: {title}", f"{slide_id}.png", f"audio/{slide_id}.mp3", start_str, dur_str, end_str))
            current_time = end_time + 1.0 # 1.0 second pause between slides
        
        # Outro narration
        outro_mp3 = os.path.join(audio_dir, "slide_outro.mp3")
        print(f"[{deck_key}] Generating slide_outro.mp3...")
        await generate_track(OUTRO_TEXT, outro_mp3)
        
        audio = MP3(outro_mp3)
        duration = audio.info.length
        start_str = format_time(current_time)
        end_time = current_time + duration
        end_str = format_time(end_time)
        dur_str = f"{duration:.2f}s"
        timeline_rows.append(("Outro: Master Resources", "slide_outro.png", "audio/slide_outro.mp3", start_str, dur_str, end_str))
        
        # Generate VSDC Timeline Map Markdown
        map_path = os.path.join(deck_dir, "VSDC_TIMELINE_MAP.md")
        with open(map_path, "w", encoding="utf-8") as f:
            f.write(f"# VSDC Pro Timeline Alignment Map — {deck_data['title']}\n\n")
            f.write(f"**Total Video Duration:** `{format_time(end_time)}`\n\n")
            f.write("Use this exact table to position each image and audio track in VSDC Video Editor Pro:\n\n")
            f.write("| Slide / Segment | Visual Track (PNG) | Audio Track (MP3) | Timeline Start | Duration | Timeline End |\n")
            f.write("| :--- | :--- | :--- | :--- | :--- | :--- |\n")
            for row in timeline_rows:
                f.write(f"| **{row[0]}** | `{row[1]}` | `{row[2]}` | `{row[3]}` | `{row[4]}` | `{row[5]}` |\n")
            f.write("\n\n### VSDC Setup Instructions:\n")
            f.write("1. Set Project Resolution: **1280 x 720 (16:9)** at **30 fps**.\n")
            f.write("2. Drag the `.png` slides in order onto Layer 1.\n")
            f.write("3. Drag the matching `audio/*.mp3` tracks onto Layer 2, aligning each start time to the `Timeline Start` column above.\n")
            f.write("4. Export video via `Export Project` -> `To MP4` (H.264/AAC).\n")
            
        print(f"[{deck_key}] Wrote {map_path}")

    print("\nAll technical audio narration tracks and VSDC timeline maps generated successfully!")

if __name__ == "__main__":
    asyncio.run(main())
