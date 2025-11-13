# Streamlit Dashboard Setup

## Quick Start

The Streamlit dashboard is ready! Here's how to run it:

### 1. Install Dependencies

```bash
cd /Users/davidawe/Desktop/GMFHACK/team-15-silence-of-the-rams/Hackathon-2025-GMF
source venv/bin/activate

# Install Streamlit and dependencies
pip install streamlit plotly

# If pyarrow fails to build, try:
# Option 1: Use conda (if available)
conda install -c conda-forge pyarrow

# Option 2: Install pre-built wheel
pip install --only-binary :all: pyarrow

# Option 3: Use system Python with conda
# (pyarrow often works better with conda environments)
```

### 2. Run the App

```bash
# Using the run script
./run_app.sh

# Or directly
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## Features

- **📈 Dashboard**: Overview metrics and charts
- **🔍 Company Comparison**: Side-by-side metrics comparison
- **🗺️ Geographic Analysis**: State-by-state breakdown
- **📊 Detailed Metrics**: Full data table with CSV download
- **💬 AI Assistant**: Placeholder for Bedrock integration

## Troubleshooting

### PyArrow Installation Issues

If you encounter pyarrow build errors:

1. **Use Conda** (recommended):
   ```bash
   conda install -c conda-forge pyarrow
   ```

2. **Install pre-built wheel**:
   ```bash
   pip install --only-binary :all: pyarrow
   ```

3. **Use system Python** (if conda is available):
   ```bash
   # Create new environment with conda
   conda create -n autoloan python=3.10
   conda activate autoloan
   conda install -c conda-forge pyarrow streamlit plotly pandas
   ```

### Missing Dependencies

If you see import errors, install missing packages:

```bash
pip install toml altair blinker cachetools click pillow protobuf requests rich tornado tzlocal validators importlib-metadata
```

## Usage

1. **Select Companies**: Use the sidebar to filter by company
2. **Select Periods**: Filter by reporting period
3. **Explore Tabs**: 
   - Dashboard for overview
   - Company Comparison for side-by-side analysis
   - Geographic Analysis for state distributions
   - Detailed Metrics for full data table
   - AI Assistant (coming soon with Bedrock)

## Data Source

The app reads data from DynamoDB table `AutoLoanMetrics`. Make sure you have:
- AWS credentials configured in `.env`
- Data processed and stored in DynamoDB
- Run: `python src/pipeline.py --s3-bucket abs-ee` to process files

