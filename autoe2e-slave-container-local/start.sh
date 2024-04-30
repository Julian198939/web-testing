#!/bin/bash
java -jar selenium-server-4.8.1.jar standalone > ./logfile 2>&1 &
PID=$!

# selenium啟動成功後, 才能執行sideex-runner
while true; do
  if grep -q "INFO \[Standalone\.execute\] - Started Selenium Standalone" ./logfile; then
    break
  else
    sleep 1
  fi
done

# 运行第二条命令
echo "Service is started successfully. Running the second command now."
sideex-runner --config config.json