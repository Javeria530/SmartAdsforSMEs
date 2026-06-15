# Engagement Sentiment Analyzer - Comprehensive Documentation

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [System Architecture](#system-architecture)
3. [Installation & Setup](#installation--setup)
4. [Hybrid Sentiment Flow](#hybrid-sentiment-flow)
5. [Configurable Thresholds](#configurable-thresholds)
6. [API Reference](#api-reference)
7. [Usage Examples](#usage-examples)
8. [Integration Points](#integration-points)
9. [Performance Considerations](#performance-considerations)
10. [Troubleshooting](#troubleshooting)

---

## 📖 Project Overview

### Purpose
The **Engagement Sentiment Analyzer** is an academic-grade sentiment analysis system designed for analyzing engagement feedback on posts and ads. It combines text-based sentiment analysis with likes-based engagement metrics to provide comprehensive engagement insights.

### Key Features
- ✅ **Text Sentiment Analysis**: Transformer-based classification (Positive/Neutral/Negative)
- ✅ **Likes Engagement Mapping**: Rule-based numeric sentiment conversion
- ✅ **Hybrid Aggregation**: Intelligent combination of text and likes signals
- ✅ **Streamlit UI**: Interactive web-based dashboard
- ✅ **CSV Support**: Batch processing of engagement data
- ✅ **Analytics Dashboard**: Visualizations and engagement trends
- ✅ **Configurable Thresholds**: Customizable sentiment mapping rules
- ✅ **Integration-Ready**: Prepared for future social media publisher APIs

### Use Cases
- Social media engagement analysis (academic research)
- Ad performance evaluation
- Comment sentiment tracking
- Engagement trend monitoring
- Campaign effectiveness measurement

---

## 🏗️ System Architecture

### Modular Design

The system is organized into independent, reusable modules:

```
sentiment_analyzer/
├── config.py                    # Configuration & thresholds
├── sentiment_analyzer.py        # Core analysis modules
└── app.py                       # Streamlit UI

Key Components:
├── TextPreprocessor             # Text normalization
├── TextSentimentAnalyzer        # Transformer-based classification
├── LikesSentimentMapper         # Rule-based likes mapping
├── HybridSentimentAnalyzer      # Combined analysis
└── BatchSentimentProcessor      # Batch record processing
```

### Component Responsibilities

#### 1. **TextPreprocessor**
- Normalizes text according to TweetEval standards
- Replaces URLs with `http` token
- Replaces @mentions with `@user` token
- Validates text length and format

#### 2. **TextSentimentAnalyzer**
- Loads pre-trained Transformer model
- Performs sentiment classification
- Returns confidence scores for each label
- Handles model loading and inference

#### 3. **LikesSentimentMapper**
- Maps numeric likes to sentiment categories
- Uses configurable thresholds (High/Medium/Low)
- Assigns confidence scores based on threshold ranges
- Supports custom threshold adjustment

#### 4. **HybridSentimentAnalyzer**
- Combines text and likes sentiments
- Applies weighted averaging
- Generates overall engagement sentiment
- Produces human-readable summaries

#### 5. **BatchSentimentProcessor**
- Processes multiple records sequentially
- Handles error cases gracefully
- Maintains record indices for tracking
- Returns structured result sets

---

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8+
- pip (Python package manager)
- ~2-3 GB disk space for model files
- GPU (optional, but recommended for faster inference)

### Installation Steps

#### Option 1: Automatic Setup (Recommended)
```bash
# Navigate to project directory
cd tweeteval

# Run setup script
python setup.py
```

#### Option 2: Manual Setup
```bash
# Install dependencies
pip install -r requirements.txt

# (Optional) For faster inference with GPU
pip install torch==2.1.1+cu118 -f https://download.pytorch.org/whl/torch_stable.html
```

### Verify Installation
```bash
# Test imports
python -c "from sentiment_analyzer import HybridSentimentAnalyzer; print('✓ Installation successful')"
```

### Running the Application

```bash
# Start Streamlit server
streamlit run app.py

# Application will open at: http://localhost:8501
```

---

## 🔄 Hybrid Sentiment Flow

### Overview Diagram

```
┌─────────────────────────────────────────────────────────┐
│                   Input Data                             │
├──────────────────────┬──────────────────────────────────┤
│   Text (optional)    │   Likes (optional)               │
└──────────┬───────────┴──────────────┬────────────────────┘
           │                          │
           ▼                          ▼
┌──────────────────────┐  ┌──────────────────────────┐
│ Text Preprocessing   │  │ Likes Validation         │
│ (URL/mention clean)  │  │ (0 ≤ likes)              │
└──────────┬───────────┘  └──────────┬───────────────┘
           │                          │
           ▼                          ▼
┌──────────────────────┐  ┌──────────────────────────┐
│ TextSentimentAnalyzer│  │ LikesSentimentMapper     │
│ (Transformer model)  │  │ (Rule-based mapping)     │
│ Returns:             │  │ Returns:                 │
│ • Sentiment label    │  │ • Sentiment label        │
│ • Confidence (0-1)   │  │ • Confidence (0-1)       │
│ • Raw scores         │  │ • Threshold range        │
└──────────┬───────────┘  └──────────┬───────────────┘
           │                          │
           │ (75% weight)             │ (25% weight)
           └──────────────┬───────────┘
                          │
                          ▼
            ┌─────────────────────────────┐
            │ Hybrid Aggregation          │
            │ 1. Convert to numeric       │
            │    (Neg=0, Neu=0.5, Pos=1) │
            │ 2. Apply weights            │
            │ 3. Average weighted scores  │
            │ 4. Convert back to label    │
            │ 5. Calculate final conf     │
            └──────────────┬──────────────┘
                           │
                           ▼
            ┌─────────────────────────────┐
            │ Overall Sentiment            │
            │ • Final sentiment label      │
            │ • Combined confidence score  │
            │ • Numeric score (0-1)        │
            │ • Component breakdown        │
            └─────────────────────────────┘
```

### Step-by-Step Process

#### Step 1: Text Processing
```python
Input:  "Great post! 🎉 Check @twitter http://example.com"
Output: "Great post! 🎉 Check @user http"
```

#### Step 2: Text Sentiment Analysis
```python
Model:  cardiffnlp/twitter-roberta-base-sentiment-latest
Input:  Preprocessed text
Output: {
    'sentiment': 'Positive',
    'confidence': 0.92,
    'raw_scores': {
        'positive': 0.92,
        'neutral': 0.05,
        'negative': 0.03
    }
}
```

#### Step 3: Likes Sentiment Mapping
```python
Thresholds:
  High   (≥100) → Positive confidence=0.95
  Medium (20-99) → Neutral confidence=0.75
  Low    (<20) → Negative confidence=0.60

Input:  75 likes
Output: {
    'sentiment': 'Neutral',
    'confidence': 0.75,
    'threshold_range': 'medium'
}
```

#### Step 4: Hybrid Aggregation
```python
Weights: text=0.75, likes=0.25

Score calculation:
  text_score = 1.0 (Positive)
  likes_score = 0.5 (Neutral)
  
  weighted_text = 1.0 × 0.75 = 0.75
  weighted_likes = 0.5 × 0.25 = 0.125
  
  final_score = 0.75 + 0.125 = 0.875
  final_sentiment = 'Positive' (score > 0.67)
  
  confidence = (0.92 × 0.75) + (0.75 × 0.25) = 0.8775 ≈ 0.88
```

#### Step 5: Output Generation
```python
{
    'overall_sentiment': {
        'sentiment': 'Positive',
        'confidence': 0.88,
        'score': 0.875,
        'components': {
            'text': {'weight': 0.75, 'included': True},
            'likes': {'weight': 0.25, 'included': True}
        }
    },
    'text_sentiment': { ... },
    'likes_sentiment': { ... },
    'engagement_summary': 'Text sentiment: Positive (92%) | Likes engagement: Neutral (75 likes) | Overall engagement: Positive (Confidence: 88%)'
}
```

### Sentiment Score Mapping

| Score Range | Sentiment | Interpretation |
|-----------|-----------|-----------------|
| 0.00 - 0.33 | Negative | Low/negative engagement |
| 0.33 - 0.67 | Neutral | Moderate/mixed engagement |
| 0.67 - 1.00 | Positive | High/positive engagement |

---

## ⚙️ Configurable Thresholds

### Likes Sentiment Thresholds

Configured in `config.py`:

```python
LIKES_SENTIMENT_THRESHOLDS = {
    "high": {
        "min": 100,              # Likes ≥ 100 = Positive
        "sentiment": "Positive",
        "confidence": 0.95      # High confidence for high engagement
    },
    "medium": {
        "min": 20,              # Likes ≥ 20 and < 100 = Neutral
        "max": 100,
        "sentiment": "Neutral",
        "confidence": 0.75      # Medium confidence
    },
    "low": {
        "max": 20,              # Likes < 20 = Negative
        "sentiment": "Negative",
        "confidence": 0.60      # Lower confidence for ambiguous low engagement
    }
}
```

### Customizing Thresholds

#### Method 1: Direct Configuration Change
```python
# In config.py
LIKES_SENTIMENT_THRESHOLDS = {
    "high": {"min": 50, "sentiment": "Positive", "confidence": 0.95},
    "medium": {"min": 10, "max": 50, "sentiment": "Neutral", "confidence": 0.75},
    "low": {"max": 10, "sentiment": "Negative", "confidence": 0.60}
}
```

#### Method 2: Programmatic Configuration
```python
from sentiment_analyzer import LikesSentimentMapper
from config import LIKES_SENTIMENT_THRESHOLDS

# Modify thresholds before analysis
LIKES_SENTIMENT_THRESHOLDS['high']['min'] = 150
mapper = LikesSentimentMapper()
result = mapper.map_likes_to_sentiment(175)
```

### Sentiment Weights

Configured in `config.py`:

```python
SENTIMENT_WEIGHTS = {
    "text": 0.75,    # Text sentiment contributes 75%
    "likes": 0.25    # Likes engagement contributes 25%
}
```

**Rationale:**
- Text sentiment is more reliable (comes from sophisticated model)
- Likes are context-dependent (platform-specific, subject to algorithm)
- 75/25 split balances both signals while favoring text analysis

### Threshold Recommendations

#### For Academic Research
```python
# Conservative thresholds - focus on clear signals
"high": {"min": 200},
"medium": {"min": 50},
# Weights toward text (more reliable)
SENTIMENT_WEIGHTS = {"text": 0.85, "likes": 0.15}
```

#### For Campaign Performance
```python
# Lower thresholds - capture more engagement
"high": {"min": 50},
"medium": {"min": 10},
# Equal weighting of both signals
SENTIMENT_WEIGHTS = {"text": 0.5, "likes": 0.5}
```

#### For Twitter/X-like Platforms
```python
# Aggressive engagement (high likes typical)
"high": {"min": 500},
"medium": {"min": 100},
# Slightly favor text
SENTIMENT_WEIGHTS = {"text": 0.70, "likes": 0.30}
```

---

## 📚 API Reference

### HybridSentimentAnalyzer

Main interface for sentiment analysis.

#### Initialization
```python
from sentiment_analyzer import HybridSentimentAnalyzer

analyzer = HybridSentimentAnalyzer()
```

#### analyze_hybrid(text, likes)
Perform complete sentiment analysis.

**Parameters:**
- `text` (str, optional): Text to analyze
- `likes` (int, optional): Number of likes

**Returns:** Dict with complete analysis result

**Example:**
```python
result = analyzer.analyze_hybrid(
    text="This is amazing!",
    likes=150
)
print(result['overall_sentiment']['sentiment'])  # Output: Positive
```

#### Response Structure
```python
{
    'text_sentiment': {
        'sentiment': 'Positive',
        'confidence': 0.92,
        'raw_scores': {'positive': 0.92, 'neutral': 0.05, 'negative': 0.03},
        'original_text': '...',
        'preprocessed_text': '...'
    },
    'likes_sentiment': {
        'sentiment': 'Positive',
        'confidence': 0.95,
        'likes_count': 150,
        'threshold_range': 'high'
    },
    'overall_sentiment': {
        'sentiment': 'Positive',
        'confidence': 0.88,
        'score': 0.875,
        'components': {...}
    },
    'engagement_summary': '...'
}
```

### TextSentimentAnalyzer

Standalone text sentiment analysis.

#### analyze(text)
```python
from sentiment_analyzer import TextSentimentAnalyzer

analyzer = TextSentimentAnalyzer()
result = analyzer.analyze("Great product!")
# Returns: {'sentiment': 'Positive', 'confidence': 0.91, ...}
```

### LikesSentimentMapper

Standalone likes-to-sentiment mapping.

#### map_likes_to_sentiment(likes)
```python
from sentiment_analyzer import LikesSentimentMapper

mapper = LikesSentimentMapper()
result = mapper.map_likes_to_sentiment(75)
# Returns: {'sentiment': 'Neutral', 'confidence': 0.75, 'likes_count': 75, ...}
```

### BatchSentimentProcessor

Process multiple records efficiently.

#### process_batch(records)
```python
from sentiment_analyzer import BatchSentimentProcessor

processor = BatchSentimentProcessor()
records = [
    {'text': 'Great!', 'likes': 50},
    {'text': 'Bad experience', 'likes': 5},
    {'likes': 200}
]

results = processor.process_batch(records)
# Returns: List[Dict] with analysis for each record
```

---

## 💡 Usage Examples

### Example 1: Single Record Analysis
```python
from sentiment_analyzer import HybridSentimentAnalyzer

analyzer = HybridSentimentAnalyzer()

# Analyze with both text and likes
result = analyzer.analyze_hybrid(
    text="Love this feature! Makes my workflow so much easier",
    likes=250
)

print(f"Overall Sentiment: {result['overall_sentiment']['sentiment']}")
print(f"Confidence: {result['overall_sentiment']['confidence']:.1%}")
print(f"Summary: {result['engagement_summary']}")
```

### Example 2: Batch CSV Processing
```python
import pandas as pd
from sentiment_analyzer import BatchSentimentProcessor

processor = BatchSentimentProcessor()

# Load CSV
df = pd.read_csv('engagement_data.csv')

# Convert to records
records = df[['text', 'likes']].to_dict('records')

# Process batch
results = processor.process_batch(records)

# Extract results
sentiments = [r['overall_sentiment']['sentiment'] for r in results]
confidences = [r['overall_sentiment']['confidence'] for r in results]

print(f"Analyzed {len(results)} records")
print(f"Average confidence: {sum(confidences)/len(confidences):.1%}")
```

### Example 3: Text-Only Analysis
```python
from sentiment_analyzer import TextSentimentAnalyzer

analyzer = TextSentimentAnalyzer()

tweets = [
    "This is absolutely wonderful!",
    "Not bad, pretty average",
    "Worst experience ever"
]

for tweet in tweets:
    result = analyzer.analyze(tweet)
    print(f"{result['sentiment']}: {result['confidence']:.1%}")
```

### Example 4: Likes-Only Analysis
```python
from sentiment_analyzer import LikesSentimentMapper

mapper = LikesSentimentMapper()

like_counts = [500, 100, 25, 10, 0]

for likes in like_counts:
    result = mapper.map_likes_to_sentiment(likes)
    print(f"{likes} likes → {result['sentiment']}")
```

### Example 5: Custom Threshold Analysis
```python
from sentiment_analyzer import LikesSentimentAnalyzer, BatchSentimentProcessor
from config import LIKES_SENTIMENT_THRESHOLDS

# Modify thresholds for a specific campaign
LIKES_SENTIMENT_THRESHOLDS['high']['min'] = 300  # High-engagement platform

processor = BatchSentimentProcessor()
results = processor.process_batch(campaign_data)
```

---

## 🔗 Integration Points

### For Future Social Media Publishers

The system is designed to integrate with social media APIs while maintaining modularity:

#### Integration Pattern

```python
# 1. Fetch engagement data from platform
class TwitterPublisher:
    def fetch_engagement_data(self, post_ids):
        """Fetch text and likes from Twitter API"""
        data = []
        for post_id in post_ids:
            post = twitter_api.get_tweet(post_id)
            data.append({
                'text': post.text,
                'likes': post.favorite_count,
                'post_id': post_id
            })
        return data
    
    def analyze_engagement(self, posts):
        """Analyze engagement using sentiment system"""
        processor = BatchSentimentProcessor()
        results = processor.process_batch(posts)
        
        # Map back to posts
        for i, result in enumerate(results):
            posts[i]['sentiment_analysis'] = result
        
        return posts
    
    def publish_analytics(self, campaign_id, results):
        """Publish results to analytics dashboard"""
        # Extract summary statistics
        avg_sentiment_score = np.mean([
            r['overall_sentiment']['score'] for r in results
        ])
        
        # Send to dashboard
        dashboard_api.update_campaign(
            campaign_id=campaign_id,
            metrics={
                'avg_sentiment_score': avg_sentiment_score,
                'sentiment_distribution': self._get_distribution(results),
                'top_posts': self._get_top_posts(results)
            }
        )
```

#### Extension Points

1. **Custom Text Preprocessing**
   ```python
   from sentiment_analyzer import TextPreprocessor
   
   class CustomPreprocessor(TextPreprocessor):
       @staticmethod
       def preprocess(text):
           # Add platform-specific cleaning
           text = super().preprocess(text)
           # Remove platform-specific tags, emojis, etc.
           return text
   ```

2. **Additional Sentiment Signals**
   ```python
   class ExtendedSentimentAnalyzer(HybridSentimentAnalyzer):
       def analyze_extended(self, text, likes, shares, comments):
           # Incorporate additional engagement metrics
           shares_sentiment = self._map_shares(shares)
           comments_sentiment = self._analyze_comments(comments)
           
           # Combine all signals
           return self._aggregate_all_signals(
               text, likes, shares_sentiment, comments_sentiment
           )
   ```

3. **Platform-Specific Thresholds**
   ```python
   class PlatformThresholds:
       TWITTER = {"high": 500, "medium": 100, "low": 10}
       INSTAGRAM = {"high": 5000, "medium": 1000, "low": 100}
       FACEBOOK = {"high": 1000, "medium": 200, "low": 50}
       
       @classmethod
       def get_for_platform(cls, platform_name):
           return getattr(cls, platform_name.upper(), cls.TWITTER)
   ```

#### API Deployment Pattern

```python
from fastapi import FastAPI
from sentiment_analyzer import HybridSentimentAnalyzer

app = FastAPI()
analyzer = HybridSentimentAnalyzer()

@app.post("/analyze")
def analyze_engagement(text: str = None, likes: int = None):
    """REST endpoint for sentiment analysis"""
    result = analyzer.analyze_hybrid(text, likes)
    return {
        "sentiment": result['overall_sentiment']['sentiment'],
        "confidence": result['overall_sentiment']['confidence'],
        "score": result['overall_sentiment']['score']
    }

@app.post("/analyze_batch")
def analyze_batch(records: List[Dict]):
    """Batch analysis endpoint"""
    from sentiment_analyzer import BatchSentimentProcessor
    processor = BatchSentimentProcessor()
    return processor.process_batch(records)
```

---

## ⚡ Performance Considerations

### Model Loading & Caching

The Streamlit app caches the model using `@st.cache_resource`:

```python
@st.cache_resource
def load_analyzer():
    """Load and cache sentiment analyzer"""
    return HybridSentimentAnalyzer()  # Loaded once per session
```

### Inference Speed

- **First inference**: ~2-5 seconds (model initialization)
- **Subsequent inferences**: ~0.5-1.5 seconds
- **GPU**: ~3-5x faster than CPU

### Memory Usage

- **Model size**: ~500MB (Twitter-RoBERTa)
- **Runtime memory**: ~1-2GB
- **Recommended system RAM**: ≥4GB

### Batch Processing Optimization

For large batches, consider:

```python
# Process in chunks for large datasets
def process_large_batch(records, chunk_size=100):
    processor = BatchSentimentProcessor()
    all_results = []
    
    for i in range(0, len(records), chunk_size):
        chunk = records[i:i+chunk_size]
        results = processor.process_batch(chunk)
        all_results.extend(results)
    
    return all_results
```

---

## 🔧 Troubleshooting

### Issue: Model fails to load
```
Error: "Model not found on huggingface"
```
**Solution:** Check internet connection and ensure model name is correct in `config.py`

### Issue: Out of memory error
```
RuntimeError: CUDA out of memory
```
**Solution:** 
- Switch to CPU: Set `DEVICE = "cpu"` in `config.py`
- Use smaller batches
- Ensure no other GPU processes running

### Issue: Streamlit not starting
```
Error: "module 'streamlit' not found"
```
**Solution:** 
```bash
pip install streamlit==1.28.1
```

### Issue: Slow inference
**Solutions:**
1. Use GPU: Install CUDA-enabled PyTorch
2. Enable batch processing
3. Cache results for repeated queries

### Issue: CSV upload fails
**Solution:**
- Ensure CSV has `text` and/or `likes` columns
- Check for encoding issues (use UTF-8)
- Verify numeric values in likes column

---

## 📞 Support & Contact

For issues or questions:
1. Check `Troubleshooting` section above
2. Review `config.py` comments
3. Run in verbose mode for debugging

---

## 📄 License & Attribution

- **TweetEval Dataset**: Based on Cardiff NLP's TweetEval benchmark
- **Model**: `cardiffnlp/twitter-roberta-base-sentiment-latest`
- **Framework**: Streamlit
- **Purpose**: Academic research and education

---

**Last Updated:** 2025-01-31
**Version:** 1.0
**Python:** 3.8+
