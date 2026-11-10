import os
import re
import subprocess

MD_PATH = "/mnt/d/JRFK/docs/JRFK_EM.md"
HTML_PATH = "/mnt/d/JRFK/docs/JRFK_EM.html"
PDF_PATH = "/mnt/d/JRFK/docs/JRFK_EM.pdf"
DIAGRAM_DIR = "/mnt/d/JRFK/docs/images/diagrams"

with open(MD_PATH, 'r', encoding='utf-8') as f:
    md_content = f.read()

# Map mermaid diagram blocks to rendered clean SVGs
diagram_map = {
    "Legacy 32-bit Architecture": "arch_migration.svg",
    "Phase 1: Golden Master Extraction": "lifecycle_sequence.svg",
    "Controller MCU (USB)": "hardware_parity.svg",
    "Operator Initiates": "update_pipeline.svg",
    "Active Internal": "backup_flow.svg",
    "Telemetry & Data Plane": "diagnostics_arch.svg",
    "SimpleRPC: get_all_values()": "controller_comm_flow.svg",
    "RFK Tools Web UI (:8088/backup)": "backup_restore_sequence.svg",

    # Staging Panels (Chapter 17)
    "Insert Original SD into USB Card Reader": "lifecycle_stage1_extract.svg",
    "Insert New 32GB High-Endurance SD Card": "lifecycle_stage2_target_sd.svg",
    "Boot 1 Initial Hardware Discovery": "lifecycle_stage3_boot1.svg",
    "Launch RFKGUI via Pure KMS": "lifecycle_stage4_boot2.svg",

    # Calibration Panels (Chapter 9)
    "Phase 1: Bench Safety & DC Setup": "calibration_phase1.svg",
    "Phase 2: Frequency & Filter Integration": "calibration_phase2.svg",
    "Phase 3: SWR Bridge & RF Power Alignment": "calibration_phase3.svg",
    "Phase 4: Protection Trips & PA Reassembly": "calibration_phase4.svg",

    # RF Signal Chain Panels (Chapter 7)
    "Chassis Step Attenuator": "rf_stage1_input.svg",
    "Push-Pull Ampleon BLF189XR": "rf_stage2_pallet.svg",
    "Toroidal Low-Pass Filter": "rf_stage3_lpf_swr.svg",
    "High-Speed Vacuum / PIN T/R Relay": "rf_stage4_output.svg"
}

html_body = []
lines = md_content.split('\n')
in_code = False
code_lang = ""
code_buffer = []

def md_to_basic_html(text):
    t = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    t = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', t)
    t = re.sub(r'\*(.*?)\*', r'<em>\1</em>', t)
    t = re.sub(r'`(.*?)`', r'<code>\1</code>', t)
    return t

i = 0
in_table = False
in_blockquote = False
blockquote_buffer = []

