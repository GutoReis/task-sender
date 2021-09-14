from datetime import datetime
import os

from dotenv import load_dotenv
import requests
from slack_sdk.webhook import WebhookClient

load_dotenv()
TODOIST_TOKEN = os.environ["TODOIST_API_KEY"]
TODOIST_URL = os.environ["TODOIST_URL"]
TODOIST_PROJECT = os.environ["TODOIST_PROJECT"]


def get_today_goal():
    SECTION_ID = os.environ["TODOIST_SECTION_GOAL"]
    url = f"{TODOIST_URL}/tasks"
    params = {"project_id": TODOIST_PROJECT,
              "section_id": SECTION_ID}
    header = {"Authorization": f"Bearer {TODOIST_TOKEN}"}
    response = requests.get(url=url, params=params, headers=header)
    content = response.json()
    goal = content[0]["content"].replace("*", "").strip()
    return goal

def get_labels_name(labels_ids):
    label_names = list()
    header = {"Authorization": f"Bearer {TODOIST_TOKEN}"}
    for label_id in labels_ids:
        url = f"{TODOIST_URL}/labels/{label_id}"
        response = requests.get(url=url, headers=header)
        label = response.json()["name"].upper()
        label_names.append(label)
    return label_names

def get_yesterday_tasks():
    SECTION_ID = os.environ["TODOIST_SECTION_YESTERDAY"]
    url = f"{TODOIST_URL}/tasks"
    params = {"project_id": TODOIST_PROJECT,
              "section_id": SECTION_ID}
    header = {"Authorization": f"Bearer {TODOIST_TOKEN}"}
    response = requests.get(url=url, params=params, headers=header)
    content = response.json()
    full_text = ""
    for item in content:
        if "parent" not in item:
            labels = get_labels_name(item["label_ids"])
            task_text = ">"
            if "RECURRING" in labels:
                labels.remove("RECURRING")
                task_text += "TD - "
            elif "MEETING" in labels:
                task_text += "R - "
            else:
                task_text += "T - "
            task_text += f"[{labels[0]}]"
            task_text += item["content"]
            task_text += "\n"
            full_text += task_text
    if full_text:
        return full_text
    else:
        return "> -"       


def get_today_tasks():
    SECTION_ID = os.environ["TODOIST_SECTION_TODAY"]
    url = f"{TODOIST_URL}/tasks"
    params = {"project_id": TODOIST_PROJECT,
              "section_id": SECTION_ID}
    header = {"Authorization": f"Bearer {TODOIST_TOKEN}"}
    response = requests.get(url=url, params=params, headers=header)
    content = response.json()
    full_text = ""
    for item in content:
        if "parent" not in item:
            labels = get_labels_name(item["label_ids"])
            task_text = ">"
            if "RECURRING" in labels:
                labels.remove("RECURRING")
                task_text += "TD - "
            elif "MEETING" in labels:
                task_text += "R - "
            else:
                task_text += "T - "
            task_text += f"[{labels[0]}]"
            task_text += item["content"]
            task_text += "\n"
            full_text += task_text
    if full_text:
        return full_text
    else:
        return "> -"


def get_blocked_tasks():
    SECTION_ID = os.environ["TODOIST_SECTION_BLOCKED"]
    url = f"{TODOIST_URL}/tasks"
    params = {"project_id": TODOIST_PROJECT,
              "section_id": SECTION_ID}
    header = {"Authorization": f"Bearer {TODOIST_TOKEN}"}
    response = requests.get(url=url, params=params, headers=header)
    content = response.json()
    full_text = ""
    for item in content:
        if "parent" not in item:
            labels = get_labels_name(item["label_ids"])
            task_text = "> B -"
            task_text += f"[{labels[0]}]"
            task_text += item["content"]
            task_text += "\n"
            full_text += task_text
    if full_text:
        return full_text
    else:
        return "> -"


def build_msg_block():
    blocks = list()
    today = datetime.now().strftime("%d/%m/%Y")
    morning = {"type": "context",
               "elements": [{"type": "plain_text",
                             "text": ":tea: Bom dia",
                             "emoji": True}]}
    blocks.append(morning)
    day_block = {"type": "context",
                 "elements": [{"type": "mrkdwn",
                               "text": f":date: *Tarefas Dia: {today}*"}]}
    blocks.append(day_block)
    blocks.append({"type": "divider"})
    # NOTE: TODAY GOAL SECTION
    goal_header = {"type": "header",
                    "text": {"type": "plain_text",
                             "text": ":dart: Meta do dia:",
                             "emoji": True}}
    todoist_goal = get_today_goal()
    goal_block = {"type": "context",
                  "elements": [{"type": "mrkdwn",
                                "text": f">{todoist_goal}"}]}
    blocks.append(goal_header)
    blocks.append(goal_block)
    # NOTE: YESTERDAY TASK SECTION
    yesterday_header = {"type": "header",
                        "text": {"type": "plain_text",
                                 "text": ":crescent_moon: Planejadas Ontem",
                                 "emoji": True}}
    yesterday_tasks = get_yesterday_tasks()
    yesterday_block = {"type": "context",
                       "elements": [{"type": "mrkdwn",
                                     "text": yesterday_tasks}]}
    blocks.append(yesterday_header)
    blocks.append(yesterday_block)
    # NOTE: TODAY TASK SECTION
    today_header = {"type": "header",
                    "text": {"type": "plain_text",
                             "text": ":sunny: Planejadas Hoje",
                             "emoji": True}}
    today_tasks = get_today_tasks()
    today_block = {"type": "context",
                   "elements": [{"type": "mrkdwn",
                                 "text": today_tasks}]}
    blocks.append(today_header)
    blocks.append(today_block)
    # NOTE: BLOCKED TASK SECTION
    blocked_header = {"type": "header",
                      "text": {"type": "plain_text",
                               "text": ":no_entry: Bloqueado",
                               "emoji": True}}
    blocked_tasks = get_blocked_tasks()
    blocked_block = {"type": "context",
                   "elements": [{"type": "mrkdwn",
                                 "text": blocked_tasks}]}
    blocks.append(blocked_header)
    blocks.append(blocked_block)
    return blocks


def send_msg_slack():
    block_structure = build_msg_block()
    slack_url = os.environ["SLACK_WEBHOOK"]
    webhook = WebhookClient(slack_url)
    response = webhook.send(text="Today tasks", blocks=block_structure)


if __name__ == "__main__":
    send_msg_slack()
