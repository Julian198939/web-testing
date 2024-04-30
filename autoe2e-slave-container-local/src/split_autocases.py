import os
import json
import sys

plt = sys.argv[1]
path = sys.argv[2]
split_number = int(sys.argv[3])

current_path = os.path.dirname(os.path.abspath(__file__))
result = []
dir_path = "{}/suites/{}/{}/".format(current_path, plt, path)
json_files = [dir_path + file for file in os.listdir(dir_path) if file.endswith('.json')]
json_file_number = len(json_files)
global data

if split_number == None or split_number == 0:
    result = json_files
    with open('config.json', 'r') as f:
            data = json.load(f)
            data["input"]["testSuites"] = result
            data["report"]["path"] = current_path + "/test_report/{}/".format(plt)
    f.close()
    with open('config.json', 'w') as f:
        json.dump(data, f, sort_keys=True)
    f.close()
else:
    print(f"Splitting into {split_number} files with {json_file_number // split_number} files per split")    
    # split json files into split_number parts
    if split_number > json_file_number:
        print("Error: split number should be smaller than or equal to the number of json files.")
        exit()
    remainder = json_file_number % split_number
    start = 0
    end = 0
    for i in range(1, split_number+1):
        end += json_file_number // split_number
        if remainder > 0:
            end += 1
            remainder -= 1
        result.append(json_files[start:end])
        start = end
    # create result1, result2, result3, ... based on the number of splits
    for i in range(split_number):
        exec(f"result{i+1} = result[i]")
        with open('config.json', 'r') as f:
            data = json.load(f)
            data["input"]["testSuites"] = result[i]
            data["report"]["path"] = current_path + "/test_report/{}/".format(plt)
        f.close()
        with open('config{}.json'.format(i), 'w') as f:
            json.dump(data, f, sort_keys=True)
        f.close()
