import unittest
from unittest.mock import mock_open, patch
import json
from alerts import AlertStore

class TestAlertStore(unittest.TestCase):
    def setUp(self):
        # Sample CloudTrail data containing various types of events
        self.sample_data = {
            "Records": [
                {
                    "eventTime": "2024-10-16T03:54:00Z",
                    "eventSource": "sts.amazonaws.com",
                    "eventName": "AssumeRole",
                    "sourceIPAddress": "32.118.234.47",
                    "userAgent": "aws-cli/2.0.0",
                    "userIdentity": {
                        "userName": "admin-user"
                    }
                },
                {
                    "eventTime": "2024-10-16T04:20:00Z",
                    "eventSource": "s3.amazonaws.com",
                    "eventName": "CreateBucket",
                    "sourceIPAddress": "142.130.179.217",
                    "userAgent": "boto3/1.17.78",
                    "userIdentity": {
                        "userName": "system-user"
                    }
                },
                {
                    "eventTime": "2024-10-16T04:30:00Z",
                    "eventSource": "s3.amazonaws.com",
                    "eventName": "ListBuckets",  # This should be filtered out
                    "sourceIPAddress": "142.130.179.217",
                    "userAgent": "boto3/1.17.78",
                    "userIdentity": {
                        "userName": "system-user"
                    }
                }
            ]
        }

    def test_init_with_valid_data(self):
        """Test initialization with valid mock data"""
        with patch('builtins.open', mock_open(read_data=json.dumps(self.sample_data))):
            store = AlertStore()
            self.assertIsNotNone(store.alerts)
            self.assertEqual(len(store.alerts), 2)  # AssumeRole and CreateBucket events

    def test_alert_generation_for_assume_role(self):
        """Test alert generation for AssumeRole events"""
        with patch('builtins.open', mock_open(read_data=json.dumps(self.sample_data))):
            store = AlertStore()
            assume_role_alerts = [
                alert for alert in store.alerts.values()
                if alert['eventName'] == 'AssumeRole'
            ]
            
            self.assertEqual(len(assume_role_alerts), 1)
            alert = assume_role_alerts[0]
            self.assertEqual(alert['severity'], 'MEDIUM')
            self.assertEqual(alert['status'], 'NEW')
            self.assertEqual(alert['userName'], 'admin-user')
            self.assertEqual(alert['sourceIP'], '32.118.234.47')
            self.assertEqual(alert['userAgent'], 'aws-cli/2.0.0')

    def test_alert_generation_for_suspicious_api(self):
        """Test alert generation for suspicious API calls"""
        with patch('builtins.open', mock_open(read_data=json.dumps(self.sample_data))):
            store = AlertStore()
            create_bucket_alerts = [
                alert for alert in store.alerts.values()
                if alert['eventName'] == 'CreateBucket'
            ]
            
            self.assertEqual(len(create_bucket_alerts), 1)
            alert = create_bucket_alerts[0]
            self.assertEqual(alert['severity'], 'HIGH')  # CreateBucket should be HIGH severity
            self.assertEqual(alert['status'], 'NEW')
            self.assertEqual(alert['userName'], 'system-user')
            self.assertEqual(alert['sourceIP'], '142.130.179.217')

    def test_filtering_of_read_operations(self):
        """Test that read operations (Get*, List*, Describe*, Head*) are filtered out"""
        with patch('builtins.open', mock_open(read_data=json.dumps(self.sample_data))):
            store = AlertStore()
            list_bucket_alerts = [
                alert for alert in store.alerts.values()
                if alert['eventName'] == 'ListBuckets'
            ]
            self.assertEqual(len(list_bucket_alerts), 0)

    def test_error_handling_with_invalid_file(self):
        """Test error handling when mock file is invalid or not found"""
        with patch('builtins.open', mock_open()) as mock_file:
            mock_file.side_effect = FileNotFoundError()
            store = AlertStore()
            self.assertEqual(store.alerts, {})

    def test_error_handling_with_invalid_json(self):
        """Test error handling when mock file contains invalid JSON"""
        with patch('builtins.open', mock_open(read_data="invalid json")):
            store = AlertStore()
            self.assertEqual(store.alerts, {})

    def test_alert_id_generation(self):
        """Test that alert IDs are properly generated and unique"""
        with patch('builtins.open', mock_open(read_data=json.dumps(self.sample_data))):
            store = AlertStore()
            alert_ids = set(store.alerts.keys())
            self.assertEqual(len(alert_ids), len(store.alerts))
            
            # Check that IDs are strings and properly formatted
            for alert_id in alert_ids:
                self.assertIsInstance(alert_id, str)
                self.assertTrue(alert_id.isdigit())

    def test_empty_records(self):
        """Test handling of empty Records array"""
        empty_data = {"Records": []}
        with patch('builtins.open', mock_open(read_data=json.dumps(empty_data))):
            store = AlertStore()
            self.assertEqual(store.alerts, {})

    def test_missing_fields(self):
        """Test handling of events with missing fields"""
        incomplete_data = {
            "Records": [
                {
                    "eventTime": "2024-10-16T03:54:00Z",
                    "eventName": "AssumeRole",
                    "sourceIPAddress": "1.2.3.4",
                    "userIdentity": {}  # Missing userName
                }
            ]
        }
        with patch('builtins.open', mock_open(read_data=json.dumps(incomplete_data))):
            store = AlertStore()
            alert = list(store.alerts.values())[0]
            self.assertEqual(alert['userName'], 'Unknown')
            self.assertEqual(alert['userAgent'], 'N/A')

if __name__ == '__main__':
    unittest.main()