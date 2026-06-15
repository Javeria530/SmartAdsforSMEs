# Technical Architecture & Implementation Details

## System Design

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Streamlit UI Layer                          │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ • Manual Input Mode • CSV Upload • Batch Analysis       │   │
│  │ • Analytics Dashboard • Configuration Panel             │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────┬───────────────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────────────┐
│              Sentiment Analysis Layer                           │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────────┐    │
│  │   Text       │  │   Likes      │  │   Hybrid          │    │
│  │ Sentiment    │  │ Sentiment    │  │ Aggregation       │    │
│  │ Analyzer     │  │ Mapper       │  │ Module            │    │
│  └──────────────┘  └──────────────┘  └───────────────────┘    │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ Batch Processor (orchestrates above modules)           │    │
│  └────────────────────────────────────────────────────────┘    │
└─────────────────┬───────────────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────────────┐
│              Data Processing Layer                              │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────────┐    │
│  │ Text         │  │ CSV          │  │ Result            │    │
│  │ Preprocessor │  │ Parser       │  │ Formatter         │    │
│  └──────────────┘  └──────────────┘  └───────────────────┘    │
└─────────────────┬───────────────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────────────┐
│              External Dependencies                              │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ • Transformers Library (HuggingFace)                    │  │
│  │ • PyTorch/TensorFlow (Model Inference)                  │  │
│  │ • Pandas (Data Handling)                                │  │
│  │ • Matplotlib/Seaborn (Visualization)                    │  │
│  └──────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
```

---

## Module Deep Dive

### 1. Configuration Module (`config.py`)

**Responsibility:** Centralized configuration management

**Key Variables:**
- `TEXT_SENTIMENT_MODEL`: HuggingFace model identifier
- `DEVICE`: Inference device (cpu/cuda)
- `LIKES_SENTIMENT_THRESHOLDS`: Rule thresholds
- `SENTIMENT_WEIGHTS`: Weighting factors
- `SENTIMENT_LABELS`: Label mappings

**Design Pattern:** Single source of truth for all configuration

```python
# Architecture benefit: Change one file to affect entire system
# No hardcoded values scattered throughout codebase
```

---

### 2. Text Preprocessing (`TextPreprocessor`)

**Purpose:** Normalize text according to TweetEval standards

**Algorithm:**

```
Input: "Check @john and http://example.com great job!"

Step 1: Split by spaces
        ["Check", "@john", "and", "http://example.com", "great", "job!"]

Step 2: For each token:
        - If starts with '@' and len > 1 → replace with '@user'
        - If starts with 'http' → replace with 'http'
        - Otherwise → keep as-is

Step 3: Rejoin with spaces
Output: "Check @user and http great job!"
```

**Validation Rules:**
- Text must be non-empty
- Text must be ≤ 5000 characters
- Input must be string type

**Rationale:** TweetEval models were trained on this preprocessed format

---

### 3. Text Sentiment Analyzer (`TextSentimentAnalyzer`)

**Purpose:** Classify text into sentiment categories

**Model Details:**
- **Architecture:** RoBERTa (Robustly Optimized BERT)
- **Training Data:** Twitter/X posts (TweetEval dataset)
- **Labels:** Positive, Neutral, Negative
- **Output:** Confidence scores for each label

**Loading Process:**

```python
1. Initialize pipeline("sentiment-analysis", model=model_name)
2. Download model on first use (~500MB)
3. Cache for subsequent uses
4. Use GPU if available (else CPU)
```

**Inference Process:**

```python
1. Preprocess input text
2. Tokenize using model's tokenizer
3. Forward pass through model
4. Convert logits to probabilities (softmax)
5. Extract top-k predictions
6. Parse and normalize output format
```

**Output Structure:**
```python
{
    'sentiment': 'Positive',           # Most likely label
    'confidence': 0.92,                # Max probability
    'raw_scores': {                    # All label scores
        'positive': 0.92,
        'neutral': 0.05,
        'negative': 0.03
    },
    'original_text': '...',
    'preprocessed_text': '...'
}
```

**Performance:**
- First inference: ~2-5s (includes model load)
- Subsequent: ~0.5-1.5s
- GPU: ~3-5x faster

---

### 4. Likes Sentiment Mapper (`LikesSentimentMapper`)

**Purpose:** Convert numeric likes to sentiment categories

**Algorithm:**

```python
def map_likes_to_sentiment(likes):
    if likes >= THRESHOLD_HIGH:
        return {sentiment: 'Positive', confidence: 0.95}
    elif likes >= THRESHOLD_MEDIUM:
        return {sentiment: 'Neutral', confidence: 0.75}
    else:
        return {sentiment: 'Negative', confidence: 0.60}
