## jira-sprint-report

This is a Python script that generates a Jira Sprint and Jira Servicedesk report for the given project in html and eml formats. The tasks in the result are separated in 2 sections by labels that are defined in `LABEL_1` and `LABEL_2` variables. If you do not specify those, then all the tasks in the result files will be in the same section.
## Prerequisites

Adjust all the variables according to your project.

You need to set the following env vars before running the script:

* EMAIL - Should contain your email address

* JIRA_API_KEY - Should contain a JIRA API token with at least read access to the required projects (https://developer.atlassian.com/server/jira/platform/basic-authentication/)

To add emoji icons to the report, you need to install an [emoji module](https://pypi.org/project/emoji/) by running the following command: 
* `pip3 install emoji`

To be able to create a eml file, you need to install an [html2eml module](https://pypi.org/project/html2eml/) by running the following command: 
* `pip3 install html2eml`

Make sure that you have write access to the directory stated in the OUTPUT_PATH var, otherwise you won't be able to create a result html\eml file.

## Running script
Once the above prerequisites are fulfilled, please run the below command from the script directory:
python3 ./Script.py
