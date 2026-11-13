import asyncio
import edge_tts

async def list_au_voices():
    voices = await edge_tts.list_voices()
    au_voices = [v for v in voices if 'AU' in v['Locale']]
    for v in au_voices:
        print(f"{v['ShortName']} ({v['Gender']}) - {v.get('FriendlyName', '')}")

if __name__ == "__main__":
    asyncio.run(list_au_voices())
