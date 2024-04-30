import os
import json
import sys
import argparse

# 從命令行參數中獲取平台名稱和分割數量
plt = sys.argv[1]
split_number = sys.argv[2]

# 只跑特定的 Suite，須同步修改 pipeline 增加給第三個參數，參數格式字串如 W311,W302,W323
mySuite = []
if len(sys.argv) > 3:
    mySuite = (sys.argv[3]).split(',')

# 創建命令行參數解析器
parser = argparse.ArgumentParser()
parser.add_argument("plt", help="platform name")
parser.add_argument("split_number", help="split number")
parser.add_argument("mySuite", help="running suites")
parser.add_argument("-s", "--split", help="Output split suites to json", action="store_true")
args = parser.parse_args()

result = []
dir_path = "./{}/".format(plt)

# 不要計入切分的數量中的檔案名稱，eg.共用檔
skipSplit = ['COMMON']

# 遞迴地搜索當前資料夾及其子資料夾中的所有 JSON 檔案，當有指定 suite 時過濾出特定檔名，如果是"ALL"就全部都列出。
json_files = []
# 計算切分檔案大小
all_files = []
total_size = 0
for root, dirs, files in os.walk(dir_path):
    for file in files:
        if file.endswith('.json') and (file[0:6] in skipSplit)==False:
            if mySuite[0] != "ALL" :
                # 針對前四個字元判斷，符合的才列出
                if file[0:4] in mySuite :
                    file_path = os.path.join(root, file).replace('.json', '')
                    json_files.append((file_path + '.json', os.path.getsize(file_path + '.json')))
            else:
                # 全部都列出
                file_path = os.path.join(root, file).replace('.json', '')
                json_files.append((file_path + '.json', os.path.getsize(file_path + '.json')))

print(json_files)

#======================================================
# 設置 split_slave.json 的格式，以了解分割後的套件組
#======================================================
split_output = {
    "input": {
        "testsuites": []
    }
}

#===========
# 主要程式碼
#===========
if split_number == None or split_number == 0:
    result = json_files
    split_number = 1
    print(f"Splitting into 1 file with all {len(json_files)} json files")
    print("result1:", result)
    list_of_files = json_files
else:
    split_number = int(split_number)
    json_file_number = len(json_files)
    print(f"Splitting into {split_number} files with {json_file_number // split_number} files per split")
    if split_number > json_file_number:
        print("Error: split number should be smaller than or equal to the number of json files.")
        exit()
    # 以下為依照檔案大小做切分
    partitioned_files = [[] for _ in range(split_number)]
    all_files.extend(json_files)
    # 根據檔案大小排序
    all_files.sort(key=lambda x: x[1])
    # 進行均分
    for i, file_info in enumerate(all_files):
        partitioned_files[i % split_number].append(file_info[0])
    # 印出分割區塊檔案大小總和
    for i, partition_files in enumerate(partitioned_files):
        total_size = sum(file_info[1] for file_info in filter(lambda x: x[0] in partition_files, all_files))
        print(f'Partition {i + 1}: {partition_files} 此 Test suites 檔案大小總和= {total_size / (1024 * 1024):.2f}MB')
    if not os.path.exists("config_splitted"):
        os.makedirs("config_splitted")
    for i in range(split_number):
        list_of_files = partitioned_files[i]
        # 增加共用檔
        list_of_files.append("./"+ plt +"/COMMON.json")
        # 寫入各config檔
        with open('./autoe2e-scripts-sideex/config.json', 'r', encoding="utf-8") as f:
            global data
            data = json.load(f)
            list_of_files = [file for file in list_of_files]
            data["input"]["testSuites"] = list_of_files
            data["report"]["path"] = os.path.join("./test_report", plt)
        f.close()
        new_slave_json = 'config_splitted/config{}.json'.format(i)
        with open(new_slave_json, 'w') as f:
            json.dump(data, f, sort_keys=True)
        f.close()
