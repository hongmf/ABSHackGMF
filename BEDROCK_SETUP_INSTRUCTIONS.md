# Bedrock Model Access Setup

## Issue Found

✅ **Knowledge Base**: Found and ACTIVE (ID: `A7EOGV6BHS`)  
✅ **Region**: Corrected to `us-west-2`  
❌ **Model Access**: Claude 3 Sonnet access not enabled

## Solution: Enable Model Access

### Step 1: Enable Claude Model Access in AWS Console

1. Go to **AWS Bedrock Console**: https://console.aws.amazon.com/bedrock/
2. Select region: **us-west-2** (Oregon)
3. Click on **"Model access"** in the left sidebar
4. Click **"Manage model access"** or **"Enable specific models"**
5. Find and enable:
   - ✅ **Anthropic Claude 3 Sonnet**
   - ✅ **Anthropic Claude 3 Haiku** (optional, cheaper alternative)
   - ✅ **Anthropic Claude 3.5 Sonnet** (optional, newest version)
6. Click **"Save changes"**
7. Wait 1-2 minutes for access to be granted

### Step 2: Verify Model Access

After enabling, wait 2-3 minutes, then test:

```bash
cd /Users/davidawe/Desktop/GMFHACK/team-15-silence-of-the-rams/Hackathon-2025-GMF
source venv/bin/activate
python test_bedrock_connection.py
```

You should see:
```
✅ ALL TESTS PASSED - Bedrock Knowledge Base is working!
```

### Step 3: Restart Streamlit

```bash
streamlit run app.py
```

Navigate to the AI Assistant tab and start asking questions!

---

## Alternative: Use Different Model

If you can't enable Claude 3 Sonnet, update `.env` to use a model you have access to:

### Option 1: Claude 3 Haiku (Faster, Cheaper)
```bash
BEDROCK_MODEL_ARN=arn:aws:bedrock:us-west-2::foundation-model/anthropic.claude-3-haiku-20240307-v1:0
```

### Option 2: Claude 3.5 Sonnet (Newest)
```bash
BEDROCK_MODEL_ARN=arn:aws:bedrock:us-west-2::foundation-model/anthropic.claude-3-5-sonnet-20240620-v1:0
```

### Option 3: Claude Instant (Legacy)
```bash
BEDROCK_MODEL_ARN=arn:aws:bedrock:us-west-2::foundation-model/anthropic.claude-instant-v1
```

---

## Troubleshooting

### "Model access is denied"
- You haven't enabled the model in Bedrock console
- Wait 15 minutes after enabling
- Check you're in the correct region (us-west-2)

### "Access denied due to IAM"
Your IAM user needs:
```json
{
  "Effect": "Allow",
  "Action": [
    "bedrock:InvokeModel",
    "bedrock:InvokeModelWithResponseStream"
  ],
  "Resource": "arn:aws:bedrock:us-west-2::foundation-model/anthropic.claude-*"
}
```

### Still not working?
Contact your AWS administrator to:
1. Enable Bedrock model access
2. Grant IAM permissions for bedrock:InvokeModel

---

## What Was Fixed

1. ✅ **Region**: Changed from `us-east-1` → `us-west-2`
2. ✅ **Knowledge Base ID**: Confirmed `A7EOGV6BHS` is correct
3. ✅ **Model ARN**: Updated to use us-west-2 region
4. ⏳ **Model Access**: Needs to be enabled in console (see above)

---

## Current Configuration

Your `.env` file now has:
```bash
BEDROCK_KB_ID=A7EOGV6BHS
BEDROCK_REGION=us-west-2
BEDROCK_MODEL_ARN=arn:aws:bedrock:us-west-2::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0
```

After enabling model access, the AI Assistant will work!