while i < len(lines):
    line = lines[i]
    if line.startswith('```'):
        if not in_code:
            in_code = True
            code_lang = line.replace('```', '').strip()
            code_buffer = []
        else:
            in_code = False
            code_text = '\n'.join(code_buffer)
            if code_lang == 'mermaid':
                matched_svg = None
                for key, svg_file in diagram_map.items():
                    if key in code_text:
                        matched_svg = svg_file
                        break
                
                if matched_svg and os.path.exists(os.path.join(DIAGRAM_DIR, matched_svg)):
                    with open(os.path.join(DIAGRAM_DIR, matched_svg), 'r', encoding='utf-8') as svg_f:
                        raw_svg = svg_f.read()
                    html_body.append(f'<div class="diagram-wrapper">{raw_svg}</div>')
                else:
                    html_body.append(f'<pre class="code-block"><code>{md_to_basic_html(code_text)}</code></pre>')
            else:
                html_body.append(f'<pre class="code-block"><code>{md_to_basic_html(code_text)}</code></pre>')
        i += 1
        continue

    if in_code:
        code_buffer.append(line)
        i += 1
        continue

    # Blockquotes / Callout handling
    if line.startswith('> '):
        blockquote_buffer.append(line[2:])
        in_blockquote = True
        i += 1
        continue
    else:
        if in_blockquote:
            in_blockquote = False
            bq_text = '\n'.join(blockquote_buffer)
            blockquote_buffer = []
            
            bq_class = "callout-info"
            if "[!CAUTION]" in bq_text:
                bq_class = "callout-caution"
                bq_text = bq_text.replace("[!CAUTION]", "")
            elif "[!IMPORTANT]" in bq_text:
                bq_class = "callout-important"
                bq_text = bq_text.replace("[!IMPORTANT]", "")
            
            bq_html_lines = []
            for bql in bq_text.strip().split('\n'):
                if bql.startswith('### '):
                    bq_html_lines.append(f'<h4 class="callout-title">{md_to_basic_html(bql[4:])}</h4>')
                elif bql.startswith('* ') or bql.startswith('- '):
                    bq_html_lines.append(f'<li>{md_to_basic_html(bql[2:])}</li>')
                elif bql.startswith('1. ') or bql.startswith('2. ') or bql.startswith('3. '):
                    bq_html_lines.append(f'<p class="num-item">{md_to_basic_html(bql)}</p>')
                elif bql.strip() == '':
                    pass
                else:
                    bq_html_lines.append(f'<p>{md_to_basic_html(bql)}</p>')
            
            html_body.append(f'<div class="callout {bq_class}">{"".join(bq_html_lines)}</div>')

    # Markdown Table Handling
    if line.strip().startswith('|') and line.strip().endswith('|'):
        cols = [c.strip() for c in line.strip()[1:-1].split('|')]
        # Check if separator
        if all(re.match(r'^:?-+:?$', c) for c in cols):
            i += 1
            continue
        if not in_table:
            in_table = True
            html_body.append('<table class="doc-table"><thead><tr>')
            for col in cols:
                html_body.append(f'<th>{md_to_basic_html(col)}</th>')
            html_body.append('</tr></thead><tbody>')
        else:
            html_body.append('<tr>')
            for col in cols:
                html_body.append(f'<td>{md_to_basic_html(col)}</td>')
            html_body.append('</tr>')
        i += 1
        continue
    else:
        if in_table:
            in_table = False
            html_body.append('</tbody></table>')

    if line.startswith('# '):
        html_body.append(f'<h1>{md_to_basic_html(line[2:])}</h1>')
    elif line.startswith('## '):
        html_body.append(f'<h2>{md_to_basic_html(line[3:])}</h2>')
    elif line.startswith('### '):
        html_body.append(f'<h3>{md_to_basic_html(line[4:])}</h3>')
    elif line.startswith('* ') or line.startswith('- '):
        html_body.append(f'<li>{md_to_basic_html(line[2:])}</li>')
    elif line.startswith('---'):
        # Skip <hr/> before <h1> to prevent empty page creations
        pass
    elif line.strip() == '':
        html_body.append('<div class="spacer"></div>')
    else:
        html_body.append(f'<p>{md_to_basic_html(line)}</p>')
    i += 1

if in_table:
    html_body.append('</tbody></table>')

