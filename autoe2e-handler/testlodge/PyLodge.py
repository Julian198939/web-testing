##import common library
import json

##Import Framework common library
import Logger
from Logger import apilogger

class PyLodge():
    def __init__(self, username, password, api_url, project_id):
        ##Get initial value
        self.username = username
        self.password = password
        self._api_url = api_url
        self._auth_tuple = (self.username, self.password)
        self.project_id = project_id
    
    def create_test_run(self, run_name=None):
        """
        This method will create a test run in TestLodge including all test suites in it. It will return the test run id of the created test run.
            Input argu : 
                run_name: Test run name
        """

        project_id = self.project_id

        apilogger.info("Start creating a test run.")

        # Get the test suites id for the provided test run name in the project
        url = self._api_url + "/projects/%s/suites.json" % (project_id)
        response = Logger.SendHttpRequest({"http_method": "get", "url": url, "auth": self._auth_tuple})
        response_dict = response.json()
        suite_ids = [suite_dict['id'] for suite_dict in response_dict['suites']]

        # Create a Test run including all the test suites in the project and get the Test run ID
        url = self._api_url + "/projects/%s/runs.json" % (project_id)
        json={'run': {'name': run_name, 'suite_ids': suite_ids}}
        response = Logger.SendHttpRequest({"http_method": "post", "url": url, "body_data_format": True, "body": json, "auth": self._auth_tuple})

        if response.status_code == 201:
            apilogger.info("Create test run successfully!!! And test run name is \"%s\"." % (run_name))
        else:
            apilogger.info("Failed to create test run.")

    def fetch_test_run_id(self, test_run_name, dic={}):
        """
        Get test run id for test run name is the date of the day and ensure it exists in TestLodge.
            Input argu :
                    test_run_name - which test run name you want to fetch test run id
            Return argu :
                    test_run_id - which test run id you fetch
        """

        project_id = self.project_id
        url = self._api_url + '/projects/%s/runs.json' % (project_id)

        apilogger.info("Start fetching a test run id.")

        response = Logger.SendHttpRequest({"http_method": "get", "url": url, "auth": self._auth_tuple, "verify": False})
        response_dict = response.json()
        for i in range(len(response_dict["runs"])):
            test_run_name_temp = response_dict["runs"][i]["name"]
            test_run_id = response_dict["runs"][i]["id"]
            dic[test_run_name_temp]= test_run_id

        if response.status_code == 200:
            if test_run_name in dic:
                print("Test run name: \"{}\" and test run id: \"{}\"".format(test_run_name, dic[test_run_name]))
                apilogger.info("Test run name: \"{}\" and test run id: \"{}\"".format(test_run_name, dic[test_run_name]))
                return dic[test_run_name]
            else:
                print("Test run name: \"{}\" doesn't exist in TestLodge. Please check again!".format(test_run_name))
                apilogger.info("Test run name: \"{}\" doesn't exist in TestLodge. Please check again!".format(test_run_name))
                return None
        else:
            apilogger.info("Failed to fetch test run id.")
            return None

    def get_test_case_name_list_from_test_run(self, run_id):
        """
        Get all test case name and store in a list
            1.Know how many page in test run
            2.Collect all the case name in each page
            Input argu :
                    run_id - which test run id you want to get test case name
            Return argu :
                    case_name_list - which store a list of test case names you fetch
        """
        case_name_list = []
        project_id = self.project_id
        url = self._api_url + '/projects/%s/runs/%s/executed_steps.json' % (project_id, run_id)

        apilogger.info("Start getting a test case name list from a test run.")

        response = Logger.SendHttpRequest({"http_method": "get", "url": url, "auth": self._auth_tuple})
        response_dict = response.json()
        total_pages = response_dict["pagination"]["total_pages"]

        for i in range(total_pages):
            page = i + 1
            response = Logger.SendHttpRequest({"http_method": "get", "url": url, "auth": self._auth_tuple, "params": {'page': page}})
            response_dict = response.json()
            for i in range(len(response_dict["executed_steps"])):
                title = response_dict["executed_steps"][i]["title"]
                case_name_list.append(title)
        apilogger.info("The resulting list is as follows: {}".format(case_name_list))
        return case_name_list

    def get_test_case_name_and_id_dic_from_test_run(self, test_run_id):
        """
        Get the dictionary which is composed of key for test case name and value for test case id from the provided test run id.
            Input argu :
                    test_run_id - which test run id you want to get dictionary
            Return argu :
                    dic - is composed of key for test case name and value for test case id
        """
        dic = {}
        project_id = self.project_id
        url = self._api_url + '/projects/%s/runs/%s/executed_steps.json' % (project_id, test_run_id)

        apilogger.info("Start getting a dictionary from a test run.")

        response = Logger.SendHttpRequest({"http_method": "get", "url": url, "auth": self._auth_tuple})
        response_dict = response.json()
        total_pages = response_dict["pagination"]["total_pages"]

        for i in range(total_pages):
            page = i + 1
            response = Logger.SendHttpRequest({"http_method": "get", "url": url, "auth": self._auth_tuple, "params": {'page': page}})
            response_dict = response.json()
            for i in range(len(response_dict["executed_steps"])):
                test_case_name = response_dict["executed_steps"][i]["title"]
                test_case_id = response_dict["executed_steps"][i]["id"]
                dic[test_case_name]= test_case_id

        apilogger.info("The resulting dictionary is as follows: {}".format(dic))
        return dic

    def case_name_success(self, json_Files):
            """
            Load json file for getting test case title which status is success
                Input argu :
                        json_File - which json file name
                Return argu :
                        list_success - test case title which status is success
            """
            list_success = []

            for json_File in json_Files:
                with open(json_File, 'r', encoding='UTF8') as f:
                    data = json.load(f)
                result = data['reports']
                cases = result[0]["cases"] # get cases data
                for j in range(len(cases)): # find success cases
                    if cases[j]["status"] == 'success':   
                        list_success.append(cases[j]["title"])
            return list_success

    def case_name_fail(self, json_Files):
        """
        Load json file for getting test case title which status is fail
            Input argu :
                    json_File - which json file name
            Return argu :
                    list_fail - test case title which status is fail
        """
        list_fail = []

        for json_File in json_Files:
            with open(json_File, 'r', encoding='UTF8') as f:
                data = json.load(f)
            result = data['reports']
            cases = result[0]["cases"] # get cases data
            for j in range(len(cases)): # find fail cases
                if cases[j]["status"] == 'fail':   
                    list_fail.append(cases[j]["title"])
        return list_fail

    def mark_status_by_api(self, All_parm, test_run_id):
        """
        Mark test case status in TestLodge by api
            Input argu :
                    All_parm - which test case payload
        """

        apilogger.info("Start marking status to a test run.")

        if All_parm == {}:
            apilogger.info("The api body for marking test case status is empty. Please check report json file.")
        else:
            url = self._api_url + '/projects/%s/runs/%s/executed_steps/bulk_update.json' % (self.project_id, test_run_id)

            # Content-Type was x-www-form-urlencoded
            headers={
                        'Authorization': 'Basic cGNob21lLnNxYS5zZXJ2aWNlQGdtYWlsLmNvbTo2OGFBdzM0NHQwT0hnOXozUzVrUW5SRmEzdHVhRjhGTnIyWDBmcFA4Y2g0R1ZnV3l6VTJWaHd0dA==',
                        'Content-Type': 'application/x-www-form-urlencoded'
                    }

            # Send api and payload key(body_data_format) format is data(False)
            response = Logger.SendHttpRequest({"http_method": "patch", "url": url, "body_data_format": False, "body": All_parm, "headers": headers})
            if response.status_code == 200:
                apilogger.info("Mark all test cases successfully!!!")
            else:
                apilogger.info("Failed to mark test cases! Please check the log file.")