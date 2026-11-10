import re

with open('/mnt/d/JRFK/docs/images/diagrams/arch_migration.svg', 'r', encoding='utf-8') as f:
    svg = f.read()

def convert_foreign_object_to_text(match):
    w = float(match.group(1))
    h = float(match.group(2))
    inner = match.group(3)
    
    # Extract line breaks or text blocks
    # Replace <br/>, <br>, </p><p> with \n
    s = re.sub(r'</p>\s*<p>', '\n', inner)
    s = re.sub(r'<br\s*/?>', '\n', s)
    # Strip remaining HTML tags
    s = re.sub(r'<[^>]+>', '', s)
    lines = [line.strip() for line in s.split('\n') if line.strip()]
    
    if not lines:
        return ""
    
    cx = w / 2.0
    # Calculate baseline
    font_size = 11.5
    line_height = 14.0
    total_text_h = len(lines) * line_height
    start_y = (h - total_text_h) / 2.0 + (font_size * 0.8)
    
    tspans = []
    for idx, line in enumerate(lines):
        y_pos = start_y + (idx * line_height)
        # Escape XML entities
        esc_line = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        tspans.append(f'<tspan x="{cx:.1f}" y="{y_pos:.1f}">{esc_line}</tspan>')
    
    return f'<text x="{cx:.1f}" text-anchor="middle" font-family="-apple-system, BlinkMacSystemFont, \'Segoe UI\', Roboto, \'Helvetica Neue\', Arial, sans-serif" font-size="{font_size}px" font-weight="600" fill="#1a202c">{"".join(tspans)}</text>'

cleaned_svg = re.sub(r'<foreignObject[^>]*width="([^"]+)"[^>]*height="([^"]+)"[^>]*>(.*?)</foreignObject>', convert_foreign_object_to_text, svg, flags=re.DOTALL)

with open('/mnt/d/JRFK/scripts/cleaned_arch.svg', 'w', encoding='utf-8') as f:
    f.write(cleaned_svg)

print("Cleaned SVG saved. Checking for text tags:", "<text" in cleaned_svg)
