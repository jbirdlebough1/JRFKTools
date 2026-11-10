import urllib.request
import base64

code = """flowchart TD
    A["Hello World"] --> B["Second Line"]
"""
enc = base64.b64encode(code.encode('utf-8')).decode('ascii')
url = f"https://mermaid.ink/img/{enc}?bgColor=!white"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    resp = urllib.request.urlopen(req, timeout=10)
    data = resp.read()
    print("PNG Length:", len(data))
    print("Header:", data[:8])
    with open("/mnt/d/JRFK/scripts/test.png", "wb") as f:
        f.write(data)
    print("Saved test.png")
except Exception as e:
    print("Error:", e)
