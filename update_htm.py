import re
import shutil

html_path = 'D:/JRFK/JRFK_32_to_64Bit_Migration_tool.htm'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Update top bar pills
old_pills = '''    <div class="pill ok" id="hostPill">● Windows 11 Host Ready</div>
    <div class="pill" id="sdPill">○ Target SD: None Detected</div>'''

new_pills = '''    <div class="pill ok" id="hostPill">● Windows 11 Host Ready</div>
    <div class="pill" id="imagerPill">○ Imager: Checking...</div>
    <div class="pill" id="adminPill">○ Admin: Checking...</div>
    <div class="pill" id="sdPill">○ Target SD: None Detected</div>'''

if old_pills in html:
    html = html.replace(old_pills, new_pills)
    print("Updated topbar pills.")

# 2. Update Migrate button row
old_btn_flash = '''        <div style="display:flex; gap:8px; margin-top:6px;">
          <button class="btn-primary" id="btnFlash" onclick="buildTargetImage()">
            ⚡ Build & Flash 64-Bit Appliance Image
          </button>
          <button class="btn-secondary" onclick="ejectTargetCard()">⏏️ Safely Eject</button>
        </div>'''

new_btn_flash = '''        <div style="display:flex; gap:8px; margin-top:6px; flex-wrap:wrap;">
          <button class="btn-primary" id="btnFlash" onclick="buildTargetImage()">
            ⚡ Build & Flash 64-Bit Appliance Image
          </button>
          <button class="btn-secondary" onclick="launchImagerGui()">
            🚀 Open RPi Imager (64-Bit)
          </button>
          <button class="btn-secondary" onclick="scanDisks()">🔄 Rescan</button>
          <button class="btn-secondary" onclick="ejectTargetCard()">⏏️ Safely Eject</button>
        </div>'''

if old_btn_flash in html:
    html = html.replace(old_btn_flash, new_btn_flash)
    print("Updated migrate button row.")

# 3. Update Fresh button row
old_btn_fresh = '''        <div style="display:flex; gap:8px;">
          <button class="btn-success" id="btnFreshBuild" onclick="buildFreshSystem()">
            🚀 Partition, Format & Build 64-Bit System
          </button>
          <button class="btn-secondary" onclick="scanDisks()">🔄 Rescan Drives</button>
          <button class="btn-secondary" onclick="ejectTargetCard()">⏏️ Eject</button>
        </div>'''

new_btn_fresh = '''        <div style="display:flex; gap:8px; flex-wrap:wrap;">
          <button class="btn-success" id="btnFreshBuild" onclick="buildFreshSystem()">
            🚀 Partition, Format & Build 64-Bit System
          </button>
          <button class="btn-secondary" onclick="launchImagerGui()">
            🖥️ Open RPi Imager GUI
          </button>
          <button class="btn-secondary" onclick="scanDisks()">🔄 Rescan Drives</button>
          <button class="btn-secondary" onclick="ejectTargetCard()">⏏️ Eject</button>
        </div>'''

if old_btn_fresh in html:
    html = html.replace(old_btn_fresh, new_btn_fresh)
    print("Updated fresh button row.")

# 4. Replace the JavaScript section from scanDisks down to ejectTargetCard
old_js_start = "async function scanDisks() {"
old_js_end = "function ejectTargetCard() {"

