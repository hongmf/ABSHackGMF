import streamlit as st

st.title("🧪 Streamlit Test")
st.write("✅ If you can see this, Streamlit is working!")
st.write("Now try running the main app with: `streamlit run app.py`")

# Test imports
try:
    import pyarrow
    st.success("✅ PyArrow is available")
except ImportError:
    st.error("❌ PyArrow not found - install with: conda install -c conda-forge pyarrow -y")

try:
    import plotly
    st.success("✅ Plotly is available")
except ImportError:
    st.error("❌ Plotly not found - install with: pip install plotly")

try:
    import pandas
    st.success("✅ Pandas is available")
except ImportError:
    st.error("❌ Pandas not found - install with: pip install pandas")

try:
    import boto3
    st.success("✅ Boto3 is available")
except ImportError:
    st.error("❌ Boto3 not found - install with: pip install boto3")

st.write("---")
st.write("All green? Run the main app:")
st.code("streamlit run app.py", language="bash")

