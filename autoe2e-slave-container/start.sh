#!/bin/bash

# GCS_BUCKET
# TC_CONF
# CT_ID
# DEBUG
# PLATFORM
# PAGE
# GITHUB_REPO
# RUN_BRANCH
# STAGE

# 設定IFS
SAVEIFS=$IFS
IFS=$(echo -en "\n\b")

set -x

if [ "$DEBUG" -gt "0" ]
then
  #-- for jenkins pipeline testing, not run sideex --
  for ((i=1;i<=$DEBUG;i++))
  do
    echo "Sleep $i second"
    sleep 1
  done
else
  #--- Run on Stage
  if [ "$STAGE" -eq "1" ]
  then
    # 新增 container 外部 ip 到 firewall rule (allow-ingress-sideex-proxy-tcp-3456)

    # 進行 stage 環境回歸測試
    #   指定 HOST 並走 Proxy
    export https_proxy=http://104.199.234.246:3456
    export SE_PROXY=http://104.199.234.246:3456
    # export https_proxy=http://sideexboy:8DHfA15G3mSePZlKgi@104.199.234.246:3456

    #----- TODO: auth (非預期，部分訪問沒有套用？！)
    # export https_proxy=http://sideexboy:8DHfA15G3mSePZlKgi@104.199.234.246:3456
    # export SE_PROXY=sideexboy@8DHfA15G3mSePZlKgi:104.199.234.246:3456

    # show stage hosts
    cat /app/stage_host.txt

    # no auth: test ok
    java -Djdk.net.hosts.file=/app/stage_host.txt -Djava.security.egd=file:/dev/./urandom -Dselenium.LOGGER.level=DEBUG -Dwebdriver.chrome.args="--disable-dev-shm-usage --single-process --disable-gpu --disable-notifications --window-size=1280,720" -Xmx4g -Xms4g -jar selenium-server-4.18.1.jar standalone --selenium-manager true > ./logfile 2>&1 &
    PID=$!
  else
    #--- Run on Production
    # run se server
    java -Djava.security.egd=file:/dev/./urandom -Dselenium.LOGGER.level=DEBUG -Dwebdriver.chrome.args="--disable-dev-shm-usage --single-process --disable-gpu --disable-notifications --window-size=1280,720" -Xmx4g -Xms4g -jar selenium-server-4.18.1.jar standalone --selenium-manager true 2>&1 | tee ./logfile &
    PID=$!
  fi

  # selenium 啟動成功後, 才能執行 rapi-runner
  while true; do
    if grep -q "INFO \[Standalone\.execute\] - Started Selenium Standalone" ./logfile; then
      break
    else
      sleep 2
    fi
  done

  # Download TC
  github_token=`cat github_token.txt`
  git clone -b ${RUN_BRANCH} --single-branch --depth 1 https://${github_token}@${GITHUB_REPO}

  # Copy autoe2e-scripts-sideex suites
  repo=`echo "${GITHUB_REPO}" | cut -d'/' -f3`
  mkdir autoe2e-scripts-sideex
  cp -r $repo/autoe2e-scripts-sideex/* ./autoe2e-scripts-sideex
  cp $repo/autoe2e-scripts-sideex/*.json .

  # Download split config.json file
  gcloud auth activate-service-account --key-file=/app/pchomeec-devops-github-autoe2e-web.json
  gsutil cp ${SRC_TC_CONF} config.json

  # Run Rapi runner
  chmod +x rapi-runner-linux
  ./rapi-runner-linux --config config.json

  # Upload to GCS
  cp ./test_report/autoe2e-scripts-sideex/${PLATFORM}/*.json output.json
  gsutil cp output.json gs://${BUCKET}/output/${PLATFORM}/${JOB_NAME}-output.json
  gsutil cp logfile gs://${BUCKET}/output/${PLATFORM}/${JOB_NAME}-logfile.log
fi

# Reset IFS
IFS=$SAVEIFS
