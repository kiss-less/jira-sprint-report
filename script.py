import requests, os, json, datetime
import emoji
import html2eml

JIRA_DOMAIN = "https://jira.yourdomain.com"
JIRA_SERVICEDESK_DOMAIN = "https://yourjiraservicedesk.atlassian.net"
JIRA_AGILE_API = "{0}/rest/agile/1.0/board".format(JIRA_DOMAIN)
JIRA_SINGLE_ISSUE_API = "{0}/rest/agile/1.0/issue".format(JIRA_DOMAIN)
JIRA_GREENHOPPER_API = "{0}/rest/greenhopper/latest/rapid/charts/sprintreport".format(JIRA_DOMAIN)
JIRA_SERVICEDESK_SERVICEDESK_ID = "15"
JIRA_SERVICEDESK_OPEN_QUEUE_ID = "134"
JIRA_SERVICEDESK_COMPLETED_QUEUE_ID = "132"
JIRA_BOARD_ID = "33"
JIRA_STORY_POINTS_FIELD_ID = "11300"
JIRA_TEAM_NAME = "Your Team Name"
FULL_JIRA_AGILE_API_URL = "{0}/{1}/issue".format(JIRA_AGILE_API, JIRA_BOARD_ID)
FULL_JIRA_SPRINT_API_URL = "{0}/{1}/sprint".format(JIRA_AGILE_API, JIRA_BOARD_ID)
FULL_JIRA_GREENHOPPER_API_URL = "{0}?rapidViewId={1}".format(JIRA_GREENHOPPER_API, JIRA_BOARD_ID)
FULL_JIRA_SERVICEDESK_OPEN_QUEUE_API = "{0}/rest/servicedeskapi/servicedesk/{1}/queue/{2}/issue".format(JIRA_SERVICEDESK_DOMAIN, JIRA_SERVICEDESK_SERVICEDESK_ID, JIRA_SERVICEDESK_OPEN_QUEUE_ID)
FULL_JIRA_SERVICEDESK_COMPLETED_QUEUE_API = "{0}/rest/servicedeskapi/servicedesk/{1}/queue/{2}/issue".format(JIRA_SERVICEDESK_DOMAIN, JIRA_SERVICEDESK_SERVICEDESK_ID, JIRA_SERVICEDESK_COMPLETED_QUEUE_ID)
JIRA_USER_EMAIL = os.environ["EMAIL"] or ""
JIRA_API_KEY = os.environ["JIRA_API_KEY"] or ""
ADD_COMMENTS_AS_TASKS_STATUS = True
PRINT_INFO_LOG_MESSAGES = True
PRINT_WARNING_LOG_MESSAGES = True
PRINT_ERROR_LOG_MESSAGES = True
JIRA_LABEL_1 = "Infrastructure"
JIRA_LABEL_2 = "Adhoc"
LOG_TO_FILE = True
CREATE_EML_FILE = True
OUTPUT_PATH = "."
OUTPUT_HTML_FILE_NAME = "result.html"
OUTPUT_EML_FILE_NAME = "email.eml"


def check_jira_auth_env_vars():
    print_log_message(PRINT_INFO_LOG_MESSAGES, "Checking environment variables configuration", "[Info]")
    if (not JIRA_USER_EMAIL or not JIRA_API_KEY):
        print_log_message(PRINT_ERROR_LOG_MESSAGES, "Please set the environment variables before running the script to be able to authenticate against Jira APIs. More info about Jira API auth: https://developer.atlassian.com/server/jira/platform/basic-authentication/", "[Error]")
        exit(1)

def print_log_message(send, msg, log_level):
    log_filename = "script.log"
    log_message = "{0} {1}: {2}".format(datetime.datetime.now(), log_level, msg)
    if (send):
        print(log_message)
        if (LOG_TO_FILE):
            try:
                f = open(log_filename, "a")
                f.write("{0}\n".format(log_message))
                f.close()
            except:
                print("{0} {1}: There was a problem writing logs to file {2}".format(datetime.datetime.now(), "[Error]", log_filename))
                pass

def get_response_text_from_get_request_with_basic_auth(url, user = JIRA_USER_EMAIL, password = JIRA_API_KEY):
    try:
        print_log_message(PRINT_INFO_LOG_MESSAGES, "Sending GET request with basic auth to {0}".format(url), "[Info]")
        r = requests.get(url, auth=(user, password))
        print_log_message(PRINT_INFO_LOG_MESSAGES, "Request has been sent. Status code: {0}".format(r.status_code), "[Info]")
        return r.text
    except:
        print_log_message(PRINT_ERROR_LOG_MESSAGES, "Something went wrong with sending the request to {0}. Status code: {1}".format(url, r.status_code), "[Error]")
        exit(1)

