import os
import json
import sys

plt = sys.argv[1]
path = sys.argv[2]
current_path = os.path.dirname(os.path.abspath(__file__))
result = []
list_of_files = []
dir_path = "{}/suites/{}/{}".format(current_path, plt, path)
for filename in os.listdir(dir_path):
    if filename.endswith(".json"):
        list_of_files.append(os.path.join(dir_path, filename))

with open('config.json', 'r') as f:
    global data
    data = json.load(f)
    data["input"]["testSuites"] = list_of_files
    data["report"]["path"] = current_path + "/test_report/{}/".format(plt)
f.close()

with open('config.json', 'w') as f:
    json.dump(data, f, sort_keys=True)
f.close()
