"""
JRFK Audio Voiceover & VSDC Timeline Generator
Generates Richard Feynman persona audio narration for all slides using open-source Edge-TTS
and outputs timeline synchronization maps for VSDC Pro.
"""

import os
import asyncio
import edge_tts
from mutagen.mp3 import MP3

BASE_DIR = r"D:\JRFK\Presentations"
VOICE = "en-US-GuyNeural"
RATE = "+8%"
PITCH = "+0Hz"

# Feynman narration scripts per deck and slide
NARRATIONS = {
    "Deck_1_Intro": {
        "slide_1": "Look, nature cannot be fooled! When you have fifteen hundred watts of RF power cruising through a pair of LDMOS transistors, the computer controlling it has to be fast, stable, and completely dependable. Today we take the great leap into pure 64-bit architecture!",
        "slide_2": "Think about it like this: running an ancient 32-bit operating system on a modern linear amplifier is like bolting a high-performance jet engine onto a wooden wagon! It works until the wheels fall off. Bookworm gives us 64-bit precision and rock-solid DRM display drivers.",
        "slide_3": "Here's the secret to reliable engineering: isolation! The tool that sets up the system on your PC lives on port 8089. The actual amplifier cockpit lives on port 8088 on the Pi itself. They never get in each other's way. Brilliant and clean!",
        "slide_4": "Now, for the builders who love getting solder on their fingers: we've included John K7BIT's legendary 193-page cookbook in the portal. It's an older reference now, but it has every wire, bolt, and schematic diagram you'll ever need. Plus our complete modern 4-volume engineering manuals!",
        "slide_outro": "And that wraps up this briefing! Every link you need—the turnkey JRFK.exe download, the live web documentation portal on GitHub Pages, the full source repository, and the community forum—is right on your screen. Go ahead and grab the files, have fun experimenting, and 73 from the shack!"
    },
    "Deck_2_Migration": {
        "slide_1": "Welcome to Part 2! Today we walk step-by-step through the migration. You don't need to be a Linux guru, and you don't need developer tools. One clean executable does the whole job with surgical precision.",
        "slide_2": "Step one: download JRFK.exe and run it! Our custom C# wrapper handles Windows UAC elevation, suppresses annoying popups, and immediately opens your browser to the local migration dashboard on port 8089.",
        "slide_3": "Before you take off, you check the instruments! The migrator scans your network, finds the amplifier, verifies SSH communication, and makes sure your secondary backup storage is ready before touching a single byte.",
        "slide_4": "Now the magic happens: the migrator flashes pure 64-bit Debian Bookworm. It injects the custom 1024 by 600 video modelines so the physical touch screen is crisp and stable, and patches the Python runtime for smooth SimpleRPC telemetry.",
        "slide_5": "Here is the ultimate peace of mind: the 3-minute disaster recovery card. If a power spike ever kills your primary SD card in the middle of a DX contest, you simply swap in the secondary backup card, boot up, and you're back on the air!",
        "slide_outro": "And that wraps up this briefing! Every link you need—the turnkey JRFK.exe download, the live web documentation portal on GitHub Pages, the full source repository, and the community forum—is right on your screen. Go ahead and grab the files, have fun experimenting, and 73 from the shack!"
    },
    "Deck_3_Operations": {
        "slide_1": "Welcome to Part 3! Today we explore the cockpit. Why should you have to bend down and squint at the front panel when you can have all seven amplifier screens running smoothly in your web browser? Let's break down each screen: why it exists, what it measures, and how to use it.",
        "slide_2": "Screen one is your primary cockpit: real-time forward power, reflected power, and SWR. Screen two is the band switching matrix. When you turn the VFO on your transceiver, CAT commands automatically switch the low-pass filter relays with zero hot-switching.",
        "slide_3": "Screen three watches your amplifier's heart: the dual LDMOS transistors. You get continuous readouts of the 53.5 volt DC rail, drain current, and temperature. Screen four gives you a four-way antenna matrix with memory for every band.",
        "slide_4": "Transistors are fast, but high SWR spikes are just as fast! Screen five shows your active protection thresholds. If your antenna blows down in a windstorm, the software clamps the drive and trips standby in microseconds, saving your amplifier from destruction.",
        "slide_5": "Finally, screens six and seven: diagnostic event logs showing exactly what the SimpleRPC controller is doing, and a five-point touch calibration screen that aligns your physical touchscreen with sub-millimeter precision!",
        "slide_outro": "And that wraps up this briefing! Every link you need—the turnkey JRFK.exe download, the live web documentation portal on GitHub Pages, the full source repository, and the community forum—is right on your screen. Go ahead and grab the files, have fun experimenting, and 73 from the shack!"
    },
    "Deck_4_Dev_DeepDive": {
        "slide_1": "Welcome to Part 4, our technical deep dive! As I always used to say, what I cannot create, I do not understand! Today we look at every engineering layer: video modelines, Python deprecation patches, electrical characteristics, and Gemini Pro automation.",
        "slide_2": "In the old days, video was handled by clunky user-space drivers that would choke under RF interference. We moved to Linux Full KMS DRM with custom 1024 by 600 kernel modelines. And we eliminated deprecated Python sockets, giving us a non-blocking SimpleRPC pipeline.",
        "slide_3": "Let's be crystal clear on hardware: the amplifier runs dual Ampleon BLF189 LDMOS devices. And the RF-KIT does NOT use CAN bus power supplies! Voltage and current are read directly through clean, discrete analog shunts. No CAN bus crashes, no firmware handshakes—just pure, reliable DC physics.",
        "slide_4": "How was this built? Through modern AI automation! Using Google Gemini Pro and Antigravity, we automated the entire build and verification pipeline. Every release passes all 18 automated unit tests before a single byte touches production.",
        "slide_5": "In real science, you keep a laboratory notebook! Every step, command, and test result in this project is recorded in structured JSONL session logs and committed directly to Git. It's completely transparent, fully auditable, and reproducible.",
        "slide_outro": "And that wraps up this briefing! Every link you need—the turnkey JRFK.exe download, the live web documentation portal on GitHub Pages, the full source repository, and the community forum—is right on your screen. Go ahead and grab the files, have fun experimenting, and 73 from the shack!"
    },
    "Deck_5_Community_Mods": {
        "slide_1": "Welcome to Part 5! When thousands of ham radio operators build and run an amplifier, the collective community discovers what truly works. Today we consolidate the most critical, field-proven modifications for the B26 and RF2K-S—proven improvements that give you massive reliability headroom.",
        "slide_2": "Modification number one: thermal clamping! Individual screws can warp transistor flanges. A solid CNC clamp bar applies perfectly uniform pressure. And replacing silicone grease with 0.1 millimeter Indium foil stops grease pump-out forever—solid metal heat transfer that never degrades!",
        "slide_3": "Modification number two: the 16 dB input attenuator. Modern 100-watt transceivers hate putting out only twenty watts—their ALC circuits overshoot and spike the input! Swapping to a 16 dB pad lets your radio drive comfortably at fifty watts, right in its linear sweet spot.",
        "slide_4": "Mods three and four: low-pass filters and couplers! High RF circulating currents can crack standard mica capacitors on ten meters. Upgrading to ATC porcelain caps handles extreme RF current. And adding copper foil shielding over the SWR bridge stops false SWR trips on six meters!",
        "slide_5": "Mod five: RFI hardening! When you have fifteen hundred watts radiating nearby, digital ribbon cables act like little antennas. Snapping Mix 31 and 43 ferrite beads onto the display and I2C cables keeps the RF out and prevents your touchscreen from ever freezing up.",
        "slide_6": "Here is your master table of links! Every single modification we just covered—from the clamp bars and Indium foil to the 16 dB attenuator and ATC caps—is listed right here with direct references so you can find the parts and forum discussions instantly.",
        "slide_outro": "And that wraps up this briefing! Every link you need—the turnkey JRFK.exe download, the live web documentation portal on GitHub Pages, the full source repository, and the community forum—is right on your screen. Go ahead and grab the files, have fun experimenting, and 73 from the shack!"
    }
}

