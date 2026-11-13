# tools/generate_docs.py
"""
Generates the complete JRFK Documentation Suite:
- JRFK_Users_Guide.html & .pdf
- JRFK_EM.html & .pdf
- JRFK_Cookbook.html & .pdf
- JRFK_Disaster_Recovery.html & .pdf
- docs_viewer.html
"""
import os
import re
import subprocess
import shutil

DOCS_DIR = r"D:\JRFK\tools\rfk_tools_suite\docs"
DIST_DIR = r"D:\JRFK\docs"
STATIC_DIR = r"D:\JRFK\tools\rfk_tools_suite\static"
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

def build_users_guide():
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RF-KIT Linear Amplifier: 32-Bit to 64-Bit OS Migration, Disaster Recovery & Operator's Guide</title>
    <style>
        :root {
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
        }

        * {
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: var(--bg-light);
            color: var(--text-dark);
            line-height: 1.6;
            margin: 0;
            padding: 0;
        }

        .manual-container {
            max-width: 980px;
            margin: 0 auto;
            background: #ffffff;
            padding: 45px 55px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.06);
        }

        /* Publication Cover Header */
        .cover-header {
            border-bottom: 4px solid var(--bp-blue);
            padding-bottom: 25px;
            margin-bottom: 25px;
        }
        .doc-badge {
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
        }
        h1 {
            color: var(--bp-blue);
            font-size: 28px;
            line-height: 1.25;
            margin: 0 0 10px 0;
            font-weight: 800;
        }
        .subtitle {
            font-size: 16px;
            color: var(--text-muted);
            margin: 0 0 15px 0;
            font-weight: 500;
        }
        .meta-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 10px;
            font-size: 12px;
            color: var(--text-muted);
            background: #f1f5f9;
            padding: 12px 16px;
            border-radius: 6px;
            border-left: 4px solid var(--bp-blue);
        }

        /* Front Matter: Quick Web Access */
        .front-matter-banner {
            background: #081d33;
            border: 2px solid var(--bp-blue);
            color: #ffffff;
            padding: 20px 26px;
            border-radius: 6px;
            margin: 25px 0 35px 0;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 20px;
            flex-wrap: wrap;
        }
        .front-matter-text h3 {
            color: var(--bp-cyan);
            margin: 0 0 6px 0;
            font-size: 18px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .front-matter-text p {
            margin: 0;
            font-size: 13.5px;
            color: #dbeafe;
            line-height: 1.5;
        }
        .url-pill {
            background: #1e3a8a;
            border: 1px solid var(--bp-cyan);
            color: #ffffff;
            font-family: 'Consolas', monospace;
            font-size: 17px;
            font-weight: bold;
            padding: 10px 20px;
            border-radius: 4px;
            white-space: nowrap;
            box-shadow: 0 0 12px rgba(103, 232, 249, 0.3);
        }

        /* Section Headings */
        h2 {
            color: var(--bp-blue);
            font-size: 20px;
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 8px;
            margin-top: 40px;
            margin-bottom: 15px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        h2 .sec-num {
            background: var(--bp-blue);
            color: #ffffff;
            font-size: 13px;
            padding: 2px 8px;
            border-radius: 3px;
            font-family: 'Consolas', monospace;
        }
        h3 {
            color: #1e3a8a;
            font-size: 16px;
            margin-top: 25px;
            margin-bottom: 10px;
        }

        /* Callouts */
        .alert {
            padding: 14px 18px;
            border-radius: 6px;
            margin: 18px 0;
            font-size: 14px;
            line-height: 1.5;
            border-left: 4px solid;
        }
        .alert-info { background: #eff6ff; border-color: #3b82f6; color: #1e40af; }
        .alert-warning { background: #fffbeb; border-color: #f59e0b; color: #92400e; }
        .alert-danger { background: #fef2f2; border-color: #ef4444; color: #991b1b; }
        .alert-success { background: #f0fdf4; border-color: #22c55e; color: #166534; }

        /* Classic Medium-Blue Blueprint Card */
        .blueprint-card {
            background: var(--bp-blue);
            background-image: 
                linear-gradient(var(--bp-grid) 1px, transparent 1px),
                linear-gradient(90deg, var(--bp-grid) 1px, transparent 1px);
            background-size: 18px 18px;
            color: #ffffff;
            border: 2px solid #ffffff;
            padding: 20px;
            border-radius: 6px;
            margin: 20px 0;
            font-family: 'Consolas', 'Courier New', monospace;
            font-size: 13px;
            box-shadow: 0 4px 15px rgba(26, 86, 149, 0.25);
        }
        .blueprint-card .bp-title {
            color: #ffffff;
            font-size: 14px;
            font-weight: bold;
            border-bottom: 1px solid rgba(255, 255, 255, 0.35);
            padding-bottom: 6px;
            margin-bottom: 12px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        /* Step progression blocks */
        .step-block {
            border: 1px solid var(--card-border);
            border-radius: 8px;
            padding: 18px 22px;
            margin-bottom: 20px;
            background: #ffffff;
            box-shadow: 0 2px 6px rgba(0,0,0,0.03);
        }
        .step-block h4 {
            margin: 0 0 10px 0;
            font-size: 15px;
            color: var(--bp-blue);
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .step-badge {
            background: var(--bp-blue);
            color: #ffffff;
            font-size: 11px;
            font-weight: bold;
            padding: 2px 8px;
            border-radius: 3px;
        }

        /* Screen walkthrough feature box */
        .screen-feature-box {
            border: 1px solid #93c5fd;
            border-radius: 6px;
            background: #f0f7ff;
            padding: 16px 20px;
            margin: 15px 0 25px 0;
        }
        .screen-feature-box h4 {
            margin: 0 0 8px 0;
            color: var(--bp-blue);
            font-size: 15px;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        /* Data Tables */
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0 25px 0;
            font-size: 13px;
        }
        th, td {
            border: 1px solid #cbd5e1;
            padding: 9px 12px;
            text-align: left;
        }
        th {
            background: #f1f5f9;
            color: var(--bp-blue);
            font-weight: 700;
        }
        tr:nth-child(even) {
            background: #f8fafc;
        }

        /* Print formatting */
        @media print {
            body { background: #ffffff !important; }
            .manual-container { padding: 0 !important; box-shadow: none !important; width: 100% !important; max-width: 100% !important; }
            h2 { page-break-before: always; }
            h2:first-of-type { page-break-before: avoid; }
            .step-block, .blueprint-card, .screen-feature-box, table, .front-matter-banner { page-break-inside: avoid; }
        }
    </style>
</head>
<body>

<div class="manual-container">

    <!-- Title & Executive Overview -->
    <div class="cover-header">
        <span class="doc-badge">OFFICIAL USER &amp; OPERATOR'S MANUAL</span>
        <h1>RF-KIT Linear Amplifier: 32-Bit to 64-Bit OS Migration, Disaster Recovery &amp; Operator's Guide</h1>
        <div class="subtitle">Turnkey Migration, Golden Master Preservation, Port 8088 Blueprint Suite, 3-Boot Walkthrough, System Report &amp; Automated Patching</div>
        <div class="meta-grid">
            <div><strong>Document ID:</strong> JRFK-UG-2026-V2.1</div>
            <div><strong>Author:</strong> John Birdlebough (K7BIT)</div>
            <div><strong>Target Platforms:</strong> RF-KIT RF2K-S / RF2K+</div>
            <div><strong>Operating System:</strong> 64-Bit Debian Trixie (aarch64)</div>
        </div>
    </div>

    <!-- Front Matter: Quick Web Access & Port 8088 Connection -->
    <div class="front-matter-banner">
        <div class="front-matter-text">
            <h3>🌐 Shack Web Suite: Instant Browser Connection (:8088)</h3>
            <p>Access the 24/7 amplifier diagnostic console from any PC, tablet, or smartphone on your local network:</p>
            <p style="margin-top: 5px; font-size: 12.5px; color: #93c5fd;">Enter your amplifier's IP address or mDNS hostname followed by port <code>:8088</code></p>
        </div>
        <div class="url-pill">http://&lt;amplifier-ip&gt;:8088/</div>
    </div>

    <!-- Section 1: Introduction to JRFK.exe and Dual-Architecture -->
    <h2><span class="sec-num">01</span> System Architecture &amp; Introduction to JRFK.exe</h2>

    <p>The <strong>JRFK 32-to-64-Bit Migration &amp; Diagnostic Suite</strong> provides a comprehensive, zero-risk upgrade path for RF-KIT RF2K-S and RF2K+ linear power amplifiers. Over years of broadcast, DX, and contest operation, legacy 32-bit Raspberry Pi operating systems suffer from lack of upstream security patches, driver deprecation, and slow single-core telemetry polling. JRFK upgrades your amplifier to a high-performance, 64-bit Debian Trixie (<code>aarch64</code>) appliance while guaranteeing <strong>zero data loss</strong> and total preservation of all factory calibrations.</p>

    <h3>The Purpose of JRFK.exe</h3>
    <p><code>JRFK.exe</code> is a dedicated, self-contained Windows utility engineered to safely transition your amplifier storage. It solves three critical operational challenges:</p>
    <ul>
        <li><strong>Golden Master Data Extraction:</strong> Safely mounts the 32-bit ext4 Linux filesystem on Windows in strict read-only mode, validating station callsign, Wi-Fi credentials, ATU relay solutions, and detector null calibration offsets before anything is altered.</li>
        <li><strong>Turnkey 64-Bit Provisioning:</strong> Wipes and partitions target high-endurance MicroSD media, writes the verified ~6.28 GB 64-bit Debian Trixie operating system image, and injects all preserved station parameters into the exact target paths required for plug-and-play operation.</li>
        <li><strong>System Recovery &amp; Cloning:</strong> Provides the software engine to generate redundant field spares, rebuild lost media from scratch, and create verified backups without needing complex Linux commands.</li>
    </ul>

    <h3>The Dual-Architecture Model: Strict PC vs. Amplifier Separation</h3>
    <p>To eliminate operational confusion, the JRFK ecosystem is split into two completely separate, decoupled components that run on different hardware hosts:</p>

    <table>
        <thead>
            <tr>
                <th>Component</th>
                <th>Hardware Host</th>
                <th>Port / Access</th>
                <th>Core Function &amp; Scope</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><strong>PC Migration Utility (<code>JRFK.exe</code>)</strong></td>
                <td>Windows PC (Host)</td>
                <td>Port 8089 (Localhost)</td>
                <td><strong>One-time offline SD card migration.</strong> Reads 32-bit GOLD SD, verifies safety signatures, wipes and partitions target MicroSD, writes the ~6.28 GB 64-bit OS image, stages factory calibrations, Wi-Fi credentials, and sets up turnkey firstboot. Has NO runtime web sub-pages.</td>
            </tr>
            <tr>
                <td><strong>Amplifier Appliance Suite (<code>rfk_tools_suite</code>)</strong></td>
                <td>Raspberry Pi (Inside Amp)</td>
                <td>Port 8088 (LAN)</td>
                <td><strong>24/7 operational station diagnostics.</strong> Natively hosts the Technical Blueprint web interface: Antenna Mapper, Health Monitor with 60°C emergency thermal trip, Remote Screen mirror, automated weekly backups, System Report, and Log Viewer.</td>
            </tr>
        </tbody>
    </table>

    <!-- Section 2: What GOLD Data Migrates to 64-Bit -->
    <h2><span class="sec-num">02</span> The GOLD Migration Matrix: Preserved Calibration Assets</h2>

    <p>When migrating an existing amplifier, <code>JRFK.exe</code> extracts your station parameters directly from your working 32-bit SD card (<strong>GOLD1</strong>) and maps them cleanly into the 64-bit environment:</p>

    <table>
        <thead>
            <tr>
                <th>Calibration / Data Item</th>
                <th>32-Bit Source Location</th>
                <th>64-Bit Destination Target</th>
                <th>Operational Impact &amp; Role</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><strong>RF-KIT GUI Application</strong></td>
                <td><code>/home/pi/rf-kit-gui/</code></td>
                <td><code>/home/pi/rf-kit-gui/</code></td>
                <td>Preserved in full. Patched with 64-bit Python 3.13 shims (Pillow <code>Image.ANTIALIAS</code> shim and Hamlib bindings).</td>
            </tr>
            <tr>
                <td><strong>PA Calibrations &amp; Offsets</strong></td>
                <td><code>/home/pi/rf-kit-statics/calibrations.json</code></td>
                <td><code>/home/pi/rf-kit-statics/calibrations.json</code></td>
                <td>Retains exact detector null voltages (0.042V / 0.038V), frequency scaling, and power meter calibrations.</td>
            </tr>
            <tr>
                <td><strong>Per-Band ATU Tuning Data</strong></td>
                <td><code>/home/pi/PA-Files/</code></td>
                <td><code>/home/pi/PA-Files/</code></td>
                <td>All tuned segment component tables (inductor nH and capacitor pF relay values) across 160m..6m remain intact.</td>
            </tr>
            <tr>
                <td><strong>Antenna Matrix &amp; Custom Names</strong></td>
                <td><code>/home/pi/rf-kit-statics/config.json</code></td>
                <td><code>/home/pi/rf-kit-statics/config.json</code></td>
                <td>Preserves <code>selected_antennas</code> matrix, custom antenna labels (e.g. Dipole, SteppIR, Beam), and auto-tune thresholds.</td>
            </tr>
            <tr>
                <td><strong>Operator Callsign &amp; CAT Rig</strong></td>
                <td><code>/home/pi/rf-kit-statics/config.json</code></td>
                <td><code>/home/pi/rf-kit-statics/config.json</code></td>
                <td>Retains callsign (<code>customDeviceName</code>), transceiver model (ICOM, Yaesu, Kenwood, Elecraft, Flex), baud rates, and UDP port 50001.</td>
            </tr>
            <tr>
                <td><strong>Wi-Fi &amp; Network Configuration</strong></td>
                <td><code>/etc/wpa_supplicant/wpa_supplicant.conf</code></td>
                <td><code>/boot/firmware/wpa_supplicant.conf</code></td>
                <td>Preserves station SSID and PSK so the amplifier auto-associates with your local network on first boot.</td>
            </tr>
            <tr>
                <td><strong>Linux Password &amp; SSH Auth</strong></td>
                <td><code>/etc/shadow</code> (User <code>pi</code>)</td>
                <td><code>/boot/firmware/userconf.txt</code></td>
                <td>Original user password hash extracted and re-injected. Headless OpenSSH enabled out of the box.</td>
            </tr>
            <tr>
                <td><strong>1024x600 Display Drivers</strong></td>
                <td>Legacy <code>/boot/config.txt</code> (fkms)</td>
                <td>Pure KMS <code>/boot/firmware/config.txt</code></td>
                <td>Upgrades legacy firmware KMS to Full KMS DRM pipeline with hardware CVT 1024x600 60Hz timing. Suppresses desktop background.</td>
            </tr>
        </tbody>
    </table>

    <!-- Section 3: Setting Up and Connecting to Port 8088 -->
    <h2><span class="sec-num">03</span> Connecting to the Port 8088 Web Suite</h2>

    <p>The 64-bit appliance runs an embedded, asynchronous Python web server (<code>rfk_tools_suite</code>) listening on TCP port <strong>8088</strong>. This diagnostic console is completely standalone from the RF-KIT touch GUI, allowing simultaneous local touchscreen control and remote browser monitoring.</p>

    <h3>Network Address Resolution</h3>
    <p>To connect from any device in your shack (desktop PC, laptop, iPad, or Android phone):</p>
    <ol>
        <li><strong>By IP Address:</strong> If your router assigns the amplifier IP <code>192.168.1.150</code>, enter:
            <div style="background:#0f2c4d; color:#67e8f9; padding:8px 14px; font-family:Consolas, monospace; border-radius:4px; margin:6px 0;">http://192.168.1.150:8088/</div>
        </li>
        <li><strong>By mDNS Hostname:</strong> The appliance broadcasts its hostname via Zeroconf/Avahi. If your station callsign is configured as <code>k7bit</code>, enter:
            <div style="background:#0f2c4d; color:#67e8f9; padding:8px 14px; font-family:Consolas, monospace; border-radius:4px; margin:6px 0;">http://k7bit.local:8088/</div>
        </li>
    </ol>

    <div class="alert alert-info">
        <strong>Browser Compatibility:</strong> The Port 8088 suite is fully responsive and rendered in classic Blueprint technical styling. It is tested and verified on Google Chrome, Mozilla Firefox, Apple Safari (iOS/macOS), and Microsoft Edge. No browser plugins or extensions are required.
    </div>

    <!-- Section 4: Detailed Walkthrough of All 7 Screens -->
    <h2><span class="sec-num">04</span> Exhaustive Walkthrough of the 7 Blueprint Screens</h2>

    <p>The top navigation header provides instant, one-click access across all seven operational screens. Below is the complete operating guide for each screen:</p>

    <!-- Screen 1: Station Docs -->
    <div class="screen-feature-box">
        <h4>1. 📖 Station Documentation Library (<code>/docs</code>)</h4>
        <p><strong>Purpose:</strong> Serves as the central technical reference repository for the amplifier station, hosting four complete, publication-grade manuals in both interactive HTML and downloadable PDF formats.</p>
        <p><strong>How to Read It:</strong> The screen displays four unified document cards across the top and an embedded high-resolution reading frame below. The active document is highlighted with a green border and labeled in the reader toolbar.</p>
        <p><strong>How to Use It:</strong></p>
        <ul>
            <li>Click <strong>📖 View Document</strong> on any card to load that manual directly into the embedded viewport.</li>
            <li>Click <strong>⬇️ Download PDF</strong> to download or open the print-ready, vectorized PDF file with zero formatting defects.</li>
            <li>Use the toolbar controls: <strong>🔄 Reload</strong> refreshes the document; <strong>🌐 Open Full Window</strong> expands the document into a dedicated browser tab; <strong>🖨️ Print Document</strong> initiates direct local printing formatted cleanly without web navigation elements.</li>
        </ul>
    </div>

    <!-- Screen 2: Antenna Mapper -->
    <div class="screen-feature-box">
        <h4>2. 🗺️ Antenna Matrix Mapper &amp; Tuner Bode Plot (<code>/antenna</code>)</h4>
        <p><strong>Purpose:</strong> Visualizes the amplifier's 4-port coaxial antenna relay matrix, active band selection, and per-band automatic tuner (ATU) LC solutions in real time.</p>
        <p><strong>How to Read It:</strong></p>
        <ul>
            <li><strong>4 Coaxial Port Cards:</strong> Displays <code>ANT 1</code>, <code>ANT 2</code>, <code>ANT 3</code>, and <code>ANT 4</code>. The physically energized RF relay glows in vivid green with <code>● ACTIVE RELAY</code>. Standby ports remain in muted blueprint blue with <code>STANDBY</code>. Custom labels configured in <code>config.json</code> (e.g., "160M INVERTED L", "STEPPIR 20-6M") appear directly on the cards.</li>
            <li><strong>Band Ribbon:</strong> An interactive ribbon displaying all supported amateur bands (160m, 80m, 60m, 40m, 30m, 20m, 17m, 15m, 12m, 10m, 6m).</li>
            <li><strong>Interactive Tuner Bode Plot:</strong> Graphs the calculated SWR curve across the band. Frequency segment boundaries are clearly indicated with vertical dividers (<strong>|</strong>).</li>
        </ul>
        <p><strong>How to Use It:</strong></p>
        <ul>
            <li><strong>Telemetry Auto-Tracking:</strong> As you turn the transceiver VFO or switch bands via CAT, the antenna mapper automatically tracks the frequency, updating the active antenna card and tuning curve without user interaction.</li>
            <li><strong>Component Inspection:</strong> Click on any band or segment boundary to inspect the exact physical LC network solution: Inductance (<i>L</i> in nanohenries / nH or microhenries / µH) and Capacitance (<i>C</i> in picofarads / pF). This allows rapid verification that the internal ATU relays are latching to the correct values.</li>
        </ul>
    </div>

    <!-- Screen 3: Health Monitor -->
    <div class="screen-feature-box">
        <h4>3. 📈 Amplifier Health Monitor &amp; 60°C Thermal Guard (<code>/health</code>)</h4>
        <p><strong>Purpose:</strong> Continuous, high-precision monitoring of the amplifier's electrical operating points and heatsink thermal dissipation to protect the push-pull Ampleon BLF189 / BLF189XR LDMOS transistors.</p>
        <p><strong>How to Read It:</strong></p>
        <ul>
            <li><strong>5 Real-Time Telemetry Gauges:</strong>
                <ol>
                    <li><em>Heatsink Temperature:</em> Current PA copper heat-spreader temperature in °C.</li>
                    <li><em>Forward Output Power:</em> Real-time RF power delivery in Watts (0 to 2000 W).</li>
                    <li><em>Reflected Power &amp; SWR:</em> Return loss and antenna SWR ratio (1.0:1 to 5.0:1).</li>
                    <li><em>53.5V DC Rail Voltage:</em> Heiwoo main power supply rail voltage under static and key-down conditions.</li>
                    <li><em>Drain Current (Id):</em> Total PA drain current in Amperes (0 to 55 A).</li>
                </ol>
            </li>
            <li><strong>3 Real-Time Canvas Trend Charts:</strong> Continuously graph 15-minute rolling windows of Temperature trend, RF envelope power, and DC voltage sag during transmissions.</li>
        </ul>
        <p><strong>Multi-Tier Thermal Safety Guard:</strong></p>
        <ul>
            <li><code>Nominal State</code> (&le; 50°C): Normal operation. High-efficiency chassis cooling fans engage automatically above 42°C.</li>
            <li><code>Warning State</code> (&gt; 50°C): Visual banner warning indicating heavy contest duty cycle.</li>
            <li><code>Red Alert State</code> (&gt; 55°C): Critical warning indicating heatsink is approaching maximum thermal dissipation limits.</li>
            <li><code>Emergency Thermal Trip</code> (&gt; 60°C): <strong>Automatic unkey protection!</strong> The health engine immediately transmits an autonomous SimpleRPC command to switch the amplifier into Standby mode, dropping PTT. An emergency modal dialog locks the web screen, initiates a <strong>300-second live cooldown countdown</strong>, and strictly locks out re-enabling until the heatsink cools below <strong>50.0°C</strong>.</li>
        </ul>
    </div>

    <!-- Screen 4: Remote Screen -->
    <div class="screen-feature-box">
        <h4>4. 📺 Remote Screen Mirror (<code>/screen</code>)</h4>
        <p><strong>Purpose:</strong> Delivers a real-time, low-latency, pixel-accurate stream of the physical 1024x600 front-panel touchscreen display to any remote browser.</p>
        <p><strong>How to Read It:</strong> Exactly reproduces the front-panel cross-pointer meters, bar graphs, operating frequency, and amplifier status annunciators (OPERATE / STANDBY, BAND, ANT).</p>
        <p><strong>How to Use It:</strong></p>
        <ul>
            <li>Operates via the Raspberry Pi's secondary Full KMS DRM display pipeline, capturing frames directly from the frame buffer without loading the CPU.</li>
            <li><strong>Strictly Read-Only:</strong> Touch events and mouse clicks are deliberately disabled on the remote mirror. This guarantees that an accidental brush of a tablet or smartphone in the shack cannot alter amplifier settings, trip relays, or inadvertently key the amplifier.</li>
            <li>Prop up an iPad or phone next to your logging computer or SDR console for instantaneous, heads-up status verification.</li>
        </ul>
    </div>

    <!-- Screen 5: SD Backup -->
    <div class="screen-feature-box">
        <h4>5. 💾 Disaster Recovery &amp; SD Backup Manager (<code>/backup</code>)</h4>
        <p><strong>Purpose:</strong> Manages raw, byte-level binary cloning of the active production MicroSD storage to provide instant failover in the event of storage failure.</p>
        <p><strong>How to Read It:</strong> Displays primary storage health, secondary backup target device (<code>/dev/sda</code>, labeled <code>BACKUP-AUTO</code> in the rear USB reader), last completed backup timestamp, compressed image size, and cron scheduling status.</p>
        <p><strong>How to Use It:</strong></p>
        <ul>
            <li><strong>On-Demand Instant Cloning:</strong> Click <strong>⚡ Run Full SD Backup Now</strong> before performing any station reconfigurations, firmware updates, or Shack electrical work.</li>
            <li><strong>Automated Weekly Cron:</strong> Runs autonomously every Sunday morning at 04:00 GMT, writing a compressed <code>dd | xz</code> raw disk image to <code>/home/pi/backups/</code>.</li>
            <li><strong>Emergency Hot-Swap:</strong> In the event of primary MicroSD failure during a contest, remove the card from the rear USB reader, insert it directly into the Raspberry Pi internal slot, and power on. Recovery takes under 3 minutes!</li>
        </ul>
    </div>

    <!-- Automated OS Autopatching -->
    <div class="screen-feature-box">
        <h4>⚙️ Automated RPi OS Autopatching (Sunday Cron Engine)</h4>
        <p><strong>Purpose:</strong> Keeps the Debian 13 Trixie 64-bit operating system, kernel security patches, hardware drivers, and network protocols fully up to date without manual sysadmin work.</p>
        <p><strong>How It Operates:</strong></p>
        <ul>
            <li>Immediately after the weekly binary raw image backup completes on Sunday at 04:00 GMT, the system executes:
                <div style="background:#0f2c4d; color:#67e8f9; padding:8px 14px; font-family:Consolas, monospace; border-radius:4px; margin:6px 0;">sudo apt update &amp;&amp; sudo apt upgrade -y</div>
            </li>
            <li><strong>Bulletproof Fail-Safe:</strong> Because a verified raw disk image was created minutes prior to executing <code>apt upgrade</code>, you are permanently protected against upstream Debian regressions. If an update ever creates an anomaly, you can immediately restore the Sunday pre-upgrade image.</li>
        </ul>
    </div>

    <!-- Screen 6: System Report -->
    <div class="screen-feature-box">
        <h4>6. 📋 JRFK Complete Station System Report (<code>/report</code>)</h4>
        <p><strong>Purpose:</strong> Generates an exhaustive, publication-grade diagnostic audit of the entire host compute platform, Linux kernel, storage subsystems, and RF-KIT hardware interfaces.</p>
        <p><strong>How to Read It:</strong> Organized into clear, high-contrast blueprint diagnostic tables:
            <ol>
                <li><em>Compute Subsystem:</em> CPU architecture (<code>aarch64</code>), Broadcom BCM2711/2712 core clock frequencies, load averages, memory utilization, and ARM SoC silicon junction temperature.</li>
                <li><em>MicroSD Storage Health:</em> Root filesystem mount options, remaining storage capacity, and wear-leveling endurance telemetry for Application Performance Class 2 (A2) high-endurance media.</li>
                <li><em>Network &amp; CAT Subsystems:</em> Assigned IPv4 address, MAC address, Wi-Fi RSSI signal quality (dBm), transceiver CAT rig interface, and UDP port 50001 listener status.</li>
                <li><em>RF-KIT Calibrations:</em> Forward and Reflected detector null voltage offsets (0.042V / 0.038V), SimpleRPC device link status (<code>/dev/ttyUSB_RFK</code>), and 64-bit calibration audit.</li>
            </ol>
        </p>
        <p><strong>How to Use It:</strong> Run this report during routine station maintenance or pre-contest equipment checks to confirm that voltage rails, thermal margins, and storage endurance are optimal.</p>
    </div>

    <!-- Screen 7: Log Viewer -->
    <div class="screen-feature-box">
        <h4>7. 📜 Centralized Station Log Viewer (<code>/logs</code>)</h4>
        <p><strong>Purpose:</strong> Provides a unified, real-time filtered inspection window across four distinct station log streams without requiring SSH terminal logins.</p>
        <p><strong>How to Read &amp; Use the 4 Log Streams:</strong></p>
        <ul>
            <li><code>telemetry_rolling.log</code>: 10MB rotating circular log tracking continuous min, max, and typical values for PA temperature, forward power, 53.5V DC rail stability, and drain current. Use this to audit power supply rail sag under full CW key-down.</li>
            <li><code>rfk_backup.log</code>: Audit log of weekly scheduled disk cloning, compression duration, image checksums, and Debian apt package upgrade histories.</li>
            <li><code>rfk_gui</code>: Live stdout/stderr log stream from the RF-KIT touch GUI process, recording touchscreen interactions, band switch events, and SimpleRPC packet acknowledgments.</li>
            <li><code>systemd journal</code>: Kernel-level messages, USB serial device attachment (<code>/dev/ttyUSB_RFK</code>), udev symlink generation, and Wi-Fi DHCP association events.</li>
        </ul>
        <p>Use the built-in level filters (<strong>ALL</strong>, <strong>WARN</strong>, <strong>ERROR</strong>) and the <strong>Auto-Refresh</strong> toggle to monitor live operations or diagnose anomalous behavior.</p>
    </div>

    <!-- Section 5: Hardware Prerequisites & Fleet Strategy -->
    <h2><span class="sec-num">05</span> Hardware Prerequisites &amp; The 6-Card Fleet</h2>

    <p>Before beginning the migration, ensure your amplifier firmware meets the minimum standard and prepare your MicroSD media fleet.</p>

    <div class="alert alert-warning">
        <strong>FIRMWARE PREREQUISITE:</strong> Your RF-KIT amplifier must run <strong>firmware version v199, v200, or later</strong> prior to starting the migration. Internal controller parameter schemas were updated in v199 to support 64-bit SimpleRPC protocol parity.
    </div>

    <h3>The 6-Card MicroSD Fleet Strategy</h3>
    <table>
        <thead>
            <tr>
                <th>Card Identifier</th>
                <th>Physical Label</th>
                <th>Specification</th>
                <th>Dedicated Purpose &amp; Safety Role</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><strong>Card 1</strong></td>
                <td><span style="background:#fef08a; padding:2px 6px; border:1px solid #ca8a04; font-weight:bold;">GOLD1</span></td>
                <td>32GB V30/A2 MicroSD</td>
                <td><strong>Primary 32-Bit Golden Master.</strong> Exact clone of your working 32-bit SD. Air-gapped vault storage; NEVER written to.</td>
            </tr>
            <tr>
                <td><strong>Card 2</strong></td>
                <td><span style="background:#fef08a; padding:2px 6px; border:1px solid #ca8a04; font-weight:bold;">GOLD2</span></td>
                <td>32GB V30/A2 MicroSD</td>
                <td><strong>Secondary 32-Bit Golden Master.</strong> Redundant shack backup. Guarantees instant fail-safe rollback to 32-bit at any time.</td>
            </tr>
            <tr>
                <td><strong>Card 3</strong></td>
                <td><span style="background:#bbf7d0; padding:2px 6px; border:1px solid #16a34a; font-weight:bold;">PROD-64</span></td>
                <td>32GB V30/A2 MicroSD</td>
                <td><strong>Main 64-Bit Production SD.</strong> Runs inside the Raspberry Pi in your amplifier (Debian Trixie aarch64 + RFK GUI).</td>
            </tr>
            <tr>
                <td><strong>Card 4</strong></td>
                <td><span style="background:#bbf7d0; padding:2px 6px; border:1px solid #16a34a; font-weight:bold;">FIELD-64</span></td>
                <td>32GB V30/A2 MicroSD</td>
                <td><strong>Cold-Spare 64-Bit Field Backup.</strong> Ready for immediate physical card-swap during contests or DXpeditions.</td>
            </tr>
            <tr>
                <td><strong>Card 5</strong></td>
                <td><span style="background:#bae6fd; padding:2px 6px; border:1px solid #0284c7; font-weight:bold;">BACKUP-AUTO</span></td>
                <td>32GB V30/A2 MicroSD</td>
                <td><strong>Automated Rolling Backup Target.</strong> Left permanently inserted in the amplifier's USB 2.0 reader for weekly cron clones.</td>
            </tr>
            <tr>
                <td><strong>Card 6</strong></td>
                <td><span style="background:#e2e8f0; padding:2px 6px; border:1px solid #64748b; font-weight:bold;">VIRGIN-SPARE</span></td>
                <td>32GB V30/A2 MicroSD</td>
                <td><strong>Spare / Virgin Setup Card.</strong> Dedicated for Option 2 (fresh setup without GOLD) or bench experimentation.</td>
            </tr>
        </tbody>
    </table>

    <!-- Section 6: The Golden Rule of Safety -->
    <h2><span class="sec-num">06</span> The Golden Rule of Safety: Creating GOLD1 &amp; GOLD2</h2>

    <p>Before writing a single byte of 64-bit software, you will clone your existing 32-bit working system into two physical Golden Masters directly on the Raspberry Pi using the desktop <strong>SD Card Copier</strong> tool (<code>piclone</code>):</p>

    <ol>
        <li>Boot the amplifier normally into your 32-bit system. Plug a blank 32GB MicroSD card into a USB reader connected to the Raspberry Pi.</li>
        <li>Open the Raspberry Pi desktop menu &rarr; <em>Accessories</em> &rarr; <em>SD Card Copier</em>.</li>
        <li>Select <strong>Copy From Device:</strong> <code>Internal SD Card (/dev/mmcblk0)</code>.</li>
        <li>Select <strong>Copy To Device:</strong> <code>USB Card Reader (/dev/sda)</code>.</li>
        <li>Click <strong>Start</strong>. Once complete, remove the card and label it <strong>GOLD1</strong>.</li>
        <li>Repeat this exact procedure with a second blank card and label it <strong>GOLD2</strong>.</li>
    </ol>

    <div class="alert alert-success">
        <strong>ZERO RISK GUARANTEED:</strong> You now possess two independent, bootable, exact physical copies of your factory 32-bit system. Even in the worst-case scenario, re-inserting GOLD1 returns your amplifier to 100% factory operation in under 60 seconds.
    </div>

    <!-- Section 7: Option 1 Migration -->
    <h2><span class="sec-num">07</span> Option 1: 64-Bit OS Migration with JRFK.exe</h2>

    <p>With GOLD1 created, you can now generate your production 64-bit SD card (<strong>PROD-64</strong>) using the Windows PC utility:</p>

    <div class="step-block">
        <h4><span class="step-badge">STEP 1</span> Launch JRFK.exe on Windows</h4>
        <p>Connect your USB MicroSD reader to your Windows PC with <strong>GOLD1</strong> inserted. Launch <code>JRFK.exe</code>. Accept the Windows UAC Administrator prompt. The tool will automatically open your default browser to <code>http://127.0.0.1:8089/</code>.</p>
    </div>

    <div class="step-block">
        <h4><span class="step-badge">STEP 2</span> Read-Only GOLD Asset Extraction</h4>
        <p>Click <strong>1. Validate &amp; Extract GOLD SD</strong>. JRFK reads the Linux ext4 rootfs in strict read-only mode, validating your callsign, Wi-Fi SSID, calibration files, and tuning tables. It computes SHA-256 signatures to confirm data integrity.</p>
    </div>

    <div class="step-block">
        <h4><span class="step-badge">STEP 3</span> Swap to Target Blank SD Card</h4>
        <p>Eject GOLD1 and safely store it in your shack vault. Insert a fresh blank 32GB card (labeled <strong>PROD-64</strong>). Click <strong>Rescan Disks</strong> and select the target drive.</p>
    </div>

    <div class="step-block">
        <h4><span class="step-badge">STEP 4</span> Write 64-Bit Image &amp; Inject Factory Calibrations</h4>
        <p>Click <strong>2. Provision SD (Migrate to 64-Bit)</strong>. JRFK wipes the card, flashes the verified 64-bit Debian Trixie image (~6.28 GB), and injects all your preserved calibrations, Wi-Fi network credentials, headless SSH keys, and custom 1024x600 display modelines.</p>
    </div>

    <!-- Section 8: The 3-Boot Walkthrough -->
    <h2><span class="sec-num">08</span> The 3-Boot Walkthrough: From Automation to Production</h2>

    <p>Insert the newly created <strong>PROD-64</strong> card into your amplifier's Raspberry Pi and power on. The amplifier will perform an automated 3-boot initialization:</p>

    <ul>
        <li><strong>Boot 1 (Partition Expansion &amp; Offline Debs):</strong> The system auto-expands the Linux rootfs to utilize the full 32GB card, unpacks the 15 offline Debian packages, installs Python 3.13 shims, and reboots automatically (~90 seconds).</li>
        <li><strong>Boot 2 (Hardware Link &amp; Controller Handshake):</strong> The system tests the USB serial link to the Arduino / proprietary controller (<code>/dev/ttyUSB_RFK</code>). Once verified, it displays a green completion confirmation and reboots into production mode.</li>
        <li><strong>Boot 3 (Production Mode):</strong> Boots directly into the fullscreen 1024x600 RF-KIT touchscreen GUI. The Linux desktop is completely hidden. All RF-KIT meters, antenna ports, and menus are live.</li>
    </ul>

    <!-- Section 9: Option 2 Virgin Setup -->
    <h2><span class="sec-num">09</span> Option 2: Virgin Fresh 64-Bit Setup (Without GOLD Card)</h2>

    <p>If your original 32-bit SD card was lost or corrupted, JRFK allows building a complete, clean 64-bit OS from scratch:</p>
    <ol>
        <li>Open <code>JRFK.exe</code> and navigate to <strong>Option 2: Fresh Setup</strong>.</li>
        <li>Enter your <strong>Callsign</strong>, <strong>Shack Wi-Fi SSID and Password</strong>, and select your transceiver CAT rig.</li>
        <li>Click <strong>Build Fresh 64-Bit SD</strong>. JRFK generates a turnkey 64-bit image populated with standard K7BIT cookbook tuning profiles ready for on-air alignment.</li>
    </ol>

    <!-- Section 10: Disaster Recovery Procedure -->
    <h2><span class="sec-num">10</span> Emergency Disaster Recovery &amp; Field Hot-Swap</h2>

    <p>If your primary production SD card ever experiences hardware degradation or read errors during a contest:</p>

    <div class="alert alert-danger">
        <strong>THE 3-MINUTE RECOVERY PROCEDURE:</strong>
        <ol style="margin-top: 8px;">
            <li>Switch AC mains power to <strong>OFF</strong>. Disconnect AC power cord. Wait 30 seconds for power supply capacitors to bleed down.</li>
            <li>Press and remove the degraded card from the internal Raspberry Pi slot.</li>
            <li>Insert your <strong>BACKUP-AUTO</strong> card (from the rear USB reader) or your pre-provisioned <strong>FIELD-64</strong> card into the internal slot.</li>
            <li>Reconnect AC power and switch power to <strong>ON</strong>. The amplifier boots immediately into full operation with all calibrations intact.</li>
        </ol>
    </div>

    <!-- Section 11: Troubleshooting -->
    <h2><span class="sec-num">11</span> Field Troubleshooting &amp; Diagnostics</h2>

    <table>
        <thead>
            <tr>
                <th>Symptom</th>
                <th>Probable Root Cause</th>
                <th>Remedy &amp; Resolution</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>Screen displays black or "No Signal" on first boot</td>
                <td>HDMI cable loose or timing initialization in progress</td>
                <td>Boot 1 takes ~90 seconds to expand the filesystem. Wait for automated reboot. Check that the micro-HDMI cable is connected to <strong>HDMI 0</strong> (closest to USB-C power).</td>
            </tr>
            <tr>
                <td>GUI displays "Connecting..." or voltage reads 0.0V</td>
                <td>Controller serial handshake timeout</td>
                <td>Verify the internal USB cable from the controller to the Raspberry Pi is seated. Check that <code>/dev/ttyUSB_RFK</code> is listed in the System Report (<code>:8088/report</code>).</td>
            </tr>
            <tr>
                <td>Thermal Alert modal appears on web interface</td>
                <td>PA heatsink temperature exceeded 60°C safety ceiling</td>
                <td>Amplifier was automatically unkeyed to prevent damage. Allow the 300-second countdown to complete. Verify fan operation. Amplifier will auto-reenable when <i>T</i> &lt; 50.0°C.</td>
            </tr>
        </tbody>
    </table>

</div>

</body>
</html>
"""
    out_path = os.path.join(DOCS_DIR, "JRFK_Users_Guide.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print("Generated JRFK_Users_Guide.html")

def build_cookbook():
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RF-KIT Linear Amplifier: K7BIT Hardware Alignment, Potentiometer Adjustments & Calibration Cookbook</title>
    <style>
        :root {
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
        }

        * {
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: var(--bg-light);
            color: var(--text-dark);
            line-height: 1.6;
            margin: 0;
            padding: 0;
        }

        .manual-container {
            max-width: 980px;
            margin: 0 auto;
            background: #ffffff;
            padding: 45px 55px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.06);
        }

        /* Publication Cover Header */
        .cover-header {
            border-bottom: 4px solid var(--bp-blue);
            padding-bottom: 25px;
            margin-bottom: 25px;
        }
        .doc-badge {
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
        }
        h1 {
            color: var(--bp-blue);
            font-size: 27px;
            line-height: 1.25;
            margin: 0 0 10px 0;
            font-weight: 800;
        }
        .subtitle {
            font-size: 15px;
            color: var(--text-muted);
            margin: 0 0 15px 0;
            font-weight: 500;
        }
        .meta-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 10px;
            font-size: 12px;
            color: var(--text-muted);
            background: #f1f5f9;
            padding: 12px 16px;
            border-radius: 6px;
            border-left: 4px solid var(--bp-blue);
        }

        /* Section Headings */
        h2 {
            color: var(--bp-blue);
            font-size: 20px;
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 8px;
            margin-top: 40px;
            margin-bottom: 15px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        h2 .sec-num {
            background: var(--bp-blue);
            color: #ffffff;
            font-size: 13px;
            padding: 2px 8px;
            border-radius: 3px;
            font-family: 'Consolas', monospace;
        }
        h3 {
            color: #1e3a8a;
            font-size: 16px;
            margin-top: 25px;
            margin-bottom: 10px;
        }

        /* Callouts */
        .alert {
            padding: 14px 18px;
            border-radius: 6px;
            margin: 18px 0;
            font-size: 14px;
            line-height: 1.5;
            border-left: 4px solid;
        }
        .alert-info { background: #eff6ff; border-color: #3b82f6; color: #1e40af; }
        .alert-warning { background: #fffbeb; border-color: #f59e0b; color: #92400e; }
        .alert-danger { background: #fef2f2; border-color: #ef4444; color: #991b1b; }
        .alert-success { background: #f0fdf4; border-color: #22c55e; color: #166534; }

        /* Classic Medium-Blue Blueprint Card */
        .blueprint-card {
            background: var(--bp-blue);
            background-image: 
                linear-gradient(var(--bp-grid) 1px, transparent 1px),
                linear-gradient(90deg, var(--bp-grid) 1px, transparent 1px);
            background-size: 18px 18px;
            color: #ffffff;
            border: 2px solid #ffffff;
            padding: 20px;
            border-radius: 6px;
            margin: 20px 0;
            font-family: 'Consolas', 'Courier New', monospace;
            font-size: 13px;
            box-shadow: 0 4px 15px rgba(26, 86, 149, 0.25);
        }
        .blueprint-card .bp-title {
            color: #ffffff;
            font-size: 14px;
            font-weight: bold;
            border-bottom: 1px solid rgba(255, 255, 255, 0.35);
            padding-bottom: 6px;
            margin-bottom: 12px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        /* Step progression blocks */
        .step-block {
            border: 1px solid var(--card-border);
            border-radius: 8px;
            padding: 18px 22px;
            margin-bottom: 18px;
            background: #ffffff;
            box-shadow: 0 2px 6px rgba(0,0,0,0.03);
        }
        .step-block h4 {
            margin: 0 0 10px 0;
            font-size: 15px;
            color: var(--bp-blue);
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .step-badge {
            background: var(--bp-blue);
            color: #ffffff;
            font-size: 11px;
            font-weight: bold;
            padding: 2px 8px;
            border-radius: 3px;
        }

        /* Potentiometer Item Card */
        .pot-card {
            border-left: 4px solid var(--bp-blue);
            background: #f8fafc;
            border-top: 1px solid #e2e8f0;
            border-right: 1px solid #e2e8f0;
            border-bottom: 1px solid #e2e8f0;
            padding: 14px 18px;
            margin-bottom: 14px;
            border-radius: 0 6px 6px 0;
        }
        .pot-card h4 {
            margin: 0 0 6px 0;
            color: var(--bp-blue);
            font-size: 15px;
            font-family: 'Consolas', monospace;
        }
        .pot-card p {
            margin: 0;
            font-size: 13.5px;
            color: var(--text-dark);
        }

        /* Data Tables */
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0 25px 0;
            font-size: 13px;
        }
        th, td {
            border: 1px solid #cbd5e1;
            padding: 9px 12px;
            text-align: left;
        }
        th {
            background: #f1f5f9;
            color: var(--bp-blue);
            font-weight: 700;
        }
        tr:nth-child(even) {
            background: #f8fafc;
        }

        /* Print formatting */
        @media print {
            body { background: #ffffff !important; }
            .manual-container { padding: 0 !important; box-shadow: none !important; width: 100% !important; max-width: 100% !important; }
            h2 { page-break-before: always; }
            h2:first-of-type { page-break-before: avoid; }
            .step-block, .blueprint-card, .pot-card, table { page-break-inside: avoid; }
        }
    </style>
</head>
<body>

<div class="manual-container">

    <!-- Title & Executive Overview -->
    <div class="cover-header">
        <span class="doc-badge">HARDWARE ALIGNMENT &amp; CALIBRATION COOKBOOK</span>
        <h1>RF-KIT Linear Amplifier: K7BIT Hardware Alignment, Potentiometer Adjustments &amp; Calibration Cookbook</h1>
        <div class="subtitle">Bench Alignment Guide, 9-Potentiometer Calibration Matrix, 17-Step Precision Procedure &amp; 10-Part Characterization Suite</div>
        <div class="meta-grid">
            <div><strong>Document ID:</strong> JRFK-CB-2026-V2.1</div>
            <div><strong>Author:</strong> John Birdlebough (K7BIT)</div>
            <div><strong>Target Platforms:</strong> RF2K-S / RF2K+ (B26 Architecture)</div>
            <div><strong>Hardware Specs:</strong> Heiwoo 53.5V PSU | BLF189 LDMOS</div>
        </div>
    </div>

    <div class="alert alert-danger">
        <strong>HIGH VOLTAGE &amp; RF POWER SAFETY WARNING:</strong> This amplifier operates at lethal DC voltages (53.5 VDC @ 55 A) and delivers hazardous RF power levels (1500W+ PEP/CW). Calibration must only be performed by experienced technical personnel using insulated alignment tools, a 50Ω 2kW dummy load, and calibrated laboratory test equipment. Never touch internal components while AC power is connected.
    </div>

    <!-- Section 1: Provenance & Controller Parity -->
    <h2><span class="sec-num">01</span> Historical Provenance &amp; Controller Architectural Parity</h2>

    <p>The alignment principles, detector calibration formulas, and potentiometer adjustment procedures documented in this Cookbook originate from John Birdlebough's (K7BIT) seminal work on the <strong>RF-KIT B26-RF2K+</strong> linear amplifier. Over successive production generations, two primary microcontroller backplane variants have been deployed:</p>

    <ul>
        <li><strong>First-Generation Backplane:</strong> Based on the standard <strong>Arduino Mega 2560 R3</strong> daughtercard plugged into the motherboard.</li>
        <li><strong>Updated Production Controller:</strong> Features an integrated proprietary surface-mount microcontroller backplane deployed in the RF2K-S and modern RF2K+ amplifiers.</li>
    </ul>

    <p>While RF-KIT has declined to release proprietary schematics for the updated controller board, rigorous bus analysis and reverse-engineering confirm that <strong>operational circuit parity is 100% maintained</strong>. The analog sensing circuitry, the 9 potentiometer calibration trimmers (R1, R2, R14, R15, R17, R19, R20, R21, SPARE), the relay drivers, and the binary SimpleRPC protocol are identical across all hardware revisions. Every calibration step in this cookbook applies universally to both controller variants.</p>

    <!-- Section 2: Hardware Architecture & Test Bench Setup -->
    <h2><span class="sec-num">02</span> Hardware Architecture &amp; Test Bench Configuration</h2>

    <h3>Subsystem Architecture</h3>
    <ul>
        <li><strong>Main DC Power Supply:</strong> High-efficiency <strong>Heiwoo 53.5V Switching Power Supply</strong> (53.5 VDC @ ~55 A / 3000 W capacity). The power supply is managed via discrete hardware AC line switching and standby/operate inhibit control lines. <em>Note: CAN bus communication is NOT used for power supply control in production units.</em></li>
        <li><strong>RF Power Deck:</strong> Dual <strong>Ampleon BLF189 / BLF189XR 50V LDMOS</strong> transistors configured in a high-efficiency push-pull topology on a copper heat-spreader.</li>
        <li><strong>Low Pass Filter &amp; ATU:</strong> Toroidal low-pass filters (160m to 6m) and an integrated 8-step inductor / 8-step capacitor automatic antenna tuner (ATU).</li>
    </ul>

    <h3>Required Test Equipment</h3>
    <table>
        <thead>
            <tr>
                <th>Equipment</th>
                <th>Specification / Model</th>
                <th>Calibration Role</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><strong>High-Power Dummy Load</strong></td>
                <td>50Ω 1500W+ Continuous (Alpha 198 / Bird 8201)</td>
                <td>RF power termination and SWR bridge nulling.</td>
            </tr>
            <tr>
                <td><strong>Auxiliary Dummy Load</strong></td>
                <td>50Ω 100W with Coaxial T-Connector</td>
                <td>Paralleled to create a certified 25Ω load (2.0:1 SWR).</td>
            </tr>
            <tr>
                <td><strong>Digital Multimeter (DMM)</strong></td>
                <td>Fluke 87V or equivalent (10 MΩ input Z)</td>
                <td>Precision DC rail voltage and quiescent current measurement.</td>
            </tr>
            <tr>
                <td><strong>Calibrated In-Line Wattmeter</strong></td>
                <td>LP-100A, LP-700, or Bird 43</td>
                <td>Forward and reflected RF power reference standards.</td>
            </tr>
            <tr>
                <td><strong>HF Transceiver / Exciter</strong></td>
                <td>Clean CW carrier, adjustable 1W to 50W</td>
                <td>RF drive signal source across 160m through 6m.</td>
            </tr>
            <tr>
                <td><strong>Alignment Tool</strong></td>
                <td>Non-inductive ceramic / plastic trimming tool</td>
                <td>Adjustment of multi-turn trimmers without capacitive detuning.</td>
            </tr>
        </tbody>
    </table>

    <div class="blueprint-card">
        <div class="bp-title">The PA Bypass Test Harness (Safety Isolation)</div>
        <p>To safely calibrate the low-level logic, frequency counter, and SWR detectors without risking damage to the Ampleon BLF189 LDMOS transistors:</p>
        <ol style="margin-left: 15px; padding-left: 0;">
            <li>Disconnect the SMA cable from the RF2K5 PA pallet RF input.</li>
            <li>Leave PA output solder pads disconnected from the 11.5-inch PTFE coax.</li>
            <li>Connect the transceiver drive directly through the LPF and SWR bridge via the bypass SMA link. Transceiver drive now passes safely to the wattmeter and load without energizing the PA pallet!</li>
        </ol>
    </div>

    <!-- Section 3: The 9 Potentiometers -->
    <h2><span class="sec-num">03</span> The 9 Potentiometer Alignment Matrix</h2>

    <p>The controller backplane contains 9 precision multi-turn potentiometers that calibrate sensor scaling, protection comparators, and display readouts:</p>

    <table>
        <thead>
            <tr>
                <th>Potentiometer</th>
                <th>Subsystem Function</th>
                <th>Calibration Target</th>
                <th>Adjustment Procedure</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><strong>R1</strong></td>
                <td>Input Overdrive Trip Comparator</td>
                <td>28W CW RF Drive Threshold</td>
                <td>Preset 5 turns CCW during setup; trim clockwise until fault trips at 28W.</td>
            </tr>
            <tr>
                <td><strong>R2</strong></td>
                <td>53.5V Main DC Rail Display Scale</td>
                <td>±0.1 VDC vs Calibrated DMM</td>
                <td>Adjust until front-panel voltage display exactly matches DMM on DC bus.</td>
            </tr>
            <tr>
                <td><strong>R14</strong></td>
                <td>Front-Panel Relative Drive Bar</td>
                <td>Full-Scale at 50W CW Drive</td>
                <td>Adjust drive bargraph sensitivity to reach 100% indication at 50W drive.</td>
            </tr>
            <tr>
                <td><strong>R15</strong></td>
                <td>ATU Pre-Amplifier Gain</td>
                <td>600 ADC Units @ 10W into 25Ω</td>
                <td>Set transceiver to 10W CW into 25Ω load; trim R15 until A1 reads 600.</td>
            </tr>
            <tr>
                <td><strong>R17</strong></td>
                <td>LPF Difference Power Trip Limit</td>
                <td>93 ADC Units @ 50W Drive</td>
                <td>Key 50W through bypass harness; trim R17 until A2 reads 93 ADC counts.</td>
            </tr>
            <tr>
                <td><strong>R19</strong></td>
                <td>Forward Power Display Multiplier</td>
                <td>50W Display @ 50W CW Input</td>
                <td>Standby mode; key 50W into calibrated wattmeter; adjust R19 to 50W.</td>
            </tr>
            <tr>
                <td><strong>R20</strong></td>
                <td>Reflected Power / SWR Calibration</td>
                <td>2.0:1 SWR @ 25Ω Load (50W)</td>
                <td>Attach 25Ω parallel load; key 50W; trim R20 until SWR reads exactly 2.0:1.</td>
            </tr>
            <tr>
                <td><strong>R21</strong></td>
                <td>LDMOS Idle Quiescent Current (Idq)</td>
                <td>Exact Match to DMM in DC Rail</td>
                <td>Key PA in standby/idle; adjust R21 until GUI current matches series DMM.</td>
            </tr>
            <tr>
                <td><strong>SPARE</strong></td>
                <td>Hardware PA Over-Current Latch</td>
                <td>1000 ADC Units at Idle Bias</td>
                <td>Preset 5 turns CCW; trim until ADC current trip threshold reaches 1000.</td>
            </tr>
        </tbody>
    </table>

    <!-- Section 4: 17-Step Precision Bench Calibration -->
    <h2><span class="sec-num">04</span> The 17-Step Precision Bench Calibration Procedure</h2>

    <p>Perform the 17 steps in exact chronological order to ensure safe and accurate alignment:</p>

    <!-- Phase 1 -->
    <h3>Phase 1: Initial Safety Presets &amp; DC Rail Alignment</h3>

    <div class="step-block">
        <h4><span class="step-badge">STEP 1</span> Temporarily Disable Input Overdrive Trip (R1)</h4>
        <p>Turn potentiometer <strong>R1</strong> 5 full turns counter-clockwise (CCW). This prevents premature comparator tripping during initial drive calibration.</p>
    </div>

    <div class="step-block">
        <h4><span class="step-badge">STEP 2</span> Temporarily Disable LPF Difference Trip (R17)</h4>
        <p>Turn potentiometer <strong>R17</strong> 5 full turns counter-clockwise (CCW) to prevent differential trip locks while measuring low-pass filters.</p>
    </div>

    <div class="step-block">
        <h4><span class="step-badge">STEP 3</span> Preset SPARE Potentiometer</h4>
        <p>Locate the <strong>SPARE</strong> potentiometer positioned below R21 and above R17. Turn 5 full turns counter-clockwise (CCW).</p>
    </div>

    <div class="step-block">
        <h4><span class="step-badge">STEP 4</span> Calibrate 53.5V DC Voltage Display (R2)</h4>
        <p>Energize the amplifier on AC mains with PA bias jumpers set to Bypass. Connect your calibrated DMM across the Heiwoo DC power supply output bus studs (target: 53.5 VDC). Observe the front-panel touch display voltage. Adjust multiturn potentiometer <strong>R2</strong> until the display matches the DMM within ±0.1 VDC.</p>
    </div>

    <div class="step-block">
        <h4><span class="step-badge">STEP 5</span> Verify PA Pallet Bias Inhibit Jumpers</h4>
        <p>Confirm that both 2-pin bias jumpers on the RF2K5 PA pallet are set to the <strong>REAR position (Disabled/Bypass)</strong>. This guarantees gate bias cannot be energized while initial RF switching tests are executed.</p>
    </div>

    <div class="step-block">
        <h4><span class="step-badge">STEP 6</span> RF Coaxial Harness Continuity &amp; Port Verification</h4>
        <p>Connect transceiver at 14.175 MHz CW (5W drive) through the PA bypass harness into the 50Ω dummy load at ANT 1. Key transceiver and verify with in-line wattmeter that 5W passes through with &lt; 1.1:1 SWR, proving all relays and coaxial connections are sound.</p>
    </div>

    <div class="step-block">
        <h4><span class="step-badge">STEP 7</span> Frequency Counter Prescaler Calibration (C18 / R_FREQ)</h4>
        <p>Navigate on the GUI to <code>Menu -&gt; Hardware -&gt; Frequency Detector</code>. Set transceiver to 28.500 MHz CW at 10W drive. Key transceiver and observe display. Adjust ceramic trimmer capacitor <strong>C18</strong> on the backplane until the counter reads exactly <strong>28,500 kHz</strong>. Test across 1.8 MHz, 7.0 MHz, 14.0 MHz, and 50.0 MHz to confirm clean counting.</p>
    </div>

    <div class="step-block">
        <h4><span class="step-badge">STEP 8</span> Low Pass Filter (LPF) Auto-Selection Verification</h4>
        <p>Verify that switching bands on the transceiver instantly energizes the matching toroidal low-pass filter relay bank within 15 ms in both UNIVERSAL RF-sensing mode and CAT interface mode.</p>
    </div>

    <!-- Phase 2 -->
    <h3>Phase 2: SWR Bridge Nulling &amp; Power Calibration</h3>

    <div class="step-block">
        <h4><span class="step-badge">STEP 9</span> SWR Bridge Balance &amp; Reflected Detector Nulling</h4>
        <p>Connect certified 50Ω dummy load to ANT 1. Temporarily reverse TRX and ANT 1 coaxial cables (transceiver connected to ANT 1, dummy load to TRX input). Set transceiver to 50.0 MHz CW at 20W drive. Key transceiver and adjust the ceramic coupling trimmer on the SWR Bridge board using a non-inductive plastic tool for <strong>absolute minimum voltage reading at the Reflected test pin (&lt; 5 mV DC null)</strong>. Restore cables to normal orientation.</p>
    </div>

    <div class="step-block">
        <h4><span class="step-badge">STEP 10</span> Calibrate Forward (R19) and Reflected (R20) Power Displays</h4>
        <p><strong>Forward Power:</strong> Place amplifier in STANDBY. Set transceiver to 14.175 MHz CW at 50W into calibrated external wattmeter. Key transceiver; adjust potentiometer <strong>R19</strong> until the front-panel forward power bar reads exactly <strong>50W</strong>.<br/>
        <strong>Reflected Power &amp; SWR:</strong> Attach coaxial T-connector with two 50Ω dummy loads in parallel (25Ω load = 2.0:1 SWR). Key transceiver at 50W CW; adjust potentiometer <strong>R20</strong> until the SWR display reads exactly <strong>2.0:1 SWR</strong>. Remove parallel load.</p>
    </div>

    <div class="step-block">
        <h4><span class="step-badge">STEP 11</span> Calibrate Antenna Tuner Pre-Amplifier Gain (R15)</h4>
        <p>Attach the 25Ω load (2.0:1 SWR). On the GUI, navigate to <code>Menu -&gt; Debug</code> and locate analog reading <strong>A1 PowerTunerGain</strong>. Set transceiver to 10W CW at 14.175 MHz. Key transceiver and adjust potentiometer <strong>R15</strong> until the <strong>A1 reading displays exactly 600 ADC counts</strong>.</p>
    </div>

    <!-- Phase 3 -->
    <h3>Phase 3: LDMOS Quiescent Current (Idq) Calibration</h3>

    <div class="step-block">
        <h4><span class="step-badge">STEP 12</span> Restore PA Pallet RF Connections</h4>
        <p>Power down the amplifier and wait 30 seconds. Disconnect the temporary PA bypass harness. Reconnect the SMA input cable to the RF2K5 pallet RF input. Solder the PA output pads to the 11.5-inch PTFE coaxial cable leading to the Relay Board.</p>
    </div>

    <div class="step-block">
        <h4><span class="step-badge">STEP 13</span> Connect In-Line DMM for Drain Current Measurement</h4>
        <p>Insert your calibrated DMM (switched to 10A DC current mode) in series with the 53.5V DC positive supply lead feeding the RF2K5 PA pallet.</p>
    </div>

    <div class="step-block">
        <h4><span class="step-badge">STEP 14</span> Enable PA Gate Bias Jumpers &amp; Adjust Idle Current</h4>
        <p>Move both 2-pin bias jumpers on the RF2K5 pallet to the <strong>FORWARD position (Enabled)</strong>. Power on amplifier in OPERATE mode (no RF drive applied). Key the PTT line. Adjust the gate bias trimmers on the PA pallet until the DMM reads the specified idle current for the Ampleon BLF189 / BLF189XR transistors (typically <strong>1.8A to 2.2A per device</strong>, total ~3.6A to 4.4A).</p>
    </div>

    <div class="step-block">
        <h4><span class="step-badge">STEP 15</span> Calibrate Quiescent Current Display (R21)</h4>
        <p>While PTT is keyed at idle bias, observe the current readout on the front-panel touchscreen. Adjust potentiometer <strong>R21</strong> until the displayed current matches the physical DMM reading within ±0.05A.</p>
    </div>

    <!-- Phase 4 -->
    <h3>Phase 4: Hardware Protection Comparators</h3>

    <div class="step-block">
        <h4><span class="step-badge">STEP 16</span> Calibrate Input Overdrive Trip Threshold (R1)</h4>
        <p>Set transceiver to 28W CW carrier at 14.175 MHz. Slowly turn potentiometer <strong>R1</strong> clockwise (CW) while keying until the amplifier hardware instantly trips on <strong>"INPUT OVERDRIVE"</strong> fault at exactly 28W drive.</p>
    </div>

    <div class="step-block">
        <h4><span class="step-badge">STEP 17</span> Calibrate LPF Forward Power Difference Trip (R17)</h4>
        <p>Set transceiver to 50W CW drive. In the Debug menu, monitor analog reading <strong>A2 LPF_FWD_DIFF</strong>. Turn potentiometer <strong>R17</strong> clockwise until the reading reaches <strong>93 ADC counts</strong>.</p>
    </div>

    <!-- Section 5: 10-Part Characterization Suite -->
    <h2><span class="sec-num">05</span> The 10-Part Comprehensive Characterization Plan</h2>

    <p>Following calibration, perform this exhaustive 10-part verification suite to validate station readiness:</p>

    <table>
        <thead>
            <tr>
                <th>Test</th>
                <th>Test Parameter</th>
                <th>Methodology &amp; Conditions</th>
                <th>Pass / Fail Criteria</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><strong>T1</strong></td>
                <td>Cold DC Isolation Audit</td>
                <td>Measure resistance from 53.5V bus to ground (unpowered).</td>
                <td>R &gt; 100 kΩ after filter cap charge; no shorts.</td>
            </tr>
            <tr>
                <td><strong>T2</strong></td>
                <td>Low-Voltage Rail Accuracy</td>
                <td>DMM verification of +12V, +5V, and +3.3V backplane rails.</td>
                <td>All rails within ±2.5% of nominal voltage.</td>
            </tr>
            <tr>
                <td><strong>T3</strong></td>
                <td>SWR Bridge Detector Null</td>
                <td>50W CW into certified 50Ω load at 50 MHz.</td>
                <td>Reflected detector voltage &lt; 5 mV DC.</td>
            </tr>
            <tr>
                <td><strong>T4</strong></td>
                <td>LPF Return Loss Verification</td>
                <td>Network analyzer / transceiver SWR through all 7 filters.</td>
                <td>Return loss &gt; 20 dB (SWR &lt; 1.2:1) across passband.</td>
            </tr>
            <tr>
                <td><strong>T5</strong></td>
                <td>Antenna Matrix Isolation</td>
                <td>Measure RF isolation between unenergized coaxial ports.</td>
                <td>Isolation &gt; 55 dB from 1.8 MHz to 54 MHz.</td>
            </tr>
            <tr>
                <td><strong>T6</strong></td>
                <td>ATU Component Step Audit</td>
                <td>Verify all 8 L-steps and 8 C-steps latch relay contacts.</td>
                <td>Inductance 0.05µH to 6.4µH; Capacitance 10pF to 2600pF.</td>
            </tr>
            <tr>
                <td><strong>T7</strong></td>
                <td>Bias Thermal Stability</td>
                <td>Key idle bias for 10 minutes; monitor current drift.</td>
                <td>Idq drift &lt; ±5% over 20°C to 50°C heatsink range.</td>
            </tr>
            <tr>
                <td><strong>T8</strong></td>
                <td>Harmonic Suppression</td>
                <td>Spectrum analyzer audit of 2nd and 3rd harmonics at 1500W.</td>
                <td>All harmonics &gt; 60 dB below fundamental carrier.</td>
            </tr>
            <tr>
                <td><strong>T9</strong></td>
                <td>Full-Power Saturation &amp; Sag</td>
                <td>1500W CW key-down for 30s into high-power load.</td>
                <td>53.5V rail sag &lt; 1.5 VDC; RF gain &gt; 14.5 dB.</td>
            </tr>
            <tr>
                <td><strong>T10</strong></td>
                <td>Protection State Machine Latency</td>
                <td>Assert high SWR (&gt; 3.0:1) and measure fault trip time.</td>
                <td>Hardware fault trip latency &lt; 15 ms; PA unkeyed.</td>
            </tr>
        </tbody>
    </table>

    <!-- Section 6: Inspection Checklist -->
    <h2><span class="sec-num">06</span> Post-Calibration Bench Verification Checklist</h2>

    <div class="blueprint-card">
        <div class="bp-title">Pre-Flight Shack Verification Sign-Off</div>
        <p>☐ All 9 potentiometers calibrated and locking nuts/trimmers verified.</p>
        <p>☐ Heiwoo 53.5V switching power supply output verified at 53.50 VDC under load.</p>
        <p>☐ Ampleon BLF189 / BLF189XR LDMOS quiescent bias set to exact specification.</p>
        <p>☐ PA bypass harness removed; RF coaxial cables torqued to 8 in-lbs.</p>
        <p>☐ Frequency counter counter-checks correctly across all bands (160m..6m).</p>
        <p>☐ Emergency thermal safety trip verified at 60°C on Port 8088 Health Monitor.</p>
        <p>☐ GOLD1 MicroSD card safely placed in air-gapped shack vault.</p>
    </div>

</div>

</body>
</html>
"""
    out_path = os.path.join(DOCS_DIR, "JRFK_Cookbook.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print("Generated JRFK_Cookbook.html")

def build_docs_viewer():
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
    <title>RF-KIT Documentation & Station Reference Library (Blueprint Format)</title>
    <style>
        :root {
            --bp-bg: #1a5695;          /* Classic medium blueprint cyanotype blue */
            --bp-grid: rgba(255, 255, 255, 0.18);
            --bp-line: #ffffff;
            --bp-line-dim: #dbeafe;
            --bp-card-bg: rgba(26, 86, 149, 0.92);
            --bp-border: #93c5fd;
            --bp-border-bright: #ffffff;
            --data-green: #22c55e;
            --data-yellow: #facc15;
            --data-red: #ef4444;
            --data-cyan: #67e8f9;
        }

        * {
            box-sizing: border-box;
        }

        body {
            font-family: 'Consolas', 'Monaco', 'Courier New', -apple-system, sans-serif;
            background-color: var(--bp-bg);
            background-image: 
                linear-gradient(var(--bp-grid) 1px, transparent 1px),
                linear-gradient(90deg, var(--bp-grid) 1px, transparent 1px);
            background-size: 20px 20px;
            color: var(--bp-line);
            margin: 0;
            padding: 20px;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }

        /* Technical Blueprint Header */
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 12px;
            border: 2px solid var(--bp-line);
            padding: 14px 20px;
            margin-bottom: 20px;
            background: var(--bp-card-bg);
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
            position: relative;
        }
        .header::after {
            content: "DWG NO. RFK-DOC-001 | REV 2.6 | ARCHITECTURE: 64-BIT STATION LIBRARY";
            position: absolute;
            bottom: 3px;
            right: 15px;
            font-size: 10px;
            color: var(--bp-line-dim);
            letter-spacing: 1px;
        }

        .header h1 {
            margin: 0;
            font-size: 20px;
            letter-spacing: 1.5px;
            text-transform: uppercase;
            font-weight: 800;
        }
        .header .meta {
            font-size: 12px;
            color: var(--bp-line-dim);
            margin-top: 4px;
        }

        .nav-tools {
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
            align-items: center;
        }
        .btn {
            background-color: var(--bp-bg);
            border: 1px solid var(--bp-line);
            color: var(--bp-line);
            padding: 7px 12px;
            font-family: inherit;
            font-size: 12px;
            font-weight: 700;
            cursor: pointer;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            transition: all 0.15s ease;
            text-transform: uppercase;
        }
        .btn:hover {
            background-color: #2563eb;
            color: #ffffff;
            box-shadow: 0 0 10px rgba(59, 130, 246, 0.5);
        }
        .btn-active {
            background-color: #1e40af !important;
            border-color: #ffffff !important;
            box-shadow: 0 0 8px rgba(255,255,255,0.4);
            color: #ffffff !important;
        }

        /* Document Selector Grid (4 Cards) */
        .doc-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
            gap: 16px;
            margin-bottom: 20px;
        }
        .doc-card {
            background: #081d33;
            border: 2px solid var(--bp-border);
            padding: 16px 18px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            transition: border-color 0.2s;
        }
        .doc-card:hover {
            border-color: #ffffff;
        }
        .doc-card.selected {
            border-color: var(--data-green);
            background: #0c2d54;
            box-shadow: 0 0 12px rgba(34, 197, 94, 0.4);
        }
        .doc-title {
            font-size: 14px;
            font-weight: 800;
            color: #ffffff;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .doc-desc {
            font-size: 11.5px;
            color: var(--bp-line-dim);
            line-height: 1.5;
            margin-bottom: 14px;
        }
        .doc-actions {
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
        }

        /* Embedded Reader Frame */
        .viewer-container {
            background: var(--bp-card-bg);
            border: 2px solid var(--bp-line);
            box-shadow: 0 4px 20px rgba(0,0,0,0.4);
            display: flex;
            flex-direction: column;
            flex: 1;
            min-height: 650px;
        }
        .viewer-toolbar {
            background: #0d2847;
            padding: 10px 18px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 10px;
            border-bottom: 1px solid var(--bp-border);
        }
        .viewer-title {
            font-size: 13px;
            font-weight: bold;
            color: var(--data-cyan);
            letter-spacing: 0.5px;
        }
        .doc-iframe {
            width: 100%;
            height: 850px;
            border: none;
            background: #ffffff;
        }

        @media print {
            body { background: white !important; color: black !important; }
            .header, .nav-tools, .doc-grid, .viewer-toolbar { display: none !important; }
            .doc-iframe { height: 100% !important; }
        }
    </style>
</head>
<body>

    <!-- Technical Header with all 7 Buttons -->
    <div class="header">
        <div>
            <h1>RF-KIT Documentation &amp; Reference Library</h1>
            <div class="meta">STATION CALLSIGN: K7BIT | ARCHITECTURE: 64-BIT AARCH64 DOCUMENTATION REPOSITORY</div>
        </div>
        <div class="nav-tools">
            <a href="/docs" class="btn btn-active">📖 Station Docs</a>
            <a href="/antenna" class="btn">🗺️ Antenna Mapper</a>
            <a href="/health" class="btn">📈 Health Monitor</a>
            <a href="/screen" class="btn">📺 Remote Screen</a>
            <a href="/backup" class="btn">💾 SD Backup</a>
            <a href="/report" class="btn">📋 System Report</a>
            <a href="/logs" class="btn">📜 Log Viewer</a>
        </div>
    </div>

    <!-- Document Selection Grid: 4 Unified Cards (View in HTML + Download PDF) -->
    <div class="doc-grid">
        <!-- Card 1: User's & Operator's Guide -->
        <div class="doc-card selected" id="card-ug">
            <div>
                <div class="doc-title">📘 JRFK Operator's Manual &amp; Architecture Guide</div>
                <div class="doc-desc">
                    Comprehensive operational manual: JRFK.exe dual-architecture, GOLD data migration matrix, 7 post-migration web diagnostic tools, 3-boot visual verification, and automated Sunday autopatching.
                </div>
            </div>
            <div class="doc-actions">
                <button class="btn" style="border-color:var(--data-green); color:var(--data-green);" onclick="loadDoc('/docs/JRFK_Users_Guide.html', 'JRFK Operator\'s Manual & Architecture Guide', 'card-ug')">📖 View Document</button>
                <a href="/docs/JRFK_Users_Guide.pdf" target="_blank" class="btn">⬇️ Download PDF</a>
            </div>
        </div>

        <!-- Card 2: Engineering Manual (EM) -->
        <div class="doc-card" id="card-em">
            <div>
                <div class="doc-title">⚙️ JRFK Engineering Manual</div>
                <div class="doc-desc">
                    Exhaustive engineering manual detailing pure-Python SimpleRPC schemas, Python 3.13 deprecation patches, Full KMS DRM 1024x600 modelines, and 60°C thermal guard state machine dynamics.
                </div>
            </div>
            <div class="doc-actions">
                <button class="btn" style="border-color:var(--data-green); color:var(--data-green);" onclick="loadDoc('/docs/JRFK_EM.html', 'JRFK Engineering Manual', 'card-em')">📖 View Document</button>
                <a href="/docs/JRFK_EM.pdf" target="_blank" class="btn">⬇️ Download PDF</a>
            </div>
        </div>

        <!-- Card 3: Disaster Recovery Procedure -->
        <div class="doc-card" id="card-dr">
            <div>
                <div class="doc-title">🚨 Disaster Recovery Procedure</div>
                <div class="doc-desc">
                    Emergency "Swap, Boot, Reboot, Run" card. Rapid recovery walkthrough for primary MicroSD failure using the secondary automated USB backup card (under 3 minutes target recovery time).
                </div>
            </div>
            <div class="doc-actions">
                <button class="btn" style="border-color:var(--data-green); color:var(--data-green);" onclick="loadDoc('/docs/JRFK_Disaster_Recovery.html', 'Disaster Recovery & Field Hot-Swap Procedure', 'card-dr')">📖 View Document</button>
                <a href="/docs/JRFK_Disaster_Recovery.pdf" target="_blank" class="btn">⬇️ Download PDF</a>
            </div>
        </div>

        <!-- Card 4: Hardware Alignment & Calibration Cookbook -->
        <div class="doc-card" id="card-cb">
            <div>
                <div class="doc-title">🔧 Alignment &amp; Calibration Cookbook</div>
                <div class="doc-desc">
                    K7BIT hardware calibration guide: 9 potentiometer adjustment procedures (R1, R2, R14, R15, R17, R19, R20, R21, SPARE), 17-step precision calibration procedure, and 10-part bench test verification suite.
                </div>
            </div>
            <div class="doc-actions">
                <button class="btn" style="border-color:var(--data-green); color:var(--data-green);" onclick="loadDoc('/docs/JRFK_Cookbook.html', 'K7BIT Hardware Alignment & Calibration Cookbook', 'card-cb')">📖 View Document</button>
                <a href="/docs/JRFK_Cookbook.pdf" target="_blank" class="btn">⬇️ Download PDF</a>
            </div>
        </div>
    </div>

    <!-- Embedded Reader Frame with Dedicated Toolbar Controls -->
    <div class="viewer-container">
        <div class="viewer-toolbar">
            <span class="viewer-title" id="activeDocTitle">ACTIVE DOCUMENT: JRFK OPERATOR'S MANUAL &amp; ARCHITECTURE GUIDE</span>
            <div style="display:flex; gap:8px;">
                <button class="btn" style="padding:5px 10px; font-size:11px;" onclick="reloadFrame()">🔄 Reload</button>
                <button class="btn" style="padding:5px 10px; font-size:11px;" onclick="openExternal()">🌐 Open Full Window</button>
                <button class="btn" style="padding:5px 10px; font-size:11px;" onclick="printDoc()">🖨️ Print Document</button>
            </div>
        </div>
        <iframe id="docFrame" class="doc-iframe" src="/docs/JRFK_Users_Guide.html"></iframe>
    </div>

    <script>
        let currentDocUrl = '/docs/JRFK_Users_Guide.html';

        function loadDoc(url, title, cardId) {
            currentDocUrl = url;
            let frame = document.getElementById('docFrame');
            frame.src = url;
            document.getElementById('activeDocTitle').innerText = `ACTIVE DOCUMENT: ${title.toUpperCase()}`;

            document.querySelectorAll('.doc-card').forEach(c => c.classList.remove('selected'));
            let activeCard = document.getElementById(cardId);
            if (activeCard) activeCard.classList.add('selected');
        }

        function reloadFrame() {
            let frame = document.getElementById('docFrame');
            frame.src = currentDocUrl;
        }

        function openExternal() {
            window.open(currentDocUrl, '_blank');
        }

        function printDoc() {
            let frame = document.getElementById('docFrame');
            try {
                frame.contentWindow.print();
            } catch (e) {
                window.open(currentDocUrl, '_blank');
            }
        }
    </script>
</body>
</html>
"""
    out_path = os.path.join(STATIC_DIR, "docs_viewer.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print("Generated docs_viewer.html")

def update_em_document():
    """Updates JRFK_EM.md and JRFK_EM.html with hardware changes and clean math."""
    md_path = os.path.join(DOCS_DIR, "JRFK_EM.md")
    html_path = os.path.join(DOCS_DIR, "JRFK_EM.html")

    with open(md_path, "r", encoding="utf-8") as f:
        md_text = f.read()

    # Hardware & Title updates in Markdown
    # 1. Update Title
    md_text = md_text.replace(
        "# RFK2K+ / RFK2K-S: 32-Bit to 64-Bit Raspberry Pi OS Migration & Tools Upgrade for RPi 4 or RPi 5 Manual",
        "# RF-KIT Linear Amplifier: JRFK Engineering Manual (32-Bit to 64-Bit Architecture, SimpleRPC & Hardware Reference)"
    )
    md_text = md_text.replace("Engineering Specification", "Engineering Manual")

    # 2. Power Supply: Heiwoo 53.5V Switching Power Supply, no CAN bus PSU control
    md_text = md_text.replace("Eltek Flatpack2 48/3000 HE", "Heiwoo 53.5V Switching Power Supply")
    md_text = md_text.replace("Eltek Flatpack2 48V/3000W HE (High Efficiency)", "Heiwoo 53.5V Switching Power Supply")
    md_text = md_text.replace("Eltek Flatpack2", "Heiwoo 53.5V Power Supply")
    md_text = md_text.replace("Eltek", "Heiwoo")

    # CAN bus explanation: clarify NOT used for PSU
    md_text = md_text.replace(
        "CAN bus controlled voltage setpoint (125 kbps).",
        "Hardware AC line switching & discrete inhibit (CAN bus not used for power supply in production units)."
    )
    md_text = md_text.replace(
        "* **CAN Bus Communication Protocol:** The Eltek Flatpack2 communicates over CAN bus at 125 kbps using identifier `0x05004804`. The controller transmits periodic keep-alive and voltage target frames:\n  `[0x05, 0x00, 0x48, 0x04, Data: 0x14, 0xE6, 0x00, 0x00]` setting rail voltage to 53.50 VDC.",
        "* **Power Supply Control Architecture:** Production units utilize discrete hardware AC line switching and standby/operate inhibit control lines. CAN bus communication is **NOT** used for power supply control in production units; the Heiwoo PSU operates autonomously with hardware over-voltage, over-current, and thermal shutdown protections."
    )

    # 3. LDMOS: Ampleon BLF189 / BLF189XR
    md_text = md_text.replace("MRFE6VP11KH", "Ampleon BLF189 / BLF189XR")

    # 4. Clean LaTeX in Markdown
    md_text = md_text.replace(r"$L$", "<i>L</i>").replace(r"$C$", "<i>C</i>")
    md_text = md_text.replace(r"$T < 50.0^\circ\text{C}$", "<i>T</i> < 50.0°C")
    md_text = md_text.replace(r"^\circ\text{C}", "°C").replace(r"^\circ C", "°C").replace(r"^\circ", "°")

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_text)
    print("Updated JRFK_EM.md")

    # Now update JRFK_EM.html
    with open(html_path, "r", encoding="utf-8") as f:
        html_text = f.read()

    html_text = html_text.replace(
        "RFK2K+ / RFK2K-S: 32-Bit to 64-Bit Raspberry Pi OS Migration & Tools Upgrade for RPi 4 or RPi 5 Manual",
        "RF-KIT Linear Amplifier: JRFK Engineering Manual (32-Bit to 64-Bit Architecture, SimpleRPC & Hardware Reference)"
    )
    html_text = html_text.replace("Engineering Specification", "Engineering Manual")
    html_text = html_text.replace("Eltek Flatpack2 48/3000 HE", "Heiwoo 53.5V Switching Power Supply")
    html_text = html_text.replace("Eltek Flatpack2", "Heiwoo 53.5V Power Supply")
    html_text = html_text.replace("Eltek", "Heiwoo")
    html_text = html_text.replace("MRFE6VP11KH", "Ampleon BLF189 / BLF189XR")
    html_text = html_text.replace(r"$L$", "<i>L</i>").replace(r"$C$", "<i>C</i>")
    html_text = html_text.replace(r"$T < 50.0^\circ\text{C}$", "<i>T</i> &lt; 50.0°C")
    html_text = html_text.replace(r"$T &lt; 50.0^\circ\text{C}$", "<i>T</i> &lt; 50.0°C")
    html_text = html_text.replace(r"^\circ\text{C}", "°C").replace(r"^\circ C", "°C").replace(r"^\circ", "°")
    html_text = html_text.replace("CAN bus controlled voltage setpoint", "Hardware AC switching & discrete inhibit (CAN bus not used for power supply in production units)")

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_text)
    print("Updated JRFK_EM.html")

def compile_all_pdfs():
    """Compiles all HTML docs into PDFs using headless Chrome."""
    docs = [
        "JRFK_Users_Guide",
        "JRFK_EM",
        "JRFK_Disaster_Recovery",
        "JRFK_Cookbook"
    ]
    for doc in docs:
        html_file = os.path.join(DOCS_DIR, f"{doc}.html")
        pdf_file = os.path.join(DOCS_DIR, f"{doc}.pdf")
        if not os.path.exists(html_file):
            print(f"File not found: {html_file}")
            continue
        print(f"Compiling {doc}.pdf...")
        cmd = [
            CHROME,
            "--headless",
            "--disable-gpu",
            "--no-pdf-header-footer",
            f"--print-to-pdf={pdf_file}",
            html_file
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if os.path.exists(pdf_file) and os.path.getsize(pdf_file) > 1000:
            print(f"  [SUCCESS] {doc}.pdf: {os.path.getsize(pdf_file):,} bytes")
        else:
            print(f"  [FAIL] Failed to compile {doc}.pdf: {res.stderr}")

def sync_to_dist():
    """Copies all doc files to D:\\JRFK\\docs."""
    os.makedirs(DIST_DIR, exist_ok=True)
    for fname in os.listdir(DOCS_DIR):
        src = os.path.join(DOCS_DIR, fname)
        dst = os.path.join(DIST_DIR, fname)
        if os.path.isfile(src):
            shutil.copy2(src, dst)
    print(f"Synchronized docs to {DIST_DIR}")

if __name__ == "__main__":
    print("--- 1. Building Users Guide ---")
    build_users_guide()
    print("--- 2. Building Alignment & Calibration Cookbook ---")
    build_cookbook()
    print("--- 3. Updating Engineering Manual ---")
    update_em_document()
    print("--- 4. Updating docs_viewer.html ---")
    build_docs_viewer()
    print("--- 5. Compiling PDFs via Headless Chrome ---")
    compile_all_pdfs()
    print("--- 6. Synchronizing to docs distribution ---")
    sync_to_dist()
    print("--- Documentation Build Complete ---")
