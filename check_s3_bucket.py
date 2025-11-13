#!/usr/bin/env python3
"""
Script to check S3 bucket contents and test AWS connection
Usage: python check_s3_bucket.py [bucket_name] [region]
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from s3_utils import S3FileManager

# Load environment variables
load_dotenv()


def test_aws_connection():
    """Test basic AWS connection"""
    print("Testing AWS connection...")
    try:
        import boto3
        # Try to create an S3 client
        s3_client = boto3.client('s3')
        # List buckets to test connection
        response = s3_client.list_buckets()
        print("✓ AWS connection successful!")
        print(f"  Found {len(response.get('Buckets', []))} bucket(s) accessible")
        return True
    except Exception as e:
        print(f"✗ AWS connection failed: {e}")
        print("\nTroubleshooting:")
        print("  1. Check AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY in .env")
        print("  2. Verify credentials are valid")
        print("  3. Check AWS region is correct")
        return False


def check_s3_bucket(bucket_name: str, region: str = 'us-east-1', prefix: str = ''):
    """
    Check S3 bucket and list files
    
    Args:
        bucket_name: Name of the S3 bucket
        region: AWS region (default: us-east-1)
        prefix: Optional prefix to filter files
    """
    print("="*80)
    print("S3 BUCKET CHECKER")
    print("="*80)
    print(f"Bucket: s3://{bucket_name}")
    print(f"Region: {region}")
    print(f"Prefix: {prefix or '(root)'}")
    print("="*80)
    print()
    
    try:
        # Initialize S3 manager
        print("Connecting to S3 bucket...")
        s3_manager = S3FileManager(bucket_name, region)
        
        # Get bucket info
        bucket_info = s3_manager.get_bucket_info()
        print(f"✓ Connected to bucket: {bucket_info['bucket_name']}")
        print()
        
        # List all .txt files
        print("Scanning for .txt files...")
        files = s3_manager.list_sec_files(prefix=prefix, suffix='.txt')
        
        if not files:
            print("⚠ No .txt files found in bucket")
            print()
            print("Trying to list all files (any extension)...")
            # Try listing all files
            all_files = s3_manager.list_sec_files(prefix=prefix, suffix='')
            if all_files:
                print(f"Found {len(all_files)} file(s) with other extensions:")
                for file_info in all_files[:10]:  # Show first 10
                    size_mb = file_info['Size'] / (1024 * 1024)
                    print(f"  - {file_info['FileName']} ({file_info['Size']:,} bytes, {size_mb:.2f} MB)")
                if len(all_files) > 10:
                    print(f"  ... and {len(all_files) - 10} more files")
            else:
                print("No files found at all. Check:")
                print("  1. Bucket name is correct")
                print("  2. Prefix is correct (if using)")
                print("  3. AWS credentials have s3:ListBucket permission")
            return
        
        # Display results
        print(f"✓ Found {len(files)} .txt file(s)")
        print()
        print("Files:")
        print("-" * 80)
        
        total_size = 0
        for i, file_info in enumerate(files, 1):
            size_mb = file_info['Size'] / (1024 * 1024)
            total_size += file_info['Size']
            print(f"{i}. {file_info['FileName']}")
            print(f"   Key: {file_info['Key']}")
            print(f"   Size: {file_info['Size']:,} bytes ({size_mb:.2f} MB)")
            print(f"   Modified: {file_info['LastModified']}")
            print()
        
        total_size_mb = total_size / (1024 * 1024)
        print("-" * 80)
        print(f"Total: {len(files)} file(s), {total_size:,} bytes ({total_size_mb:.2f} MB)")
        print()
        
        # Test file access
        if files:
            print("Testing file access (reading first file metadata)...")
            first_file = files[0]
            exists = s3_manager.file_exists(first_file['Key'])
            if exists:
                print(f"✓ Can access file: {first_file['FileName']}")
            else:
                print(f"⚠ Cannot access file: {first_file['FileName']}")
            print()
        
        print("="*80)
        print("✓ S3 bucket check completed successfully")
        print("="*80)
        print()
        print("Next steps:")
        print(f"  To process all files: python src/pipeline.py --s3-bucket {bucket_name}")
        if prefix:
            print(f"  With prefix: python src/pipeline.py --s3-bucket {bucket_name} --s3-prefix {prefix}")
        
    except Exception as e:
        print()
        print("="*80)
        print("ERROR")
        print("="*80)
        print(f"Failed to check S3 bucket: {e}")
        print()
        print("Troubleshooting:")
        print("  1. Check AWS credentials are set:")
        print("     - Environment variables (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)")
        print("     - AWS CLI config (aws configure)")
        print("     - .env file")
        print("  2. Verify bucket name is correct")
        print("  3. Check AWS region is correct")
        print("  4. Ensure IAM user has s3:ListBucket permission")
        print()
        import traceback
        traceback.print_exc()
        sys.exit(1)


def list_available_buckets():
    """List all S3 buckets accessible with current credentials"""
    try:
        import boto3
        s3_client = boto3.client('s3')
        response = s3_client.list_buckets()
        buckets = response.get('Buckets', [])
        
        if buckets:
            print("Available S3 buckets:")
            for bucket in buckets:
                print(f"  - {bucket['Name']} (created: {bucket['CreationDate']})")
            return [b['Name'] for b in buckets]
        else:
            print("No buckets found or no access to list buckets")
            return []
    except Exception as e:
        print(f"Error listing buckets: {e}")
        return []


if __name__ == "__main__":
    print("="*80)
    print("AWS S3 CONNECTION TESTER")
    print("="*80)
    print()
    
    # Test AWS connection first
    if not test_aws_connection():
        sys.exit(1)
    
    print()
    
    # Get bucket name from command line or .env
    if len(sys.argv) > 1:
        bucket_name = sys.argv[1]
    else:
        bucket_name = os.getenv('S3_BUCKET_NAME', '')
        if not bucket_name or bucket_name == 'your-bucket-name-here':
            print("No bucket name provided. Listing available buckets...")
            print()
            available_buckets = list_available_buckets()
            print()
            if available_buckets:
                print("Please provide bucket name:")
                print("  python check_s3_bucket.py <bucket_name> [region] [prefix]")
                print()
                print("Or set S3_BUCKET_NAME in your .env file")
            sys.exit(0)
    
    region = sys.argv[2] if len(sys.argv) > 2 else os.getenv('AWS_REGION', 'us-east-1')
    prefix = sys.argv[3] if len(sys.argv) > 3 else ''
    
    check_s3_bucket(bucket_name, region, prefix)

