import shutil

path = 'D:/JRFK/JRFK_32_to_64Bit_Migration_tool.htm'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

# Add API_BASE at the top of script
old_vars = 'let detectedDisks = [];\nlet logPollTimer = null;'
new_vars = """const API_BASE = (window.location.protocol === 'file:' || window.location.port !== '8089') ? 'http://127.0.0.1:8089' : '';
let detectedDisks = [];
let logPollTimer = null;"""

text = text.replace(old_vars, new_vars)

# Replace all fetch('/api/ with fetch(`${API_BASE}/api/
text = text.replace("fetch('/api/", "fetch(`${API_BASE}/api/")

# Enhance checkTools error handling to flag offline server
old_catch = 'console.warn("Could not check tools:", e);'
new_catch = """console.warn("Could not check tools:", e);
    const hostPill = document.getElementById('hostPill');
    if (hostPill) {
      hostPill.textContent = '▲ Server Offline (Launch JRFK_Migrator.bat)';
      hostPill.classList.remove('ok');
    }"""

text = text.replace(old_catch, new_catch)

# Also update hostPill to ok when checkTools succeeds
old_ok = 'if (data.imager_installed) {'
new_ok = """const hostPill = document.getElementById('hostPill');
      if (hostPill) {
        hostPill.textContent = '● Backend Server Connected (:8089)';
        hostPill.classList.add('ok');
      }
      if (data.imager_installed) {"""

text = text.replace(old_ok, new_ok)

with open(path, 'w', encoding='utf-8') as f:
    f.write(text)

shutil.copyfile(path, 'D:/JRFK/tools/migrator/JRFK_32_to_64Bit_Migration_tool.htm')
print('Updated HTML and mirrored successfully.')