def get_issue_labels(id):
    issue_json = json.loads(get_response_text_from_get_request_with_basic_auth("{0}/{1}".format(JIRA_SINGLE_ISSUE_API, id)))
    return issue_json["fields"]["labels"]

def get_jira_servicedesk_issues_opened_last_sprint():
    issues_json = json.loads(get_response_text_from_get_request_with_basic_auth(FULL_JIRA_SERVICEDESK_OPEN_QUEUE_API, JIRA_USER_EMAIL, JIRA_API_KEY))
    return issues_json["size"]

def get_jira_servicedesk_issues_completed_last_sprint():
    issues_json = json.loads(get_response_text_from_get_request_with_basic_auth(FULL_JIRA_SERVICEDESK_COMPLETED_QUEUE_API, JIRA_USER_EMAIL, JIRA_API_KEY))
    return issues_json["size"]

def get_issues_removed_from_current_sprint_json(greenhopper_api_url, sprint_id):
    print_log_message(PRINT_INFO_LOG_MESSAGES, "Getting the issues removed from the current Sprint", "[Info]")
    removed_issues_json = json.loads(get_response_text_from_get_request_with_basic_auth("{0}&sprintId={1}".format(greenhopper_api_url, sprint_id)))
    return removed_issues_json["contents"]["puntedIssues"]

def get_current_sprint_json(sprint_api_url, JIRA_TEAM_NAME):
    print_log_message(PRINT_INFO_LOG_MESSAGES, "Getting the current Sprint info for the team {0}".format(JIRA_TEAM_NAME), "[Info]")
    sprints_json = json.loads(get_response_text_from_get_request_with_basic_auth("{0}?state=active".format(sprint_api_url)))
    for sprint in sprints_json["values"]:
        if (JIRA_TEAM_NAME in sprint["name"]):
            print_log_message(PRINT_INFO_LOG_MESSAGES, "Successfully received the current Sprint info for the team {0}".format(JIRA_TEAM_NAME), "[Info]")
            return sprint
    print_log_message(PRINT_ERROR_LOG_MESSAGES, "Couldn't get the current sprint for the team {0} from the API!".format(JIRA_TEAM_NAME), "[Error]")
    exit(1)

def get_next_sprint_json(sprint_api_url, JIRA_TEAM_NAME):
    print_log_message(PRINT_INFO_LOG_MESSAGES, "Getting the next Sprint info for the team {0}".format(JIRA_TEAM_NAME), "[Info]")
    future_sprints_json = json.loads(get_response_text_from_get_request_with_basic_auth("{0}?state=future".format(sprint_api_url)))
    if (JIRA_TEAM_NAME in future_sprints_json["values"][0]["name"]):
        print_log_message(PRINT_INFO_LOG_MESSAGES, "Successfully received the next Sprint info for the team {0}".format(JIRA_TEAM_NAME), "[Info]")
        return future_sprints_json["values"][0]
    print_log_message(PRINT_ERROR_LOG_MESSAGES, "Couldn't get the next sprint for the team {0} from the API!".format(JIRA_TEAM_NAME), "[Error]")
    exit(1)

def get_emoji(status):
    print_log_message(PRINT_INFO_LOG_MESSAGES, "Getting emoji for status '{0}'".format(status), "[Info]")
    successful_msg = "Emoji successfully received"
    if (status == "To Do"):
        print_log_message(PRINT_INFO_LOG_MESSAGES, successful_msg, "[Info]")
        return ":memo:"
    if (status == "In Progress"):
        print_log_message(PRINT_INFO_LOG_MESSAGES, successful_msg, "[Info]")
        return ":construction:"
    if (status == "Waiting for Dependency"):
        print_log_message(PRINT_INFO_LOG_MESSAGES, successful_msg, "[Info]")
        return ":counterclockwise_arrows_button:"
    if (status == "In Review"):
        print_log_message(PRINT_INFO_LOG_MESSAGES, successful_msg, "[Info]")
        return ":bookmark_tabs:"
    if (status == "Done"):
        print_log_message(PRINT_INFO_LOG_MESSAGES, successful_msg, "[Info]")
        return ":check_mark_button:"
    else:
        print_log_message(PRINT_WARNING_LOG_MESSAGES, "Couldn't get emoji for status '{0}'".format(status), "[Warn]")
        return ""

