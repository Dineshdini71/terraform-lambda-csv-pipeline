import unittest
from unittest.mock import patch, MagicMock
import lambda_function
import os

class TestLambdaCSVProcessor(unittest.TestCase):

    def setUp(self):
        os.environ['DEST_BUCKET'] = 'destination-bucket-csv-output'
        os.environ['SNS_TOPIC'] = 'arn:aws:sns:us-east-1:039612856702:lambda-failure-alerts'

    @patch('lambda_function.s3')
    @patch('lambda_function.sns')
    def test_lambda_handler_success(self, mock_sns, mock_s3):
        # Mock event
        event = {
            'Records': [{
                's3': {
                    'bucket': {'name': 'source-bucket-csv-input'},
                    'object': {'key': 'input.csv'}
                }
            }]
        }

        # CSV input
        input_csv = "Name,Age\nJohn,25\nJane,30"
        mock_body = MagicMock()
        mock_body.read.return_value = input_csv.encode('utf-8')
        mock_s3.get_object.return_value = {'Body': mock_body}

        # Run lambda
        lambda_function.lambda_handler(event, None)

        # Check S3 get and put were called
        mock_s3.get_object.assert_called_once_with(Bucket='source-bucket-csv-input', Key='input.csv')
        mock_s3.put_object.assert_called_once()

        # Confirm no SNS triggered
        mock_sns.publish.assert_not_called()

    @patch('lambda_function.s3')
    @patch('lambda_function.sns')
    def test_lambda_handler_failure_triggers_sns(self, mock_sns, mock_s3):
        # Simulate error
        mock_s3.get_object.side_effect = Exception("S3 error")

        event = {
            'Records': [{
                's3': {
                    'bucket': {'name': 'source-bucket-csv-input'},
                    'object': {'key': 'input.csv'}
                }
            }]
        }

        with self.assertRaises(Exception):
            lambda_function.lambda_handler(event, None)

        mock_sns.publish.assert_called_once()