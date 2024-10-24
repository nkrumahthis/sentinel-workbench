import json

class MockAWSEnrichmentService:
    def __init__(self, mock_file='backend/test_cloudtrail.json'):
        self.mock_file = mock_file
        self.load_mock_data()
    
    def load_mock_data(self):
        """Load mock CloudTrail data from JSON file."""
        try:
            with open(self.mock_file, 'r') as f:
                data = json.load(f)
                self.events = data.get('Records', [])
                print(f"Loaded {len(self.events)} events from mock data")
        except Exception as e:
            print(f"Error loading mock data: {e}")
            self.events = []
            
    def enrich(self, user_name: str, alert_data: dict):
        return {
            'assumedRoleDetails': self.get_assumed_role_details(alert_data),
            'recentRoleAssumptions': self.get_recent_role_assumptions(user_name),
            'serviceInteractions': self.get_service_interactions(user_name),
            'interestingApiCalls': self.get_interesting_api_calls(user_name)
        }

    def get_assumed_role_details(self, event: dict) -> dict:
        """Get details about who assumed a role if the alert involves an assumed role."""
        try:
            user_identity = event.get('userIdentity', {})
            if user_identity.get('type') != 'AssumedRole':
                return {}

            # Get the access key ID from the event
            access_key_id = user_identity.get('accessKeyId')
            if not access_key_id:
                return {}

            # Look for matching AssumeRole event
            for e in self.events:
                print("events", e)
                if (e['eventName'] == 'AssumeRole' and 
                    e.get('responseElements', {}).get('credentials', {}).get('accessKeyId') == access_key_id):
                    return {
                        'assumedBy': e['userIdentity']['userName'],
                        'assumedAt': e['eventTime'],
                        'sourceIP': e['sourceIPAddress'],
                        'roleArn': e.get('requestParameters', {}).get('roleArn')
                    }
            return {}

        except Exception as e:
            print(f"Error in get_assumed_role_details: {e}")
            return {'error': str(e)}

    def get_recent_role_assumptions(self, user_name: str) -> list:
        """Get recent role assumptions by the user."""
        try:
            role_assumptions = []
            for event in self.events:
                if (event['eventName'] == 'AssumeRole' and 
                    event['userIdentity'].get('userName') == user_name):
                    role_assumptions.append({
                        'roleArn': event.get('requestParameters', {}).get('roleArn'),
                        'eventTime': event['eventTime'],
                        'successful': bool(event.get('responseElements')),
                        'sourceIP': event['sourceIPAddress']
                    })
            return role_assumptions

        except Exception as e:
            print(f"Error in get_recent_role_assumptions: {e}")
            return [{'error': str(e)}]

    def get_service_interactions(self, user_name: str) -> dict:
        """Get count of interactions with different AWS services."""
        try:
            service_counts = {}
            for event in self.events:
                if event['userIdentity'].get('userName') == user_name:
                    service = event['eventSource'].split('.')[0]
                    service_counts[service] = service_counts.get(service, 0) + 1
            return service_counts

        except Exception as e:
            print(f"Error in get_service_interactions: {e}")
            return {'error': str(e)}

    def get_interesting_api_calls(self, user_name: str) -> list:
        """Get non-read API calls (excluding Get*, List*, Describe*)."""
        try:
            interesting_calls = []
            for event in self.events:
                if event['userIdentity'].get('userName') == user_name:
                    event_name = event['eventName']
                    if not any(event_name.startswith(prefix) 
                             for prefix in ['Get', 'List', 'Describe', 'Head']):
                        interesting_calls.append({
                            'eventName': event_name,
                            'eventTime': event['eventTime'],
                            'eventSource': event['eventSource'],
                            'sourceIP': event['sourceIPAddress'],
                            'userAgent': event.get('userAgent', 'N/A'),
                            'successful': bool(event.get('responseElements'))
                        })
            return interesting_calls

        except Exception as e:
            print(f"Error in get_interesting_api_calls: {e}")
            return [{'error': str(e)}]