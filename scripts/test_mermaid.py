import urllib.request
import json
import base64

payload = {
    "code": """flowchart TD
    A["Hello World"] --> B["Second Line"]
""",
    "mermaid": {
        "flowchart": {
            "htmlLabels": False
        }
    }
}

json_str = json.dumps(payload)
enc = base64.b64encode(json_str.encode('utf-8')).decode('ascii')
url = f"https://mermaid.ink/svg/{enc}"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    resp = urllib.request.urlopen(req, timeout=10)
    svg = resp.read().decode('utf-8')
    print("Has foreignObject:", "foreignObject" in svg)
    print("Has text element:", "<text" in svg)
    # Print some text elements
    for line in svg.splitlines():
        if "<text" in line or "<tspan" in line:
            print("LINE:", line[:120])
except Exception as e:
    print("Error:", e)
