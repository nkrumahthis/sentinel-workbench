# mock_cloudtrail.py
import json
import random
from datetime import datetime, timedelta
import ipaddress
import uuid
import os

class CloudTrailMockGenerator:
    def __init__(self):
        self.users = ["admin-user", "developer1", "system-user", "lambda-role"]
        self.roles = ["AdminRole", "DeveloperRole", "ReadOnlyRole"]
        self.services = ["ec2", "s3", "iam", "lambda", "rds", "dynamodb"]
        self.api_calls = {
            "ec2": [
                "DescribeInstances",
                "RunInstances",
                "StopInstances",
                "StartInstances",
            ],
            "s3": ["GetObject", "PutObject", "ListBucket", "CreateBucket"],
            "iam": ["CreateRole", "AssumeRole", "GetRole", "ListRoles"],
            "lambda": ["InvokeFunction", "CreateFunction", "UpdateFunction"],
            "rds": ["DescribeDBInstances", "StartDBInstance", "CreateDBSnapshot"],
            "dynamodb": ["GetItem", "PutItem", "Query", "Scan"],
        }
        self.user_agents = [
            "aws-cli/2.0.0 Python/3.8.5 Darwin/18.7.0 botocore/2.0.0",
            "console.amazonaws.com",
            "boto3/1.17.78 Python/3.8.5 Linux/5.4.0-42-generic",
            "aws-sdk-java/1.11.969",
        ]

    def generate_ip(self):
        return str(ipaddress.IPv4Address(random.randint(0, 2**32 - 1)))

    def generate_event(self, timestamp=None):
        service = random.choice(self.services)
        user = random.choice(self.users)

        if timestamp is None:
            # Generate timestamp within last 7 days
            timestamp = datetime.now() - timedelta(
                days=random.randint(0, 7),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59),
            )

        event = {
            "eventVersion": "1.08",
            "eventTime": timestamp.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "eventSource": f"{service}.amazonaws.com",
            "eventName": random.choice(self.api_calls[service]),
            "awsRegion": random.choice(["us-east-1", "us-west-2", "eu-west-1"]),
            "sourceIPAddress": self.generate_ip(),
            "userAgent": random.choice(self.user_agents),
            "eventID": str(uuid.uuid4()),
            "eventType": "AwsApiCall",
            "userIdentity": {
                "type": random.choice(["IAMUser", "AssumedRole"]),
                "principalId": f"AIDA{uuid.uuid4().hex[:16].upper()}",
                "arn": f"arn:aws:iam::123456789012:user/{user}",
                "accountId": "123456789012",
                "userName": user,
            },
            "responseElements": None
            if random.random() < 0.1
            else {},  # 10% chance of failed API call
            "requestID": str(uuid.uuid4()),
            "eventCategory": "Management",
        }

        # Add assumed role details if it's an AssumeRole event
        if event["eventName"] == "AssumeRole":
            event["requestParameters"] = {
                "roleArn": f"arn:aws:iam::123456789012:role/{random.choice(self.roles)}",
                "roleSessionName": f"Session_{uuid.uuid4().hex[:8]}",
            }
            event["responseElements"] = {
                "credentials": {
                    "accessKeyId": f"ASIA{uuid.uuid4().hex[:16].upper()}",
                    "sessionToken": f"FwoGZXIvYXdzE{uuid.uuid4().hex}",
                    "expiration": (timestamp + timedelta(hours=1)).strftime(
                        "%Y-%m-%dT%H:%M:%SZ"
                    ),
                }
            }

        return event

    def generate_logs(self, num_events=100, output_file="tmp/test_cloudtrail.json"):
        events = []
        for _ in range(num_events):
            events.append(self.generate_event())

        # Sort events by timestamp
        events.sort(key=lambda x: x["eventTime"])

        with open(output_file, "w") as f:
            json.dump({"Records": events}, f, indent=2)

        return events


# Helper function to create suspicious activity pattern
def generate_suspicious_pattern():
    generator = CloudTrailMockGenerator()

    # Current time
    now = datetime.now()

    # Create a series of events that might indicate suspicious activity
    suspicious_events = []

    # 1. First, some reconnaissance
    for _ in range(3):
        event = generator.generate_event(now - timedelta(minutes=30))
        event["eventName"] = "ListRoles"
        event["eventSource"] = "iam.amazonaws.com"
        suspicious_events.append(event)

    # 2. Assume a role
    assume_role_event = generator.generate_event(now - timedelta(minutes=25))
    assume_role_event["eventName"] = "AssumeRole"
    assume_role_event["eventSource"] = "iam.amazonaws.com"
    suspicious_events.append(assume_role_event)

    # 3. Create some resources
    for _ in range(2):
        event = generator.generate_event(now - timedelta(minutes=20))
        event["eventName"] = "RunInstances"
        event["eventSource"] = "ec2.amazonaws.com"
        suspicious_events.append(event)

    # 4. Access sensitive data
    for _ in range(2):
        event = generator.generate_event(now - timedelta(minutes=15))
        event["eventName"] = "GetObject"
        event["eventSource"] = "s3.amazonaws.com"
        suspicious_events.append(event)

    return suspicious_events


if __name__ == "__main__":
    # Generate regular logs
    generator = CloudTrailMockGenerator()
    regular_events = generator.generate_logs(50)

    # Generate suspicious pattern
    suspicious_events = generate_suspicious_pattern()

    # Combine and save all events
    all_events = regular_events + suspicious_events
    all_events.sort(key=lambda x: x["eventTime"])
    
    os.mkdir("tmp")

    with open("tmp/mock_cloudtrail.json", "w") as f:
        json.dump({"Records": all_events}, f, indent=2)

    print(f"Generated {len(all_events)} events, including a suspicious pattern.")
