# Quick Fix: Enable Bedrock Model Access

## What You Need to Do

### 1. Go to AWS Bedrock Console
🔗 https://us-west-2.console.aws.amazon.com/bedrock/home?region=us-west-2#/modelaccess

### 2. Click "Manage model access"

### 3. Check the box for:
- ✅ Anthropic / Claude 3 Sonnet
- ✅ Anthropic / Claude 3 Haiku (optional)

### 4. Click "Save changes"

### 5. Wait 2-3 minutes

### 6. Test again:
```bash
cd /Users/davidawe/Desktop/GMFHACK/team-15-silence-of-the-rams/Hackathon-2025-GMF
source venv/bin/activate
python test_bedrock_connection.py
```

### 7. If successful, start Streamlit:
```bash
streamlit run app.py
```

---

## That's it!

The AI Assistant tab will now work with your Knowledge Base.

**Note**: Model access is free to enable - you only pay for actual usage.