full_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>RFK2K+ / RFK2K-S: 32-Bit to 64-Bit Raspberry Pi OS Migration & Tools Upgrade Manual</title>
<style>
    @page {{
        size: A4 portrait;
        margin: 16mm 14mm 16mm 14mm;
        @bottom-right {{
            content: "Page " counter(page) " of " counter(pages);
            font-size: 8.5pt;
            color: #718096;
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        }}
        @bottom-left {{
            content: "RFK2K+/RFK2K-S 32-bit to 64-bit RPI OS Migration and tools upgrade for RPI4 or RPI5 Manual";
            font-size: 8.5pt;
            color: #718096;
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        }}
    }}
    body {{
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        font-size: 9.5pt;
        line-height: 1.45;
        color: #1a202c;
    }}
    p, li {{
        orphans: 3;
        widows: 3;
    }}
    h1 {{
        color: #1a365d;
        border-bottom: 2.5px solid #2b6cb0;
        padding-bottom: 4px;
        font-size: 17pt;
        margin-top: 14pt;
        margin-bottom: 10pt;
        page-break-before: always;
        page-break-after: avoid;
        break-after: avoid;
    }}
    h1:first-of-type {{
        page-break-before: avoid;
        margin-top: 0;
    }}
    h2 {{
        color: #2b6cb0;
        border-bottom: 1.5px solid #cbd5e0;
        padding-bottom: 3px;
        font-size: 13pt;
        margin-top: 14pt;
        margin-bottom: 8pt;
        page-break-after: avoid;
        break-after: avoid;
    }}
    h3 {{
        color: #2d3748;
        font-size: 10.5pt;
        margin-top: 10pt;
        margin-bottom: 6pt;
        page-break-after: avoid;
        break-after: avoid;
    }}
    h4 {{
        page-break-after: avoid;
        break-after: avoid;
    }}
    .callout {{
        border-radius: 4px;
        padding: 8pt 12pt;
        margin: 10pt 0;
        font-size: 9pt;
        page-break-inside: avoid;
    }}
    .callout p {{
        margin: 4pt 0;
    }}
    .callout-title {{
        margin: 0 0 4pt 0;
        font-size: 10.5pt;
    }}
    .callout-info {{
        background: #ebf8ff;
        border-left: 4px solid #3182ce;
        color: #2b6cb0;
    }}
    .callout-caution {{
        background: #fff5f5;
        border-left: 4px solid #e53e3e;
        color: #9b2c2c;
    }}
    .callout-caution strong {{
        color: #c53030;
    }}
    .callout-important {{
        background: #f7fafc;
        border-left: 4px solid #4a5568;
        color: #2d3748;
    }}
    .callout-important h4 {{
        color: #1a202c;
    }}
    .code-block {{
        background: #f7fafc;
        border: 1px solid #e2e8f0;
        border-radius: 4px;
        padding: 7pt;
        font-family: 'Courier New', Courier, monospace;
        font-size: 8pt;
        overflow: hidden;
        page-break-inside: avoid;
    }}
    .diagram-wrapper {{
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 6px;
        padding: 6pt;
        margin: 8pt auto;
        text-align: center;
        page-break-inside: avoid;
    }}
    .diagram-wrapper svg {{
        max-width: 98%;
        height: auto;
        max-height: 120mm;
    }}
    .doc-table {{
        width: 100%;
        border-collapse: collapse;
        margin: 10pt 0;
        font-size: 8pt;
        page-break-inside: auto;
    }}
    .doc-table th {{
        background: #2b6cb0;
        color: white;
        text-align: left;
        padding: 4.5pt 5.5pt;
        border: 1px solid #2b6cb0;
        font-weight: 600;
    }}
    .doc-table td {{
        padding: 4pt 5.5pt;
        border: 1px solid #e2e8f0;
        vertical-align: top;
    }}
    .doc-table tr:nth-child(even) td {{
        background: #f7fafc;
    }}
    .doc-table tr {{
        page-break-inside: avoid;
    }}
    code {{
        background: #edf2f7;
        padding: 1pt 3pt;
        border-radius: 3px;
        font-family: monospace;
        font-size: 8pt;
        color: #805ad5;
    }}
    li {{
        margin-bottom: 3pt;
    }}
    .spacer {{
        height: 2pt;
    }}
</style>
</head>
<body>
{''.join(html_body)}
</body>
</html>
"""

with open(HTML_PATH, 'w', encoding='utf-8') as f:
    f.write(full_html)
print(f"HTML written to {HTML_PATH}")

subprocess.run(["weasyprint", HTML_PATH, PDF_PATH], check=True)
print(f"SUCCESS: Publication PDF generated at {PDF_PATH}")
