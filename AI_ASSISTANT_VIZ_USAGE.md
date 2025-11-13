# AI Assistant Visualization Agent Usage

This document explains how to use the AI Assistant Visualization Agent that mimics all methods from `streamlit_viz_app.py`.

## Quick Start

```python
from src.ai_assistant_integration import process_viz_request, load_data_source

# Process a visualization request
response = process_viz_request("Show me credit score distributions and trends")

# The response contains:
# - data_overview: Dataset information
# - visualizations: List of generated plots
# - summary: Human-readable summary
# - prediction_available: Whether predictions can be made
```

## Features Mimicked from streamlit_viz_app.py

### 1. **Data Overview Display**
- Dataset size and shape information
- Column types (numeric vs categorical)
- Sample data preview
- Missing value analysis

### 2. **Core 2x2 Grid Plots**
- Credit Score Distribution (histogram)
- Employment Status Distribution (bar chart)
- Income Distribution (histogram)
- Income vs Credit Score Scatter Plot

### 3. **Relationship Analysis**
- Age vs Income scatter plot
- Credit Utilization vs Loan Balance scatter plot
- Configurable based on available columns

### 4. **Payment History Timeline**
- Stacked area plot for payment status over time
- Automatically detects Month_* columns
- Shows On-time, Late, and Missed payments

### 5. **Correlation Matrix Heatmap**
- Seaborn heatmap with annotations
- Shows correlations between all numeric variables
- Uses 'coolwarm' colormap

### 6. **Time Series Prediction**
- Triggered by keywords: 'predict', 'forecast', 'future', 'trend'
- Linear regression-based trend analysis
- 10-step future predictions

### 7. **Interactive Plotly Charts**
- Distribution histograms
- Scatter plots
- Box plots by category

## Usage Examples

### Basic Visualization Request
```python
response = process_viz_request("Create visualizations for this data")

# Access generated plots
for viz in response['visualizations']:
    print(f"Title: {viz['title']}")
    print(f"Description: {viz['description']}")
    if viz['type'] == 'matplotlib':
        # viz['image_base64'] contains the plot as base64 string
        pass
    elif viz['type'] == 'plotly':
        # viz['figure'] contains the Plotly figure object
        pass
```

### Prediction Request
```python
response = process_viz_request("Predict future trends in credit scores")

# Will include prediction plots if data supports it
prediction_plots = [v for v in response['visualizations'] 
                   if 'Prediction' in v['title']]
```

### Data Source Management
```python
from src.ai_assistant_integration import load_data_source, get_current_data_info

# Load from DynamoDB
result = load_data_source('dynamodb', 'AutoLoanMetrics')

# Load from S3
result = load_data_source('s3', 'path/to/file.csv')

# Load local file
result = load_data_source('local', 'scripts/Delinquency_prediction_dataset.csv')

# Check current data
info = get_current_data_info()
print(f"Current source: {info['data_source']}")
```

## Response Structure

```python
{
    'data_overview': {
        'shape': (rows, columns),
        'numeric_columns': ['col1', 'col2', ...],
        'categorical_columns': ['col3', 'col4', ...],
        'sample_data': [record1, record2, ...],
        'missing_values': {'col1': 0, 'col2': 5, ...}
    },
    'visualizations': [
        {
            'title': 'Plot Title',
            'type': 'matplotlib' or 'plotly',
            'image_base64': 'base64_string',  # for matplotlib
            'figure': plotly_figure_object,   # for plotly
            'description': 'Plot description'
        }
    ],
    'prediction_available': True/False,
    'user_query': 'original query',
    'data_source': 'source description',
    'summary': 'human-readable summary'
}
```

## Styling and Configuration

The agent uses the same styling as `streamlit_viz_app.py`:

- **Colors**: skyblue, lightcoral, lightgreen, purple, orange, green, red
- **Figure sizes**: (16,12), (16,6), (14,8), (12,8)
- **Grid**: alpha=0.3 transparency
- **Layout**: `plt.tight_layout()` for proper spacing

## Error Handling

```python
response = process_viz_request("Show me plots")

if 'error' in response:
    print(f"Error: {response['error']}")
    print(f"Available sources: {response['available_sources']}")
else:
    # Process successful response
    pass
```

## Integration with AI Assistant Panel

When users ask for visualizations in the AI Assistant panel:

1. **Parse the request** using `process_viz_request(user_query)`
2. **Display data overview** from `response['data_overview']`
3. **Show visualizations** from `response['visualizations']`
4. **Provide summary** from `response['summary']`
5. **Handle predictions** if requested and available

## Supported Query Types

- "Show me credit score distributions"
- "Create plots for this data"
- "Visualize the relationships between variables"
- "Predict future trends"
- "Generate correlation analysis"
- "Show payment history over time"
- "Compare different categories"

The agent automatically detects intent and generates appropriate visualizations using all methods from `streamlit_viz_app.py`.