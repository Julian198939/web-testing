#############################################################################################
#                                                                                           #
# This python file is for collecting Test cases info in TestLodge and update to Bigquery.   #
#                                                                                           #
#############################################################################################


from google.cloud import bigquery
from collections import defaultdict
from flask import Response
import requests
import os
import re
import time
import json


class WebDashboardCoverage:
    def __init__(self, user_info, projects_id):
        self._username = user_info["username"]
        self._api_key = user_info["api_key"]
        self._base_url = user_info["base_url"]
        self._auth_tuple = (self._username, self._api_key)
        self.projects_id = projects_id

    def get_regression_project_test_case_count(self):
        """
        Retrieves the number of test cases for the regression project.

        Returns:
            dict: A dictionary containing the number of test cases per page index.
        """
        project_id = self.projects_id["regression_project"]
        pages_info = defaultdict(lambda: 0)

        # Request Testlodge API
        url = self._base_url + f"/projects/{project_id}/suites.json"
        response = requests.get(url, auth=self._auth_tuple)
        if response.status_code == 200:
            response_dict = response.json()
        else:
            raise Exception(f"Error getting {url}: {response.status_code}")

        # Get info of all suites
        suites_info = [
            (suite_dict["id"], suite_dict["name"])
            for suite_dict in response_dict["suites"]
        ]

        # Get info of all sections in each suite
        for suite_info in suites_info:
            suite_id = suite_info[0]
            url = (
                self._base_url
                + f"/projects/{project_id}/suites/{suite_id}/suite_sections.json"
            )
            response = requests.get(url, auth=self._auth_tuple)
            if response.status_code == 200:
                response_dict = response.json()
            else:
                raise Exception(f"Error getting {url}: {response.status_code}")

            sections_info = [
                (suite_section_dict["id"], suite_section_dict["title"])
                for suite_section_dict in response_dict["suite_sections"]
            ]
            # Get the number of test cases in each section
            for section_info in sections_info:
                suite_section_id = section_info[0]
                url = (
                    self._base_url
                    + f"/projects/{project_id}/suites/{suite_id}/suite_sections/{suite_section_id}/steps.json"
                )
                response = requests.get(url, auth=self._auth_tuple)
                if response.status_code == 200:
                    response_dict = response.json()
                else:
                    raise Exception(f"Error getting {url}: {response.status_code}")

                total_cases = response_dict["pagination"]["total_entries"]
                if total_cases != 0:
                    # Get page index by prefix of first test case title in the section
                    first_case_title = response_dict["steps"][0]["title"]
                    page_index = first_case_title[1]

                    # Add the number to the belonged page
                    pages_info[page_index] = pages_info[page_index] + total_cases
        result = {k: v for k, v in pages_info.items()}
        return result

    def judge_title_page(self, title):
        """
        Determines the page number based on the given title.

        Args:
            title (str): The title to be checked.

        Returns:
            int: The page number corresponding to the title. If no match is found, returns 100.
        """
        re_pattern = {
            "1": ".*首頁.*",
            "2": ".*路標.*",
            "4": ".*館頁.*",
            "6": ".*單品.*"
        }
        page = 100
        for key, pattern in re_pattern.items():
            if not re.search(pattern, title) is None:
                page = key
                break
        return page

    def get_total_project_test_case_count(self):
        """
        Retrieves the total number of test cases for the project.

        :return: A dictionary containing the total number of test cases for each page.
        :rtype: dict
        """
        project_id = self.projects_id["total_project"]
        pages_info = {
            "1": 0,  # homepage
            "2": 0,  # index
            "4": 0,  # sign
            "6": 0,  # prod
        }

        # Get information of all suites in thr project
        url = self._base_url + f"/projects/{project_id}/suites.json"
        response = requests.get(url, auth=self._auth_tuple)
        if response.status_code == 200:
            response_dict = response.json()
        else:
            raise Exception(f"Error getting {url}: {response.status_code}")

        suites_info = [
            (suite_dict["id"], suite_dict["name"])
            for suite_dict in response_dict["suites"]
        ]

        # Get information of all sections in each suite
        for suite_info in suites_info:
            suite_id = suite_info[0]
            suite_name = suite_info[1]

            # Judge the page type by title of the suite
            page_index = self.judge_title_page(suite_name)

            url = self._base_url + f"/projects/{project_id}/suites/{suite_id}/suite_sections.json"
            response = requests.get(url, auth=self._auth_tuple)
            if response.status_code == 200:
                response_dict = response.json()
            else:
                raise Exception(f"Error getting {url}: {response.status_code}")

            sections_info = [
                (suite_section_dict["id"], suite_section_dict["title"])
                for suite_section_dict in response_dict["suite_sections"]
            ]

            total_cases = 0
            # Get the number of test cases in each section
            for section_info in sections_info:
                suite_section_id = section_info[0]

                url = (
                    self._base_url
                    + f"/projects/{project_id}/suites/{suite_id}/suite_sections/{suite_section_id}/steps.json"
                )
                response = requests.get(url, auth=self._auth_tuple)
                if response.status_code == 200:
                    response_dict = response.json()
                else:
                    raise Exception(f"Error getting {url}: {response.status_code}")

                total_cases += response_dict["pagination"]["total_entries"]

            # Add the number to the belonged page
            pages_info[page_index] = pages_info[page_index] + total_cases
        return pages_info

    def get_product_page_total_test_case_count(self):
        """
        Get the total test case count for the product page.

        :return: A dictionary containing the number of test cases for each page.
        :rtype: dict
        """
        project_id = self.projects_id["total_product"]
        pages_info = {
            "6": 0,  # product
        }

        # Get information of all suites in the project
        url = self._base_url + f"/projects/{project_id}/suites.json"
        response = requests.get(url, auth=self._auth_tuple)
        if response.status_code == 200:
            response_dict = response.json()
        else:
            raise Exception(f"Error getting {url}: {response.status_code}")

        suites_info = [
            (suite_dict["id"], suite_dict["name"])
            for suite_dict in response_dict["suites"]
        ]

        # Get information of all sections in each suite
        for suite_info in suites_info:
            suite_id = suite_info[0]
            page_index = "4"

            url = (
                self._base_url
                + f"/projects/{project_id}/suites/{suite_id}/suite_sections.json"
            )
            response = requests.get(url, auth=self._auth_tuple)
            if response.status_code == 200:
                response_dict = response.json()
            else:
                raise Exception(f"Error getting {url}: {response.status_code}")

            sections_info = [
                (suite_section_dict["id"], suite_section_dict["title"])
                for suite_section_dict in response_dict["suite_sections"]
            ]

            # Search '一般單品頁' section
            total_cases = 0
            for section_info in sections_info:
                suite_section_id = section_info[0]
                suite_section_name = section_info[1]

                pattern = "web_regression_test_單品頁"
                if not re.search(pattern, suite_section_name) is None:
                    url = (
                        self._base_url
                        + f"/projects/{project_id}/suites/{suite_id}/suite_sections/{suite_section_id}/steps.json"
                    )
                    response = requests.get(url, auth=self._auth_tuple)
                    if response.status_code == 200:
                        response_dict = response.json()
                    else:
                        raise Exception(f"Error getting {url}: {response.status_code}")

                    total_cases += response_dict["pagination"]["total_entries"]
                    pages_info[page_index] = pages_info[page_index] + total_cases
                    break
        return pages_info

    def get_coverage_data(self):
        """
        Retrieves coverage data.

        Returns:
            List[Dict[str, Union[str, int]]]: A list of dictionaries containing coverage data for each test case.
                - "platform" (str): The platform of the test case.
                - "page" (int): The page number of the test case.
                - "total_count" (int): The total count of test cases.
                - "regression_count" (int): The count of regression test cases.
                - "month" (str): The month of the coverage data.
        """

        # Get the number of test cases of each page in regression test
        regression_project_test_case_info = (
            self.get_regression_project_test_case_count()
        )
        # Get the number of test cases of each page
        total_project_test_case_info = self.get_total_project_test_case_count()
        product_page_total_test_case_count = (
            self.get_product_page_total_test_case_count()
        )
        total_project_test_case_info.update = product_page_total_test_case_count

        now = time.strftime("%Y-%m-01", time.localtime())
        result = []
        for k, v in regression_project_test_case_info.items():
            if total_project_test_case_info.get(k) is not None:
                json = {
                    "platform": "WEB",
                    "page": int(k),
                    "total_count": total_project_test_case_info[k],
                    "regression_count": regression_project_test_case_info[k],
                    "month": now,
                }
                result.append(json)
        return result

    def update_sytem_status(self, data):
        """
        Updates the system status in the `t_system_status` table of the `testcase_monitoring` dataset in BigQuery.

        Args:
            data (List[Dict[str, Union[str, int]]]): A list of dictionaries containing the data to be upserted. Each dictionary should have the following keys:
                - 'platform' (str): The platform name.
                - 'month' (str): The month in the format 'YYYY-MM-DD'.
                - 'page' (int): The page number.
                - 'total_count' (int): The total count.
                - 'regression_count' (int): The regression count.

        Returns:
            None

        Raises:
            None
        """
        client = bigquery.Client()
        dataset_id = "testcase_monitoring"
        table_id = "t_system_status"

        # Check if the month's data already exists, if not, insert it, if so, update it
        for row in data:
            merge_sql = f"""
            MERGE {dataset_id}.{table_id} AS target
            USING (SELECT '{row['platform']}' as platform, PARSE_DATETIME('%Y-%m-%d', '{row['month']}') as month, {row['page']} as page) AS source
            ON target.month = source.month AND target.page = source.page
            WHEN MATCHED THEN
                UPDATE SET
                    total_count = {row['total_count']},
                    regression_count = {row['regression_count']}
            WHEN NOT MATCHED THEN
                INSERT (platform, total_count, regression_count, month, page)
                VALUES ('{row['platform']}', {row['total_count']}, {row['regression_count']}, PARSE_DATETIME('%Y-%m-%d', '{row['month']}'), {row['page']});
            """

            query_job = client.query(merge_sql)  # Execute the query
            query_job.result()  # This waits for the query job to complete

            # Check for errors
            if not query_job.done():
                error_result = query_job.error_result
                print(f"Error executing query: {error_result['message']}")


def main(request):
    client = bigquery.Client()

    # Testlodge API
    user_info = {
        "username": "pchome.sqa.service@gmail.com",
        "api_key": "68aAw344t0OHg9z3S5kQnRFa3tuaF8FNr2X0fpP8ch4GVgWyzU2Vhwtt",
        "base_url": "https://api.testlodge.com/v1/account/35254",
    }
    projects_id = {
        "regression_project": 52624,
        "total_project": 52641,
        "total_product": 54802,
    }

    try:
        dashboard = WebDashboardCoverage(user_info, projects_id)
        coverage_data = dashboard.get_coverage_data()
        dashboard.update_sytem_status(coverage_data)

        response = Response()
        response.status_code = 200
        response.headers["Content-Type"] = "application/json"
        response.data = json.dumps({"message": "Test coverage data update successful"})
        return response

    except Exception as e:
        response = Response()
        response.status_code = 400
        response.headers["Content-Type"] = "application/json"
        response.data = json.dumps({"message": "Test coverage data update failed"})
        return response
