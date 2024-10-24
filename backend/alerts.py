import logging
import json
from typing import Dict


class AlertStore:
    def __init__(self, mock_file="./backend/test_cloudtrail.json"):
        self.mock_file = mock_file
        self.alerts = self._generate_sample_alerts()

    def _generate_sample_alerts(self) -> Dict:
        """Generate sample alerts from CloudTrail data."""
        try:
            with open(self.mock_file, "r") as f:
                data = json.load(f)
                events = data.get("Records", [])

            # Group interesting events into alerts
            alerts = {}
            alert_id = 1

            # Create an alert for each AssumeRole event
            for event in events:
                if event["eventName"] == "AssumeRole":
                    alerts[str(alert_id)] = {
                        "id": str(alert_id),
                        "title": f"Role Assumption: {event['userIdentity'].get('userName', 'Unknown')}",
                        "severity": "MEDIUM",
                        "status": "NEW",
                        "timestamp": event["eventTime"],
                        "userName": event["userIdentity"].get("userName", "Unknown"),
                        "eventName": event["eventName"],
                        "sourceIP": event["sourceIPAddress"],
                        "userAgent": event.get("userAgent", "N/A"),
                        "eventData": event,
                    }
                    alert_id += 1

                # Create alerts for suspicious API calls
                elif not any(
                    event["eventName"].startswith(prefix)
                    for prefix in ["Get", "List", "Describe", "Head"]
                ):
                    alerts[str(alert_id)] = {
                        "id": str(alert_id),
                        "title": f"Suspicious API: {event['eventName']}",
                        "severity": "HIGH"
                        if "Create" in event["eventName"]
                        else "MEDIUM",
                        "status": "NEW",
                        "timestamp": event["eventTime"],
                        "userName": event["userIdentity"].get("userName", "Unknown"),
                        "eventName": event["eventName"],
                        "sourceIP": event["sourceIPAddress"],
                        "userAgent": event.get("userAgent", "N/A"),
                        "eventData": event,
                    }
                    alert_id += 1

            return alerts

        except Exception as e:
            logging.error(f"Error generating alerts: {e}")
            return {}