# TODO - Grab ids from the API
def get_issue_type_from_id(id):
    print_log_message(PRINT_INFO_LOG_MESSAGES, "Getting issue type for id '{0}'".format(id), "[Info]")
    successful_msg = "Issue type successfully received"
    if (id == "10001"):
        print_log_message(PRINT_INFO_LOG_MESSAGES, successful_msg, "[Info]")
        return "Story"
    if (id == "10102"):
        print_log_message(PRINT_INFO_LOG_MESSAGES, successful_msg, "[Info]")
        return "Bug"
    if (id == "10105"):
        print_log_message(PRINT_INFO_LOG_MESSAGES, successful_msg, "[Info]")
        return "Task"
    if (id == "11100"):
        print_log_message(PRINT_INFO_LOG_MESSAGES, successful_msg, "[Info]")
        return "Action Point"
    else:
        print_log_message(PRINT_WARNING_LOG_MESSAGES, "Couldn't get type for id '{0}'".format(id), "[Warn]")
        return ""    

def assemble_msg(current_sprint_name, next_sprint_name, current_commitments_str, planned_tasks_str, html_format, JIRA_TEAM_NAME):
    result = "Hello everyone,<br><br>Please find below {0} Commitments from the past {1} and our plans for {2}.<br>".format(JIRA_TEAM_NAME, current_sprint_name, next_sprint_name)
    result += current_commitments_str
    result += planned_tasks_str
    result += "</ol><br>Please contact me if you have any questions {0}".format(emoji.emojize(":smiling_face_with_smiling_eyes:"))
    if (html_format):
        return result
    else:
        return replace_html_tags(result)

def replace_html_tags(string):
    tags_list = ["<h3>", "</h3>", "<ol>", "</ol>", "<li>", "</li>", "<h4>", "</h4>"]
    for tag in tags_list:
        string = string.replace(tag, "") 
    return string.replace("<br>", "\n")

check_jira_auth_env_vars()
print_log_message(PRINT_INFO_LOG_MESSAGES, "Starting the script", "[Info]")
current_sprint_json = get_current_sprint_json(FULL_JIRA_SPRINT_API_URL, JIRA_TEAM_NAME)
next_sprint_json = get_next_sprint_json(FULL_JIRA_SPRINT_API_URL, JIRA_TEAM_NAME)
issues_json = json.loads(get_response_text_from_get_request_with_basic_auth("{0}?maxResults=500&jql=sprint in ({1}, {2}) and issuetype!='Action Point' and issuetype!='Subtask'".format(FULL_JIRA_AGILE_API_URL, current_sprint_json["id"], next_sprint_json["id"])))
ad_hoc_tasks_str = ""
current_tasks_str = "<h3>{0} Commitments ({1} - {2})</h3>".format(current_sprint_json["name"], current_sprint_json["startDate"][0:10], current_sprint_json["endDate"][0:10])
current_tasks_JIRA_LABEL_1_str = "<h4>{0} tasks</h4><ol>".format(JIRA_LABEL_1)
current_tasks_JIRA_LABEL_2_str = "</ol><h4>{0} related tasks ⚙</h4><ol>".format(JIRA_LABEL_2)
planned_tasks_str = "<h3>{0} Plans ({1} - {2})</h3>".format(next_sprint_json["name"], next_sprint_json["startDate"][0:10], next_sprint_json["endDate"][0:10])
planned_tasks_JIRA_LABEL_1_str = current_tasks_JIRA_LABEL_1_str
planned_tasks_JIRA_LABEL_2_str = current_tasks_JIRA_LABEL_2_str
story_points = 0

