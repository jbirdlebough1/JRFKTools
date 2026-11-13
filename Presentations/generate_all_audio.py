"""
JRFK Audio Voiceover & VSDC Timeline Generator
Feynman Persona + Authentic Ham Radio Jargon
Generates enthusiastic, intuitive technical narration for amateur radio operators
using open-source Edge-TTS and outputs timeline synchronization maps for VSDC Pro.
"""

import os
import asyncio
import edge_tts
from mutagen.mp3 import MP3

BASE_DIR = r"D:\JRFK\Presentations"
VOICE = "en-US-GuyNeural"
RATE = "+7%"
PITCH = "+0Hz"

NARRATIONS = {
    "Deck_1_Intro": {
        "slide_1": (
            "Look, nature cannot be fooled, especially when you drop the key with fifteen hundred watts PEP "
            "cruising through a pair of LDMOS transistors! On 160 meters through 6 meters, the micro-controller "
            "supervising your RF deck, low-pass relays, and bias sequencing has got to be lightning fast and completely "
            "dependable. Today we take the great leap into pure 64-bit Debian Bookworm architecture!"
        ),
        "slide_2": (
            "Think about it from an RF perspective: running an obsolete 32-bit user-space driver stack on a legal-limit "
            "linear amp is like trying to feed a kilowatt beam with twin-lead taped to a rusty rain gutter! Deprecated "
            "Python sockets and old fake-KMS drivers cause the touchscreen to freeze right in the middle of a hot contest run. "
            "Bookworm gives us 64-bit precision, Full KMS DRM video, and rock-solid SimpleRPC telemetry!"
        ),
        "slide_3": (
            "Here's the secret to reliable shack engineering: strict port decoupling! The PC provisioning tool lives on "
            "port 8089 with hard physical drive safety locks. The amplifier's live operational cockpit lives on port 8088 "
            "directly on the Pi. Even if your Windows shack PC reboots or drops off the LAN, the amplifier never misses an "
            "RF cycle or loses its SWR calibration tables. Clean, isolated, and completely bulletproof!"
        ),
        "slide_4": (
            "Now, for the homebrewers and solder-slingers: John K7BIT's legendary 193-page cookbook is fully preserved "
            "right in the portal! It's an older reference now, but it's packed with every coax tap, toroid winding, "
            "and transformer schematic you'll ever need. Plus our complete modern 4-volume engineering manuals covering "
            "all seven screens and remote telemetry!"
        ),
        "slide_outro": (
            "And that wraps up this briefing! Every link you need—the turnkey JRFK.exe download, the live web documentation "
            "portal on GitHub Pages, the full source repository, and the community forum—is right on your screen. Go ahead "
            "and grab the files, have fun experimenting, and 73 from the shack!"
        )
    },
    "Deck_2_Migration": {
        "slide_1": (
            "Welcome to Part 2! Today we walk step-by-step through the migration. You don't need to be a Linux guru, "
            "and you don't need developer compilers. One clean, standalone executable—JRFK.exe—does the whole job with "
            "surgical precision while keeping your amplifier calibration data completely safe."
        ),
        "slide_2": (
            "Step one: download JRFK.exe and run it! Our custom C# wrapper handles Windows UAC elevation, suppresses "
            "those annoying Windows format-disk popups on raw SD media, and immediately opens your browser to the local "
            "migration dashboard on port 8089."
        ),
        "slide_3": (
            "Before you touch a single byte, you check the instruments! The migrator scans your local subnet, locates the "
            "amplifier controller, verifies SSH communication, and locks your target SD card with physical drive guard "
            "interlocks so you can never accidentally overwrite a system drive."
        ),
        "slide_4": (
            "Now the magic happens: the migrator flashes pure 64-bit Debian Bookworm. It injects the custom 1024 by 600 "
            "video modelines into the kernel command line so the front-panel touch screen is rock steady, and migrates "
            "your existing band tables and SWR calibration offsets automatically."
        ),
        "slide_5": (
            "Here is the ultimate peace of mind for serious operators: the 3-minute disaster recovery card. If a power "
            "spike or lightning pulse ever kills your primary SD card in the middle of a major DX contest, you simply swap "
            "in the secondary backup card, boot up, and you're back on the air in under three minutes!"
        ),
        "slide_outro": (
            "And that wraps up this briefing! Every link you need—the turnkey JRFK.exe download, the live web documentation "
            "portal on GitHub Pages, the full source repository, and the community forum—is right on your screen. Go ahead "
            "and grab the files, have fun experimenting, and 73 from the shack!"
        )
    },
    "Deck_3_Operations": {
        "slide_1": (
            "Welcome to Part 3! Today we explore the cockpit. Why bend down and squint at the front panel when you can have "
            "all seven amplifier screens running smoothly in your web browser? Let's break down each screen: why it exists, "
            "what it measures, and how to fly this machine."
        ),
        "slide_2": (
            "Screen one is your primary cockpit: real-time forward power, reflected power, and SWR. Screen two is the band "
            "switching matrix. When you spin the VFO on your transceiver, CAT commands automatically switch the low-pass "
            "filter relays with strict hardware lockout against hot-switching!"
        ),
        "slide_3": (
            "Screen three watches your amplifier's heart: the dual LDMOS transistors. You get continuous readouts of the "
            "53.5-volt DC rail, drain current, and heatsink temperature. Screen four gives you a four-way antenna matrix "
            "with persistent memory for every single band."
        ),
        "slide_4": (
            "Transistors are fast, but high SWR spikes are just as fast! Screen five shows your active protection thresholds. "
            "If your antenna matches blow out in an ice storm, the software clamps the drive and trips standby in microseconds, "
            "saving your expensive LDMOS devices from destruction!"
        ),
        "slide_5": (
            "Finally, screens six and seven: diagnostic event logs showing exactly what the SimpleRPC controller is doing, "
            "and a five-point touch calibration screen that aligns your front-panel touchscreen with sub-millimeter precision!"
        ),
        "slide_outro": (
            "And that wraps up this briefing! Every link you need—the turnkey JRFK.exe download, the live web documentation "
            "portal on GitHub Pages, the full source repository, and the community forum—is right on your screen. Go ahead "
            "and grab the files, have fun experimenting, and 73 from the shack!"
        )
    },
    "Deck_4_Dev_DeepDive": {
        "slide_1": (
            "Welcome to Part 4, our technical engineering deep dive! As I always loved to say, what I cannot create, I do not "
            "understand! Today we look at every engineering layer: kernel video modelines, Python socket deprecation patches, "
            "discrete DC telemetry, and automated build verification."
        ),
        "slide_2": (
            "In the old days, video was handled by clunky user-space drivers that would choke under intense RF fields. We moved "
            "to Linux Full KMS DRM with custom 1024 by 600 kernel modelines. And we eliminated deprecated Python sockets, giving "
            "us a non-blocking SimpleRPC pipeline that never drops a telemetry packet."
        ),
        "slide_3": (
            "Now let's clear up the hardware reality once and for all: the amplifier runs dual Ampleon BLF189 LDMOS devices. "
            "And the RF-KIT does NOT use CAN bus power supplies! Voltage and current are read directly through clean, discrete "
            "analog shunts into the controller ADC. No CAN bus packet collisions, no firmware handshakes—just pure, reliable DC physics!"
        ),
        "slide_4": (
            "How was this built? Through modern automated development pipelines! Every commit is automatically tested against "
            "18 unit test suites covering port decoupling, drive protection, and modeline syntax before a single release byte "
            "ever touches your amplifier."
        ),
        "slide_5": (
            "In real science, you keep a laboratory notebook! Every step, command, and test result in this project is recorded "
            "in structured JSONL session logs and committed directly to local Git. It's completely transparent, fully auditable, "
            "and 100% offline."
        ),
        "slide_outro": (
            "And that wraps up this briefing! Every link you need—the turnkey JRFK.exe download, the live web documentation "
            "portal on GitHub Pages, the full source repository, and the community forum—is right on your screen. Go ahead "
            "and grab the files, have fun experimenting, and 73 from the shack!"
        )
    },
    "Deck_5_Community_Mods": {
        "slide_1": (
            "Welcome to Part 5! When thousands of ham radio operators build and run an amplifier, the community discovers "
            "what truly works under legal-limit fire. Today we consolidate the most critical, field-proven hardware modifications "
            "for the B26 and RF2K-plus—modifications that give you massive operating headroom."
        ),
        "slide_2": (
            "Modification number one: thermal clamping! Individual screws can warp transistor flanges. A solid CNC clamp bar "
            "applies perfectly uniform pressure. And replacing silicone grease with 0.1-millimeter Indium foil stops grease "
            "pump-out forever under continuous FT8 duty cycles, dropping junction temps by up to 12 degrees!"
        ),
        "slide_3": (
            "Modification number two: the 16 dB input attenuator. Modern 100-watt transceivers produce brief power spikes "
            "before internal ALC loops settle, overdriving LDMOS gates! Swapping to a 16 dB pad lets your radio drive comfortably "
            "at 50 watts right in its linear sweet spot with pristine IMD3 performance."
        ),
        "slide_4": (
            "Mods three and four: low-pass filters and couplers! High circulating RF currents can crack standard mica capacitors "
            "on 10 and 12 meters. Upgrading to ATC porcelain caps handles extreme RF current. And adding copper foil shielding "
            "over the directional coupler stops false SWR trips on 6 meters!"
        ),
        "slide_5": (
            "Mod five: station RFI hardening! When you have fifteen hundred watts radiating nearby, digital ribbon cables act "
            "like little antennas. Snapping Mix 31 and Mix 43 ferrite beads onto the display and I2C cables keeps common-mode RF "
            "out and prevents your touchscreen from ever freezing up."
        ),
        "slide_6": (
            "Here is your master table of links! Every single modification we just covered—from the clamp bars and Indium foil "
            "to the 16 dB attenuator and ATC caps—is listed right here with direct references so you can source parts and review "
            "community schematics instantly."
        ),
        "slide_outro": (
            "And that wraps up this briefing! Every link you need—the turnkey JRFK.exe download, the live web documentation "
            "portal on GitHub Pages, the full source repository, and the community forum—is right on your screen. Go ahead "
            "and grab the files, have fun experimenting, and 73 from the shack!"
        )
    }
}