async def generate_deck_audio(deck_key, slides_dict):
    deck_dir = os.path.join(BASE_DIR, deck_key)
    audio_dir = os.path.join(deck_dir, "audio")
    os.makedirs(audio_dir, exist_ok=True)
    
    timeline_rows = []
    current_time = 0.0
    
    print(f"\n--- Generating Audio for {deck_key} ---")
    
    for slide_id, text in slides_dict.items():
        mp3_filename = f"{slide_id}.mp3"
        mp3_path = os.path.join(audio_dir, mp3_filename)
        
        print(f"Generating voiceover: {mp3_filename}...")
        comm = edge_tts.Communicate(text, voice=VOICE, rate=RATE, pitch=PITCH)
        await comm.save(mp3_path)
        
        # Measure duration with mutagen
        audio = MP3(mp3_path)
        duration = audio.info.length
        
        start_str = f"{int(current_time // 60):02d}:{current_time % 60:05.2f}"
        end_time = current_time + duration
        end_str = f"{int(end_time // 60):02d}:{end_time % 60:05.2f}"
        
        timeline_rows.append((slide_id, mp3_filename, f"{slide_id}.png", duration, start_str, end_str))
        
        # Add 1.0 second pause between slides
        current_time = end_time + 1.0
    
    total_duration_str = f"{int(current_time // 60):02d}:{current_time % 60:05.2f}"
    
    # Write TIMELINE_MAP.md
    timeline_path = os.path.join(deck_dir, "VSDC_TIMELINE_MAP.md")
    with open(timeline_path, "w", encoding="utf-8") as f:
        f.write(f"# VSDC Pro Timeline Map — {deck_key}\n\n")
        f.write(f"**Total Presentation Duration:** `{total_duration_str}` ({current_time:.1f} seconds)\n")
        f.write(f"**Voice Persona:** Richard Feynman (Microsoft Guy Neural @ +8% rate)\n")
        f.write(f"**Video Format Standard:** 720p HD (1280x720 @ 30 fps)\n\n")
        f.write("| Slide # | Slide Image | Audio Track | Duration | Timeline Start | Timeline End |\n")
        f.write("| :--- | :--- | :--- | :--- | :--- | :--- |\n")
        for s_id, mp3_name, png_name, dur, t_start, t_end in timeline_rows:
            f.write(f"| **{s_id}** | `{png_name}` | `audio/{mp3_name}` | {dur:.2f}s | `{t_start}` | `{t_end}` |\n")
        f.write("\n\n### How to Import into VSDC Pro:\n")
        f.write("1. Open VSDC Video Editor Pro and create a new project: **1280x720, 30 fps, Square Pixels**.\n")
        f.write("2. Add **Track 1 (Video/Image B-Roll)**: Drag in the PNG slide images sequentially.\n")
        f.write("3. Add **Track 2 (Voiceover Audio)**: Drag in the corresponding `audio/*.mp3` clips aligned to each slide's Timeline Start.\n")
        f.write("4. (Optional) Set slide image durations in the VSDC object properties to match the Duration listed above + 1.0s buffer.\n")
    
    print(f"[{deck_key}] Wrote {timeline_path} (Total duration: {total_duration_str})")

async def main():
    # Remove test file if exists
    test_path = os.path.join(BASE_DIR, "test_feynman_voice.mp3")
    if os.path.exists(test_path):
        os.remove(test_path)
        
    for deck_key, slides_dict in NARRATIONS.items():
        await generate_deck_audio(deck_key, slides_dict)
    
    print("\nAll audio tracks and VSDC timeline maps generated successfully!")

if __name__ == "__main__":
    asyncio.run(main())
