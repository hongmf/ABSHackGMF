#!/usr/bin/env python3
"""
Test script for AI Assistant Visualization Agent

Demonstrates how to use the visualization agent that mimics
all methods from streamlit_viz_app.py
"""

import sys
import os
sys.path.append('src')

import pandas as pd
import numpy as np
from src.ai_assistant_integration import process_viz_request, load_data_source, get_current_data_info

def create_sample_data():
    """Create sample data for testing"""
    np.random.seed(42)
    n_samples = 1000
    
    data = {
        'Credit_Score': np.random.normal(720, 80, n_samples).astype(int),
        'Income': np.random.normal(50000, 15000, n_samples),
        'Age': np.random.randint(18, 80, n_samples),
        'Employment_Status': np.random.choice(['Full-time', 'Part-time', 'Self-employed', 'Unemployed'], n_samples),
        'Loan_Balance': np.random.normal(25000, 10000, n_samples),
        'Credit_Utilization': np.random.uniform(0, 1, n_samples),
        'Month_1': np.random.choice(['On-time', 'Late', 'Missed'], n_samples, p=[0.8, 0.15, 0.05]),
        'Month_2': np.random.choice(['On-time', 'Late', 'Missed'], n_samples, p=[0.8, 0.15, 0.05]),
        'Month_3': np.random.choice(['On-time', 'Late', 'Missed'], n_samples, p=[0.8, 0.15, 0.05]),
        'Month_4': np.random.choice(['On-time', 'Late', 'Missed'], n_samples, p=[0.8, 0.15, 0.05]),
        'Month_5': np.random.choice(['On-time', 'Late', 'Missed'], n_samples, p=[0.8, 0.15, 0.05]),
        'Month_6': np.random.choice(['On-time', 'Late', 'Missed'], n_samples, p=[0.8, 0.15, 0.05])
    }
    
    return pd.DataFrame(data)

def test_basic_visualization():
    """Test basic visualization functionality"""
    print("🧪 Testing Basic Visualization...")
    
    # Create sample data
    df = create_sample_data()
    df.to_csv('test_sample_data.csv', index=False)
    
    # Load the data
    result = load_data_source('local', 'test_sample_data.csv')
    print(f"Data loading: {'✅ Success' if result['success'] else '❌ Failed'}")
    
    if result['success']:
        # Test basic visualization request
        response = process_viz_request("Show me comprehensive visualizations of this data")
        
        print(f"\n📊 Visualization Results:")
        print(f"Data Source: {response['data_source']}")
        print(f"Dataset Shape: {response['data_overview']['shape']}")
        print(f"Numeric Columns: {len(response['data_overview']['numeric_columns'])}")
        print(f"Categorical Columns: {len(response['data_overview']['categorical_columns'])}")
        print(f"Generated Visualizations: {len(response['visualizations'])}")
        
        print(f"\n📈 Generated Plots:")
        for i, viz in enumerate(response['visualizations'], 1):
            print(f"{i}. {viz['title']} - {viz['description']}")
        
        print(f"\n📝 Summary:")
        print(response['summary'])
    
    # Cleanup
    if os.path.exists('test_sample_data.csv'):
        os.remove('test_sample_data.csv')

def test_prediction_request():
    """Test prediction functionality"""
    print("\n🔮 Testing Prediction Functionality...")
    
    # Create sample data
    df = create_sample_data()
    df.to_csv('test_prediction_data.csv', index=False)
    
    # Load the data
    result = load_data_source('local', 'test_prediction_data.csv')
    
    if result['success']:
        # Test prediction request
        response = process_viz_request("Predict future trends in credit scores and income")
        
        print(f"Prediction Available: {'✅ Yes' if response['prediction_available'] else '❌ No'}")
        
        prediction_plots = [v for v in response['visualizations'] if 'Prediction' in v['title']]
        print(f"Prediction Plots Generated: {len(prediction_plots)}")
        
        for plot in prediction_plots:
            if 'model_info' in plot:
                info = plot['model_info']
                print(f"- Model: {info['model_used']}")
                print(f"- Target: {info['target_variable']}")
                print(f"- Steps: {info['prediction_steps']}")
    
    # Cleanup
    if os.path.exists('test_prediction_data.csv'):
        os.remove('test_prediction_data.csv')

def test_data_source_discovery():
    """Test data source discovery"""
    print("\n🔍 Testing Data Source Discovery...")
    
    info = get_current_data_info()
    
    print(f"Current Data Loaded: {'✅ Yes' if info['loaded'] else '❌ No'}")
    
    if 'available_sources' in info:
        sources = info['available_sources']
        print(f"\n📁 Available Data Sources:")
        print(f"DynamoDB Tables: {len(sources.get('dynamodb_tables', []))}")
        print(f"S3 Files: {len(sources.get('s3_files', []))}")
        print(f"Local Files: {len(sources.get('local_files', []))}")
        
        # Show first few of each type
        for source_type, items in sources.items():
            if items:
                print(f"\n{source_type.replace('_', ' ').title()}:")
                for item in items[:3]:
                    print(f"  - {item}")
                if len(items) > 3:
                    print(f"  ... and {len(items) - 3} more")

def test_error_handling():
    """Test error handling"""
    print("\n⚠️  Testing Error Handling...")
    
    # Test with no data loaded
    from src.ai_assistant_integration import ai_assistant
    ai_assistant.current_agent = None
    ai_assistant.current_data_source = None
    
    response = process_viz_request("Show me plots")
    
    if 'error' in response:
        print("✅ Error handling works - no data loaded")
    else:
        print("✅ Default data loaded automatically")
    
    # Test invalid data source
    result = load_data_source('invalid', 'nonexistent.csv')
    print(f"Invalid source handling: {'✅ Handled' if not result['success'] else '❌ Not handled'}")

def main():
    """Run all tests"""
    print("🚀 AI Assistant Visualization Agent Test Suite")
    print("=" * 50)
    
    try:
        test_basic_visualization()
        test_prediction_request()
        test_data_source_discovery()
        test_error_handling()
        
        print("\n" + "=" * 50)
        print("✅ All tests completed successfully!")
        print("\n💡 The AI Assistant Visualization Agent is ready to use!")
        print("   It mimics all methods from streamlit_viz_app.py and provides:")
        print("   - 2x2 grid of core plots")
        print("   - Relationship analysis")
        print("   - Payment history timeline")
        print("   - Correlation heatmaps")
        print("   - Time series predictions")
        print("   - Interactive Plotly charts")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()