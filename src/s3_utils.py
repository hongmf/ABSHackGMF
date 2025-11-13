"""
S3 Utility Functions for Auto Loan Data Processing

This module provides utilities for listing and accessing SEC filing files in S3.
"""

import boto3
from typing import List, Dict, Any, Optional
import os


class S3FileManager:
    """Manage S3 operations for SEC filing files"""

    def __init__(self, bucket_name: str, region_name: str = 'us-east-1'):
        """
        Initialize S3 manager

        Args:
            bucket_name: Name of the S3 bucket
            region_name: AWS region (default: us-east-1)
        """
        self.bucket_name = bucket_name
        self.region_name = region_name
        self.s3_client = boto3.client('s3', region_name=region_name)

    def list_sec_files(self, prefix: str = '', suffix: str = '.txt') -> List[Dict[str, Any]]:
        """
        List all SEC filing files in the S3 bucket

        Args:
            prefix: S3 key prefix to filter files (e.g., 'filings/')
            suffix: File extension filter (default: '.txt')

        Returns:
            List of dictionaries containing file metadata (Key, Size, LastModified)
        """
        files = []
        paginator = self.s3_client.get_paginator('list_objects_v2')

        for page in paginator.paginate(Bucket=self.bucket_name, Prefix=prefix):
            if 'Contents' in page:
                for obj in page['Contents']:
                    if obj['Key'].endswith(suffix):
                        files.append({
                            'Key': obj['Key'],
                            'Size': obj['Size'],
                            'LastModified': obj['LastModified'],
                            'FileName': os.path.basename(obj['Key'])
                        })

        return files

    def download_file(self, s3_key: str, local_path: str) -> bool:
        """
        Download a file from S3 to local filesystem

        Args:
            s3_key: S3 object key
            local_path: Local file path to save to

        Returns:
            True if successful, False otherwise
        """
        try:
            self.s3_client.download_file(self.bucket_name, s3_key, local_path)
            return True
        except Exception as e:
            print(f"Error downloading {s3_key}: {e}")
            return False

    def get_file_content(self, s3_key: str) -> Optional[str]:
        """
        Get file content as string from S3

        Args:
            s3_key: S3 object key

        Returns:
            File content as string, or None if error
        """
        try:
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=s3_key)
            content = response['Body'].read().decode('utf-8')
            return content
        except Exception as e:
            print(f"Error reading {s3_key}: {e}")
            return None

    def file_exists(self, s3_key: str) -> bool:
        """
        Check if a file exists in S3

        Args:
            s3_key: S3 object key

        Returns:
            True if file exists, False otherwise
        """
        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=s3_key)
            return True
        except:
            return False

    def get_bucket_info(self) -> Dict[str, Any]:
        """
        Get bucket information

        Returns:
            Dictionary with bucket name and region
        """
        return {
            'bucket_name': self.bucket_name,
            'region': self.region_name
        }
