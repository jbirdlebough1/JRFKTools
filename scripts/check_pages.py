import pypdf
import sys

# Ensure utf-8 output
sys.stdout.reconfigure(encoding='utf-8')

reader = pypdf.PdfReader(r'D:\JRFK\docs\JRFK_EM.pdf')
print(f"Total Pages: {len(reader.pages)}")
for i, page in enumerate(reader.pages):
    txt = page.extract_text().strip()
    first = txt.split('\n')[0] if txt else 'EMPTY'
    print(f"Page {i+1:02d}: {len(txt):4d} chars | {first[:55]}")
