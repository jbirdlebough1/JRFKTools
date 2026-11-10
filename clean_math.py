import re

with open('D:/JRFK/docs/JRFK_EM.md', 'r', encoding='utf-8') as f:
    text = f.read()

# Exact targeted replacements for inline math formulas:
replacements = {
    r'$V_{(BR)DSS}$': 'V_(BR)DSS',
    r'$I_D$': 'I_D',
    r'$V_{GS} = 1.8\text{ V to } 2.6\text{ V}$': 'V_GS = 1.8 V to 2.6 V',
    r'$I_{DQ}$': 'Idq',
    r'$T_1$': 'T1',
    r'$T_2$': 'T2',
    r'$V_{DS} = 50\text{V}$, $P_{OUT} = 1500–1700\text{W}$': 'V_DS = 50V, P_OUT = 1500–1700W',
    r'$V_{(BR)DSS} = 135\text{V}$, $I_D = 40\text{A}$, $R_{th} = 0.15\text{ K/W}$, SWR > 65:1.': 'V_(BR)DSS = 135V, I_D = 40A, R_th = 0.15 K/W, SWR > 65:1.',
    r'Clamp Voltage $V_C = 13.6\text{V} @ 100\text{A}$': 'Clamp Voltage V_C = 13.6V @ 100A',
    r'$\mu_i = 800$, Initial Permeability': 'μ_i = 800, Initial Permeability',
    r'$V_{BR} = 70\text{V}$, $C_t = 2.0\text{pF}$, $t_{rr} < 100\text{ ps}$': 'V_BR = 70V, C_t = 2.0 pF, t_rr < 100 ps',
    r'Forward drop $V_f \approx 0.38\text{V} @ 1\text{mA}$.': 'Forward drop V_f ≈ 0.38V @ 1mA.',
    r'$\mu_r = 10$, Temp Coeff +95 ppm/°C': 'μ_r = 10, Temp Coeff +95 ppm/°C',
    r'$\mu_r = 8.5$, Temp Coeff +35 ppm/°C': 'μ_r = 8.5, Temp Coeff +35 ppm/°C',
    r'($B_{sat} > 1.0\text{ T}$)': '(B_sat > 1.0 T)',
    r'$10^{14}$': '10¹⁴',
    r'($L_1–L_8$)': '(L1–L8)',
    r'($C_1–C_8$)': '(C1–C8)',
}

count = 0
for k, v in replacements.items():
    if k in text:
        text = text.replace(k, v)
        count += 1
    else:
        print(f"Warning: pattern not found: {k}")

with open('D:/JRFK/docs/JRFK_EM.md', 'w', encoding='utf-8') as f:
    f.write(text)

print(f"Replaced {count} math patterns cleanly.")
