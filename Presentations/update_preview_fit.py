import os
import json
import mutagen.mp3

DECK_DIR = r"D:\JRFK\Presentations\Deck_1_Intro"
BUILD_SCRIPT = r"D:\JRFK\Presentations\build_deck1_blueprint_final.py"

with open(BUILD_SCRIPT, "r", encoding="utf-8") as f:
    text = f.read()

# Read SLIDES from build script
scope = {}
exec_code = text[:text.find("async def generate_slides_and_audio():")]
exec(exec_code, scope)
slides_data = scope["SLIDES"]

slides_json = []
for idx, s in enumerate(slides_data):
    i = idx + 1
    num = f"{i:02d}"
    mp3_path = os.path.join(DECK_DIR, f"slide_{num}.mp3")
    dur = 20.0
    if os.path.exists(mp3_path):
        try:
            a = mutagen.mp3.MP3(mp3_path)
            dur = a.info.length
        except Exception:
            pass
    slides_json.append({
        "id": i,
        "num": num,
        "title": s["title"],
        "img": f"slide_{num}.png",
        "audio": f"slide_{num}.mp3",
        "duration": dur,
        "narration": s["narration"]
    })

slides_json_str = json.dumps(slides_json, indent=2)

player_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>JRFK Modernization Suite - Auto-Advancing Technical Player - K7BIT</title>
<style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    html, body {{
        width: 100vw;
        height: 100vh;
        overflow: hidden;
        background: #091a2e;
        color: #ffffff;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        display: flex;
        flex-direction: column;
    }}
    .player-header {{
        height: 48px;
        background: #0f2d4f;
        border-bottom: 2px solid #38bdf8;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 20px;
        flex-shrink: 0;
    }}
    .player-title {{ font-size: 16px; font-weight: 800; color: #38bdf8; display: flex; align-items: center; gap: 8px; }}
    .player-callsign {{
        background: #0284c7;
        color: white;
        padding: 3px 10px;
        border-radius: 4px;
        font-family: monospace;
        font-weight: bold;
        font-size: 13px;
    }}
    .player-main {{
        flex: 1 1 auto;
        min-height: 0;
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 8px 12px;
        background: #061524;
        overflow: hidden;
    }}
    .slide-viewport {{
        width: 100%;
        height: 100%;
        display: flex;
        justify-content: center;
        align-items: center;
        overflow: hidden;
    }}
    .slide-img {{
        max-width: 100%;
        max-height: 100%;
        width: auto;
        height: auto;
        object-fit: contain;
        border-radius: 6px;
        box-shadow: 0 8px 30px rgba(0,0,0,0.8);
        border: 2px solid #1e3a5f;
    }}
    .player-footer {{
        height: 72px;
        background: #0f2d4f;
        border-top: 2px solid #38bdf8;
        display: flex;
        flex-direction: column;
        justify-content: center;
        gap: 6px;
        padding: 6px 20px;
        flex-shrink: 0;
    }}
    .controls-row {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 16px;
    }}
    .btn-group {{ display: flex; gap: 8px; align-items: center; }}
    .btn {{
        background: #0284c7;
        color: white;
        border: 1px solid #38bdf8;
        padding: 6px 14px;
        border-radius: 5px;
        font-weight: 700;
        cursor: pointer;
        font-size: 13px;
        transition: background 0.2s;
    }}
    .btn:hover {{ background: #0369a1; }}
    .btn:disabled {{ opacity: 0.4; cursor: not-allowed; }}
    .btn-play {{ background: #059669; border-color: #34d399; font-size: 14px; padding: 6px 20px; }}
    .btn-play:hover {{ background: #047857; }}
    .slide-indicator {{
        font-family: monospace;
        font-size: 14px;
        font-weight: bold;
        color: #7dd3fc;
    }}
    .narration-display {{
        color: #e0f2fe;
        font-size: 13px;
        line-height: 1.35;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        flex: 1;
        max-width: 800px;
        background: rgba(6, 21, 36, 0.7);
        padding: 4px 10px;
        border-radius: 4px;
        border-left: 3px solid #38bdf8;
    }}
    .progress-bar-container {{
        width: 100%;
        height: 5px;
        background: #1e3a5f;
        border-radius: 3px;
        overflow: hidden;
        cursor: pointer;
    }}
    .progress-bar {{
        height: 100%;
        width: 0%;
        background: #38bdf8;
        transition: width 0.1s linear;
    }}
</style>
</head>
<body>
    <div class="player-header">
        <div class="player-title">
            <span>JRFK 64-Bit Modernization Suite • Auto-Advancing Technical Player</span>
            <span class="player-callsign">K7BIT</span>
        </div>
        <div class="slide-indicator" id="slideIndicator">Slide 1 of 20</div>
    </div>

    <div class="player-main">
        <div class="slide-viewport">
            <img id="currentSlideImg" class="slide-img" src="slide_01.png" alt="Current Slide">
        </div>
    </div>

    <div class="player-footer">
        <div class="progress-bar-container" id="progressBarContainer">
            <div class="progress-bar" id="progressBar"></div>
        </div>
        <div class="controls-row">
            <div class="btn-group">
                <button class="btn" id="btnPrev">◀ Previous</button>
                <button class="btn btn-play" id="btnPlayPause">▶ Play</button>
                <button class="btn" id="btnNext">Next ▶</button>
                <button class="btn" id="btnRestart">↺ Restart</button>
            </div>
            <div class="narration-display" id="narrationText">Loading presentation...</div>
            <audio id="slideAudio" preload="auto"></audio>
        </div>
    </div>

    <script>
        const slides = {slides_json_str};
        let currentIndex = 0;
        let isPlaying = false;

        const audio = document.getElementById('slideAudio');
        const img = document.getElementById('currentSlideImg');
        const indicator = document.getElementById('slideIndicator');
        const narration = document.getElementById('narrationText');
        const btnPlayPause = document.getElementById('btnPlayPause');
        const btnPrev = document.getElementById('btnPrev');
        const btnNext = document.getElementById('btnNext');
        const btnRestart = document.getElementById('btnRestart');
        const progressBar = document.getElementById('progressBar');

        function loadSlide(index, autoPlay = false) {{
            if (index < 0) index = 0;
            if (index >= slides.length) index = slides.length - 1;
            currentIndex = index;

            const s = slides[currentIndex];
            img.src = s.img;
            audio.src = s.audio;
            indicator.textContent = `Slide ${{s.id}} of ${{slides.length}}: ${{s.title}}`;
            narration.textContent = s.narration;
            progressBar.style.width = '0%';

            btnPrev.disabled = (currentIndex === 0);
            btnNext.disabled = (currentIndex === slides.length - 1);

            if (autoPlay) {{
                audio.play().then(() => {{
                    isPlaying = true;
                    btnPlayPause.textContent = '❚❚ Pause';
                    btnPlayPause.style.background = '#d97706';
                }}).catch(e => console.log('Autoplay deferred:', e));
            }} else {{
                isPlaying = false;
                btnPlayPause.textContent = '▶ Play';
                btnPlayPause.style.background = '#059669';
            }}
        }}

        audio.addEventListener('ended', () => {{
            if (currentIndex < slides.length - 1) {{
                setTimeout(() => {{
                    loadSlide(currentIndex + 1, true);
                }}, 600);
            }} else {{
                isPlaying = false;
                btnPlayPause.textContent = '▶ Play';
                btnPlayPause.style.background = '#059669';
            }}
        }});

        audio.addEventListener('timeupdate', () => {{
            if (audio.duration) {{
                const pct = (audio.currentTime / audio.duration) * 100;
                progressBar.style.width = pct + '%';
            }}
        }});

        btnPlayPause.addEventListener('click', () => {{
            if (isPlaying) {{
                audio.pause();
                isPlaying = false;
                btnPlayPause.textContent = '▶ Resume';
                btnPlayPause.style.background = '#059669';
            }} else {{
                audio.play();
                isPlaying = true;
                btnPlayPause.textContent = '❚❚ Pause';
                btnPlayPause.style.background = '#d97706';
            }}
        }});

        btnPrev.addEventListener('click', () => {{
            if (currentIndex > 0) loadSlide(currentIndex - 1, isPlaying);
        }});

        btnNext.addEventListener('click', () => {{
            if (currentIndex < slides.length - 1) loadSlide(currentIndex + 1, isPlaying);
        }});

        btnRestart.addEventListener('click', () => {{
            loadSlide(0, true);
        }});

        window.addEventListener('keydown', (e) => {{
            if (e.key === ' ' || e.code === 'Space') {{
                e.preventDefault();
                btnPlayPause.click();
            }} else if (e.key === 'ArrowRight') {{
                btnNext.click();
            }} else if (e.key === 'ArrowLeft') {{
                btnPrev.click();
            }}
        }});

        loadSlide(0, false);
    </script>
</body>
</html>"""

with open(os.path.join(DECK_DIR, "preview.html"), "w", encoding="utf-8") as f:
    f.write(player_html)

print("Updated preview.html successfully!")
