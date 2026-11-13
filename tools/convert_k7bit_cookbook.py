# tools/convert_k7bit_cookbook.py
"""
Converts the original 'K7BIT B26 Cookbook Vol 1 R1.5.docx' into:
- JRFK_Cookbook.html
- JRFK_Cookbook.pdf
Extracting all 157+ images into 'cookbook_media/', applying classic Blueprint styling,
preserving every page, diagram, schematic, and table without skipping anything.
"""
import os
import shutil
import subprocess
import mammoth

DOCX_PATH = r"D:\JRFK\K7BIT B26 Cookbook Vol 1 R1.5.docx"
DOCS_DIR = r"D:\JRFK\tools\rfk_tools_suite\docs"
DIST_DIR = r"D:\JRFK\docs"
MEDIA_DIR_SRC = os.path.join(DOCS_DIR, "cookbook_media")
MEDIA_DIR_DIST = os.path.join(DIST_DIR, "cookbook_media")
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

os.makedirs(MEDIA_DIR_SRC, exist_ok=True)
os.makedirs(MEDIA_DIR_DIST, exist_ok=True)

image_index = 0

@mammoth.images.img_element
def extract_and_link_image(image):
    global image_index
    image_index += 1
    sub_ext = mammoth.images.image_filename_extension(image)
    if sub_ext:
        ext = f".{sub_ext}"
    else:
        ext = ".png"
    filename = f"img_{image_index:03d}{ext}"
    src_path = os.path.join(MEDIA_DIR_SRC, filename)
    dist_path = os.path.join(MEDIA_DIR_DIST, filename)

    with image.open() as image_bytes:
        data = image_bytes.read()
        with open(src_path, "wb") as f:
            f.write(data)
        with open(dist_path, "wb") as f:
            f.write(data)

    return {
        "src": f"cookbook_media/{filename}",
        "class": "cookbook-img",
        "loading": "lazy"
    }

print(f"Reading {DOCX_PATH}...")
with open(DOCX_PATH, "rb") as docx_file:
    result = mammoth.convert_to_html(docx_file, convert_image=extract_and_link_image)
    raw_body = result.value
    messages = result.messages

print(f"Extracted {image_index} images into cookbook_media/.")
print(f"Raw body HTML size: {len(raw_body):,} characters.")

# Wrap into full publication-grade HTML document
full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>K7BIT B26-RF2K+ Linear Amplifier Master Cookbook (Rev 1.05 Master Edition)</title>
    <style>
        :root {{
            --bp-blue: #1a5695;          /* Classic medium blueprint cyanotype blue */
            --bp-dark: #0f3661;
            --bp-grid: rgba(255, 255, 255, 0.18);
            --bp-border: #93c5fd;
            --bp-cyan: #67e8f9;
            --data-green: #16a34a;
            --data-yellow: #d97706;
            --data-red: #dc2626;
            --text-dark: #1e293b;
            --text-muted: #64748b;
            --bg-light: #f8fafc;
            --card-border: #cbd5e1;
        }}

        * {{
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: var(--bg-light);
            color: var(--text-dark);
            line-height: 1.6;
            margin: 0;
            padding: 0;
        }}

        .cookbook-container {{
            max-width: 1040px;
            margin: 0 auto;
            background: #ffffff;
            padding: 50px 60px;
            box-shadow: 0 4px 25px rgba(0,0,0,0.08);
        }}

        /* Document Publication Header */
        .doc-header-card {{
            border-bottom: 4px solid var(--bp-blue);
            padding-bottom: 25px;
            margin-bottom: 35px;
        }}
        .doc-badge {{
            display: inline-block;
            background: var(--bp-blue);
            color: #ffffff;
            font-family: 'Consolas', monospace;
            font-size: 12px;
            font-weight: bold;
            padding: 4px 10px;
            border-radius: 4px;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 12px;
        }}
        h1 {{
            color: var(--bp-blue);
            font-size: 28px;
            line-height: 1.25;
            margin: 0 0 10px 0;
            font-weight: 800;
        }}
        .doc-subtitle {{
            font-size: 16px;
            color: var(--text-muted);
            margin: 0 0 15px 0;
            font-weight: 500;
        }}
        .meta-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 10px;
            font-size: 12px;
            color: var(--text-muted);
            background: #f1f5f9;
            padding: 12px 16px;
            border-radius: 6px;
            border-left: 4px solid var(--bp-blue);
        }}

        /* Body Typography */
        h2 {{
            color: var(--bp-blue);
            font-size: 22px;
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 8px;
            margin-top: 40px;
            margin-bottom: 15px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        h3 {{
            color: #1e3a8a;
            font-size: 18px;
            margin-top: 30px;
            margin-bottom: 12px;
            border-left: 4px solid var(--bp-blue);
            padding-left: 10px;
        }}
        h4 {{
            color: #0f3661;
            font-size: 15px;
            margin-top: 20px;
            margin-bottom: 8px;
        }}
        p {{
            margin: 0 0 14px 0;
            font-size: 14px;
            line-height: 1.65;
        }}
        ul, ol {{
            margin: 0 0 16px 25px;
            padding: 0;
            font-size: 14px;
            line-height: 1.65;
        }}
        li {{
            margin-bottom: 6px;
        }}

        /* Graphic Image Formatting: Centered, Crisp, Responsive */
        .cookbook-img {{
            max-width: 100%;
            height: auto;
            display: block;
            margin: 20px auto;
            border: 1px solid #cbd5e1;
            border-radius: 4px;
            box-shadow: 0 3px 12px rgba(0,0,0,0.1);
            background: #ffffff;
            image-rendering: -webkit-optimize-contrast;
        }}

        /* Tables */
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0 30px 0;
            font-size: 13px;
        }}
        th, td {{
            border: 1px solid #cbd5e1;
            padding: 10px 12px;
            text-align: left;
            vertical-align: top;
        }}
        th {{
            background: #f1f5f9;
            color: var(--bp-blue);
            font-weight: 700;
        }}
        tr:nth-child(even) {{
            background: #f8fafc;
        }}

        /* Print Media Styles: No Skipped Pages, Clean Page Breaks */
        @media print {{
            body {{
                background: #ffffff !important;
            }}
            .cookbook-container {{
                padding: 0 !important;
                margin: 0 !important;
                max-width: 100% !important;
                box-shadow: none !important;
                width: 100% !important;
            }}
            h1, h2, h3 {{
                page-break-after: avoid;
            }}
            .cookbook-img {{
                max-width: 95% !important;
                page-break-inside: avoid;
            }}
            table, tr, td {{
                page-break-inside: avoid;
            }}
        }}
    </style>
