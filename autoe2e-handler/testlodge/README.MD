# SQA Testlodge api說明文件

## 主要檔案
```
├── Logger.py
├── PyLodge.py
├── Create_test_run_dic.py
├── Mark_and_Create.py
├── testlodge_button_trigger_autoe2e(在cloud function上)
```

## 檔案個別用途

### 1. Logger.py

- 在執行```Create_test_run_dic.py```及```Mark_and_Create.py```時會記錄狀態成txt檔

### 2. Pylodge.py

- Testlodge api function
- [Testlodge api spec](<https://help.testlodge.com/hc/en-us/categories/203830188-TestLodge-API>)
- [參考文獻](<https://github.com/akondapalli/pylodge>)

### 3. Create_test_run_dic.py

- 在Testlodge上[回歸測試專案](<https://app.testlodge.com/a/35254/projects/52624/runs>)創建自動化測試所需之test run

### 4. Mark_and_Create.py

- 執行完回歸測試後寫入測試狀態(Pass、Fail、Skip)在該test run中

### 5. testlodge_button_trigger_autoe2e(在cloud function上)

- Chrome擴充套件會驅動Rerun功能，主程式在[傳送門](<https://console.cloud.google.com/functions/details/asia-east1/testlodge_button_trigger_autoe2e?env=gen1&project=pchomeec-devops&tab=source>)

## Note

1. 若需修改打Testlodge api的使用者請在```Create_test_run_dic.py```、```Mark_and_Create.py```及```testlodge_button_trigger_autoe2e```把有呼叫```Pylodge()```的參數改成該使用者帳號及Testlodge api key，e.q. 
```
Pylodge(example@gmail.com, your_testlodge_api_key, 其他參數)
```
在```Pylodge.py```中的Authorization也需替換為該使用者之Authorization code，如何取得Authorization code [傳送門](<https://app.asana.com/0/1203389441591659/1206295773149977/f>)