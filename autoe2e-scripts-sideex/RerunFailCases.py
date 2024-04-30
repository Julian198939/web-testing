import os
import json
import ast
import sys

# 輸入設定包含了平台(plt)和 JSON 清單(list_of_json)
plt = sys.argv[1]
list_of_json = ast.literal_eval(sys.argv[2])

print('傳入的資料型態是: {}'.format(type(list_of_json)))
print('您輸入的是 Testcase 名稱: {}'.format(list_of_json))

new_list_of_json = []  # 將輸入的 Cases 取得前面的編號放入新的 list
temp = []  # 存放路徑的 list

# 取得符合 plt 的資料夾路徑
find_files = "./{}/".format(plt)
print(os.listdir(os.curdir))

# 提取 list_of_json 中符合命名規則的前綴編號
for suites_son in list_of_json:
    if suites_son[4] == "_" and suites_son[5].isnumeric():
        new_list_of_json.append(suites_son[0:6])
    else:
        new_list_of_json.append(suites_son[0:4])

new_list_of_json = list(set(new_list_of_json))
new_list_of_json = sorted(new_list_of_json)

# 尋找符合 list_of_json 清單中的字串開頭的 JSON 檔案
for root, dirs, files in os.walk(find_files):
    for filename in files:
        if filename[4] == "_" and filename[5].isnumeric():
            for i in new_list_of_json:
                print("現在路徑:{}".format(root))
                print("所有輸入的:{}".format(new_list_of_json))
                print("檔案名稱前六字元:{}".format(filename[0:6]))
                if i == filename[0:6]:
                    temp.append(os.path.join(root, filename))
        else:
            for i in new_list_of_json:
                print(root)
                if i == filename[0:4]:
                    temp.append(os.path.join(root, filename))
temp.append("./"+ plt +"/COMMON.json")
print("Testcase 所在的檔案位置是: {}".format(temp))

# 讀取 config.json 檔案
with open('config.json', 'r') as f:
    data = json.load(f)
    # 把搜尋到的檔案路徑放到 config.json 檔案中的 testSuites 欄位
    data["input"]["testSuites"] = ""
    # 設定 report 檔案路徑
    data["report"]["path"] = "./test_report/{}/".format(plt)
    f.close()

# 將更新後的 config.json 寫入檔案
with open('config0.json', 'w') as f:
    data["input"]["testSuites"] = temp
    json.dump(data, f, sort_keys=True)
    f.close()