import os
import requests
from .base import BaseChannel
from backend.schemas.api import ApprovalCard


class SlackChannel(BaseChannel):
    def notify(self, card: ApprovalCard, dashboard_url: str):
        webhook_url = os.getenv("SLACK_WEBHOOK_URL")
        if not webhook_url:
            print("WARNING: SLACK_WEBHOOK_URL not set. Skipping Slack notification.")
            return

        message = (
            f"*Disruption Alert: {card.event.source}*\n"
            f"Vessel: {card.event.vessel_id} | Route: {card.event.route}\n"
            f"Impact: {len(card.exposure.matched_pos)} POs worth ${card.exposure.total_inventory_value_usd:,.2f}\n"
            f"Recommendation: {card.cost_analysis.recommendation}\n\n"
            f"Action Required: <{dashboard_url}|Review and Approve on Dashboard>"
        )

        try:
            response = requests.post(webhook_url, json={"text": message})
            response.raise_for_status()
            print(f"Slack notification sent for event {card.event.event_id}")
        except Exception as e:
            print(f"Failed to send Slack notification: {e}")
