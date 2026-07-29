"""
backend/notifications/notifier.py — Fan-out notification dispatcher

Reads NOTIFICATION_CHANNELS env var and dispatches approval card alerts
to configured channels (slack, email).
"""

import os
from backend.schemas.api import ApprovalCard
from .channels.slack_channel import SlackChannel
from .channels.email_channel import EmailChannel


def notify_channels(card: ApprovalCard):
    enabled_str = os.getenv("NOTIFICATION_CHANNELS", "")
    dashboard_url = os.getenv("DASHBOARD_BASE_URL", "http://localhost:8004/dashboard")

    if not enabled_str:
        print("[notifier] No notification channels enabled.")
        return

    enabled = [c.strip().lower() for c in enabled_str.split(",")]
    channels = []
    if "slack" in enabled:
        channels.append(SlackChannel())
    if "email" in enabled:
        channels.append(EmailChannel())

    for channel in channels:
        channel.notify(card, dashboard_url)
