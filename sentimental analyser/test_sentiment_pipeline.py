"""
Unit tests for sentiment_pipeline.py.

These tests mock TextSentimentModel.predict so they run with NO network
access and NO downloaded model weights -- they verify the aggregation
logic, likes heuristic, and batch/error-isolation behavior, not the
RoBERTa model's accuracy itself. Model accuracy must be evaluated
separately against a real labeled dataset (see README note on
"Evaluating the underlying model" below) once you have network access
to download cardiffnlp/twitter-roberta-base-sentiment-latest.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sentiment_pipeline import (  # noqa: E402
    PipelineConfig,
    SentimentPipeline,
    TextSentimentModel,
    likes_sentiment,
)


class FakeTextModel(TextSentimentModel):
    """Returns a scripted (label, score, confidence) without touching HF."""

    def __init__(self, scripted_result=("positive", 0.8, 0.9)):
        super().__init__()
        self.available = True
        self._scripted = scripted_result

    def predict(self, text):
        if not text:
            return "neutral", 0.0, 1.0
        return self._scripted


def test_likes_sentiment_below_low_threshold_is_neutral():
    cfg = PipelineConfig()
    label, score = likes_sentiment(0, cfg)
    assert label == "neutral"
    assert score == 0.0


def test_likes_sentiment_above_high_threshold_is_positive():
    cfg = PipelineConfig(likes_high_threshold=50)
    label, score = likes_sentiment(100, cfg)
    assert label == "positive"
    assert score == 1.0


def test_likes_sentiment_interpolates_between_thresholds():
    cfg = PipelineConfig(likes_low_threshold=0, likes_high_threshold=10)
    label, score = likes_sentiment(5, cfg)
    assert 0.0 < score < 1.0


def test_config_normalizes_weights():
    cfg = PipelineConfig(text_weight=3, likes_weight=1)
    assert abs((cfg.text_weight + cfg.likes_weight) - 1.0) < 1e-9
    assert cfg.text_weight == 0.75
    assert cfg.likes_weight == 0.25


def test_pipeline_combines_text_and_likes_positive():
    pipeline = SentimentPipeline(text_model=FakeTextModel(("positive", 0.8, 0.9)))
    result = pipeline.analyze("Great product, loved it!", likes=100)
    assert result.label == "positive"
    assert result.text_label == "positive"
    assert result.likes_label == "positive"
    assert -1.0 <= result.score <= 1.0


def test_pipeline_combines_text_and_likes_negative():
    pipeline = SentimentPipeline(text_model=FakeTextModel(("negative", -0.7, 0.85)))
    result = pipeline.analyze("Terrible experience, broke immediately", likes=0)
    assert result.label == "negative"


def test_pipeline_empty_text_is_neutral():
    pipeline = SentimentPipeline(text_model=FakeTextModel())
    result = pipeline.analyze("", likes=0)
    assert result.text_label == "neutral"
    assert result.text_score == 0.0


def test_batch_isolates_row_errors():
    class FlakyModel(TextSentimentModel):
        def __init__(self):
            super().__init__()
            self.available = True
            self.calls = 0

        def predict(self, text):
            self.calls += 1
            if self.calls == 2:
                raise RuntimeError("simulated row failure")
            return ("positive", 0.5, 0.6)

    pipeline = SentimentPipeline(text_model=FlakyModel())
    rows = [
        {"text": "good", "likes": 5},
        {"text": "bad-row-triggers-error", "likes": 5},
        {"text": "good again", "likes": 5},
    ]
    results = pipeline.analyze_batch(rows)
    assert len(results) == 3
    assert results[0]["error"] is None
    assert results[1]["error"] is not None  # isolated, did not raise
    assert results[2]["error"] is None  # batch continued after the failure


def test_analyze_csv_parses_and_scores_rows():
    pipeline = SentimentPipeline(text_model=FakeTextModel(("neutral", 0.0, 0.5)))
    csv_text = "text,likes\nIt was okay,3\nFine I guess,2\n"
    results = pipeline.analyze_csv(csv_text)
    assert len(results) == 2
    assert all(r["error"] is None for r in results)


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-v"]))
