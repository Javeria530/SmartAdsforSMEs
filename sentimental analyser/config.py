"""
Configuration file for sentiment analysis thresholds and model settings.
This file contains all configurable parameters for the hybrid sentiment analysis system.
"""

# ============================================================================
# TEXT SENTIMENT MODEL CONFIGURATION
# ============================================================================

# Pretrained transformer model from Hugging Face
# Options: 
#   - "cardiffnlp/twitter-roberta-base-sentiment-latest" (Twitter-specific, recommended)
#   - "distilbert-base-uncased-finetuned-sst-2-english" (General, faster)
#   - "cardiffnlp/twitter-roberta-base" (Feature extraction model)
TEXT_SENTIMENT_MODEL = "cardiffnlp/twitter-roberta-base-sentiment-latest"

# Device for inference ('cpu' or 'cuda')
DEVICE = "cpu"

# ============================================================================
# LIKES SENTIMENT MAPPING - RULE-BASED THRESHOLDS
# ============================================================================
# These thresholds convert numeric likes into sentiment categories
# Adjust these based on your application context (e.g., average likes per post)

LIKES_SENTIMENT_THRESHOLDS = {
    "high": {
        "min": 100,        # Likes >= 100 are considered HIGH (Positive)
        "sentiment": "Positive",
        "confidence": 0.95
    },
    "medium": {
        "min": 20,         # Likes >= 20 and < 100 are considered MEDIUM (Neutral)
        "max": 100,
        "sentiment": "Neutral",
        "confidence": 0.75
    },
    "low": {
        "max": 20,         # Likes < 20 are considered LOW (Negative)
        "sentiment": "Negative",
        "confidence": 0.60
    }
}

# ============================================================================
# HYBRID SENTIMENT WEIGHTS
# ============================================================================
# Controls the importance of text vs likes in final sentiment calculation
# Weights must sum to 1.0

SENTIMENT_WEIGHTS = {
    "text": 0.75,        # Text sentiment has 75% weight
    "likes": 0.25        # Likes sentiment has 25% weight
}

# Confidence score threshold for model predictions
# Predictions below this threshold are marked as "Low Confidence"
MIN_CONFIDENCE_THRESHOLD = 0.50

# ============================================================================
# SENTIMENT MAPPING & LABELS
# ============================================================================

SENTIMENT_LABELS = {
    0: "Negative",
    1: "Neutral",
    2: "Positive"
}

# Reverse mapping for processing
SENTIMENT_TO_IDX = {v: k for k, v in SENTIMENT_LABELS.items()}

# Color coding for visualizations
SENTIMENT_COLORS = {
    "Positive": "#2ecc71",   # Green
    "Neutral": "#f39c12",    # Orange
    "Negative": "#e74c3c"    # Red
}

# ============================================================================
# ANALYTICS & DISPLAY CONFIGURATION
# ============================================================================

# Number of top engagement posts to display
TOP_ENGAGEMENT_COUNT = 10

# Decimal precision for confidence scores
CONFIDENCE_DECIMAL_PLACES = 2

# ============================================================================
# TEXT PREPROCESSING
# ============================================================================

def preprocess_text(text):
    """
    Normalize tweet text to match TweetEval preprocessing standards.
    
    Args:
        text (str): Raw text input
        
    Returns:
        str: Preprocessed text
    """
    new_text = []
    for t in text.split(" "):
        t = '@user' if t.startswith('@') and len(t) > 1 else t
        t = 'http' if t.startswith('http') else t
        new_text.append(t)
    return " ".join(new_text)
