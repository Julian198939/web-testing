#############################################################################################
#                                                                                           #
# This python file is for updating  Rapi report's result from Jenkins to Bigquery.          #
#                                                                                           #
#############################################################################################

from google.cloud import bigquery
from collections import defaultdict
import requests
import os
import re
import time
import json
import datetime


def update_test_cases(data):
    """
    Updates the test cases in the 'testcase_monitoring' dataset and 't_test_cases' table in BigQuery.

    Args:
        data (List[dict]): A list of dictionaries representing the test cases to be inserted into the table.

    Returns:
        None
    """

    # Connect to BigQuery
    client = bigquery.Client()

    dataset_id = "testcase_monitoring"
    table_id = "t_test_cases"

    # Check if the first data entry exists in BigQuery
    first_row = data[0]
    query = f"""
        SELECT COUNT(*) as count
        FROM `{dataset_id}.{table_id}`
        WHERE name = '{first_row['name']}' AND executed_at = TIMESTAMP('{first_row['executed_at']}')
    """
    query_job = client.query(query)
    results = query_job.result()
    count = next(iter(results))[0]

    # Insert data into BigQuery if there's no duplicate
    if count == 0:
        errors = client.insert_rows_json(f"{dataset_id}.{table_id}", data)

    if errors:
        for error in errors:
            print(f"Error inserting row: {error}")


def main(request):

    # Connect to BigQuery
    client = bigquery.Client()

    # Get the Rapi report data from the request send by Jenkins
    json_data = request.get_json()
    update_test_cases(json_data["data"])

    return "success"
