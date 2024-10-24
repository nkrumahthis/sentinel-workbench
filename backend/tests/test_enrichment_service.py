import unittest
import json
from unittest.mock import mock_open, patch
from enrichment_service import MockAWSEnrichmentService

class TestMockAWSEnrichmentService(unittest.TestCase):
    def setUp(self):
        self.sample_data = {
            "Records": [
                {
                    "eventTime": "2024-10-16T03:54:00Z",
                    "eventSource": "rds.amazonaws.com",
                    "eventName": "StartDBInstance",
                    "sourceIPAddress": "32.118.234.47",
                    "userAgent": "aws-cli/2.0.0 Python/3.8.5 Darwin/18.7.0 botocore/2.0.0",
                    "userIdentity": {
                        "type": "AssumedRole",
                        "userName": "admin-user"
                    },
                    "responseElements": {}
                },
                {
                    "eventTime": "2024-10-16T04:20:00Z",
                    "eventSource": "lambda.amazonaws.com",
                    "eventName": "UpdateFunction",
                    "sourceIPAddress": "142.130.179.217",
                    "userAgent": "boto3/1.17.78",
                    "userIdentity": {
                        "type": "AssumedRole",
                        "userName": "lambda-role"
                    },
                    "responseElements": {}
                },
                {
                    "eventTime": "2024-10-16T07:31:00Z",
                    "eventSource": "s3.amazonaws.com",
                    "eventName": "CreateBucket",
                    "sourceIPAddress": "178.252.78.134",
                    "userAgent": "aws-sdk-java/1.11.969",
                    "userIdentity": {
                        "type": "AssumedRole",
                        "userName": "system-user"
                    },
                    "responseElements": {}
                }
            ]
        }
        
        # Mock the file opening and reading
        with patch('builtins.open', mock_open(read_data=json.dumps(self.sample_data))):
            self.service = MockAWSEnrichmentService()

    def test_load_mock_data(self):
        """Test that mock data is loaded correctly"""
        self.assertEqual(len(self.service.events), 3)
        self.assertEqual(self.service.events[0]['eventSource'], 'rds.amazonaws.com')

    def test_get_users(self):
        """Test retrieving unique users from events"""
        expected_users = {'admin-user', 'lambda-role', 'system-user'}
        self.assertEqual(set(self.service.get_users()), expected_users)

    def test_get_service_interactions(self):
        """Test counting service interactions for a specific user"""
        interactions = self.service.get_service_interactions('admin-user')
        expected = {'rds': 1}
        self.assertEqual(interactions, expected)

    def test_get_interesting_api_calls(self):
        """Test retrieving non-read API calls for a specific user"""
        calls = self.service.get_interesting_api_calls('system-user')
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0]['eventName'], 'CreateBucket')
        self.assertEqual(calls[0]['eventSource'], 's3.amazonaws.com')

    def test_get_recent_role_assumptions(self):
        """Test retrieving recent role assumptions for a user"""
        assumptions = self.service.get_recent_role_assumptions('admin-user')
        self.assertEqual(len(assumptions), 0)  # No AssumeRole events in sample data

    def test_enrich(self):
        """Test the main enrich method"""
        alert_data = {
            "userIdentity": {
                "type": "AssumedRole",
                "userName": "admin-user"
            }
        }
        
        enriched = self.service.enrich("admin-user", alert_data)
        
        self.assertIn('assumedRoleDetails', enriched)
        self.assertIn('recentRoleAssumptions', enriched)
        self.assertIn('serviceInteractions', enriched)
        self.assertIn('interestingApiCalls', enriched)

    def test_get_service_interactions_empty(self):
        """Test service interactions for non-existent user"""
        interactions = self.service.get_service_interactions('non-existent-user')
        self.assertEqual(interactions, {})

    def test_get_interesting_api_calls_empty(self):
        """Test interesting API calls for non-existent user"""
        calls = self.service.get_interesting_api_calls('non-existent-user')
        self.assertEqual(calls, [])

    def test_error_handling_file_not_found(self):
        """Test handling of missing mock data file"""
        with patch('builtins.open', mock_open()) as mock_file:
            mock_file.side_effect = FileNotFoundError()
            service = MockAWSEnrichmentService()
            self.assertEqual(service.events, [])

    def test_interesting_api_calls_filtering(self):
        """Test that Get/List/Describe calls are filtered out"""
        # Add a test event with a "List" prefix
        test_data = self.sample_data.copy()
        test_data["Records"].append({
            "eventTime": "2024-10-16T08:00:00Z",
            "eventSource": "s3.amazonaws.com",
            "eventName": "ListBuckets",
            "sourceIPAddress": "178.252.78.134",
            "userAgent": "aws-sdk-java/1.11.969",
            "userIdentity": {
                "type": "AssumedRole",
                "userName": "system-user"
            },
            "responseElements": {}
        })
        
        with patch('builtins.open', mock_open(read_data=json.dumps(test_data))):
            service = MockAWSEnrichmentService()
            calls = service.get_interesting_api_calls('system-user')
            
            # Should only include CreateBucket, not ListBuckets
            self.assertEqual(len(calls), 1)
            self.assertEqual(calls[0]['eventName'], 'CreateBucket')

if __name__ == '__main__':
    unittest.main()