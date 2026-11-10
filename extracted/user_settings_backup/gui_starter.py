import json
import os
import sys
from datetime import datetime


arg_string = ''
print(arg_string, flush=True)
for idx, arg in enumerate(sys.argv):
    if idx > 0:
        arg_string = arg_string + ' ' + arg

start_folder = None
fallback_folder = None
with open('./gui_path.json') as json_file:
    json_data = json.load(json_file)
    start_folder = json_data["start"]
    fallback_folder = json_data["fallback"]

do_fallback = False
os.chdir(start_folder)
while True:
    ts = datetime.now()
    print("\n\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n\n", flush=True)
    return_value = os.system('python3 main.py' + arg_string)
    print("\n\n")
    print('{}/main.py exited with status {}'.format(start_folder, return_value))
    runtime = datetime.now() - ts
    print('run duration was {}'.format(runtime), flush=True)
    if return_value == 0:
        break
    else:
        if runtime.total_seconds() < 3:
            do_fallback = True
            break

if do_fallback:
    os.chdir(fallback_folder)
    while True:
        ts = datetime.now()
        print("\n\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n\n", flush=True)
        return_value = os.system('python3 main.py' + arg_string)
        print("\n\n")
        print('{}/main.py exited with status {}'.format(fallback_folder, return_value))
        runtime = datetime.now() - ts
        print('run duration was {}'.format(runtime), flush=True)
        if return_value == 0:
            break
        else:
            if runtime.total_seconds() < 3:
                break
