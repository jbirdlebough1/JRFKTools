import re

MD_PATH = "/mnt/d/JRFK/docs/JRFK_EM.md"
README_PATH = "/mnt/d/JRFK/README.md"

def clean_latex(content):
    # Common mathematical substitutions
    replacements = [
        (r'\$120\\text\{\s*W\}\$', '120 W'),
        (r'\$140\\text\{\s*W\}\$', '140 W'),
        (r'\$500\\\s*\\mu\\text\{s\}\$', '500 µs'),
        (r'\$1\.5\\text\{\s*ms\}\$', '1.5 ms'),
        (r'\$53\.5\\text\{\s*VDC\}\s*@\s*55\\text\{\s*A\}\$', '53.5 VDC @ 55 A'),
        (r'\$53\.5\\,\text\{VDC\}\s*@\s*55\\,\text\{A\}\$', '53.5 VDC @ 55 A'),
        (r'\\frac\{1 \+ \\sqrt\{P_\{ref\}/P_\{fwd\}\}\}\{1 - \\sqrt\{P_\{ref\}/P_\{fwd\}\}\}', '(1 + √(Pref/Pfwd)) / (1 - √(Pref/Pfwd))'),
        (r'\\Omega', 'Ω'),
        (r'\\mu\s*s', 'µs'),
        (r'\\mu\s*H', 'µH'),
        (r'\\mu\s*A', 'µA'),
        (r'\\mu_i', 'µi'),
        (r'\\mu_r', 'µr'),
        (r'\\approx', '≈'),
        (r'\\pm', '±'),
        (r'\\le', '≤'),
        (r'\\ge', '≥'),
        (r'\\times', '×'),
        (r'\\circ', '°'),
        (r'\^\\circ', '°'),
        (r'\\text\{\s*MHz\s*\}', 'MHz'),
        (r'\\text\{\s*kHz\s*\}', 'kHz'),
        (r'\\text\{\s*Hz\s*\}', 'Hz'),
        (r'\\text\{\s*VDC\s*\}', 'VDC'),
        (r'\\text\{\s*VAC\s*\}', 'VAC'),
        (r'\\text\{\s*V\s*\}', 'V'),
        (r'\\text\{\s*W\s*\}', 'W'),
        (r'\\text\{\s*A\s*\}', 'A'),
        (r'\\text\{\s*mA\s*\}', 'mA'),
        (r'\\text\{\s*pF\s*\}', 'pF'),
        (r'\\text\{\s*ns\s*\}', 'ns'),
        (r'\\text\{\s*ms\s*\}', 'ms'),
        (r'\\text\{\s*dB\s*\}', 'dB'),
        (r'\\text\{\s*dBc\s*\}', 'dBc'),
        (r'\\text\{\s*T\s*\}', 'T'),
        (r'\\text\{\s*s\s*\}', 's'),
        (r'\\text\{\s*C\s*\}', 'C'),
        (r'\\text\{\s*K/W\s*\}', 'K/W'),
        (r'\\text\{\s*ppm/\\text\{°\}C\s*\}', 'ppm/°C'),
        (r'\\text\{\s*ppm/°C\s*\}', 'ppm/°C'),
        (r'\\text\{\s*Kbit\s*\}', 'Kbit'),
        (r'\\text\{\s*K\s*\}', 'K'),
        (r'\\text\{\s*I2C\s*\}', 'I2C'),
        (r'\\text\{\s*kbps\s*\}', 'kbps'),
        (r'\\text\{\s*10-year\s*\}', '10-year'),
        (r'\\text\{([^}]+)\}', r'\1'),
    ]
    
    s = content
    for pattern, repl in replacements:
        s = re.sub(pattern, repl, s)
        
    # Generic cleanup of $...$ remaining
    def dollar_cleaner(match):
        inner = match.group(1)
        # Remove remaining \text{...}
        clean = re.sub(r'\\text\{([^}]+)\}', r'\1', inner)
        clean = clean.replace('\\,', ' ').replace('\\ ', ' ').replace('\\', '')
        clean = clean.replace('^', '')
        return clean.strip()

    s = re.sub(r'\$([^\$]+)\$', dollar_cleaner, s)
    return s

for path in [MD_PATH, README_PATH]:
    with open(path, 'r', encoding='utf-8') as f:
        c = f.read()
    cleaned = clean_latex(c)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(cleaned)
    print(f"Cleaned LaTeX from {path}")
