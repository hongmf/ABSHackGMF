"""
Data Extractor for SEC ABS-EE Auto Loan Files

This module extracts key metrics from SEC ABS-EE filings in XML format
and calculates portfolio-level statistics for companies like GM Financial,
Ford, AmeriCredit, etc.
"""

import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Dict, List, Any, Optional
from collections import defaultdict
from decimal import Decimal
import re
import boto3
from io import StringIO


class AutoLoanDataExtractor:
    """Extract and aggregate auto loan metrics from SEC ABS-EE XML files"""

    def __init__(self, file_path: str, s3_bucket: Optional[str] = None, s3_key: Optional[str] = None):
        """
        Initialize the extractor with the file path or S3 location

        Args:
            file_path: Path to the SEC ABS-EE filing (txt file containing XML) - used if s3_bucket is None
            s3_bucket: S3 bucket name (optional, for S3 files)
            s3_key: S3 object key (optional, for S3 files)
        """
        self.file_path = file_path
        self.s3_bucket = s3_bucket
        self.s3_key = s3_key
        self.namespace = {'ns': 'http://www.sec.gov/edgar/document/absee/autoloan/assetdata'}
        self.s3_client = None

        if s3_bucket:
            self.s3_client = boto3.client('s3')

    @staticmethod
    def safe_float(value, default=0.0):
        """Safely convert a value to float, handling None and 'None' strings"""
        if value is None or value == 'None' or value == '':
            return default
        try:
            return float(value)
        except (ValueError, TypeError):
            return default

    @staticmethod
    def safe_int(value, default=0):
        """Safely convert a value to int, handling None and 'None' strings"""
        if value is None or value == 'None' or value == '':
            return default
        try:
            return int(value)
        except (ValueError, TypeError):
            return default

    def extract_xml_content(self) -> str:
        """
        Extract XML content from the SEC filing (from local file or S3)

        Returns:
            XML string content
        """
        if self.s3_bucket and self.s3_key:
            # Read from S3
            response = self.s3_client.get_object(Bucket=self.s3_bucket, Key=self.s3_key)
            content = response['Body'].read().decode('utf-8')
        else:
            # Read from local file
            with open(self.file_path, 'r', encoding='utf-8') as f:
                content = f.read()

        # Find XML section between <XML> tags
        xml_start = content.find('<XML>')
        xml_end = content.find('</XML>')

        if xml_start == -1 or xml_end == -1:
            raise ValueError("XML content not found in file")

        xml_content = content[xml_start + 5:xml_end].strip()
        return xml_content

    def parse_assets(self) -> List[Dict[str, Any]]:
        """
        Parse all asset records from the XML

        Returns:
            List of dictionaries containing asset data
        """
        xml_content = self.extract_xml_content()
        root = ET.fromstring(xml_content)

        assets = []
        for asset in root.findall('.//ns:assets', self.namespace):
            asset_data = {}
            for child in asset:
                tag = child.tag.replace('{http://www.sec.gov/edgar/document/absee/autoloan/assetdata}', '')
                asset_data[tag] = child.text
            assets.append(asset_data)

        return assets

    def calculate_metrics(self, assets: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate portfolio-level metrics from individual assets

        Args:
            assets: List of asset dictionaries

        Returns:
            Dictionary containing aggregated metrics
        """
        if not assets:
            return {}

        # Get company name and reporting period from first asset
        company_name = assets[0].get('originatorName', 'UNKNOWN')
        reporting_period_end = assets[0].get('reportingPeriodEndingDate', '')

        # Convert date format MM-DD-YYYY to YYYY-MM
        if reporting_period_end:
            parts = reporting_period_end.split('-')
            if len(parts) == 3:
                reporting_period = f"{parts[2]}-{parts[0]}"
            else:
                reporting_period = reporting_period_end
        else:
            reporting_period = datetime.now().strftime('%Y-%m')

        # Initialize accumulators
        total_loans = len(assets)
        total_balance = 0.0
        total_fico_weighted = 0.0
        delinquency_counts = {30: 0, 60: 0, 90: 0}
        loan_term_distribution = defaultdict(int)
        geographic_concentration = defaultdict(int)
        total_original_amount = 0.0
        total_remaining_term = 0.0
        total_interest_rate_weighted = 0.0
        new_vehicle_count = 0
        used_vehicle_count = 0
        repossessed_count = 0
        charged_off_balance = 0.0
        total_charged_off_principal = 0.0
        total_recovered = 0.0
        prepayment_count = 0

        for asset in assets:
            # Balance
            balance = self.safe_float(asset.get('reportingPeriodActualEndBalanceAmount', 0))
            total_balance += balance

            # FICO Score (weighted by balance)
            fico_score = self.safe_float(asset.get('obligorCreditScore', 0))
            if fico_score > 0:
                total_fico_weighted += fico_score * balance

            # Delinquency status
            delinquency_status = self.safe_int(asset.get('currentDelinquencyStatus', 0))
            if delinquency_status >= 90:
                delinquency_counts[90] += 1
                delinquency_counts[60] += 1
                delinquency_counts[30] += 1
            elif delinquency_status >= 60:
                delinquency_counts[60] += 1
                delinquency_counts[30] += 1
            elif delinquency_status >= 30:
                delinquency_counts[30] += 1

            # Loan term distribution
            original_term = self.safe_int(asset.get('originalLoanTerm', 0))
            if original_term <= 36:
                loan_term_distribution['0-36'] += 1
            elif original_term <= 48:
                loan_term_distribution['37-48'] += 1
            elif original_term <= 60:
                loan_term_distribution['49-60'] += 1
            elif original_term <= 72:
                loan_term_distribution['61-72'] += 1
            elif original_term <= 84:
                loan_term_distribution['73-84'] += 1
            else:
                loan_term_distribution['85+'] += 1

            # Geographic concentration
            state = asset.get('obligorGeographicLocation', 'UNKNOWN')
            geographic_concentration[state] += 1

            # Average loan amount
            original_amount = self.safe_float(asset.get('originalLoanAmount', 0))
            total_original_amount += original_amount

            # Average remaining term
            remaining_term = self.safe_int(asset.get('remainingTermToMaturityNumber', 0))
            total_remaining_term += remaining_term

            # Interest rate (weighted by balance)
            interest_rate = self.safe_float(asset.get('reportingPeriodInterestRatePercentage', 0))
            total_interest_rate_weighted += interest_rate * balance

            # Vehicle type (new vs used)
            vehicle_new_used = asset.get('vehicleNewUsedCode', '1')
            if vehicle_new_used == '1':
                new_vehicle_count += 1
            else:
                used_vehicle_count += 1

            # Repossession
            repossessed = asset.get('repossessedIndicator', 'false')
            if repossessed.lower() == 'true':
                repossessed_count += 1

            # Loss severity
            charged_off_principal = self.safe_float(asset.get('chargedoffPrincipalAmount', 0))
            recovered_amount = self.safe_float(asset.get('recoveredAmount', 0))
            if charged_off_principal > 0:
                total_charged_off_principal += charged_off_principal
                total_recovered += recovered_amount

            # Prepayment (loan paid off early)
            if balance == 0 and delinquency_status == 0 and remaining_term > 0:
                prepayment_count += 1

        # Calculate rates and percentages
        average_fico = total_fico_weighted / total_balance if total_balance > 0 else 0
        delinquency_30_rate = (delinquency_counts[30] / total_loans * 100) if total_loans > 0 else 0
        delinquency_60_rate = (delinquency_counts[60] / total_loans * 100) if total_loans > 0 else 0
        delinquency_90_rate = (delinquency_counts[90] / total_loans * 100) if total_loans > 0 else 0

        # Loss severity percentage
        loss_severity = 0
        if total_charged_off_principal > 0:
            loss_severity = ((total_charged_off_principal - total_recovered) / total_charged_off_principal * 100)

        # Prepayment speed (CPR - annualized)
        # Simplified calculation: monthly prepayment rate * 12
        monthly_prepayment_rate = (prepayment_count / total_loans) if total_loans > 0 else 0
        cpr = monthly_prepayment_rate * 12 * 100  # Convert to percentage

        # ABS (Absolute Prepayment Speed) - monthly prepayment rate as percentage
        abs_prepayment = monthly_prepayment_rate * 100

        # Loan term distribution as percentages
        term_dist_pct = {k: (v / total_loans * 100) if total_loans > 0 else 0
                         for k, v in loan_term_distribution.items()}

        # Geographic concentration as percentages
        geo_concentration_pct = {k: (v / total_loans * 100) if total_loans > 0 else 0
                                 for k, v in geographic_concentration.items()}

        # Average metrics
        average_loan_amount = total_original_amount / total_loans if total_loans > 0 else 0
        average_remaining_term = total_remaining_term / total_loans if total_loans > 0 else 0
        weighted_avg_interest_rate = (total_interest_rate_weighted / total_balance * 100) if total_balance > 0 else 0

        new_vehicle_pct = (new_vehicle_count / total_loans * 100) if total_loans > 0 else 0
        used_vehicle_pct = (used_vehicle_count / total_loans * 100) if total_loans > 0 else 0
        repossession_rate = (repossessed_count / total_loans * 100) if total_loans > 0 else 0

        # Compile metrics
        metrics = {
            'company_name': company_name,
            'reporting_period': reporting_period,
            'total_loans': total_loans,
            'total_pool_balance': round(total_balance, 2),
            'average_fico_score': round(average_fico, 2),
            'delinquency_30_plus_rate': round(delinquency_30_rate, 2),
            'delinquency_60_plus_rate': round(delinquency_60_rate, 2),
            'delinquency_90_plus_rate': round(delinquency_90_rate, 2),
            'loss_severity_percentage': round(loss_severity, 2),
            'prepayment_speed_cpr': round(cpr, 2),
            'prepayment_speed_abs': round(abs_prepayment, 2),
            'loan_term_distribution': {k: round(v, 2) for k, v in term_dist_pct.items()},
            'geographic_concentration': {k: round(v, 2) for k, v in sorted(geo_concentration_pct.items(), key=lambda x: x[1], reverse=True)},
            'average_loan_amount': round(average_loan_amount, 2),
            'average_remaining_term': round(average_remaining_term, 2),
            'weighted_avg_interest_rate': round(weighted_avg_interest_rate, 2),
            'new_vehicle_percentage': round(new_vehicle_pct, 2),
            'used_vehicle_percentage': round(used_vehicle_pct, 2),
            'repossession_rate': round(repossession_rate, 2),
            'last_updated': datetime.now().isoformat()
        }

        return metrics

    def extract_all_metrics(self) -> Dict[str, Any]:
        """
        Main method to extract all metrics from the file

        Returns:
            Dictionary containing all calculated metrics
        """
        print("Parsing assets from XML...")
        assets = self.parse_assets()
        print(f"Found {len(assets)} loans")

        print("Calculating metrics...")
        metrics = self.calculate_metrics(assets)

        return metrics


if __name__ == "__main__":
    # Example usage
    import json
    import sys

    file_path = r"C:\Hackathon2025\Hackathon-2025-GMF\0001347185-25-000024.txt"

    try:
        extractor = AutoLoanDataExtractor(file_path)
        metrics = extractor.extract_all_metrics()

        print("\n" + "="*80)
        print("EXTRACTED METRICS")
        print("="*80)
        print(json.dumps(metrics, indent=2))

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
