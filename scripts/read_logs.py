import urllib.request
import json

resp = urllib.request.urlopen("http://127.0.0.1:8089/api/logs")
d = json.loads(resp.read().decode())
print(f"Total log entries: {len(d['logs'])}")
for x in d['logs'][-50:]:
    print(f"[{x.get('time','')}] {x.get('message','')}")
