import glob
import os
import json

list_of_files = glob.glob('./*.json')
latest_file = max(list_of_files, key=os.path.getctime)

try:
    with open(latest_file , 'r') as f: 
        global data
        data = json.load(f)
    f.close
except:
    print("No test report !!")

try:
    os.remove(latest_file)
except OSError as e:
    print(e)
else:
    print("File is deleted successfully")

try:
    with open('test_report.json', 'w') as f:
        json.dump(data, f, sort_keys=True)
    f.close
except:
    print("Change name fail !!")