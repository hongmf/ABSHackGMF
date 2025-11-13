"""
DynamoDB Table Schema for Auto Loan Metrics

This module defines the table structure for storing auto loan metrics
from SEC ABS-EE filings for companies like GM Financial, Ford, AmeriCredit, etc.
"""

import boto3
from botocore.exceptions import ClientError


def create_auto_loan_metrics_table(dynamodb_client, table_name='AutoLoanMetrics'):
    """
    Create DynamoDB table for auto loan metrics

    Table Design:
    - Partition Key: company_name (String)
    - Sort Key: reporting_period (String) - Format: YYYY-MM

    This design allows efficient queries by company and time range
    """

    table_schema = {
        'TableName': table_name,
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
                'AttributeType': 'S'  # String
            },
            {
                'AttributeName': 'reporting_period',
                'AttributeType': 'S'  # String (YYYY-MM format)
            }
        ],
        'BillingMode': 'PAY_PER_REQUEST',  # On-demand billing
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

    try:
        response = dynamodb_client.create_table(**table_schema)
        print(f"Creating table {table_name}...")
        print(f"Table status: {response['TableDescription']['TableStatus']}")
        return response
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            print(f"Table {table_name} already exists")
        else:
            raise e


def get_item_schema():
    """
    Returns the schema for items stored in the table

    Item Attributes:
    - company_name (String, PK): Company identifier (e.g., "GM FINANCIAL", "FORD", "AMERICREDIT")
    - reporting_period (String, SK): Reporting period in YYYY-MM format
    - total_loans (Number): Total number of loans in the pool
    - total_pool_balance (Number): Total outstanding balance
    - average_fico_score (Number): Weighted average FICO score
    - delinquency_30_plus_rate (Number): Percentage of loans 30+ days delinquent
    - delinquency_60_plus_rate (Number): Percentage of loans 60+ days delinquent
    - delinquency_90_plus_rate (Number): Percentage of loans 90+ days delinquent
    - loss_severity_percentage (Number): Average loss severity on charged-off loans
    - prepayment_speed_cpr (Number): Constant Prepayment Rate (CPR)
    - prepayment_speed_abs (Number): Absolute Prepayment Speed (ABS)
    - loan_term_distribution (Map): Distribution of loan terms
    - geographic_concentration (Map): Distribution by state
    - average_loan_amount (Number): Average original loan amount
    - average_remaining_term (Number): Average remaining term to maturity
    - weighted_avg_interest_rate (Number): Weighted average interest rate
    - new_vehicle_percentage (Number): Percentage of new vehicles
    - used_vehicle_percentage (Number): Percentage of used vehicles
    - repossession_rate (Number): Percentage of repossessed loans
    - last_updated (String): ISO timestamp of last update
    """

    return {
        "company_name": "String (PK)",
        "reporting_period": "String (SK) - YYYY-MM",
        "total_loans": "Number",
        "total_pool_balance": "Number",
        "average_fico_score": "Number",
        "delinquency_30_plus_rate": "Number",
        "delinquency_60_plus_rate": "Number",
        "delinquency_90_plus_rate": "Number",
        "loss_severity_percentage": "Number",
        "prepayment_speed_cpr": "Number",
        "prepayment_speed_abs": "Number",
        "loan_term_distribution": {
            "0-36": "Number",
            "37-48": "Number",
            "49-60": "Number",
            "61-72": "Number",
            "73-84": "Number",
            "85+": "Number"
        },
        "geographic_concentration": {
            "state_code": "Number (percentage)"
        },
        "average_loan_amount": "Number",
        "average_remaining_term": "Number",
        "weighted_avg_interest_rate": "Number",
        "new_vehicle_percentage": "Number",
        "used_vehicle_percentage": "Number",
        "repossession_rate": "Number",
        "last_updated": "String (ISO timestamp)"
    }


if __name__ == "__main__":
    # Example usage
    # Note: Configure AWS credentials before running

    # For local development with DynamoDB Local:
    # dynamodb = boto3.client('dynamodb', endpoint_url='http://localhost:8000')

    # For AWS:
    dynamodb = boto3.client('dynamodb', region_name='us-east-1')

    # Create the table
    create_auto_loan_metrics_table(dynamodb)

    print("\nTable schema created successfully!")
    print("\nItem structure:")
    import json
    print(json.dumps(get_item_schema(), indent=2))