print_log_message(PRINT_INFO_LOG_MESSAGES, "Iterating through the issues_json", '[Info]')
for issue in issues_json["issues"]:
    st_emoji = get_emoji(issue["fields"]["status"]["name"])
    if (current_sprint_json["id"] == issue["fields"]["sprint"]["id"]):
        last_comment = ""
        if (issue["fields"]["comment"]["comments"] and ADD_COMMENTS_AS_TASKS_STATUS and issue["fields"]["status"]["name"] != "Done" and issue["fields"]["status"]["name"] != "In Review"):
            last_comment = issue["fields"]["comment"]["comments"][len(issue["fields"]["comment"]["comments"]) - 1]["body"]
        if (JIRA_LABEL_2 in issue["fields"]["labels"]):
            if (datetime.datetime.strptime(issue["fields"]["created"][0:10], "%Y-%m-%d") < datetime.datetime.strptime(issue["fields"]["sprint"]["startDate"][0:10], "%Y-%m-%d")):
                current_tasks_JIRA_LABEL_2_str += "<li>{0} {1} {2} {3} - {4}. {5}</li>".format(emoji.emojize(st_emoji), issue["fields"]["issuetype"]["name"], issue["key"], issue["fields"]["summary"] , issue["fields"]["status"]["name"], last_comment)
        elif (JIRA_LABEL_1 in issue["fields"]["labels"]):
            if (datetime.datetime.strptime(issue["fields"]["created"][0:10], "%Y-%m-%d") < datetime.datetime.strptime(issue["fields"]["sprint"]["startDate"][0:10], "%Y-%m-%d")):
                current_tasks_JIRA_LABEL_1_str += "<li>{0} {1} {2} {3} - {4}. {5}</li>".format(emoji.emojize(st_emoji), issue["fields"]["issuetype"]["name"], issue["key"], issue["fields"]["summary"] , issue["fields"]["status"]["name"], last_comment)
        else:
            print_log_message(PRINT_WARNING_LOG_MESSAGES, "There is an issue {0} without a label. Putting it to the top of the list".format(issue["key"]), "[Warn]")
            current_tasks_str += "[No label] {0} {1} {2} {3} - {4} {5}.<br>".format(emoji.emojize(st_emoji), issue["fields"]["issuetype"]["name"], issue["key"], issue["fields"]["summary"] , issue["fields"]["status"]["name"], last_comment)
        if (issue["fields"]["status"]["name"] == "Done" and issue["fields"]["customfield_{0}".format(JIRA_STORY_POINTS_FIELD_ID)] and issue["fields"]["customfield_{0}".format(JIRA_STORY_POINTS_FIELD_ID)]["value"].replace('.','',1).isdigit()):
            story_points += float(issue["fields"]["customfield_{0}".format(JIRA_STORY_POINTS_FIELD_ID)]["value"])
        if (datetime.datetime.strptime(issue["fields"]["created"][0:10], "%Y-%m-%d") >= datetime.datetime.strptime(issue["fields"]["sprint"]["startDate"][0:10], "%Y-%m-%d")):
            ad_hoc_tasks_str += "<li>{0} {1} {2} {3} - {4}. {5}</li>".format(emoji.emojize(st_emoji), issue["fields"]["issuetype"]["name"], issue["key"], issue["fields"]["summary"] , issue["fields"]["status"]["name"], last_comment)
    if (next_sprint_json["id"] == issue["fields"]["sprint"]["id"]):
        if (JIRA_LABEL_2 in issue["fields"]["labels"]):
            planned_tasks_JIRA_LABEL_2_str += "<li>{0} {1} {2}</li>".format(issue["fields"]["issuetype"]["name"], issue["key"], issue["fields"]["summary"])
        elif (JIRA_LABEL_1 in issue["fields"]["labels"]):
            planned_tasks_JIRA_LABEL_1_str += "<li>{0} {1} {2}</li>".format(issue["fields"]["issuetype"]["name"], issue["key"], issue["fields"]["summary"])
        else:
            print_log_message(PRINT_WARNING_LOG_MESSAGES, "There is an issue {0} without a label. Putting it to the top of the list".format(issue["key"]), "[Warn]")
            planned_tasks_str += "[No label] {0} {1} {2}<br>".format(issue["fields"]["issuetype"]["name"], issue["key"], issue["fields"]["summary"])
issues_removed_from_current_sprint_json = get_issues_removed_from_current_sprint_json(FULL_JIRA_GREENHOPPER_API_URL, current_sprint_json["id"])
if (issues_removed_from_current_sprint_json):
    print_log_message(PRINT_INFO_LOG_MESSAGES, "Iterating through the issues_removed_from_current_sprint_json", '[Info]')
    for issue in issues_removed_from_current_sprint_json:
        if  (get_issue_type_from_id(issue["typeId"]) != "Action Point"):
            if (JIRA_LABEL_2 in get_issue_labels(issue["id"])):
                current_tasks_JIRA_LABEL_2_str += "<li>{0} {1} {2} {3} - Removed from the current Sprint scope </li>".format(emoji.emojize(":counterclockwise_arrows_button:"), get_issue_type_from_id(issue["typeId"]), issue["key"], issue["summary"])
            elif (JIRA_LABEL_1 in get_issue_labels(issue["id"])):
                current_tasks_JIRA_LABEL_1_str += "<li>{0} {1} {2} {3} - Removed from the current Sprint scope </li>".format(emoji.emojize(":counterclockwise_arrows_button:"), get_issue_type_from_id(issue["typeId"]), issue["key"], issue["summary"])
            else:
                print_log_message(PRINT_WARNING_LOG_MESSAGES, "There is an issue {0} without a label. Putting it to the top of the list".format(issue["key"]), "[Warn]")
                current_tasks_str += "{0} {1} {2} {3} - Removed from the current Sprint scope <br>".format(emoji.emojize(":counterclockwise_arrows_button:"), get_issue_type_from_id(issue["typeId"]), issue["key"], issue["summary"])

