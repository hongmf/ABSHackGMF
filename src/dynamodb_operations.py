"""
DynamoDB Operations for Auto Loan Metrics

This module handles all DynamoDB operations including table creation,
data insertion, and querying.
"""

import boto3
from botocore.exceptions import ClientError
from decimal import Decimal
from typing import Dict, Any, List
import json
from datetime import datetime


class DynamoDBHandler:
    """Handle all DynamoDB operations for auto loan metrics"""

    def __init__(self, table_name='AutoLoanMetrics', region_name='us-east-1', endpoint_url=None):
        """
        Initialize DynamoDB handler

        Args:
            table_name: Name of the DynamoDB table
            region_name: AWS region
            endpoint_url: Optional endpoint URL (for local DynamoDB)
        """
        self.table_name = table_name

        # Create clients
        if endpoint_url:
            self.dynamodb_client = boto3.client('dynamodb', endpoint_url=endpoint_url, region_name=region_name)
            self.dynamodb_resource = boto3.resource('dynamodb', endpoint_url=endpoint_url, region_name=region_name)
        else:
            self.dynamodb_client = boto3.client('dynamodb', region_name=region_name)
            self.dynamodb_resource = boto3.resource('dynamodb', region_name=region_name)

        self.table = None

    def convert_floats_to_decimal(self, obj: Any) -> Any:
        """
        Recursively convert float values to Decimal for DynamoDB compatibility

        Args:
            obj: Object to convert

        Returns:
            Converted object
        """
        if isinstance(obj, float):
            return Decimal(str(obj))
        elif isinstance(obj, dict):
            return {k: self.convert_floats_to_decimal(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self.convert_floats_to_decimal(item) for item in obj]
        return obj

    def create_table(self) -> bool:
        """
        Create the DynamoDB table if it doesn't exist

        Returns:
            True if table was created or already exists, False otherwise
        """
        try:
            table_schema = {
                'TableName': self.table_name,
                'KeySchema': [
                    {
                        'AttributeName': 'company_name',
                        'KeyType': 'HASH'  # Partition key
                    },
                    {
                        'AttributeName': 'reporting_period',
                        'KeyType': 'RANGE'  # Sort key
                    }
                ],
                'AttributeDefinitions': [
                    {
                        'AttributeName': 'company_name',
                        'AttributeType': 'S'
                    },
                    {
                        'AttributeName': 'reporting_period',
                        'AttributeType': 'S'
                    }
                ],
                'BillingMode': 'PAY_PER_REQUEST',
                'Tags': [
                    {
                        'Key': 'Project',
                        'Value': 'Hackathon-2025-GMF'
                    },
                    {
                        'Key': 'DataType',
                        'Value': 'AutoLoanMetrics'
                    }
                ]
            }

            response = self.dynamodb_client.create_table(**table_schema)
            print(f"Creating table {self.table_name}...")
            print(f"Table status: {response['TableDescription']['TableStatus']}")

            # Wait for table to be created
            waiter = self.dynamodb_client.get_waiter('table_exists')
            waiter.wait(TableName=self.table_name)
            print(f"Table {self.table_name} is now active")

            return True

        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceInUseException':
                print(f"Table {self.table_name} already exists")
                return True
            else:
                print(f"Error creating table: {e}")
                return False

    def get_table(self):
        """Get the table resource"""
        if not self.table:
            self.table = self.dynamodb_resource.Table(self.table_name)
        return self.table

    def insert_metrics(self, metrics: Dict[str, Any]) -> bool:
        """
        Insert metrics data into DynamoDB table

        Args:
            metrics: Dictionary containing metrics data

        Returns:
            True if successful, False otherwise
        """
        try:
            table = self.get_table()

            # Convert floats to Decimal
            metrics_decimal = self.convert_floats_to_decimal(metrics)

            # Insert item
            response = table.put_item(Item=metrics_decimal)

            print(f"Successfully inserted metrics for {metrics['company_name']} - {metrics['reporting_period']}")
            return True

        except ClientError as e:
            print(f"Error inserting data: {e}")
            return False

    def batch_insert_metrics(self, metrics_list: List[Dict[str, Any]]) -> int:
        """
        Batch insert multiple metrics records

        Args:
            metrics_list: List of metrics dictionaries

        Returns:
            Number of successfully inserted items
        """
        table = self.get_table()
        success_count = 0

        with table.batch_writer() as batch:
            for metrics in metrics_list:
                try:
                    metrics_decimal = self.convert_floats_to_decimal(metrics)
                    batch.put_item(Item=metrics_decimal)
                    success_count += 1
                    print(f"Queued: {metrics['company_name']} - {metrics['reporting_period']}")
                except Exception as e:
                    print(f"Error queuing item: {e}")

        print(f"\nSuccessfully inserted {success_count} records")
        return success_count

    def get_metrics_by_company(self, company_name: str) -> List[Dict[str, Any]]:
        """
        Retrieve all metrics for a specific company

        Args:
            company_name: Name of the company

        Returns:
            List of metrics dictionaries
        """
        try:
            table = self.get_table()

            response = table.query(
                KeyConditionExpression='company_name = :company',
                ExpressionAttributeValues={
                    ':company': company_name
                }
            )

            return response.get('Items', [])

        except ClientError as e:
            print(f"Error querying data: {e}")
            return []

    def get_metrics_by_company_and_period(self, company_name: str, reporting_period: str) -> Dict[str, Any]:
        """
        Retrieve metrics for a specific company and reporting period

        Args:
            company_name: Name of the company
            reporting_period: Reporting period (YYYY-MM format)

        Returns:
            Metrics dictionary or empty dict if not found
        """
        try:
            table = self.get_table()

            response = table.get_item(
                Key={
                    'company_name': company_name,
                    'reporting_period': reporting_period
                }
            )

            return response.get('Item', {})

        except ClientError as e:
            print(f"Error retrieving data: {e}")
            return {}

    def scan_all_metrics(self) -> List[Dict[str, Any]]:
        """
        Scan and retrieve all metrics from the table

        Returns:
            List of all metrics
        """
        try:
            table = self.get_table()

            response = table.scan()
            items = response.get('Items', [])

            # Handle pagination
            while 'LastEvaluatedKey' in response:
                response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
                items.extend(response.get('Items', []))

            return items

        except ClientError as e:
            print(f"Error scanning table: {e}")
            return []

    def delete_table(self) -> bool:
        """
        Delete the DynamoDB table

        Returns:
            True if successful, False otherwise
        """
        try:
            response = self.dynamodb_client.delete_table(TableName=self.table_name)
            print(f"Deleting table {self.table_name}...")
            print(f"Table status: {response['TableDescription']['TableStatus']}")
            return True

        except ClientError as e:
            print(f"Error deleting table: {e}")
            return False


if __name__ == "__main__":
    # Example usage
    import json

    # For local development with DynamoDB Local:
    # db_handler = DynamoDBHandler(endpoint_url='http://localhost:8000')

    # For AWS:
    db_handler = DynamoDBHandler(region_name='us-east-1')

    # Create table
    print("Creating table...")
    db_handler.create_table()

    # Example metrics data
    example_metrics = {
        'company_name': 'GM FINANCIAL',
        'reporting_period': '2025-05',
        'total_loans': 10000,
        'total_pool_balance': 250000000.50,
        'average_fico_score': 720.5,
        'delinquency_30_plus_rate': 2.3,
        'delinquency_60_plus_rate': 1.1,
        'delinquency_90_plus_rate': 0.5,
        'loss_severity_percentage': 35.2,
        'prepayment_speed_cpr': 15.6,
        'prepayment_speed_abs': 1.3,
        'loan_term_distribution': {
            '0-36': 10.5,
            '37-48': 25.3,
            '49-60': 35.2,
            '61-72': 20.1,
            '73-84': 8.5,
            '85+': 0.4
        },
        'geographic_concentration': {
            'CA': 15.2,
            'TX': 12.8,
            'FL': 10.3,
            'NY': 8.5,
            'Other': 53.2
        },
        'average_loan_amount': 35000.00,
        'average_remaining_term': 48.5,
        'weighted_avg_interest_rate': 6.25,
        'new_vehicle_percentage': 65.5,
        'used_vehicle_percentage': 34.5,
        'repossession_rate': 0.8,
        'last_updated': datetime.now().isoformat()
    }

    # Insert example data
    print("\nInserting example data...")
    db_handler.insert_metrics(example_metrics)

    # Query data
    print("\nQuerying data...")
    results = db_handler.get_metrics_by_company('GM FINANCIAL')
    print(f"Found {len(results)} records")
    if results:
        print(json.dumps(results[0], indent=2, default=str))
