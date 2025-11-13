# S3 Batch Processing Guide

This guide explains how to use the updated pipeline to process SEC filing files from S3.

## Overview

The pipeline now supports two modes:
1. **Single File Mode**: Process a single local file or S3 file
2. **Batch Mode**: Process all files in an S3 bucket automatically

## Configuration

### 1. Update .env file

Add your S3 bucket name to the `.env` file:

```bash
# S3 Configuration (for batch processing)
S3_BUCKET_NAME=your-sec-filings-bucket
S3_PREFIX=
```

- `S3_BUCKET_NAME`: The name of your S3 bucket containing SEC filing files
- `S3_PREFIX`: Optional prefix to filter files (e.g., "filings/" to only process files in the filings folder)

### 2. Ensure AWS Credentials are Set

Make sure your AWS credentials in `.env` have permissions for:
- S3: `s3:GetObject`, `s3:ListBucket`
- DynamoDB: `dynamodb:CreateTable`, `dynamodb:PutItem`, `dynamodb:GetItem`

## Usage

### Batch Mode: Process All Files in S3 Bucket

Process all `.txt` files in your S3 bucket:

```bash
python src/pipeline.py --s3-bucket your-sec-filings-bucket
```

Process files with a specific prefix (folder):

```bash
python src/pipeline.py --s3-bucket your-sec-filings-bucket --s3-prefix filings/2025/
```

Using environment variable (from .env file):

```bash
# Set S3_BUCKET_NAME in .env, then run:
python src/pipeline.py --s3-bucket $(echo $S3_BUCKET_NAME)
```

### Single File Mode: Process One S3 File

You can still process a single local file as before:

```bash
python src/pipeline.py 0001347185-25-000024.txt
```

### Additional Options

All existing options work with S3 batch mode:

```bash
# Skip table creation (if table already exists)
python src/pipeline.py --s3-bucket my-bucket --skip-table-creation

# Save metrics to JSON files
python src/pipeline.py --s3-bucket my-bucket --output-json

# Use custom table name
python src/pipeline.py --s3-bucket my-bucket --table-name MyCustomTable

# Use custom region
python src/pipeline.py --s3-bucket my-bucket --region us-west-2
```

## Example S3 Bucket Structure

```
your-sec-filings-bucket/
├── 0001347185-25-000024.txt          # GM Financial
├── 0001234567-25-000025.txt          # Ford
├── 0009876543-25-000026.txt          # AmeriCredit
└── filings/
    ├── 2025/
    │   ├── 0001347185-25-000024.txt
    │   └── 0001234567-25-000025.txt
    └── 2024/
        └── 0001347185-24-000123.txt
```

## Batch Processing Output

When processing multiple files, you'll see:

```
================================================================================
BATCH PROCESSING: S3 BUCKET AUTO LOAN METRICS PIPELINE
================================================================================
Bucket: s3://your-sec-filings-bucket
Prefix: (root)
File Filter: *.txt
================================================================================

Scanning S3 bucket for files...
Found 3 file(s) to process

================================================================================
Processing file 1/3: 0001347185-25-000024.txt
================================================================================
...
[OK] Successfully processed 0001347185-25-000024.txt

================================================================================
Processing file 2/3: 0001234567-25-000025.txt
================================================================================
...
[OK] Successfully processed 0001234567-25-000025.txt

================================================================================
BATCH PROCESSING SUMMARY
================================================================================
Total Files:      3
Successful:       3
Failed:           0
================================================================================
```

## Features

### Automatic File Discovery
- Scans entire S3 bucket for `.txt` files
- Supports prefix filtering to process specific folders
- Lists all files before processing

### Error Handling
- Continues processing even if one file fails
- Provides detailed error messages
- Summary report at the end with success/failure counts

### Smart Table Creation
- Only creates DynamoDB table on the first file
- Subsequent files skip table creation to improve performance

### Metrics Export
- Can save JSON files for each processed filing
- Files are named: `metrics_{COMPANY}_{PERIOD}.json`

## Troubleshooting

### "Access Denied" Error

Ensure your IAM user has S3 read permissions:

```json
{
  "Effect": "Allow",
  "Action": [
    "s3:GetObject",
    "s3:ListBucket"
  ],
  "Resource": [
    "arn:aws:s3:::your-sec-filings-bucket",
    "arn:aws:s3:::your-sec-filings-bucket/*"
  ]
}
```

### No Files Found

- Check that files have `.txt` extension
- Verify the S3 prefix is correct
- Ensure bucket name is spelled correctly

### Files Processed Out of Order

Files are processed in the order returned by S3's ListObjects API. To process in a specific order, use separate prefixes or process files individually.

## Code Structure

### New Files
- `src/s3_utils.py`: S3 utility functions for listing and reading files

### Modified Files
- `src/data_extractor.py`: Now supports reading from S3
- `src/pipeline.py`: Added batch processing function and S3 arguments

### Key Functions
- `S3FileManager.list_sec_files()`: Lists all files in bucket
- `AutoLoanDataExtractor.__init__()`: Accepts S3 bucket and key
- `process_s3_bucket()`: Main batch processing loop
