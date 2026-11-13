import asyncio
import os
import sys
import edge_tts
import mutagen.mp3

sys.path.insert(0, r"D:\JRFK\Presentations")
from pronunciation_rules import clean_for_speech

DECK_DIR = r"D:\JRFK\Presentations\Deck_1_Intro"
VSDC_DIR = os.path.join(DECK_DIR, "vsdc_media")

# Script definitions
SLIDES_DATA = [
    {
        "id": 1,
        "title": "Modernizing the RF-KIT Linear Amplifier",
        "raw": "Welcome to Part 1 of our technical overview. When you are managing fifteen hundred watts PEP across 160 meters through 6 meters, the micro-controller supervising your RF deck, low-pass relays, and protection sequencing must be completely deterministic. In this briefing, we examine the technical requirement for migrating the RF-KIT platform from legacy 32-bit operating systems to pure 64-bit Debian Bookworm architecture."
    },
    {
        "id": 2,
        "title": "Why 32-Bit Must Go: Software End-of-Life",
        "raw": "Let's look at why migration is necessary. The original 32-bit operating system has reached official end-of-life. Upstream package repositories are frozen, and deprecated Python socket implementations prevent the controller from running modern network protocols or security patches. Without upgrading, the amplifier controller becomes an isolated legacy device unable to communicate reliably with modern station automation."
    },
    {
        "id": 3,
        "title": "Why 32-Bit Must Go: Display Architecture & RF Locks",
        "raw": "The second critical driver for migration is display architecture. Legacy 32-bit installations relied on user-space fake-KMS and older X11 graphics layers. In the presence of strong RF fields during legal-limit keying, memory fragmentation in these user-space drivers frequently caused touchscreen freezes and display blanking. Upgrading to 64-bit Full KMS DRM places the 1024 by 600 display modelines directly inside the Linux kernel, ensuring rock-solid display stability."
    },
    {
        "id": 4,
        "title": "64-Bit Architecture Overview: The Technical Payoff",
        "raw": "The 64-bit architecture delivers an immediate technical payoff. Debian Bookworm provides 64-bit memory protection, modern Linux kernel stability, and a fully non-blocking SimpleRPC telemetry loop. Fragile legacy startup scripts are replaced with native systemd service units, ensuring that all controller daemons automatically recover in the event of an unexpected fault."
    },
    {
        "id": 5,
        "title": "Tool 1: JRFK Standalone Migrator Architecture",
        "raw": "Now let's examine the first major component of the JRFK suite: the Standalone Migrator. Distributed as a single 166-megabyte Windows executable, JRFK.exe requires zero developer tools or Python dependencies. It incorporates a dedicated C-sharp launcher that handles administrative elevation, suppresses disruptive Windows 11 format prompts on raw media, and enforces strict physical drive guard locks to prevent accidental drive overwrites."
    },
    {
        "id": 6,
        "title": "Tool 1 in Action: Discovery, Flashing & Calibration",
        "raw": "In operation, the migrator automates the entire provisioning workflow. It scans your local network to discover the amplifier controller, flashes the verified 64-bit Bookworm base image, injects native 1024 by 600 display modelines, and extracts your amplifier's unique band tables and SWR calibration offsets from your old SD card so no factory calibration is lost."
    },
    {
        "id": 7,
        "title": "Tool 2: 7-Screen Web Suite — RF Telemetry & Bands",
        "raw": "The second major tool in the suite is the 7-screen operational web cockpit running permanently on port 8088. This tool decouples live operation from PC maintenance. Screen 1 gives you real-time forward PEP, reflected power, and SWR metering from any browser in your shack, while Screen 2 provides automatic low-pass filter band switching synchronized to your transceiver via CAT control with active hot-switch prevention."
    },
    {
        "id": 8,
        "title": "Tool 2: PA Monitoring & 4-Way Antenna Matrix",
        "raw": "Screens 3 and 4 handle RF deck health and antenna routing. Screen 3 monitors the 53.5-volt DC rail, drain current, and heatsink thermals across the dual Ampleon BLF189 LDMOS transistors. Note that the RF-KIT uses discrete analog shunts rather than CAN bus power supplies, ensuring noise-free DC telemetry. Screen 4 manages a 4-way antenna matrix that automatically recalls your selected antenna port for each band."
    },
    {
        "id": 9,
        "title": "Tool 2: Protection Systems, Logs & Touch Calibration",
        "raw": "Screens 5, 6, and 7 deliver comprehensive protection and maintenance. Screen 5 enforces hardware protection limits, clamping drive and dropping into standby within microseconds if SWR exceeds 2.5 to 1 or heatsink temperature reaches 60 degrees. Screens 6 and 7 provide real-time controller event logs and a built-in 5-point touchscreen calibration utility."
    },
    {
        "id": 10,
        "title": "Tool 3: The 3-Minute Disaster Recovery Standby Card",
        "raw": "Tool 3 is the Disaster Recovery Engine. During the migration workflow, JRFK provisions an identical secondary SD card containing the complete 64-bit operating system and all current calibration offsets. If an SD card ever suffers hardware failure during contest operations, the operator simply inserts the standby card and powers up, returning the station to full operation in under three minutes."
    },
    {
        "id": 11,
        "title": "Tool 3: First-Boot Automation & Self-Healing Services",
        "raw": "Supporting disaster recovery is our first-boot automation framework. Upon initial startup, the setup script expands the Linux root partition to fill the SD card, applies network configurations, and enables systemd service watchdogs. These watchdogs actively supervise all background daemons, automatically restarting them without operator intervention if an abnormal state occurs."
    },
    {
        "id": 12,
        "title": "Tool 4: Master Engineering Library & Cookbook Reader",
        "raw": "Tool 4 is the Master Documentation Portal. The portal hosts our complete 4-volume engineering library covering station operation, remote telemetry, and architecture. Furthermore, John K7BIT's authentic 193-page B26 cookbook is integrated directly into the portal, providing operators and builders with instant, searchable access to original schematics and wiring diagrams from any browser."
    },
    {
        "id": 13,
        "title": "Summary & Master Resource Directory",
        "raw": "In summary, the JRFK modernization suite delivers a complete 64-bit transformation: automated migration, a 7-screen operational web cockpit, instant disaster recovery, and comprehensive technical documentation. All downloads, source code, and community discussions are accessible at the links displayed on your screen. Thank you for watching, and 73 from the station."
    }
]

