import os
import json
import sys

plt = sys.argv[1]
list_of_files = []
test_suites_str = sys.argv[2]
test_suites = test_suites_str.split(",")
# W101_1首頁header版面元素確認.json,W205_路標頁_影音專區.json

dir_path = "./suites/{}/".format(plt)

if test_suites_str == 'empty':
    print('Please enter test_suites_str!!!')
    sys.exit(1)
else:
    for root, dirs, files in os.walk(dir_path):
        for filename in files:
            if filename in test_suites:
                list_of_files.append(os.path.join(root, filename))
    with open('config.json', 'r') as f:
        global data
        data = json.load(f)
        list_of_files = [os.path.join(dir_path, file) for file in list_of_files]
        data["input"]["testSuites"] = list_of_files
        data["report"]["path"] = os.path.join("./test_report", plt)
        f.close()
    new_slaff_json = 'config_test.json'
    with open(new_slaff_json , 'w') as f:
        json.dump(data, f, sort_keys=True)
    f.close()