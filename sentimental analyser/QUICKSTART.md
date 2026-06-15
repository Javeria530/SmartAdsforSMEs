# Quick Start Guide

## 5-Minute Setup

### 1. Install Dependencies (2 minutes)

```bash
cd "e:\8th Semester\FYP-II\tweeteval"
pip install -r requirements.txt
```

### 2. Launch Application (1 minute)

```bash
streamlit run app.py
```

Your browser will open at: `http://localhost:8501`

---

## First Time Usage

### Step 1: Select Analysis Mode

Choose from the **sidebar menu**:
- **📝 Single Analysis** - Analyze one comment
- **📊 Batch Upload** - Process CSV file
- **📈 Analytics Dashboard** - View charts

### Step 2: Analyze Comment (Single Mode)

1. Enter text in the comment box (optional)
2. Enter likes count (optional, use 0 to skip)
3. Click **"🔍 Analyze Sentiment"**
4. View results with confidence scores

**Example:**
```
Text: "Love this! Best ever!"
Likes: 150
→ Overall Sentiment: Positive (0.96 confidence)
```

### Step 3: Batch Upload (CSV Mode)

1. Prepare CSV file with columns:
   - `text` - Comment/review (optional)
   - `likes` - Number of likes (optional)

2. Click **"📁 Choose CSV file"**
3. Upload file (use `example_engagement_data.csv` to test)
4. Click **"🔍 Analyze All Records"**
5. Download results as CSV

### Step 4: View Analytics (Dashboard Mode)

1. After batch upload completes
2. Switch to **"📈 Analytics Dashboard"** mode
3. View:
   - Sentiment distribution (pie chart)
   - Sentiment counts (bar chart)
   - Confidence distribution
   - Engagement by sentiment
2. Upload CSV with `text` and/or `likes` columns
3. Click **"Analyze All Records"**
4. Download results

### View Analytics
1. After analyzing records, select **"Analytics Dashboard"**
2. View sentiment distribution, charts, and trends
3. Export results

---

## File Structure

```
tweeteval/
├── app.py                      # Main Streamlit application
├── sentiment_analyzer.py       # Core sentiment analysis modules
├── config.py                   # Configuration & thresholds
├── requirements.txt            # Python dependencies
├── setup.py                    # Setup script
├── DOCUMENTATION.md            # Full documentation
├── QUICKSTART.md              # This file
└── ARCHITECTURE.md            # Technical details
```

---

## Key Configuration

Edit `config.py` to customize:

```python
# Change likes thresholds (in config.py)
LIKES_SENTIMENT_THRESHOLDS['high']['min'] = 150  # Adjust as needed

# Change text/likes weights (in config.py)
SENTIMENT_WEIGHTS = {"text": 0.80, "likes": 0.20}

# Change model (in config.py)
TEXT_SENTIMENT_MODEL = "distilbert-base-uncased-finetuned-sst-2-english"  # Faster option
```

---

## Common Tasks

### Analyze Single Text
```python
from sentiment_analyzer import TextSentimentAnalyzer

analyzer = TextSentimentAnalyzer()
result = analyzer.analyze("Great product!")
print(result['sentiment'])
```

### Analyze Likes Only
```python
from sentiment_analyzer import LikesSentimentMapper

mapper = LikesSentimentMapper()
result = mapper.map_likes_to_sentiment(150)
print(result['sentiment'])  # Output: Positive
```

### Batch Process CSV
```python
import pandas as pd
from sentiment_analyzer import BatchSentimentProcessor

processor = BatchSentimentProcessor()
df = pd.read_csv('data.csv')
records = df[['text', 'likes']].to_dict('records')
results = processor.process_batch(records)
```

---

## Tips & Tricks

1. **First run slow?** → Model downloads on first use (~500MB). Subsequent runs are faster.
2. **Want faster inference?** → Use GPU or switch to lighter model in config
3. **CSV encoding issues?** → Save CSV as UTF-8
4. **Need different thresholds?** → Modify `LIKES_SENTIMENT_THRESHOLDS` in config.py

---

## Next Steps

- Read [DOCUMENTATION.md](DOCUMENTATION.md) for detailed API reference
- Check [ARCHITECTURE.md](ARCHITECTURE.md) for technical implementation
- Explore `config.py` for all customization options
- Try example CSV in Streamlit UI