new_js = '''let detectedDisks = [];
let logPollTimer = null;

async function checkTools() {
  try {
    const res = await fetch('/api/tools');
    if (res.ok) {
      const data = await res.json();
      const imagerPill = document.getElementById('imagerPill');
      const adminPill = document.getElementById('adminPill');
      
      if (data.imager_installed) {
        imagerPill.textContent = '● RPi Imager: Ready';
        imagerPill.classList.add('ok');
      } else {
        imagerPill.textContent = '▲ Imager: Missing (Click to Install)';
        imagerPill.classList.remove('ok');
        imagerPill.onclick = installImagerLocally;
        imagerPill.style.cursor = 'pointer';
      }

      if (data.is_admin) {
        adminPill.textContent = '● Admin: Elevated';
        adminPill.classList.add('ok');
      } else {
        adminPill.textContent = '○ Admin: Standard (Elevation Available)';
        adminPill.classList.remove('ok');
      }
    }
  } catch (e) {
    console.warn("Could not check tools:", e);
  }
}

async function installImagerLocally() {
  alert("Initiating silent local installation of official Raspberry Pi Imager via winget...");
  try {
    const res = await fetch('/api/install_imager', { method: 'POST' });
    const data = await res.json();
    alert(data.message || "Installation triggered.");
    setTimeout(checkTools, 5000);
  } catch (e) {
    alert("Error triggering installer: " + e);
  }
}

async function launchImagerGui() {
  try {
    const res = await fetch('/api/launch_imager', { method: 'POST' });
    const data = await res.json();
    if (data.status === 'ok') {
      logFlash("[+] Launched Raspberry Pi Imager on desktop.");
      logFresh("[+] Launched Raspberry Pi Imager on desktop.");
    } else {
      alert(data.message || "Could not launch Imager.");
    }
  } catch (e) {
    alert("Error launching Imager: " + e);
  }
}

async function scanDisks() {
  try {
    const res = await fetch('/api/disks');
    if (res.ok) {
      const data = await res.json();
      detectedDisks = data.disks || [];
      populateDrives(detectedDisks);
    } else {
      mockScan();
    }
  } catch (e) {
    mockScan();
  }
  checkTools();
}

function mockScan() {
  detectedDisks = [
    { index: 2, id: "\\\\\\\\.\\\\PHYSICALDRIVE2", model: "Generic STORAGE DEVICE (16GB SD Card)", size_gb: "15.8 GB", letter: "E:", is_sd: true },
    { index: 3, id: "\\\\\\\\.\\\\PHYSICALDRIVE3", model: "SanDisk Extreme V30 A2 (32GB Target)", size_gb: "31.9 GB", letter: "F:", is_sd: true }
  ];
  populateDrives(detectedDisks);
}

function populateDrives(drives) {
  const selOrig = document.getElementById('driveSelectOriginal');
  const selTgt = document.getElementById('driveSelectTarget');
  const selFresh = document.getElementById('driveSelectFresh');
  selOrig.innerHTML = "";
  selTgt.innerHTML = "";
  selFresh.innerHTML = "";

  if (drives.length === 0) {
    const emptyOpt = "<option value=''>No removable SD cards detected</option>";
    selOrig.innerHTML = emptyOpt;
    selTgt.innerHTML = emptyOpt;
    selFresh.innerHTML = emptyOpt;
    return;
  }

  let sdCount = 0;
  let autoSelectVal = "";

  drives.forEach(d => {
    const optText = `Disk ${d.index}: ${d.model} (${d.size_gb}) [Drive ${d.letter || 'Unmounted'}]${d.is_sd ? ' ⭐ (SD Card)' : ''}`;
    const optVal = `${d.index}|${d.letter || ''}`;

    const opt1 = document.createElement('option');
    opt1.value = optVal;
    opt1.textContent = optText;
    selOrig.appendChild(opt1);

    const opt2 = document.createElement('option');
    opt2.value = optVal;
    opt2.textContent = optText;
    selTgt.appendChild(opt2);

    const opt3 = document.createElement('option');
    opt3.value = optVal;
    opt3.textContent = optText;
    selFresh.appendChild(opt3);

    if (d.is_sd) {
      sdCount++;
      if (!autoSelectVal) autoSelectVal = optVal;
    }
  });

  if (autoSelectVal) {
    selOrig.value = autoSelectVal;
    selTgt.value = autoSelectVal;
    selFresh.value = autoSelectVal;
  }

  const sdPill = document.getElementById('sdPill');
  sdPill.textContent = `● Target SD: Ready (${sdCount > 0 ? sdCount + ' SD card(s)' : drives.length + ' drive(s)'})`;
  sdPill.classList.add('ok');
}

function startLogPolling(targetBoxId) {
  if (logPollTimer) clearInterval(logPollTimer);
  const box = document.getElementById(targetBoxId);
  box.textContent = "[*] Live background process output streaming below:\\n";

  let lastCount = 0;
  logPollTimer = setInterval(async () => {
    try {
      const res = await fetch('/api/logs');
      if (res.ok) {
        const data = await res.json();
        const logs = data.logs || [];
        if (logs.length > lastCount) {
          for (let i = lastCount; i < logs.length; i++) {
            box.textContent += `[${logs[i].time}] ${logs[i].message}\\n`;
          }
          lastCount = logs.length;
          box.scrollTop = box.scrollHeight;
        }

        if (data.job && !data.job.running) {
          if (data.job.step === 'complete') {
            document.getElementById('statusMessage').textContent = "SD Provisioning complete! Ready for amplifier deployment.";
          }
          clearInterval(logPollTimer);
          logPollTimer = null;
          const btnFresh = document.getElementById('btnFreshBuild');
          if (btnFresh) btnFresh.disabled = false;
          const btnFlash = document.getElementById('btnFlash');
          if (btnFlash) btnFlash.disabled = false;
        }
      }
    } catch (e) {
      console.warn("Log polling error:", e);
    }
  }, 700);
}

async function extractOriginalData() {
  const btn = document.getElementById('btnExtract');
  btn.disabled = true;
  const selVal = document.getElementById('driveSelectOriginal').value || "2|E:";
  const [diskIdx, driveLetter] = selVal.split('|');

  startLogPolling('extractLog');
  try {
    await fetch('/api/extract_golden_master', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ disk_index: parseInt(diskIdx || '2'), drive_letter: driveLetter || 'E:' })
    });
  } catch (e) {
    logExtract("[ERROR] Extraction failed to start: " + e);
  }
}

async function buildTargetImage() {
  const btn = document.getElementById('btnFlash');
  btn.disabled = true;
  const selVal = document.getElementById('driveSelectTarget').value || "2|E:";
  const [diskIdx, driveLetter] = selVal.split('|');

  startLogPolling('flashLog');
  try {
    await fetch('/api/start_clean_build', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        disk_index: parseInt(diskIdx || '2'),
        drive_letter: driveLetter || 'E:',
        username: 'pi',
        password: 'pi',
        hostname: 'k7bit',
        ssid: 'Shack-WiFi',
        wifipw: ''
      })
    });
  } catch (e) {
    logFlash("[ERROR] Flash failed to start: " + e);
  }
}

async function buildFreshSystem() {
  const btn = document.getElementById('btnFreshBuild');
  const user = document.getElementById('freshUsername').value || 'pi';
  const pass = document.getElementById('freshPassword').value || 'raspberry';
  const host = document.getElementById('freshHostname').value || 'k7bit';
  const ssid = document.getElementById('freshSsid').value || 'Shack-WiFi';
  const wifipw = document.getElementById('freshSsidPass').value || '';
  const selVal = document.getElementById('driveSelectFresh').value || "2|E:";
  const [diskIdx, driveLetter] = selVal.split('|');

  btn.disabled = true;
  startLogPolling('freshLog');

  try {
    const res = await fetch('/api/start_clean_build', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        disk_index: parseInt(diskIdx || '2'),
        drive_letter: driveLetter || 'E:',
        username: user,
        password: pass,
        hostname: host,
        ssid: ssid,
        wifipw: wifipw
      })
    });
    const data = await res.json();
    if (data.status !== 'ok') {
      alert("Error starting clean build: " + (data.message || "Unknown error"));
      btn.disabled = false;
    }
  } catch (e) {
    logFresh("[ERROR] Request failed: " + e);
    btn.disabled = false;
  }
}

'''

idx_start = html.find(old_js_start)
idx_end = html.find(old_js_end)
if idx_start != -1 and idx_end != -1:
    html = html[:idx_start] + new_js + html[idx_end:]
    print("Replaced JavaScript section successfully.")

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)

# Mirror to tools/migrator
shutil.copyfile(html_path, 'D:/JRFK/tools/migrator/JRFK_32_to_64Bit_Migration_tool.htm')
print("Mirrored to tools/migrator/ successfully.")
