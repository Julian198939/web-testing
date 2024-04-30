## Rapi Container

- 環境變數 (ENV)
    - BUCKET：使用的 GCS 名稱
    - SRC_TC_CONF：rapi container 使用基礎 config.json (放置於 GCS 上) 
    - CT_ID：runtime container 編號
    - DEBUG：開發流程使用，讓 container 進入 waiting 狀態，不實際執行 TC
    - PLATFORM：web 或 mobile_web (為 TC 資料夾結構名稱)
    - GITHUB_REPO：使用哪個 REPO 作為 TC 來源
    - RUN_BRANCH：執行 GITHUB_REPO 的哪個 branch
    - STAGE：是否執行於 stage 環境


- 流程
    - 打包階段 (docker build) - 使用 github actions
        - 產製 env 資料夾中需要的檔案
            - secrets: service account 與 github actions token
            - variables: stage hosts （可用於調整使用不同 stage）
        - docker build and push to GAR (https://console.cloud.google.com/artifacts/docker/pchomeec-devops/asia/asia.gcr.io/rapi-runner?project=pchomeec-devops)
        - 使用 github sha short 作為 image tag
    - 執行階段 (Jenkins Pipeline)
        - 透過參數化建置將環境變數等作為 cloud run deploy 的 env 傳入 run time 
        - 透過 STAGE 變數判斷是否需要開啟 cicd-sideex-proxy 防火牆允入
        - 透過 RUN_BRANCH 變數判斷使用哪個 branch 作為 container run time TC
        - 透過 imageVersion 指定使用哪個 image tag (參考 github sha short)