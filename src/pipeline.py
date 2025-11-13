"""
Complete Pipeline for Auto Loan Data Processing

This script orchestrates the entire data extraction and DynamoDB insertion pipeline:
1. Extract data from SEC ABS-EE filing
2. Calculate metrics
3. Create DynamoDB table
4. Insert data into DynamoDB
"""

import argparse
import json
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

from data_extractor import AutoLoanDataExtractor
from dynamodb_operations import DynamoDBHandler
from s3_utils import S3FileManager

# Load environment variables from .env file
load_dotenv()


def run_pipeline(
    file_path: str = None,
    table_name: str = 'AutoLoanMetrics',
    region: str = 'us-east-1',
    endpoint_url: str = None,
    create_table: bool = True,
    output_json: bool = False,
    s3_bucket: str = None,
    s3_key: str = None
):
    """
    Run the complete data extraction and insertion pipeline

    Args:
        file_path: Path to SEC ABS-EE filing (local file)
        table_name: Name of DynamoDB table
        region: AWS region
        endpoint_url: Optional DynamoDB endpoint (for local development)
        create_table: Whether to create the table if it doesn't exist
        output_json: Whether to output extracted metrics to JSON file
        s3_bucket: S3 bucket name (for S3 files)
        s3_key: S3 object key (for S3 files)
    """

    print("="*80)
    print("AUTO LOAN METRICS EXTRACTION & DYNAMODB INSERTION PIPELINE")
    print("="*80)
    print()

    # Step 1: Extract data
    source = f"s3://{s3_bucket}/{s3_key}" if s3_bucket else file_path
    print(f"Step 1: Extracting data from {source}")
    print("-" * 80)

    try:
        extractor = AutoLoanDataExtractor(
            file_path=file_path or s3_key,
            s3_bucket=s3_bucket,
            s3_key=s3_key
        )
        metrics = extractor.extract_all_metrics()

        print(f"\n[OK] Successfully extracted metrics for {metrics['company_name']}")
        print(f"  - Reporting Period: {metrics['reporting_period']}")
        print(f"  - Total Loans: {metrics['total_loans']:,}")
        print(f"  - Total Pool Balance: ${metrics['total_pool_balance']:,.2f}")
        print(f"  - Average FICO Score: {metrics['average_fico_score']:.2f}")
        print()

    except Exception as e:
        print(f"[ERROR] Error extracting data: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Step 2: Save to JSON (optional)
    if output_json:
        print("Step 2: Saving metrics to JSON file")
        print("-" * 80)

        try:
            output_file = Path(file_path).parent / f"metrics_{metrics['company_name'].replace(' ', '_')}_{metrics['reporting_period']}.json"
            with open(output_file, 'w') as f:
                json.dump(metrics, f, indent=2)

            print(f"[OK] Metrics saved to {output_file}")
            print()

        except Exception as e:
            print(f"[ERROR] Error saving JSON: {e}")
            print()

    # Step 3: Initialize DynamoDB handler
    print("Step 3: Initializing DynamoDB connection")
    print("-" * 80)

    try:
        db_handler = DynamoDBHandler(
            table_name=table_name,
            region_name=region,
            endpoint_url=endpoint_url
        )
        print(f"[OK] Connected to DynamoDB (Region: {region})")
        if endpoint_url:
            print(f"  - Using endpoint: {endpoint_url}")
        print()

    except Exception as e:
        print(f"[ERROR] Error connecting to DynamoDB: {e}")
        return False

    # Step 4: Create table
    if create_table:
        print(f"Step 4: Creating DynamoDB table '{table_name}'")
        print("-" * 80)

        try:
            success = db_handler.create_table()
            if success:
                print(f"[OK] Table '{table_name}' is ready")
            else:
                print(f"[ERROR] Failed to create table")
                return False
            print()

        except Exception as e:
            print(f"[ERROR] Error creating table: {e}")
            return False

    # Step 5: Insert data
    step_num = 5 if create_table else 4
    print(f"Step {step_num}: Inserting data into DynamoDB")
    print("-" * 80)

    try:
        success = db_handler.insert_metrics(metrics)
        if success:
            print(f"[OK] Data successfully inserted into DynamoDB")
            print(f"  - Company: {metrics['company_name']}")
            print(f"  - Period: {metrics['reporting_period']}")
        else:
            print(f"[ERROR] Failed to insert data")
            return False
        print()

    except Exception as e:
        print(f"[ERROR] Error inserting data: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Step 6: Verify insertion
    step_num += 1
    print(f"Step {step_num}: Verifying data insertion")
    print("-" * 80)

    try:
        retrieved_data = db_handler.get_metrics_by_company_and_period(
            metrics['company_name'],
            metrics['reporting_period']
        )

        if retrieved_data:
            print(f"[OK] Data verified successfully")
            print(f"  - Retrieved record for {retrieved_data['company_name']} - {retrieved_data['reporting_period']}")
        else:
            print(f"[ERROR] Could not retrieve inserted data")
            return False
        print()

    except Exception as e:
        print(f"[ERROR] Error verifying data: {e}")
        return False

    # Summary
    print("="*80)
    print("PIPELINE COMPLETED SUCCESSFULLY")
    print("="*80)
    print()
    print("Key Metrics Summary:")
    print(f"  Company Name:              {metrics['company_name']}")
    print(f"  Reporting Period:          {metrics['reporting_period']}")
    print(f"  Total Loans:               {metrics['total_loans']:,}")
    print(f"  Total Pool Balance:        ${metrics['total_pool_balance']:,.2f}")
    print(f"  Average FICO Score:        {metrics['average_fico_score']:.2f}")
    print(f"  Delinquency 30+ Rate:      {metrics['delinquency_30_plus_rate']:.2f}%")
    print(f"  Delinquency 60+ Rate:      {metrics['delinquency_60_plus_rate']:.2f}%")
    print(f"  Delinquency 90+ Rate:      {metrics['delinquency_90_plus_rate']:.2f}%")
    print(f"  Loss Severity:             {metrics['loss_severity_percentage']:.2f}%")
    print(f"  Prepayment Speed (CPR):    {metrics['prepayment_speed_cpr']:.2f}%")
    print(f"  Prepayment Speed (ABS):    {metrics['prepayment_speed_abs']:.2f}%")
    print(f"  Avg Loan Amount:           ${metrics['average_loan_amount']:,.2f}")
    print(f"  Avg Remaining Term:        {metrics['average_remaining_term']:.1f} months")
    print(f"  Weighted Avg Interest Rate: {metrics['weighted_avg_interest_rate']:.2f}%")
    print(f"  New Vehicle %:             {metrics['new_vehicle_percentage']:.2f}%")
    print(f"  Used Vehicle %:            {metrics['used_vehicle_percentage']:.2f}%")
    print(f"  Repossession Rate:         {metrics['repossession_rate']:.2f}%")
    print()

    print("Top 5 Geographic Concentrations:")
    for i, (state, pct) in enumerate(list(metrics['geographic_concentration'].items())[:5], 1):
        print(f"  {i}. {state}: {pct:.2f}%")
    print()

    print("Loan Term Distribution:")
    for term, pct in metrics['loan_term_distribution'].items():
        print(f"  {term} months: {pct:.2f}%")
    print()

    return True


def process_s3_bucket(
    s3_bucket: str,
    table_name: str = 'AutoLoanMetrics',
    region: str = 'us-east-1',
    endpoint_url: str = None,
    create_table: bool = True,
    output_json: bool = False,
    prefix: str = '',
    file_suffix: str = '.txt'
):
    """
    Process all SEC filing files in an S3 bucket

    Args:
        s3_bucket: S3 bucket name
        table_name: Name of DynamoDB table
        region: AWS region
        endpoint_url: Optional DynamoDB endpoint (for local development)
        create_table: Whether to create the table if it doesn't exist
        output_json: Whether to output extracted metrics to JSON file
        prefix: S3 key prefix to filter files
        file_suffix: File extension filter (default: '.txt')

    Returns:
        Dictionary with success/failure counts
    """
    print("="*80)
    print("BATCH PROCESSING: S3 BUCKET AUTO LOAN METRICS PIPELINE")
    print("="*80)
    print(f"Bucket: s3://{s3_bucket}")
    print(f"Prefix: {prefix or '(root)'}")
    print(f"File Filter: *{file_suffix}")
    print("="*80)
    print()

    # Initialize S3 manager
    s3_manager = S3FileManager(s3_bucket, region)

    # List all files
    print("Scanning S3 bucket for files...")
    files = s3_manager.list_sec_files(prefix=prefix, suffix=file_suffix)
    print(f"Found {len(files)} file(s) to process")
    print()

    if len(files) == 0:
        print("No files found in bucket. Exiting.")
        return {'total': 0, 'success': 0, 'failed': 0}

    # Process each file
    results = {'total': len(files), 'success': 0, 'failed': 0, 'errors': []}

    for idx, file_info in enumerate(files, 1):
        s3_key = file_info['Key']
        file_name = file_info['FileName']

        print("="*80)
        print(f"Processing file {idx}/{len(files)}: {file_name}")
        print("="*80)
        print()

        try:
            success = run_pipeline(
                file_path=None,
                table_name=table_name,
                region=region,
                endpoint_url=endpoint_url,
                create_table=(create_table and idx == 1),  # Only create table on first file
                output_json=output_json,
                s3_bucket=s3_bucket,
                s3_key=s3_key
            )

            if success:
                results['success'] += 1
                print(f"[OK] Successfully processed {file_name}")
            else:
                results['failed'] += 1
                results['errors'].append({'file': file_name, 'error': 'Pipeline returned False'})
                print(f"[ERROR] Failed to process {file_name}")

        except Exception as e:
            results['failed'] += 1
            results['errors'].append({'file': file_name, 'error': str(e)})
            print(f"[ERROR] Exception processing {file_name}: {e}")

        print()

    # Print summary
    print("="*80)
    print("BATCH PROCESSING SUMMARY")
    print("="*80)
    print(f"Total Files:      {results['total']}")
    print(f"Successful:       {results['success']}")
    print(f"Failed:           {results['failed']}")
    print("="*80)

    if results['errors']:
        print("\nErrors:")
        for err in results['errors']:
            print(f"  - {err['file']}: {err['error']}")

    return results


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Extract auto loan metrics from SEC filing and insert into DynamoDB'
    )

    parser.add_argument(
        'file_path',
        nargs='?',
        help='Path to SEC ABS-EE filing (txt file) - not required if using --s3-bucket'
    )

    parser.add_argument(
        '--s3-bucket',
        help='S3 bucket name to process all files from'
    )

    parser.add_argument(
        '--s3-prefix',
        default='',
        help='S3 key prefix to filter files (e.g., "filings/")'
    )

    parser.add_argument(
        '--table-name',
        default='AutoLoanMetrics',
        help='DynamoDB table name (default: AutoLoanMetrics)'
    )

    parser.add_argument(
        '--region',
        default='us-east-1',
        help='AWS region (default: us-east-1)'
    )

    parser.add_argument(
        '--endpoint-url',
        help='DynamoDB endpoint URL (for local development, e.g., http://localhost:8000)'
    )

    parser.add_argument(
        '--skip-table-creation',
        action='store_true',
        help='Skip table creation step'
    )

    parser.add_argument(
        '--output-json',
        action='store_true',
        help='Save extracted metrics to JSON file'
    )

    args = parser.parse_args()

    # Check if S3 bucket mode or single file mode
    if args.s3_bucket:
        # Process all files from S3 bucket
        s3_bucket = args.s3_bucket

        # Allow using environment variable if not provided
        if not s3_bucket:
            s3_bucket = os.getenv('S3_BUCKET_NAME')

        if not s3_bucket:
            print("[ERROR] S3 bucket name must be provided via --s3-bucket or S3_BUCKET_NAME environment variable")
            sys.exit(1)

        results = process_s3_bucket(
            s3_bucket=s3_bucket,
            table_name=args.table_name,
            region=args.region,
            endpoint_url=args.endpoint_url,
            create_table=not args.skip_table_creation,
            output_json=args.output_json,
            prefix=args.s3_prefix
        )

        sys.exit(0 if results['failed'] == 0 else 1)

    else:
        # Single file mode
        if not args.file_path:
            print("[ERROR] file_path is required when not using --s3-bucket")
            parser.print_help()
            sys.exit(1)

        success = run_pipeline(
            file_path=args.file_path,
            table_name=args.table_name,
            region=args.region,
            endpoint_url=args.endpoint_url,
            create_table=not args.skip_table_creation,
            output_json=args.output_json
        )

        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
