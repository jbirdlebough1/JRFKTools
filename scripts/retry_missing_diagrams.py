import urllib.request
import base64
import os
import time
import sys

from pathlib import Path
_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT / "scripts"))
from render_diagrams import diagrams, convert_foreign_object_to_native_text

DIAGRAM_DIR = str(_ROOT / "docs" / "images" / "diagrams")
missing = ['lifecycle_stage2_target_sd', 'calibration_phase1', 'calibration_phase2', 'calibration_phase3']

for name in missing:
    code = diagrams[name]
    svg_path = os.path.join(DIAGRAM_DIR, f"{name}.svg")
    encoded = base64.b64encode(code.encode('utf-8')).decode('ascii')
    url = f"https://mermaid.ink/svg/{encoded}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    for attempt in range(5):
        try:
            time.sleep(2)
            with urllib.request.urlopen(req, timeout=15) as resp:
                svg_content = resp.read().decode('utf-8')
                svg_content = convert_foreign_object_to_native_text(svg_content)
                with open(svg_path, 'w', encoding='utf-8') as f:
                    f.write(svg_content)
                print(f"Successfully rendered {name}")
                break
        except Exception as e:
            print(f"Attempt {attempt+1} failed for {name}: {e}")
            time.sleep(3)