async def generate_speech():
    voice = "en-US-ChristopherNeural"
    timing_rows = []
    
    print(f"Generating phonetic speech tracks using voice: {voice}...")
    
    for item in SLIDES_DATA:
        sid = item["id"]
        raw_text = item["raw"]
        clean_text = clean_for_speech(raw_text)
        
        out_deck_mp3 = os.path.join(DECK_DIR, f"slide_{sid:02d}.mp3")
        out_vsdc_mp3 = os.path.join(VSDC_DIR, f"slide_{sid:02d}.mp3")
        
        print(f"Generating Slide {sid:02d}: {item['title']}...")
        communicate = edge_tts.Communicate(clean_text, voice)
        await communicate.save(out_deck_mp3)
        
        # Copy to vsdc_media
        if os.path.exists(VSDC_DIR):
            with open(out_deck_mp3, "rb") as src, open(out_vsdc_mp3, "wb") as dst:
                dst.write(src.read())
        
        # Measure duration
        length = mutagen.mp3.MP3(out_deck_mp3).info.length
        frames = round(length * 30)
        timing_rows.append((sid, item["title"], length, frames))
        print(f"  [OK] Duration: {length:.2f}s ({frames} frames)")
    
    print("\n=== UPDATED VSDC TIMING MAP ===")
    total_sec = sum(r[2] for r in timing_rows)
    m, s = divmod(total_sec, 60)
    print(f"Total Duration: {int(m):02d}:{s:05.2f}")
    for sid, title, length, frames in timing_rows:
        print(f"Slide {sid:02d}: {length:5.2f}s | {frames:4d} frames | {title}")

if __name__ == "__main__":
    asyncio.run(generate_speech())