</head>
<body>

<div class="cookbook-container">

    <!-- Official Publication Header -->
    <div class="doc-header-card">
        <span class="doc-badge">AUTHENTIC MASTER PUBLICATION</span>
        <h1>K7BIT B26-RF2K+ Linear Amplifier Master Cookbook</h1>
        <div class="doc-subtitle">The End to End Builders, Alignment &amp; Operators Guide (Revision 1.05 Master Edition)</div>
        <div class="meta-grid">
            <div><strong>Document ID:</strong> K7BIT-B26-COOKBOOK-R1.05</div>
            <div><strong>Principal Author:</strong> John Birdlebough (K7BIT/AE)</div>
            <div><strong>Co-Author:</strong> John Stafford (Island RF CEO, US Service Center)</div>
            <div><strong>Community Collaboration:</strong> RF-KIT Authors &amp; Group.IO Community</div>
        </div>
    </div>

    <!-- Original Document Body -->
    <div class="cookbook-body">
{raw_body}
    </div>

</div>

</body>
</html>
"""

html_out_src = os.path.join(DOCS_DIR, "JRFK_Cookbook.html")
html_out_dist = os.path.join(DIST_DIR, "JRFK_Cookbook.html")

with open(html_out_src, "w", encoding="utf-8") as f:
    f.write(full_html)
with open(html_out_dist, "w", encoding="utf-8") as f:
    f.write(full_html)

print(f"Written JRFK_Cookbook.html to {html_out_src} ({os.path.getsize(html_out_src):,} bytes)")

# Now compile with Chrome to PDF
pdf_out_src = os.path.join(DOCS_DIR, "JRFK_Cookbook.pdf")
pdf_out_dist = os.path.join(DIST_DIR, "JRFK_Cookbook.pdf")

print("Compiling PDF with headless Chrome (full original document)...")
cmd = [
    CHROME,
    "--headless",
    "--disable-gpu",
    "--no-pdf-header-footer",
    f"--print-to-pdf={pdf_out_src}",
    html_out_src
]
proc = subprocess.run(cmd, capture_output=True, text=True)

if os.path.exists(pdf_out_src):
    shutil.copy2(pdf_out_src, pdf_out_dist)
    print(f"[SUCCESS] JRFK_Cookbook.pdf compiled: {os.path.getsize(pdf_out_src):,} bytes")
else:
    print(f"[ERROR] Failed to compile PDF: {proc.stderr}")
