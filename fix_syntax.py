import shutil

path = 'D:/JRFK/JRFK_32_to_64Bit_Migration_tool.htm'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

# Fix mismatched backtick/single-quote
text = text.replace("fetch(`${API_BASE}/api/tools')", "fetch(`${API_BASE}/api/tools`)")
text = text.replace("fetch(`${API_BASE}/api/install_imager', { method: 'POST' })", "fetch(`${API_BASE}/api/install_imager`, { method: 'POST' })")
text = text.replace("fetch(`${API_BASE}/api/launch_imager', { method: 'POST' })", "fetch(`${API_BASE}/api/launch_imager`, { method: 'POST' })")
text = text.replace("fetch(`${API_BASE}/api/disks')", "fetch(`${API_BASE}/api/disks`)")
text = text.replace("fetch(`${API_BASE}/api/logs')", "fetch(`${API_BASE}/api/logs`)")
text = text.replace("fetch(`${API_BASE}/api/extract_golden_master',", "fetch(`${API_BASE}/api/extract_golden_master`,")
text = text.replace("fetch(`${API_BASE}/api/start_clean_build',", "fetch(`${API_BASE}/api/start_clean_build`,")

with open(path, 'w', encoding='utf-8') as f:
    f.write(text)

shutil.copyfile(path, 'D:/JRFK/tools/migrator/JRFK_32_to_64Bit_Migration_tool.htm')
print('Fixed mismatched quote syntax and mirrored successfully.')
