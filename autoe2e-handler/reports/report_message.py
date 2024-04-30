###################################################################################################
#                                                                                                 #
# This python file is for collecting Rapi(SideeX) test report and send the result to Google Chat. #
# Update to check Rapi runner test report.                                                        #
#                                                                                                 #
###################################################################################################

import json
import os
import requests
import glob
import sys
from datetime import datetime
from collections import defaultdict

global Chrome_ver, browser, platform, status, start_time, end_time, successCaseNum, failureCaseNum
i = 0
trandict = {}
Fail_suite = []
Fail_case = []
suiteCategoryIds = []
pageNameMappingDict = {"1":"首頁", "2":"路標頁", "3":"區頁", "4":"館頁", "5":"搜尋頁", "6":"單品頁", "7":"集結頁", "8":"購物車", "9":"顧客中心"}
successCaseNum = []
failureCaseNum = []
tranlist = []
testResultMessageCard = {}
totalSuccessCaseNum = 0
totalFailureCaseNum = 0
WEBHOOK_URL = ""

pass_pic = "https://img.icons8.com/color/96/pass.png"
fail_pic = "https://img.icons8.com/color/96/fail.png"

# Get test report files
filePath = '{}/{}/*.json'.format(os.environ.get('WORKSPACE', '.'), sys.argv[1])
print('[DEBUG] Report path: {}'.format(filePath))
reportFileList = glob.glob(filePath)

# TestCase git branch
testCaseBranch = sys.argv[2]

# Testing target environment
targetEnvironmentID = sys.argv[3]
if targetEnvironmentID == "1":
  targetEnvironment = "Staging"
else:
  targetEnvironment = "Production"

# Platform
targetPlatform = sys.argv[4]

# Trigger source
triggerBy = sys.argv[5]

# parallel run for Rapi on GCP
largest_file = max(reportFileList, key=os.path.getsize)