```

**Threshold Logic:**

```
Likes Count Distribution Example:
  0-19 likes  → Negative (Low engagement)
  20-99       → Neutral (Medium engagement)
  100+        → Positive (High engagement)

Confidence Rationale:
  High confidence (0.95) for high likes = clear signal
  Medium confidence (0.75) for medium = ambiguous
  Lower confidence (0.60) for low = could be just unpopular
```

**Customization Example:**

```python
# For platform with different engagement patterns
LIKES_SENTIMENT_THRESHOLDS = {
    "high": {"min": 500, "confidence": 0.95},    # Higher threshold
    "medium": {"min": 100, "confidence": 0.75},
    "low": {"max": 100, "confidence": 0.60}
}
```

---

### 5. Hybrid Sentiment Analyzer (`HybridSentimentAnalyzer`)

**Purpose:** Combine text and likes sentiments intelligently

**Core Algorithm:**

```python
def aggregate_sentiments(text_result, likes_result, weights):
    # Step 1: Convert sentiments to numeric scores
    text_score = sentiment_to_score(text_result['sentiment'])
    likes_score = sentiment_to_score(likes_result['sentiment'])
    
    # Step 2: Apply weights
    weighted_text = text_score * weights['text']      # 0.75
    weighted_likes = likes_score * weights['likes']    # 0.25
    
    # Step 3: Average weighted scores
    final_score = weighted_text + weighted_likes
    
    # Step 4: Convert back to sentiment label
    final_sentiment = score_to_sentiment(final_score)
    
    # Step 5: Calculate confidence
    final_confidence = (
        text_result['confidence'] * weights['text'] +
        likes_result['confidence'] * weights['likes']
    )
    
    return {
        'sentiment': final_sentiment,
        'confidence': final_confidence,
        'score': final_score
    }
```

**Score Mapping:**

```python
SENTIMENT_SCORES = {
    'Negative': 0.0,    # Lowest engagement
    'Neutral': 0.5,     # Medium engagement
    'Positive': 1.0     # Highest engagement
}

SCORE_TO_SENTIMENT = {
    (0.00, 0.33): 'Negative',
    (0.33, 0.67): 'Neutral',
    (0.67, 1.00): 'Positive'
}
```

**Weighted Aggregation Example:**

```
Scenario: Text="Positive" (0.92 conf), Likes="Neutral" (0.75 conf)

text_score = 1.0 × 0.75 = 0.75
likes_score = 0.5 × 0.25 = 0.125
final_score = 0.75 + 0.125 = 0.875

0.875 is in range (0.67, 1.00) → 'Positive'

confidence = (0.92 × 0.75) + (0.75 × 0.25) = 0.8775
```

**Design Rationale:**
- Text weight (75%) > Likes weight (25%)
- Text comes from sophisticated ML model
- Likes are platform/algorithm dependent
- Weighting ensures text is primary signal while likes provide context

---

### 6. Batch Processor (`BatchSentimentProcessor`)

**Purpose:** Efficiently process multiple records

**Architecture:**

```python
class BatchSentimentProcessor:
    def process_batch(records):
        results = []
        for idx, record in enumerate(records):
            try:
                result = analyzer.analyze_hybrid(
                    text=record.get('text'),
                    likes=record.get('likes')
                )
                result['record_index'] = idx
                results.append(result)
            except Exception as e:
                # Gracefully handle errors per-record
                results.append({
                    'record_index': idx,
                    'error': str(e),
                    'overall_sentiment': {'sentiment': 'Neutral', 'confidence': 0.0}
                })
        return results
```

**Error Handling Strategy:**
- Process continues even if individual record fails
- Each result includes record index for mapping back
- Errors are logged but don't halt batch processing

**Performance Optimization:**
- Sequential processing (could be parallelized with GPU)
- Minimal memory footprint per record
- Cache model between records

---

## Data Flow Examples

### Example 1: Manual Text + Likes Input

```
User Input:
  text = "Absolutely love this!"
  likes = 250

Flow:
  1. Streamlit UI (app.py) receives input
  2. Calls analyzer.analyze_hybrid(text, likes)
  3. HybridSentimentAnalyzer.analyze_hybrid() processes:
     a) TextSentimentAnalyzer.analyze(text)
        - TextPreprocessor.preprocess(text)
        - Model inference via Transformers pipeline
        - Returns {sentiment: 'Positive', confidence: 0.95, ...}
     
     b) LikesSentimentMapper.map_likes_to_sentiment(likes)
        - Applies thresholds
        - Returns {sentiment: 'Positive', confidence: 0.95, ...}
     
     c) HybridSentimentAnalyzer._aggregate_sentiments()
        - Converts to scores: text=1.0, likes=1.0
        - Applies weights: 1.0×0.75 + 1.0×0.25 = 1.0
        - Final sentiment: 'Positive', score: 1.0, confidence: 0.95
  
  4. Generate engagement_summary
  5. Return complete result dictionary
  6. Streamlit UI displays result with badges and charts
