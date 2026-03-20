import models
import requests
import os
from sqlalchemy.orm import Session
from datetime import datetime

# Webhook URLs (configure in .env)
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", "")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "")

def check_and_trigger_workflows(task_id: int, new_status: str, db: Session):
    """
    Checks if there are any workflows associated with the task and its new status.
    Triggers actions like Slack/Discord notifications.
    """
    # Find triggers for this task
    triggers = db.query(models.WorkflowTrigger).filter(
        models.WorkflowTrigger.task_id == task_id
    ).all()

    # Get the task for context
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    
    if not task:
        return

    for trigger in triggers:
        # Check if condition matches
        if f"Status Changed to {new_status}" in trigger.condition:
            print(f"⚡ WORKFLOW TRIGGERED: {trigger.action} for task {task.title}")
            execute_workflow_action(trigger.action, task, trigger)

def execute_workflow_action(action: str, task: models.Task, trigger: models.WorkflowTrigger):
    """
    Executes workflow actions like Slack/Discord notifications.
    """
    try:
        if "Slack" in action:
            send_slack_notification(task, action)
        elif "Discord" in action:
            send_discord_notification(task, action)
        elif "Email" in action:
            send_email_notification(task, action)
        else:
            print(f"✅ Action executed: {action}")
    except Exception as e:
        print(f"❌ Error executing workflow: {e}")

def send_slack_notification(task: models.Task, action: str):
    """
    Sends a notification to Slack webhook.
    """
    if not SLACK_WEBHOOK_URL:
        print("⚠️  Slack webhook not configured")
        return

    color_map = {
        "Done": "#36a64f",
        "InProgress": "#3b82f6",
        "Todo": "#9ca3af",
        "High": "#ef4444"
    }

    payload = {
        "attachments": [
            {
                "color": color_map.get(task.status, "#3b82f6"),
                "title": f"Task {task.status}: {task.title}",
                "text": task.description or "No description",
                "fields": [
                    {
                        "title": "Priority",
                        "value": task.priority,
                        "short": True
                    },
                    {
                        "title": "Status",
                        "value": task.status,
                        "short": True
                    },
                    {
                        "title": "Action",
                        "value": action,
                        "short": False
                    }
                ],
                "footer": "VoiceFlow Automation",
                "ts": int(datetime.now().timestamp())
            }
        ]
    }

    try:
        response = requests.post(SLACK_WEBHOOK_URL, json=payload, timeout=5)
        if response.status_code == 200:
            print(f"✅ Slack notification sent for task: {task.title}")
        else:
            print(f"❌ Slack error: {response.text}")
    except Exception as e:
        print(f"❌ Slack webhook error: {e}")

def send_discord_notification(task: models.Task, action: str):
    """
    Sends a notification to Discord webhook.
    """
    if not DISCORD_WEBHOOK_URL:
        print("⚠️  Discord webhook not configured")
        return

    color_map = {
        "Done": 3381759,      # Green
        "InProgress": 3447003, # Blue
        "Todo": 10592673,      # Gray
        "High": 15158332       # Red
    }

    embed = {
        "title": f"📌 Task {task.status}: {task.title}",
        "description": task.description or "No description provided",
        "color": color_map.get(task.status, 3447003),
        "fields": [
            {
                "name": "Priority",
                "value": f"🔴 {task.priority}" if task.priority == "High" else f"🟡 {task.priority}",
                "inline": True
            },
            {
                "name": "Status",
                "value": task.status,
                "inline": True
            },
            {
                "name": "Workflow Action",
                "value": action,
                "inline": False
            }
        ],
        "footer": {
            "text": "VoiceFlow Automation Engine"
        },
        "timestamp": datetime.now().isoformat()
    }

    payload = {"embeds": [embed]}

    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=5)
        if response.status_code == 204 or response.status_code == 200:
            print(f"✅ Discord notification sent for task: {task.title}")
        else:
            print(f"❌ Discord error: {response.text}")
    except Exception as e:
        print(f"❌ Discord webhook error: {e}")

def send_email_notification(task: models.Task, action: str):
    """
    Placeholder for email notification.
    In production, integrate with SendGrid, AWS SES, etc.
    """
    print(f"📧 Email notification (placeholder): {task.title} - {action}")
