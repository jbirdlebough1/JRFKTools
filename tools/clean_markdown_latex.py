#!/usr/bin/env python3
"""
clean_markdown_latex.py
Purges raw LaTeX math delimiters ($ and $$), \text{...}, \mu, \Omega, etc.,
converting them into clean, universally readable Markdown with standard Unicode.
"""

import re
import sys

def clean_content(content):
    # First, handle display blocks $$ ... $$
    def replace_block(match):
        inner = match.group(1).strip()
        cleaned = clean_inner(inner)
        return cleaned

    content = re.sub(r'\$\$(.*?)\$\$', replace_block, content, flags=re.DOTALL)

    # Next, handle inline math $ ... $ (ensuring not literal escaped \$)
    def replace_inline(match):
        inner = match.group(1).strip()
        # Avoid replacing things that look like shell variables or empty
        if not inner or inner.startswith('/') or inner.startswith('env:'):
            return match.group(0)
        cleaned = clean_inner(inner)
        return cleaned

    # Match $...$ where neither end has another $ and does not cross double newlines
    content = re.sub(r'(?<!\\)\$([^\$\n]+?)(?<!\\)\$', replace_inline, content)

    # Clean any leftover unrendered fragments
    content = content.replace(r'^\circ\text{C}', '°C')
    content = content.replace(r'^\circ C', '°C')
    content = content.replace(r'^\circ', '°')
    content = content.replace(r'\text{', '')
    content = content.replace(r'\mu s', 'µs')
    content = content.replace(r'\mu H', 'µH')
    content = content.replace(r'\mu A', 'µA')
    content = content.replace(r'\mu', 'µ')
    content = content.replace(r'\Omega', 'Ω')
    content = content.replace(r'\approx', '≈')
    content = content.replace(r'\le', '≤')
    content = content.replace(r'\ge', '≥')
    content = content.replace(r'\times', '×')
    content = content.replace(r'\rightarrow', '→')
    content = content.replace(r'\equiv', '≡')
    content = content.replace(r'\pm', '±')

    return content

def clean_inner(s):
    # Remove \text{...}
    s = re.sub(r'\\text\{([^}]*)\}', r'\1', s)

    # Temperatures
    s = re.sub(r'\^\\circ\s*C?', '°C', s)
    s = s.replace('°C C', '°C')

    # Greek and mathematical symbols
    s = s.replace(r'\mu\text{s}', 'µs').replace(r'\mu s', 'µs').replace(r'\mu\text{H}', 'µH').replace(r'\mu H', 'µH')
    s = s.replace(r'\mu\text{A}', 'µA').replace(r'\mu A', 'µA').replace(r'\mu', 'µ')
    s = s.replace(r'\Omega', 'Ω')
    s = s.replace(r'\approx', '≈')
    s = s.replace(r'\le', '≤').replace(r'\ge', '≥')
    s = s.replace(r'\times', '×')
    s = s.replace(r'\rightarrow', '→')
    s = s.replace(r'\equiv', '≡')
    s = s.replace(r'\pm', '±')
    s = s.replace(r'\,', ' ').replace(r'\ ', ' ')

    # Fractions \frac{A}{B}
    s = re.sub(r'\\frac\{([^}]*)\}\{([^}]*)\}', r'(\1) / (\2)', s)

    # Square roots \sqrt{X}
    s = re.sub(r'\\sqrt\{([^}]*)\}', r'sqrt(\1)', s)

    # Subscripts like P_{fwd} -> Pfwd, C_{in} -> Cin, R_1 -> R1
    s = s.replace(r'C_{in}', 'Cin').replace(r'C_{out}', 'Cout')
    s = s.replace(r'P_{fwd}', 'Pfwd').replace(r'P_{ref}', 'Pref')
    s = s.replace(r'I_{dq}', 'Idq')
    s = s.replace(r'f_c', 'fc')
    s = re.sub(r'([A-Za-z]+)_\{([A-Za-z0-9]+)\}', r'\1_\2', s)
    s = re.sub(r'([A-Za-z]+)_([0-9]+)', r'\1\2', s)

    # Powers like 10^{14} -> 10^14, x^2 -> x²
    s = s.replace('^{14}', '^14').replace('^{10}', '^10').replace('^2', '²')

    # Remove extra spaces
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def process_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        orig = f.read()

    cleaned = clean_content(orig)
    if cleaned != orig:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(cleaned)
        print(f"[+] Cleaned LaTeX from: {path}")
    else:
        print(f"[-] No changes needed for: {path}")

if __name__ == '__main__':
    for p in sys.argv[1:]:
        process_file(p)
