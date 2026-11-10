import urllib.request
import base64

code = """flowchart TD
    A --> B
"""
enc = base64.b64encode(code.encode('utf-8')).decode('ascii')
url = f"https://mermaid.ink/img/{enc}"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    resp = urllib.request.urlopen(req, timeout=10)
    data = resp.read()
    print("PNG size:", len(data))
except Exception as e:
    print("Error:", e)