try:
    # Get browser name, platform name, status, start time and end time
    with open(largest_file, 'r', encoding='UTF8') as f:
        data = json.load(f)
        result = data['reports']
        browser = result[0]["browser"]
        platform = result[0]["platform"]
        status = result[0]["status"]
        start_time = result[0]["startTime"]
        end_time = result[0]["endTime"]
        f.close
    # Check fail suites and cases in test report
    for filename in reportFileList:
        with open(os.path.join(os.getcwd(), filename), 'r', encoding='UTF8') as f:
            data = json.load(f)
            reports = data['reports']
            successCaseNum.append(int(reports[0]["successCaseNum"]))
            suites = reports[0]["suites"]  # get suites data
            cases = reports[0]["cases"]  # get cases data
            for suiteIndex in range(len(suites)):
                suiteCategoryIds.append(suites[suiteIndex]["title"][1:2])
                # find fail suites
                if suites[suiteIndex]["status"] == 'fail':
                    for caseIndex in range(len(cases)):  # find fail cases
                        if cases[caseIndex]["status"] == 'fail' and cases[caseIndex]["suiteIdText"] == suites[suiteIndex]["idText"]:
                            Fail_suite.append(suites[suiteIndex]["title"])
                            Fail_case.append(cases[caseIndex]["title"])
                            result = defaultdict(list)
                            for key, value in zip(Fail_suite, Fail_case):
                                result[key].append(value)
                            trandict = dict(result)
                            trandict = {k: v for k, v in result.items()}
            # Fail cases information process
            if (int(reports[0]["failureCaseNum"])) != 0:
                failureCaseNum.append(int(reports[0]["failureCaseNum"]))
                tranlist = ["<b>Suite {}: {}</b>\n┗ {}".format(suiteIndex+1, k, "\n┗ ".join(v)) for suiteIndex, (k, v) in enumerate(trandict.items())]

    totalSuccessCaseNum = sum(successCaseNum)
    totalFailureCaseNum = sum(failureCaseNum)
    start_time = datetime.strptime(start_time, "%Y%m%d %H:%M:%S")
    end_time = datetime.strptime(end_time, "%Y%m%d %H:%M:%S")

    # Set google chat card template
    testResultMessageCard = {
        "cardsV2": [
            {
                "cardId": "e2e-autotesting-results",
                "card": {
                    "header": {
                        "title": "網頁自動化測試結果",
                        "subtitle": "Rapi ( SideeX ) 自動化測試系統 by SQA",
                        "imageUrl": "https://img.icons8.com/external-smashingstocks-flat-smashing-stocks/100/external-Testing-testing-services-smashingstocks-flat-smashing-stocks-2.png",
                        "imageType": "SQUARE"
                    },
                    "sections": [
                        {
                            "collapsible": "true",
                            "uncollapsibleWidgetsCount": 8,
                            "widgets": [
                                {
                                    "decoratedText": {
                                        "icon": {
                                            "knownIcon": "STAR"
                                        },
                                        "topLabel": "測試案例成功率",
                                        "text": "{}% ".format(round((totalSuccessCaseNum/(totalSuccessCaseNum + totalFailureCaseNum))*100, 2)) + " | Cases ( {} / {} )".format(totalSuccessCaseNum, totalSuccessCaseNum + totalFailureCaseNum)
                                    }
                                },
                                {
                                    "decoratedText": {
                                        "topLabel": '失敗 Suite 與 Case 名稱'
                                    }
                                },
                                {
                                    "textParagraph": {
                                        "text": '{}'.format("\n".join(tranlist))
                                    }
                                },
                                {
                                    "decoratedText": {
                                        "icon": {
                                            "knownIcon": "MAP_PIN"
                                        },
                                        "topLabel": "測試目標環境",
                                        "text": "{} @ {}".format(targetPlatform, targetEnvironment)
                                    }
                                },
                                {
                                    "decoratedText": {
                                        "icon": {
                                            "knownIcon": "MEMBERSHIP"
                                        },
                                        "topLabel": "測試目標頁面",
                                        "text": "{}".format("、".join([pageNameMappingDict[value] for value in set(sorted(suiteCategoryIds, key=int))])),
                                    }
                                },
                                {
                                    "decoratedText": {
                                        "icon": {
                                            "knownIcon": "FLIGHT_ARRIVAL"
                                        },
                                        "topLabel": "測試觸發來源",
                                        "text": "{}".format(triggerBy)
                                    }
                                },
                                {
                                    "decoratedText": {
                                        "icon": {
                                            "knownIcon": "CLOCK"
                                        },
                                        "topLabel": "測試開始時間",
                                        "text": "{}".format(start_time.strftime("%Y-%m-%d %H:%M:%S"))
                                    }
                                },
                                {
                                    "decoratedText": {
                                        "icon": {
                                            "knownIcon": "CLOCK"
                                        },
                                        "topLabel": "測試結束時間",
                                        "text": "{}".format(end_time.strftime("%Y-%m-%d %H:%M:%S"))
                                    }
                                },
                                {
                                    "decoratedText": {
                                        "icon": {
                                            "knownIcon": "BOOKMARK"
                                        },
                                        "topLabel": "測試腳本版本",
                                        "text": "{}".format(testCaseBranch)
                                    }
                                },
                                {
                                    "decoratedText": {
                                        "icon": {
                                            "knownIcon": "STORE"
                                        },
                                        "topLabel": "測試使用作業系統",
                                        "text": "{}".format(platform)
                                    }
                                },
                                {
                                    "decoratedText": {
                                        "icon": {
                                            "knownIcon": "VIDEO_PLAY"
                                        },
                                        "topLabel": "測試使用瀏覽器",
                                        "text": "{}".format(browser)
                                    }
                                },
                                {
                                    "decoratedText": {
                                        "icon": {
                                            "knownIcon": "INVITE"
                                        },
                                        "topLabel": "測試狀態",
                                        "text": "{}".format(status)
                                    }
                                }
                            ]
                        }
                    ]
                }
            }
        ]
    }
    print('[DEBUG] Successfully get test report.')
    print(testResultMessageCard)
    # For generate rerange test report  as json file
    with open('test_report.json', 'a') as f:
        json.dump(testResultMessageCard, f, sort_keys=True)
        f.close
except Exception as e:
    print("[ERROR] No input test report json file, or wrong format json file, or wrong file name!")
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print(exc_type, fname, exc_tb.tb_lineno)

# Send message card to Google Chat
try:
    if tranlist != []:
        testResultMessageCard["cardsV2"][0]["card"]["header"]["imageUrl"] = fail_pic
        f = open('chatbot_url.txt')
        WEBHOOK_URL = f.read()
        f.close
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url=WEBHOOK_URL, headers=headers, data=json.dumps(testResultMessageCard))
        print('[DEBUG] Google Chat API response status code: %s' % response.status_code)
        if response.status_code == 200:
            print('[INFO] Successfully send test result message')
        else:
            print('[ERROR] Fail to send test result message')
    else:
        testResultMessageCard["cardsV2"][0]["card"]["header"]["imageUrl"] = pass_pic
        testResultMessageCard["cardsV2"][0]["card"]["sections"][0]["widgets"][1]["decoratedText"]["topLabel"] = "測試結果"
        testResultMessageCard["cardsV2"][0]["card"]["sections"][0]["widgets"][2]["textParagraph"]["text"] = "測試通過"
        f = open('chatbot_url.txt')
        WEBHOOK_URL = f.read()
        f.close
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url=WEBHOOK_URL, headers=headers, data=json.dumps(testResultMessageCard))
        print('[DEBUG] Google Chat API response status code: %s' % response.status_code)
        if response.status_code == 200:
            print('[INFO] Successfully send test result message')
        else:
            print('[ERROR] Fail to send test result message')
except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print(exc_type, fname, exc_tb.tb_lineno)