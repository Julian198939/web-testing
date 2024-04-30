#############################################################################################
#                                                                                           #
# This python file is for collecting Sideex test report and send the result to google chat. #
#                                                                                           #
#############################################################################################

import json
import os
import requests
import glob
import sys
from datetime import datetime
from collections import defaultdict

global Chrome_ver,browser,platform,status,start_time,end_time,successCaseNum,failureCaseNum,Fail_suite_case
i = 0
trandict = {}
Fail_suite = []
Fail_case = []
title = []
successCaseNum = []
failureCaseNum = []
tranlist = []
Fail_suite_case = {} 
json_test_report = {}
totalsuccessCaseNum = 0
totalfailureCaseNum = 0
out = ""

WEBHOOK_URL = ''

plt = sys.argv[1]
list_of_files = glob.glob('./{}/*.json'.format(plt))
latest_file = max(list_of_files, key=os.path.getctime)
oldest_file = min(list_of_files, key=os.path.getctime)

try:
  # Get start time
  with open(oldest_file, 'r', encoding='UTF8') as f:
      data = json.load(f)
      Chrome_ver = next(iter(data))
      result = data[Chrome_ver]
      browser = result[0]["browser"]
      platform = result[0]["platform"]
      status = result[0]["status"]
      start_time = result[0]["startTime"]
      f.close
  # Get end time
  with open(latest_file, 'r', encoding='UTF8') as f:
      data = json.load(f)
      Chrome_ver = next(iter(data))
      result = data[Chrome_ver]
      end_time = result[0]["endTime"]
      f.close
  # Find all fail suites and cases       
  for filename in list_of_files:
    with open(os.path.join(os.getcwd(), filename), 'r', encoding='UTF8') as f:
      data = json.load(f)
      Chrome_ver = next(iter(data)) # select report in dic
      result = data[Chrome_ver]
      successCaseNum.append(int(result[0]["successCaseNum"]))
      failureCaseNum.append(int(result[0]["failureCaseNum"]))
      suites = result[0]["suites"] # get suites data
      cases = result[0]["cases"] # get cases data
      for i in range(len(suites)): # find fail suites
          if suites[i]["status"] == 'fail':
              for j in range(len(cases)): # find fail cases
                  if cases[j]["status"] == 'fail' and cases[j]["suiteIdText"] == "suite-{}".format(i+1):
                    Fail_suite.append(suites[i]["title"])
                    Fail_case.append(cases[j]["title"])
                    result = defaultdict(list)
                    for key, value in zip(Fail_suite, Fail_case):
                      result[key].append(value)
                    trandict = dict(result)
                    trandict = {k: v for k, v in result.items()}
                  else:
                      pass
          else:
              pass
  tranlist = ["{}.{}下失敗的case:{}".format(i+1,k,",".join(v)) for i, (k, v) in enumerate(trandict.items())]
  totalsuccessCaseNum = sum(successCaseNum)
  totalfailureCaseNum = sum(failureCaseNum)
  for item in tranlist:
      out += item.replace(":",":\n").replace(",","\n") + "\n"
  start_time = datetime.strptime(start_time, "%Y%m%d %H:%M:%S")
  formatted_start_time = start_time.strftime("%Y-%m-%d %H:%M:%S")
  end_time = datetime.strptime(end_time, "%Y%m%d %H:%M:%S")
  formatted_end_time = end_time.strftime("%Y-%m-%d %H:%M:%S")
  # Set google chat card template
  json_test_report = {
  "cardsV2": [
  {
    "cardId": "unique-card-id",
    "card": {
      "header": {
        "title": "Sideex report",
        "subtitle": "web regression test",
        "imageUrl":
        "https://developers.google.com/chat/images/quickstart-app-avatar.png",
        "imageType": "CIRCLE",
      },
      "sections": [
        {
          "uncollapsibleWidgetsCount": 1,
          "widgets": [
            {
              "decoratedText": {
                "topLabel": "Case成功率",
                "text": "{}% ".format(round((totalsuccessCaseNum/(totalsuccessCaseNum + totalfailureCaseNum))*100, 2)) + "({}/{})".format(totalsuccessCaseNum, totalsuccessCaseNum + totalfailureCaseNum),
              }
            },
            {
              "decoratedText": {
                "topLabel": '失敗suites名稱:失敗case名稱',
              }
            },
            {
              "textParagraph": {
                "text": '{}'.format(out)
              }
            },
            {
              "decoratedText": {
                "topLabel": "測試開始時間",
                "text": "{}".format(formatted_start_time),
              }
            },
            {
              "decoratedText": {
                "topLabel": "測試結束時間",
                "text": "{}".format(formatted_end_time),
              }
            },
            {
              "decoratedText": {
                "topLabel": "平台",
                "text": "{}".format(platform),
              }
            },
            {
              "decoratedText": {
                "topLabel": "瀏覽器",
                "text": "{}".format(browser),
              }
            },
            {
              "decoratedText": {
                "topLabel": "狀態",
                "text": "{}".format(status),
              }
            },
          ],
        },
      ],
    },
  }
],
}
  print('Successfully get test report')
  # For generate rerange test report  as json file
  # with open('test_report.json', 'a') as f:
  #     json.dump(json_test_report, f, sort_keys=True)
  #     f.close
except:
    print("No input test report json file or wrong format json file or wrong file name!")
# Send card to google chat
try:
  if tranlist != []:
    f = open('url.txt')
    WEBHOOK_URL = f.read()
    f.close
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url=WEBHOOK_URL, headers=headers, data=json.dumps(json_test_report), verify=False)
    print('POST Status Code: %s' % response.status_code)
    if response.status_code == 200:
        print('Successfully send test report!!')
    else:
        print('Fail to send test report!!')
  else:
    print('No fail test case \OAO/')
except:
    print('POST Status Code: %s' % response.status_code)
    print("Fail to send test report!!")