# AWS Bedrock Knowledge Base Integration

## Overview

The Streamlit dashboard now integrates with AWS Bedrock Knowledge Base to provide AI-powered question answering about auto loan metrics.

**Knowledge Base ID:** `A7EOGV6BHS`

## Features

### 🤖 AI Assistant Tab

The dashboard includes a conversational AI assistant that:
- Answers questions about auto loan metrics
- Uses your Bedrock Knowledge Base for context
- Provides source citations for transparency
- Maintains conversation history
- Supports natural language queries

### Example Questions

- "What are delinquency rates in auto loans?"
- "Compare FICO scores between GM Financial and Ford Credit"
- "Explain loss severity percentage"
- "What factors affect prepayment speed?"
- "Analyze geographic distribution of auto loans"

## Configuration

### 1. Environment Variables

Add to your `.env` file:

```bash
# Bedrock Configuration
BEDROCK_KB_ID=A7EOGV6BHS
BEDROCK_REGION=us-east-1
BEDROCK_MODEL_ARN=arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0
```

### 2. AWS Permissions

Your AWS credentials need the following permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:Retrieve",
        "bedrock:RetrieveAndGenerate"
      ],
      "Resource": "arn:aws:bedrock:us-east-1:*:knowledge-base/A7EOGV6BHS"
    },
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel"
      ],
      "Resource": "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-*"
    }
  ]
}
```

### 3. Install Dependencies

Make sure boto3 is up to date:

```bash
pip install -r requirements.txt
```

Or specifically:

```bash
pip install boto3>=1.34.0
```

## How It Works

### Architecture

```
User Question → Streamlit App → Bedrock RetrieveAndGenerate API → Knowledge Base
                                                                    ↓
                    ← Answer with Citations ← Claude 3 Sonnet ← Retrieved Documents
```

### Technical Details

1. **Retrieval**: Uses vector search to find relevant documents in your Knowledge Base
2. **Generation**: Claude 3 Sonnet generates answers based on retrieved context
3. **Citations**: Tracks which documents were used to generate the answer
4. **Session Management**: Maintains conversation context for follow-up questions

### API Used

The integration uses `retrieve_and_generate` API with:
- **numberOfResults**: 5 (retrieves top 5 relevant documents)
- **temperature**: 0.7 (balanced creativity and accuracy)
- **maxTokens**: 2000 (sufficient for detailed answers)
- **topP**: 0.9 (nucleus sampling for better responses)

## Usage in Streamlit App

### Starting a Conversation

1. Navigate to the **"🤖 AI Assistant"** tab
2. Type your question in the chat input
3. Press Enter or click outside the input
4. Wait for the AI to search the knowledge base and generate an answer

### Features

- **📚 View Sources**: Click to see which documents were used
- **🗑️ Clear Chat**: Reset the conversation
- **ℹ️ KB Info**: View Knowledge Base configuration
- **💡 Examples**: See sample questions

### Conversation History

The assistant maintains conversation history within a session:
- Ask follow-up questions
- Reference previous answers
- Build context over multiple questions

## Troubleshooting

### "Error connecting to Bedrock Knowledge Base"

**Possible Causes:**
1. AWS credentials not configured
2. Insufficient IAM permissions
3. Wrong Knowledge Base ID
4. Bedrock service not available in region

**Solutions:**

```bash
# Verify credentials
aws sts get-caller-identity

# Test Bedrock access
aws bedrock list-foundation-models --region us-east-1

# Check Knowledge Base
aws bedrock-agent get-knowledge-base --knowledge-base-id A7EOGV6BHS --region us-east-1
```

### "Invalid model ARN"

Update the model ARN in `.env`:

```bash
# For Claude 3 Sonnet
BEDROCK_MODEL_ARN=arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0

# For Claude 3 Haiku (faster, cheaper)
BEDROCK_MODEL_ARN=arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-haiku-20240307-v1:0
```

### No sources shown

Sources are only available if:
- The Knowledge Base returns citation metadata
- Documents in S3 have proper metadata
- The `citations` field is included in the response

## Cost Considerations

### Pricing Components

1. **Bedrock Model Invocation**: ~$0.003 per 1K input tokens, ~$0.015 per 1K output tokens
2. **Knowledge Base Retrieval**: ~$0.10 per 1K retrieval units
3. **Storage**: S3 storage costs for your documents

### Optimization Tips

- Use Claude 3 Haiku for faster, cheaper responses
- Limit `numberOfResults` to reduce retrieval costs
- Reduce `maxTokens` for shorter answers
- Cache frequent queries in Streamlit

## Advanced Configuration

### Custom Prompt Template

Edit the prompt in `app.py`:

```python
'textPromptTemplate': '''You are a specialized auto loan analyst.

Context: $search_results$
Question: $query$

Provide a concise answer with specific numbers and citations.'''
```

### Adjust Retrieval Settings

```python
'numberOfResults': 10  # Retrieve more documents (default: 5)
```

### Change Model

```python
# Use Haiku for faster responses
MODEL_ARN = 'arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-haiku-20240307-v1:0'
```

## Integration with Live Data

The AI Assistant uses the Knowledge Base for general information. To also query live DynamoDB data, you can enhance the prompt:

```python
# Get current metrics from DynamoDB
db_handler = DynamoDBHandler()
current_data = db_handler.scan_all_metrics()

# Add to prompt context
context = f"""
Knowledge Base Information: [Retrieved from KB]

Current Live Data:
- Total Records: {len(current_data)}
- Latest Period: {current_data[0].get('reporting_period')}
...

Question: {question}
"""
```

## Next Steps

### Enhance the Knowledge Base

1. Add more SEC filings to S3
2. Include industry reports and analysis
3. Add regulatory documentation
4. Update with latest market data

### Add More Features

- Export conversation history
- Share insights via email
- Schedule automated reports
- Multi-language support

### Connect to Other AWS Services

- **Lambda**: Trigger analysis on new data
- **EventBridge**: Schedule periodic summaries
- **SES**: Email insights to stakeholders
- **QuickSight**: Embed dashboards

## Support

For issues or questions:
1. Check CloudWatch Logs for Bedrock API calls
2. Review IAM permissions
3. Test Knowledge Base in AWS Console
4. Verify boto3 version compatibility

## References

- [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [Knowledge Bases for Amazon Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base.html)
- [RetrieveAndGenerate API](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent-runtime_RetrieveAndGenerate.html)

