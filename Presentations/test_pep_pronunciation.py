import asyncio
import edge_tts
import mutagen.mp3

# Testing the exact pronunciation requested:
# "1500 <pause 500ms> Watts PEE EEE PEE"
# In edge-tts / SSML: "fifteen hundred ... Watts, P E P" or using SSML <break time="500ms"/>

async def test_ssml_pep():
    voice = "en-US-BrianNeural"
    
    # Variant 1: SSML with exact 500ms break
    ssml_text = """<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">
        <voice name="en-US-BrianNeural">
            Welcome to Part 1 of our technical overview from K7BIT. When you are managing fifteen hundred <break time="500ms"/> Watts P E P across one sixty through six meters, the controller supervising your R F deck, low-pass relays, and protection sequencing must be completely deterministic.
        </voice>
    </speak>"""
    
    out_file = r"D:\JRFK\Presentations\Deck_1_Intro\voice_shootout\test_ssml_pep.mp3"
    comm = edge_tts.Communicate(ssml_text, voice)
    await comm.save(out_file)
    print("Saved test_ssml_pep.mp3")

if __name__ == "__main__":
    asyncio.run(test_ssml_pep())