else:
    print_log_message(PRINT_INFO_LOG_MESSAGES, "No issues were removed from the current sprint", '[Info]')

current_tasks_str += current_tasks_JIRA_LABEL_1_str
current_tasks_str += current_tasks_JIRA_LABEL_2_str
current_tasks_str += "</ol><h3>Sprint velocity {0} - {1} Story Points<br><br>Ad-hoc tasks</h3><ol>".format(emoji.emojize(":rocket:"), story_points)
planned_tasks_str += planned_tasks_JIRA_LABEL_1_str
planned_tasks_str += planned_tasks_JIRA_LABEL_2_str
if (ad_hoc_tasks_str): current_tasks_str += ad_hoc_tasks_str
current_tasks_str += "</ol><h3>Jira Servicedesk tickets</h3>{0} {1} Created <br>{2} {3} Resolved<br>".format(emoji.emojize(":fire:"), get_jira_servicedesk_issues_opened_last_sprint() , emoji.emojize(":check_mark_button:"), get_jira_servicedesk_issues_completed_last_sprint())
print_log_message(PRINT_INFO_LOG_MESSAGES, "Iteration through the issues_json has been successfully finished", '[Info]')

try:
    full_path_html = "{0}/{1}".format(OUTPUT_PATH, OUTPUT_HTML_FILE_NAME)
    last_modified = os.path.getmtime(full_path_html)
    new_name = "{0}_{1}.bak".format(OUTPUT_HTML_FILE_NAME, last_modified)
    print_log_message(PRINT_INFO_LOG_MESSAGES, "Trying to rename {0} to {1}".format(full_path_html, new_name), "[Info]")
    os.rename(full_path_html, "{0}/{1}".format(OUTPUT_PATH, new_name))
    print_log_message(PRINT_INFO_LOG_MESSAGES, "Successfully renamed {0} to {1}".format(full_path_html, new_name), "[Info]")
except:
    print_log_message(PRINT_WARNING_LOG_MESSAGES, "{0} wasn't renamed!".format(full_path_html), "[Warn]")
print_log_message(PRINT_INFO_LOG_MESSAGES, "Opening {0} with the Write attribute".format(full_path_html), "[Info]")

try:
    f = open(full_path_html, "w")
    print_log_message(PRINT_INFO_LOG_MESSAGES, "Assembling the message in HTML format and writing results to the file", "[Info]")
    result_msg_html = assemble_msg(current_sprint_json["name"], next_sprint_json["name"], current_tasks_str, planned_tasks_str, True, JIRA_TEAM_NAME)
    f.write(result_msg_html)
    f.close()
except:
    print_log_message(PRINT_ERROR_LOG_MESSAGES, "Something went wrong with writing to the file {0}".format(full_path_html), "[Error]")
    print_to_stdout = input("Do you want to print the results to stdout? y/n: ")
    if (print_to_stdout.lower() == "y" or print_to_stdout.lower() == "yes"):
        print_log_message(PRINT_INFO_LOG_MESSAGES, "Assembling the message in stdout format and printing results to stdout", "[Info]")
        print("")
        result_msg_stdout = assemble_msg(current_sprint_json["name"], next_sprint_json["name"], current_tasks_str, planned_tasks_str, False, JIRA_TEAM_NAME)
        print(result_msg_stdout)

print_log_message(PRINT_INFO_LOG_MESSAGES, "The script has been finished successfully. Please check {0}".format(full_path_html), "[Info]")

if CREATE_EML_FILE:
    full_path_eml = "{0}/{1}".format(OUTPUT_PATH, OUTPUT_EML_FILE_NAME)
    try:
        e = open(full_path_eml, "w")
        print_log_message(PRINT_INFO_LOG_MESSAGES, "Creating {0} file".format(full_path_eml), "[Info]")
        result_msg_eml = html2eml.from_html(result_msg_html, subject='{0} Commitments'.format(current_sprint_json["name"]))
        e.write(result_msg_eml.as_string())
        e.close()
    except:
        print_log_message(PRINT_ERROR_LOG_MESSAGES, "Something went wrong with writing to the file {0}".format(full_path_eml), "[Error]")
