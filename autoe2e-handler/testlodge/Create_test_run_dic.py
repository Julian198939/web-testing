##import common library
import sys
import json
import datetime

##Import Framework common library
from PyLodge import PyLodge

def main():
    """
        Create a test run in TestLodge and write all test case names of this test run into "Testcase_name_dic.txt" file.
    """
    dic = {}
    project_id = (sys.argv[1])

    Testcase = PyLodge("pchome.sqa.service@gmail.com", "68aAw344t0OHg9z3S5kQnRFa3tuaF8FNr2X0fpP8ch4GVgWyzU2Vhwtt", "https://api.testlodge.com/v1/account/35254", project_id)
    
    ##Setting the run name is today and in the format '%Y_%m_%d'
    run_name = datetime.datetime.now().strftime('%Y_%m_%d').format()

    ##Create a test run 
    Testcase.create_test_run(run_name)
    # print(run_name)

    test_run_id = Testcase.fetch_test_run_id(run_name)
    # print(test_run_id)

    dic = Testcase.get_test_case_name_and_id_dic_from_test_run(test_run_id)
    # print(dic)

    with open("Testcase_name_dic.txt", "w") as f:
        json.dump(dic, f)

if __name__=="__main__":
    main()