```

### Example 2: CSV Batch Processing

```
CSV File:
  text,likes
  "Great product",150
  "Not satisfied",25
  "Could be better",75

Flow:
  1. Read CSV using pandas
  2. Validate columns (has 'text' and/or 'likes')
  3. Convert to records list
  4. BatchSentimentProcessor.process_batch(records)
     - For each record:
       a) Extract text and likes
       b) Call HybridSentimentAnalyzer.analyze_hybrid()
       c) Append result with record_index
  5. Convert results to DataFrame
  6. Display table and charts
  7. Export to CSV with results
```

---

## Caching Strategy

### Streamlit Caching

```python
@st.cache_resource  # Cached per session
def load_analyzer():
    """Loads model once per Streamlit session"""
    return HybridSentimentAnalyzer()

# Benefits:
# - Model loaded only once
# - Reused across multiple analyses
# - Cleared only on app restart
# - Significantly improves UX
```

### Model Caching

```python
# HuggingFace caches downloaded models in:
# Windows: %USERPROFILE%\.cache\huggingface\hub
# Linux: ~/.cache/huggingface/hub

# First run: Downloads ~500MB
# Subsequent runs: Loads from cache (~1-2 seconds)
```

---

## Error Handling

### Multi-Level Error Handling

```python
# Level 1: Input Validation
if not text.strip():
    return {sentiment: 'Neutral', error: 'Empty text'}

# Level 2: Processing Error Catch
try:
    result = model.predict(text)
except ModelError as e:
    return {sentiment: 'Neutral', error: str(e)}

# Level 3: Batch Error Isolation
for record in records:
    try:
        result = process(record)
    except:
        results.append({error: '...', sentiment: 'Neutral'})
        continue  # Continue processing other records
```

---

## Integration Architecture

### Extension Points

1. **Custom Model Integration**
   ```python
   class CustomSentimentAnalyzer(TextSentimentAnalyzer):
       def analyze(self, text):
           # Use custom model instead
           return custom_model.predict(text)
   ```

2. **Additional Signals**
   ```python
   class MultiSignalAnalyzer(HybridSentimentAnalyzer):
       def analyze_extended(self, text, likes, shares, comments):
           # Add more signals to aggregation
   ```

3. **Platform Integration**
   ```python
   class TwitterIntegration:
       def fetch_and_analyze(self, post_ids):
           posts = twitter_api.get_posts(post_ids)
           analyzer = HybridSentimentAnalyzer()
           results = [analyzer.analyze_hybrid(
               text=post.text, likes=post.likes
           ) for post in posts]
   ```

---

## Performance Profiling

### Typical Latency Breakdown

```
Single Text+Likes Analysis:
├─ Text Preprocessing:      5ms
├─ Text Tokenization:       50ms
├─ Model Inference:         800ms (CPU) / 150ms (GPU)
├─ Likes Mapping:           1ms
├─ Aggregation:             5ms
└─ Total:                   ~860ms (CPU) / ~210ms (GPU)

Batch of 100 records:
├─ Model Loading:           2000ms (first run)
├─ Analysis:                86000ms (CPU) or 21000ms (GPU)
├─ CSV Generation:          500ms
└─ Total:                   ~88500ms (CPU) / ~23500ms (GPU)
```

### Optimization Opportunities

1. **GPU Acceleration**: 3-5x faster inference
2. **Batch Inference**: Process multiple texts at once
3. **Model Quantization**: Smaller, faster model
4. **Async Processing**: Non-blocking Streamlit UI

---

## Testing & Validation

### Unit Test Examples

```python
# Test text preprocessing
assert preprocess("@user http://example.com") == "@user http"

# Test sentiment mapping
assert mapper.map_likes_to_sentiment(150)['sentiment'] == 'Positive'

# Test score conversion
assert score_to_sentiment(0.9) == 'Positive'
assert score_to_sentiment(0.4) == 'Neutral'
assert score_to_sentiment(0.1) == 'Negative'

# Test aggregation
result = analyzer._aggregate_sentiments(
    {'sentiment': 'Positive', 'confidence': 1.0},
    {'sentiment': 'Positive', 'confidence': 1.0}
)
assert result['sentiment'] == 'Positive'
```

---

## Future Enhancements

1. **Multi-Language Support**: Add translation + analysis
2. **Real-Time Updates**: WebSocket integration
3. **Custom Model Training**: Fine-tune on domain-specific data
4. **Explainability**: LIME/SHAP for model interpretation
5. **A/B Testing**: Compare different weighting strategies
6. **Real Publisher APIs**: Twitter/Instagram/TikTok integration

---

**Document Version:** 1.0
**Last Updated:** 2025-01-31
