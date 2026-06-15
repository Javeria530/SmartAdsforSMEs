"""Sentiment inference wrapper.

This module tries to load a Hugging Face transformers model from a local path
(`models/roberta-sentiment` by default). If transformers or the model are not
available, the module exposes `MODEL_AVAILABLE = False` and `predict()` will
raise ImportError or return None depending on the runtime situation.

The `predict(text)` function returns a tuple: `(label, score)` where label is
one of 'positive', 'negative', 'neutral' and score is a float where higher
means more positive.
"""
from typing import Tuple

MODEL_AVAILABLE = False
_model = None
_tokenizer = None


def _lazy_load(model_dir: str = None): #perform initilization model
    global MODEL_AVAILABLE, _model, _tokenizer
    if MODEL_AVAILABLE:
        return
    try:
        from transformers import AutoTokenizer, AutoModelForSequenceClassification
        import torch
    except Exception:
        MODEL_AVAILABLE = False
        return

    if model_dir is None:
        import os
        base_dir = os.path.dirname(os.path.abspath(__file__))
        model_dir = os.path.abspath(os.path.join(base_dir, "..", "..", "models", "roberta-sentiment"))

    try:
        _tokenizer = AutoTokenizer.from_pretrained(model_dir)
        _model = AutoModelForSequenceClassification.from_pretrained(model_dir)
        _model.eval()
        MODEL_AVAILABLE = True
    except Exception:
        MODEL_AVAILABLE = False


# Simple TweetEval-style preprocessing (adapted from pasted project)
def _preprocess_text(text: str) -> str:
    if not isinstance(text, str):
        return ""
    new_text = []
    for t in text.split(" "):
        t = '@user' if t.startswith('@') and len(t) > 1 else t
        t = 'http' if t.startswith('http') else t
        new_text.append(t)
    return " ".join(new_text)


def unload():
    """Unload the model from memory."""
    global MODEL_AVAILABLE, _model, _tokenizer
    _model = None
    _tokenizer = None
    MODEL_AVAILABLE = False


def status():
    """Return a dict with model availability and basic info."""
    return {
        "available": MODEL_AVAILABLE,
        "loaded_model": None if _model is None else getattr(_model, "name_or_path", "loaded_model")
    }


def predict(text: str) -> Tuple[str, float]:
    """Return (label, score).

    score is in the range [-1.0, 1.0] (negative to positive).
    """
    if not text:
        return "neutral", 0.0

    if not MODEL_AVAILABLE:
        _lazy_load()
    if not MODEL_AVAILABLE:
        raise ImportError("Local RoBERTa sentiment model not available. Ensure files exist at models/roberta-sentiment")

    import torch
    # Apply tweet-style preprocessing for better TweetEval compatibility
    prepped = _preprocess_text(text)
    inputs = _tokenizer(prepped, return_tensors="pt", truncation=True)
    with torch.no_grad():
        logits = _model(**inputs).logits
        probs = torch.softmax(logits, dim=-1).squeeze().cpu().numpy()

    # Handle common classification outputs:
    # - len(probs) == 1: regression-like
    # - len(probs) == 2: binary [neg, pos]
    # - len(probs) == 3: [neg, neutral, pos] (TweetEval-style)
    import numpy as _np
    if len(probs) == 1:
        score = float(probs[0])
        label = "positive" if score > 0.5 else "negative"
    elif len(probs) == 2:
        neg = float(probs[0])
        pos = float(probs[1])
        score = pos - neg
        label = "positive" if pos > neg else "negative"
    elif len(probs) == 3:
        neg = float(probs[0])
        neu = float(probs[1])
        pos = float(probs[2])
        top = int(_np.argmax(probs))
        label = ["negative", "neutral", "positive"][top]
        score = pos - neg
    else:
        # fallback: choose argmax
        top = int(_np.argmax(probs))
        label = str(top)
        score = float(probs[top])

    # normalize score to -1..1
    norm_score = max(-1.0, min(1.0, score))
    return label, norm_score


# allow manual initialization
def init(model_dir: str = "models/roberta-sentiment"):
    _lazy_load(model_dir)
