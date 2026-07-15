import os
import smtplib
from email.message import EmailMessage
from .base import BaseChannel
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))
from shared.schemas import ApprovalCard

class EmailChannel(BaseChannel):
    def notify(self, card: ApprovalCard, dashboard_url: str):
        smtp_user = os.getenv("SMTP_USER")
        smtp_pass = os.getenv("SMTP_PASSWORD")
        recipient = os.getenv("ALERT_RECIPIENT_EMAIL")

        if not all([smtp_user, smtp_pass, recipient]):
            print("WARNING: Email credentials or recipient not set. Skipping Email notification.")
            return

        msg = EmailMessage()
        msg['Subject'] = f"ACTION REQUIRED: Supply Chain Disruption - {card.event.source}"
        msg['From'] = smtp_user
        msg['To'] = recipient

        content = (
            f"Disruption Alert: {card.event.source}\n"
            f"Vessel: {card.event.vessel_id} | Route: {card.event.route}\n"
            f"Expected Delay: {card.event.delay_days_estimate} days\n"
            f"Impact: {len(card.exposure.matched_pos)} POs worth ${card.exposure.total_inventory_value_usd:,.2f}\n"
            f"Recommendation: {card.cost_analysis.recommendation}\n\n"
            f"Please review and approve the action on the dashboard:\n{dashboard_url}\n"
        )
        msg.set_content(content)

        try:
            # Assuming Gmail for demo, would normally be configurable
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login(smtp_user, smtp_pass)
                smtp.send_message(msg)
            print(f"Email notification sent for event {card.event.event_id}")
        except Exception as e:
            print(f"Failed to send Email notification: {e}")
