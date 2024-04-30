# SQA Web 自動化測試

## Git 分支命名規則

- 當有需要對此repo做更動時需創建分支來修改，修改完成後請發PR請求merge到main，分支命名規則如下:

### **Category**

|Category|用途|
|-|-|
|`feature`|用於一般需求開發、新增功能、刪除功能、重構、文件|
|`bugfix`|用於 BUG 修復|
|`hotfix`|用於緊急情況的暫時性調整，後續可能需要透過 `bugfix` 或 `feature` 重新發佈解決方案|
|`test`|用於實驗或測試性質|

### **Description**

在 category 之後使用 `/` 分隔

簡短描述該分支目的或專案標題，並以全部小寫的 kebab-case 串燒式命名

```shell
git branch category/description-in-kebab-case
```

範例:

```shell
git branch feature/create-foo-bar
git branch bugfix/fix-code-bug
git branch hotfix/foo-bar
git branch test/test-code-usage
```

## Web E2E testing on GCP 主要元件

- Jenkins Pipeline
    - 參數化切檔，上傳切檔後 TC 設定至 GCS
    - 部署、執行、銷毀 Cloud Run job
    - 拉回 output.json 並產製 Report
    - 發送通知到 Google Chat ，將 report.json 上傳 GCS

- Google Cloud Run job
    - 從 GCS 拉回 TC 設定 (configX.json)
    - 執行 Rapi TC ( 或 dry-run )
    - 推送 output.json 至 GCS

- Google Cloud Storage ([e2e-testing-sideex](https://console.cloud.google.com/storage/browser/e2e-testing-sideex))
    - 存放 TC 設定
    - 存放 output.json
    - 存放 report.json


## 主要目錄結構說明

[autoe2e-handler](/autoe2e-handler)：腳本切檔、產製報表用 Python 程式。

[autoe2e-scripts-sideex](/autoe2e-scripts-sideex)：Rapi 腳本檔。

[autoe2e-slave-container](/autoe2e-slave-container)：Rapi Container 部署於 Google Cloud Run Job，執行 Test Case。

[autoe2e-slave-container-local](/autoe2e-slave-container-local)：Rapi Container 部署於本地 docker 環境執行 Test Case 測試開發使用。

[jenkins-pipeline](/jenkins-pipeline)：Jenkins pipeline script。命名方式：jenkinsfile-<JobId> eg. jenkinsfile-rapi-automated-testing。

```bash
├── README.md
├── autoe2e-handler
│   ├── dashboard                               # 儀錶板資料同步程式資料夾
│   ├── reports                                 # 測試結果處理程式資料夾
│   ├── splitter                                # 分割腳本設定檔程式資料夾
│   └── testlodge                               # TestLodge 相關處理程式資料夾
├── autoe2e-scripts-sideex
│   ├── mobile_web                              # Rapi mobile-web 腳本資料夾
│   ├── web                                     # Rapi web 腳本資料夾
│   ├── config.json                             # Rapi 執行環境設定
│   └── globalvar.json                          # Rapi 腳本共用變數
├── autoe2e-slave-container                     # GCP Cloud Run Job 使用
│   ├── Dockerfile
│   ├── src
│   │   ├── rapi-runner-linux                   # Rapi runner 執行程式
│   │   └── selenium-server-4.18.1.jar          # Selenium server 執行程式
│   └── start.sh
├── autoe2e-slave-container-local               # 本地開發用 docker
└── jenkins-pipeline                            # Jenkins pipeline 正式執行用
    └── jenkinsfile-rapi-automated-testing
```

## 創建 Rapi runner image
- 使用 [GitHub Actions](/.github/workflows/build-and-upload.yaml) 執行

## Image History
- Image URL: https://console.cloud.google.com/artifacts/docker/pchomeec-devops/asia/asia.gcr.io/rapi-runner?project=pchomeec-devops
