import asyncio
import edge_tts
import os

OUT_DIR = r"D:\JRFK\Presentations\Deck_1_Intro\voice_shootout"
os.makedirs(OUT_DIR, exist_ok=True)

VOICES = [
    ("en-US-BrianNeural", "Brian (Natural, warm conversational)"),
    ("en-US-RogerNeural", "Roger (Natural, calm technical)"),
    ("en-US-EricNeural", "Eric (Natural, documentary/technical)"),
    ("en-US-SteffanNeural", "Steffan (Natural, measured pacing)"),
]

# Variations in how hams say 1500W PEP
VARIATIONS = [
    ("variant_A", "fifteen hundred watts, P-E-P,"),
    ("variant_B", "fifteen hundred watts pep,"),
    ("variant_C", "full legal limit power,"),
]

async def generate_samples():
    for v_id, v_desc in VOICES:
        for var_name, phrase in VARIATIONS:
            text = f"Welcome to Part 1 of our technical overview from station K 7 B I T. When you are managing {phrase} across one hundred sixty through six meters, the controller supervising your R F deck, low-pass relays, and protection sequencing must be completely deterministic."
            fn = f"{v_id.split('-')[2]}_{var_name}.mp3"
            path = os.path.join(OUT_DIR, fn)
            print(f"Generating {fn} ({v_desc} with '{phrase}')...")
            comm = edge_tts.Communicate(text, v_id)
            await comm.save(path)

if __name__ == "__main__":
    asyncio.run(generate_samples())