async def generate_deck_audio(deck_key, slides_dict):
    deck_dir = os.path.join(BASE_DIR, deck_key)
    audio_dir = os.path.join(deck_dir, "audio")
    os.makedirs(audio_dir, exist_ok=True)
    
    timeline_rows = []
    current_time = 0.0
    
    print(f"\n--- Generating Audio for {deck_key} (Feynman Persona + Ham Jargon) ---")
    
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
        current_time = end_time + 1.0
    
    total_duration_str = f"{int(current_time // 60):02d}:{current_time % 60:05.2f}"
    
    # Write VSDC_TIMELINE_MAP.md
    timeline_path = os.path.join(deck_dir, "VSDC_TIMELINE_MAP.md")
    with open(timeline_path, "w", encoding="utf-8") as f:
        f.write(f"# VSDC Pro Timeline Map — {deck_key}\n\n")
        f.write(f"**Total Presentation Duration:** `{total_duration_str}` ({current_time:.1f} seconds)\n")
        f.write(f"**Voice Persona:** Richard Feynman Style + Ham Radio Jargon (Microsoft Guy Neural @ {RATE} rate)\n")
        f.write(f"**Video Format Standard:** 720p HD (1280x720 @ 30 fps)\n\n")
        f.write("| Slide # | Slide Image | Audio Track | Duration | Timeline Start | Timeline End |\n")
        f.write("| :--- | :--- | :--- | :--- | :--- | :--- |\n")
        for s_id, mp3_name, png_name, dur, t_start, t_end in timeline_rows:
            f.write(f"| **{s_id}** | `{png_name}` | `audio/{mp3_name}` | {dur:.2f}s | `{t_start}` | `{t_end}` |\n")
        f.write("\n\n### How to Import into VSDC Pro:\n")
        f.write("1. Open VSDC Video Editor Pro and create a new project: **1280x720, 30 fps, Square Pixels**.\n")
        f.write("2. Add **Track 1 (Visual Slides)**: Drag in the PNG slide images sequentially.\n")
        f.write("3. Add **Track 2 (Feynman Voiceover)**: Drag in the corresponding `audio/*.mp3` clips aligned to each slide's Timeline Start.\n")
    
    print(f"[{deck_key}] Wrote {timeline_path} (Total duration: {total_duration_str})")

async def main():
    for deck_key, slides_dict in NARRATIONS.items():
        await generate_deck_audio(deck_key, slides_dict)
    print("\nAll audio tracks and VSDC timeline maps generated successfully with Feynman Style + Ham Jargon!")

if __name__ == "__main__":
    asyncio.run(main())
