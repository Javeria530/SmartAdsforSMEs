"""
sentiment_pipeline.py
----------------------
Core sentiment analysis engine for the SmartAds engagement-feedback module.

Combines two signals into one hybrid sentiment score:
  1. Text sentiment  - cardiffnlp/twitter-roberta-base-sentiment-latest
                        (the TweetEval-trained RoBERTa model already used
                        by backend/services/sentiment_service.py)
  2. Likes sentiment - a simple rule-based mapping from engagement counts
                        to a sentiment signal (more likes -> more positive)

The two signals are combined with a configurable weighted average
(default: 75% text, 25% likes), matching the ratio referenced in the
project's PHASE2_SUMMARY.md.

This module intentionally has NO network calls at import time -- the
HuggingFace model is lazy-loaded on first use, exactly like
backend/services/sentiment_service.py, so importing this file (e.g. for
unit tests with a mocked model) never requires internet access.
"""
from __future__ import annotations

import csv
import io
import logging
from dataclasses import dataclass, field
from typing import Iterable, List, Optional, Tuple

logger = logging.getLogger(__name__)

DEFAULT_MODEL_NAME = "cardiffnlp/twitter-roberta-base-sentiment-latest"
LABELS = ("negative", "neutral", "positive")


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

@dataclass
class PipelineConfig:
    """Runtime-adjustable parameters (mirrors the sidebar sliders in app.py)."""

    model_name: str = DEFAULT_MODEL_NAME
    text_weight: float = 0.75
    likes_weight: float = 0.25
    # Likes thresholds: counts >= high_threshold are treated as strongly
    # positive engagement, counts <= low_threshold as weak/no engagement.
    likes_low_threshold: int = 1
    likes_high_threshold: int = 50

    def __post_init__(self) -> None:
        total = self.text_weight + self.likes_weight
        if total <= 0:
            raise ValueError("text_weight + likes_weight must be > 0")
        # normalize so weights always sum to 1.0
        self.text_weight /= total
        self.likes_weight /= total


@dataclass
class SentimentResult:
    label: str
    score: float  # normalized -1.0 (negative) .. 1.0 (positive)
    text_label: str
    text_score: float
    likes_label: str
    likes_score: float
    confidence: float


# ---------------------------------------------------------------------------
# Text sentiment (lazy-loaded HF model)
# ---------------------------------------------------------------------------

class TextSentimentModel:
    """Thin wrapper around the TweetEval RoBERTa sentiment model.

    Mirrors backend/services/sentiment_service.py's lazy-load pattern so
    the two modules can eventually be unified instead of duplicated.
    """

    def __init__(self, model_name: str = DEFAULT_MODEL_NAME):
        self.model_name = model_name
        self._tokenizer = None
        self._model = None
        self.available = False

    def load(self) -> None:
        if self.available:
            return
        try:
            from transformers import AutoTokenizer, AutoModelForSequenceClassification
        except ImportError as exc:
            raise ImportError(
                "transformers is required for TextSentimentModel. "
                "Install with: pip install transformers torch"
            ) from exc

        self._tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self._model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
        self._model.eval()
        self.available = True

    @staticmethod
    def preprocess(text: str) -> str:
        """TweetEval-style normalization: anonymize @mentions and links."""
        if not isinstance(text, str):
            return ""
        tokens = []
        for tok in text.split(" "):
            if tok.startswith("@") and len(tok) > 1:
                tok = "@user"
            elif tok.startswith("http"):
                tok = "http"
            tokens.append(tok)
        return " ".join(tokens)

    def predict(self, text: str) -> Tuple[str, float, float]:
        """Return (label, score in [-1, 1], confidence in [0, 1])."""
        if not text:
            return "neutral", 0.0, 1.0

        if not self.available:
            self.load()

        import torch

        prepped = self.preprocess(text)
        inputs = self._tokenizer(prepped, return_tensors="pt", truncation=True)
        with torch.no_grad():
            logits = self._model(**inputs).logits
            probs = torch.softmax(logits, dim=-1).squeeze().tolist()

        if isinstance(probs, float):
            probs = [probs]

        if len(probs) == 3:
            neg, neu, pos = probs
        elif len(probs) == 2:
            neg, pos = probs
            neu = 0.0
        else:
            # Fall back to argmax over whatever the model returns
            top = max(range(len(probs)), key=lambda i: probs[i])
            label = LABELS[min(top, len(LABELS) - 1)]
            return label, float(probs[top]) * 2 - 1, float(probs[top])

        label = LABELS[max(range(3), key=lambda i: (neg, neu, pos)[i])]
        score = max(-1.0, min(1.0, pos - neg))
        confidence = max(neg, neu, pos)
        return label, score, float(confidence)


# ---------------------------------------------------------------------------
# Likes-based rule sentiment
# ---------------------------------------------------------------------------

def likes_sentiment(likes: int, config: PipelineConfig) -> Tuple[str, float]:
    """Map an engagement (likes) count to a coarse sentiment signal.

    This is explicitly a heuristic, not a learned model: likes are a proxy
    for positive reception, not a measurement of it. It should be reported
    in a paper as a simple weighted heuristic, not as a classifier.
    """
    try:
        likes = int(likes)
    except (TypeError, ValueError):
        return "neutral", 0.0

    if likes <= config.likes_low_threshold:
        return "neutral", 0.0
    if likes >= config.likes_high_threshold:
        return "positive", 1.0
    # linear interpolation between thresholds
    span = config.likes_high_threshold - config.likes_low_threshold
    frac = (likes - config.likes_low_threshold) / span
    return ("positive" if frac >= 0.5 else "neutral"), round(frac, 4)


# ---------------------------------------------------------------------------
# Hybrid aggregation
# ---------------------------------------------------------------------------

class SentimentPipeline:
    def __init__(self, config: Optional[PipelineConfig] = None,
                 text_model: Optional[TextSentimentModel] = None):
        self.config = config or PipelineConfig()
        self.text_model = text_model or TextSentimentModel(self.config.model_name)

    def analyze(self, text: str, likes: int = 0) -> SentimentResult:
        text_label, text_score, confidence = self.text_model.predict(text)
        likes_label, likes_score = likes_sentiment(likes, self.config)

        combined_score = (
            self.config.text_weight * text_score
            + self.config.likes_weight * likes_score
        )
        combined_score = max(-1.0, min(1.0, combined_score))

        if combined_score > 0.15:
            combined_label = "positive"
        elif combined_score < -0.15:
            combined_label = "negative"
        else:
            combined_label = "neutral"

        return SentimentResult(
            label=combined_label,
            score=round(combined_score, 4),
            text_label=text_label,
            text_score=round(text_score, 4),
            likes_label=likes_label,
            likes_score=round(likes_score, 4),
            confidence=round(confidence, 4),
        )

    def analyze_batch(self, rows: Iterable[dict]) -> List[dict]:
        """rows: iterable of {"text": str, "likes": int, ...}. Errors on a
        single row are isolated (recorded, not raised) so one bad row
        doesn't fail the whole batch."""
        results = []
        for i, row in enumerate(rows):
            text = row.get("text", "")
            likes = row.get("likes", 0)
            try:
                r = self.analyze(text, likes)
                results.append({**row, **r.__dict__, "row_index": i, "error": None})
            except Exception as exc:  # noqa: BLE001 - intentional error isolation
                logger.exception("Row %s failed sentiment analysis", i)
                results.append({**row, "row_index": i, "error": str(exc)})
        return results

    def analyze_csv(self, csv_text: str) -> List[dict]:
        reader = csv.DictReader(io.StringIO(csv_text))
        return self.analyze_batch(reader)
