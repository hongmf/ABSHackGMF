# Visualization Agent

## Overview
The Visualization Agent is an intelligent system that automatically generates relevant charts and visualizations based on natural language queries in the AI Assistant tab. It analyzes user questions and dynamically creates visualizations from the Dashboard, Company Comparison, Geographic Analysis, and Detailed Metrics tabs.

## Features

### Automatic Visualization Generation
When you ask questions in the AI Assistant, the agent:
1. **Analyzes your query** to understand what you're asking about
2. **Identifies relevant companies** mentioned in your question
3. **Generates appropriate visualizations** based on detected topics
4. **Displays charts** alongside the AI's text response

### Supported Visualization Types

#### 1. Portfolio Balance
**Keywords:** portfolio, total, overall, balance, pool
**Example queries:**
- "Show me the total pool balance by company"
- "What's the overall portfolio size?"

**Generated chart:** Bar chart of total pool balance by company

#### 2. FICO Scores
**Keywords:** fico, credit score, credit quality
**Example queries:**
- "Compare FICO scores between companies"
- "What are the credit quality metrics?"

**Generated chart:** Grouped bar chart of average FICO scores by company and period

#### 3. Delinquency Rates
**Keywords:** delinquency, delinquent, late payment, past due
**Example queries:**
- "Show delinquency rates"
- "What are the late payment statistics?"

**Generated chart:** Grouped bar chart showing 30+, 60+, and 90+ day delinquency rates

#### 4. Vehicle Mix
**Keywords:** vehicle, new vs used, car type, auto type
**Example queries:**
- "Show vehicle mix for GM Financial"
- "What percentage are new vs used cars?"

**Generated chart:** Grouped bar chart of new vs used vehicle percentages

#### 5. Geographic Distribution
**Keywords:** geography, geographic, state, location, region, where
**Example queries:**
- "Display geographic distribution"
- "Which states have the most loans?"

**Generated chart:** Bar chart of top 10 states by loan concentration

#### 6. Loan Terms
**Keywords:** term, loan term, maturity, duration
**Example queries:**
- "Show loan term distribution"
- "What are the typical loan durations?"

**Generated chart:** Bar chart of loan term distribution by range

#### 7. Company Comparison
**Keywords:** compare, comparison, versus, vs, difference, between
**Example queries:**
- "Compare GM Financial and Ford Credit"
- "Show differences between companies"

**Generated chart:** Comparison table with key metrics

#### 8. Interest Rates
**Keywords:** interest rate, rate, apr, pricing
**Example queries:**
- "Compare interest rates"
- "What are the average rates?"

**Generated chart:** Grouped bar chart of weighted average interest rates

## How It Works

### Query Analysis
The agent uses keyword matching to identify:
- **Topics:** What type of data you're asking about (FICO, delinquency, etc.)
- **Companies:** Which companies are mentioned in your query
- **Intent:** Whether you want comparisons, distributions, or specific metrics

### Intelligent Filtering
- Automatically filters data to relevant companies mentioned in your query
- Falls back to all companies if none are specifically mentioned
- Generates multiple visualizations if your query matches multiple categories

### Dynamic Generation
The agent:
1. Analyzes your natural language query
2. Extracts relevant keywords and entities
3. Selects appropriate visualization types
4. Generates Plotly charts with proper formatting
5. Displays them below the AI's text response

## Usage Examples

### Basic Queries
```
User: "Show me portfolio balances"
→ Generates: Bar chart of total pool balance by company
```

```
User: "What are the FICO scores?"
→ Generates: FICO score comparison chart
```

### Company-Specific Queries
```
User: "Show delinquency rates for GM Financial"
→ Generates: Delinquency chart filtered to GM Financial
```

```
User: "Display geographic distribution for Ford Credit"
→ Generates: Top 10 states chart for Ford Credit
```

### Comparison Queries
```
User: "Compare GM Financial and Ford Credit"
→ Generates: Comparison table with all key metrics
```

```
User: "How do interest rates differ between companies?"
→ Generates: Interest rate comparison chart
```

### Multi-Topic Queries
```
User: "Show me FICO scores and delinquency rates"
→ Generates: Both FICO chart and delinquency chart
```

## Integration

The Visualization Agent is integrated into the AI Assistant tab:
- **Seamless experience:** No need to switch between tabs
- **Context-aware:** Uses the same filters and data as other tabs
- **Real-time:** Generates visualizations on-demand based on your questions
- **Interactive:** All charts are interactive Plotly visualizations

## Benefits

1. **Faster insights:** Get visualizations without manually navigating tabs
2. **Natural interaction:** Ask questions in plain English
3. **Comprehensive view:** Combine AI explanations with visual data
4. **Contextual:** Visualizations match exactly what you're asking about
5. **Consistent:** Uses the same visualization logic as manual tabs

## Technical Details

### Architecture
- **Module:** `src/visualization_agent.py`
- **Class:** `VisualizationAgent`
- **Integration:** Embedded in AI Assistant tab workflow
- **Dependencies:** pandas, plotly

### Key Methods
- `analyze_query()`: NLP-based query analysis
- `generate_visualizations()`: Main orchestration method
- `_create_*_chart()`: Individual chart generation methods

### Performance
- Charts generated in real-time (< 1 second)
- Uses cached data from DynamoDB
- No additional API calls required
- Fully client-side visualization rendering

## Limitations

1. **Keyword-based:** Uses keyword matching, not full NLP
2. **English only:** Currently supports English queries
3. **Exact company names:** Best results with exact company name mentions
4. **Data availability:** Limited to data in DynamoDB

## Future Enhancements

Potential improvements:
- Advanced NLP with entity recognition
- More sophisticated query understanding
- Custom date range filtering from queries
- Export visualizations to PDF/PNG
- Saved visualization templates
- Multi-language support
