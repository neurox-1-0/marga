import os
from .channels.slack_channel import SlackChannel
from .channels.email_channel import EmailChannel
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from shared.schemas import ApprovalCard

def notify_channels(card: ApprovalCard):
    enabled_channels_str = os.getenv("NOTIFICATION_CHANNELS", "")
    dashboard_base_url = os.getenv("DASHBOARD_BASE_URL", "http://localhost:8000/dashboard.html")
    
    if not enabled_channels_str:
        print("No notification channels enabled.")
        return

    enabled_channels = [c.strip().lower() for c in enabled_channels_str.split(",")]
    
    channels = []
    if "slack" in enabled_channels:
        channels.append(SlackChannel())
    if "email" in enabled_channels:
        channels.append(EmailChannel())

    for channel in channels:
        channel.notify(card, dashboard_base_url)
