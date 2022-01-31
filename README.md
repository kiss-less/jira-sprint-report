## Prerequisites

You need to set the following env vars before running the script:

* EMAIL - Should contain your email address

* JIRA_API_KEY - Should contain a JIRA API token with at least read access to the DevOps Sprints (https://developer.atlassian.com/server/jira/platform/basic-authentication/)

To add emoji icons to the report, you need to install an emoji module by running the following command: 
* `pip3 install emoji`

To be able to create a eml file, you need to install an html2eml module by running the following command: 
* `pip3 install html2eml`


Make sure that you have write access to the directory stated in the OUTPUT_PATH var, otherwise you won't be able to create a result html\eml file.

## Running script
Once the above prerequisites are fulfilled, please run the below command from the script directory:
python3 ./Script.py
