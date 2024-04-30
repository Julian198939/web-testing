#############################################################################################
#                                                                                           #
# This python file is for collecting Rapi test report and post the result to Cloud Function.#
#                                                                                           #
#############################################################################################

import requests
import json
import os
import glob
import sys
import subprocess
from datetime import datetime, timezone, timedelta
from collections import defaultdict

global Chrome_ver, browser, platform, status, start_time, end_time, successCaseNum, failureCaseNum, Fail_suite_case
tranlist = []

# Get Rapi report file dir name and path
list_of_files = glob.glob('{}/{}/*.json'.format(os.environ.get('WORKSPACE', '.'), sys.argv[1]))

try:
    largest_file = max(list_of_files, key=os.path.getsize)

    # Get Rapi runner start time
    with open(largest_file, "r", encoding="UTF8") as f:
        data = json.load(f)
        result = data["reports"]
        start_time = result[0]["startTime"]
        start_time = datetime.strptime(start_time, "%Y%m%d %H:%M:%S")
        local_start_time = start_time.replace(
            tzinfo=timezone(timedelta(hours=8))
        ).astimezone(tz=None)

        formatted_start_time = local_start_time.timestamp()
        formatted_start_time = datetime.utcfromtimestamp(formatted_start_time).strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    # Find all cases in all rapi report files
    for filename in list_of_files:
        with open(os.path.join(os.getcwd(), filename), "r", encoding="UTF8") as f:
            data = json.load(f)
            result = data["reports"]
            cases = result[0]["cases"]  # Get cases data

            # Get info of each case
            for case in cases:
                # Get page index by prefix of test case title
                page_index = int(case["title"][1])
                if case["status"] == "success":
                    is_success = True
                else:
                    is_success = False

                tran_dict = {
                    "name": case["title"],
                    "platform": "WEB",
                    "page": page_index,
                    "success": is_success,
                    "executed_at": formatted_start_time,
                }
                tranlist.append(tran_dict)

    print("Successfully get test report")
    print("Num of test case:", len(tranlist))
    print("Start to update test cases info...")

    # Update test cases info by sending request to cloud function
    # with open("./config.json", "r") as f:
    #     token = json.load(f)
    #     token = token["cloudFuncToken"]
    # url = "https://asia-east1-gcp-poc-384805.cloudfunctions.net/grafana-testcase-2"

    # with open('./token.txt', 'r') as file:
    #     token = file.read()

    p = subprocess.Popen('gcloud auth print-identity-token',
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        shell=True)

    token = p.communicate()[0].decode('utf-8').strip()

    url = "https://asia-east1-pchomeec-devops.cloudfunctions.net/grafana-testcase-2"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    data = {
        "data": tranlist,
    }

    # Check the response of cloud function
    response = requests.post(url, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        print("Success to post the rapi report data to bigQuery.")
    else:
        print("Failed to post the rapi report data to bigQuery. HTTP response code: {}".format(response.status_code))
        print("Error message: {}".format(response.raise_for_status()))
    print("End to update test cases info...")

except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print(exc_type, fname, exc_tb.tb_lineno)
