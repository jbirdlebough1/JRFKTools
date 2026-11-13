import urllib.request
import re

url = 'http://192.168.12.193:8088/'
html = urllib.request.urlopen(url).read().decode('utf-8', errors='ignore')

# find all links or iframes or cards
print("Length of index page:", len(html))
links = re.findall(r'href=["\']([^"\']+)["\']', html)
for l in sorted(set(links)):
    print("  Link:", l)

# also search for sections or card titles
cards = re.findall(r'<h[23][^>]*>(.*?)</h[23]>', html)
for c in cards:
    print("  Card heading:", c)
