##import common library
import json
import sys
import os
import datetime
import glob

##Import Framework common library
from Logger import apilogger
from PyLodge import PyLodge

def main():
    """
        Mark passed and failed test case status to TestLodge.

            Input argv :
                            project_id - which project you want to mark
    """

    test_run_name = datetime.datetime.now().strftime('%Y_%m_%d').format()
    json_files = glob.glob('{}/{}/*.json'.format(os.environ.get('WORKSPACE', '.'), sys.argv[1]))
    project_id = (sys.argv[2])
    print("[INFO] test_run_name : {}".format(test_run_name))
    apilogger.info("Test run name is: \"%s\"" % (test_run_name))
    print("[DEBUG] All json file list : {}" .format(json_files))
    apilogger.debug("All json file list : {}".format(json_files))

    ## Construct
    test_case = PyLodge("pchome.sqa.service@gmail.com", "68aAw344t0OHg9z3S5kQnRFa3tuaF8FNr2X0fpP8ch4GVgWyzU2Vhwtt", "https://api.testlodge.com/v1/account/35254", project_id)
    ## All of passed and failed test case id list
    test_case_id_list = []
    ## The string of the entire string payload
    all_parm = ""

    ## Get the test run id for the provided test run name
    test_runs_id = test_case.fetch_test_run_id(test_run_name)

    if test_runs_id != None:
        ####################### PASS #######################
        ##Get all passed test case id in TestLodge from json file and append them into a list
        for index in (test_case.case_name_success(json_files)):
            with open('{}/Testcase_name_dic.txt'.format(os.environ.get('WORKSPACE', '.')), "r") as f:
                temp = json.load(f)
            test_case_id_list.append(temp[index])
            apilogger.info("Passed case names are :%s" % (index))

        ## Use test case id to compose its body payload in x-www-form-urlencoded format
        for index in test_case_id_list:
            parm_pass = "\"executed_steps[%s][passed]\": \"1\",\"executed_steps[%s][create_issue_tracker_ticket]\": \"1\",\"executed_steps[%s][optional_callback_actions]\": \"1\",!!" % (index, index, index)
            all_parm = all_parm + parm_pass

        ## Clean the test id list
        test_case_id_list = []
        test_case_name_list = []

        ####################### FAIL #######################
        ##Get all failed test case id in TestLodge from json file and append them into a list
        for index in (test_case.case_name_fail(json_files)):
            with open('{}/Testcase_name_dic.txt'.format(os.environ.get('WORKSPACE', '.')), "r") as f:
                temp = json.load(f)
            test_case_name_list.append(index)
            test_case_id_list.append(temp[index])
            apilogger.info("Failed case names are :%s" % (index))

        ## Use test case id to compose its body payload in x-www-form-urlencoded format
        with open('{}/failed_TestCaseURL_list.txt'.format(os.environ.get('WORKSPACE', '.')), "w", encoding='utf-8') as f:
            i = 0
            for index in test_case_id_list:
                parm_fail ="\"executed_steps[%s][passed]\": \"0\",\"executed_steps[%s][create_issue_tracker_ticket]\": \"1\",!!" % (index, index)
                all_parm = all_parm + parm_fail
                failed_url = "https://app.testlodge.com/a/35254/projects/%s/runs/%s/run?selected=%s\n" % (project_id, test_runs_id, index)
                f.write('{}.錯誤的case名稱: {}\n'.format(i + 1, test_case_name_list[i]))
                f.write('錯誤的case URL: {}\n'.format(failed_url))
                i+=1

        ## Remove the last character that is ",!!"
        all_parm = all_parm[:-3]
        ## Add {} at the front and at the back to fit json format
        all_parm = "{"+ all_parm + "}"
        ## Convert string to list
        all_parm = all_parm.split('!!')

        ## Testloge Api have string upper limit
        ## Split the string to request api
        while(True):
            if len(all_parm) <= 150:
                string_a = "".join(all_parm)
                string_a = string_a[:-1]
                string_a = string_a + "}"
                result = json.loads(string_a)
                test_case.mark_status_by_api(result, test_runs_id)
                break
            else:
                string_a = "".join(all_parm[0:149])
                string_a = string_a[:-1]
                string_a = string_a + "}"
                result = json.loads(string_a)
                test_case.mark_status_by_api(result, test_runs_id)
                all_parm = all_parm[150:]
                all_parm[0] = "{" + all_parm[0]
    else:
        apilogger.error({'Fail to get test run id'})

if __name__=="__main__":
    main()
