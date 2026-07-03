"""
evaluation_script.py
---------------------
Computes REAL accuracy / precision / recall / F1 of the sentiment model
against the official TweetEval sentiment test set already included in
datasets/sentiment/.

IMPORTANT - read this before you put any number from this script into
your paper:

  This script does NOT run inside Claude's sandbox, because downloading
  cardiffnlp/twitter-roberta-base-sentiment-latest requires network
  access to huggingface.co, which the sandbox cannot reach. You must
  run this yourself, once, on a machine with internet access:

      cd "sentimental analyser"
      pip install -r requirements.txt
      python evaluation_script.py

  It will print a real classification report and save results to
  evaluation_results.json. Copy those numbers -- not invented ones --
  into your paper's Results section. This is the difference between a
  legitimate evaluation and a fabricated one.
"""
import json
import sys
import time
from pathlib import Path

from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
)

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sentiment_pipeline import TextSentimentModel  # noqa: E402

DATASET_DIR = Path(__file__).resolve().parent / "datasets" / "sentiment"
LABEL_NAMES = {0: "negative", 1: "neutral", 2: "positive"}


def load_tweeteval_test_split():
    text_path = DATASET_DIR / "test_text.txt"
    label_path = DATASET_DIR / "test_labels.txt"
    if not text_path.exists() or not label_path.exists():
        raise FileNotFoundError(
            f"Expected {text_path} and {label_path}. "
            "Make sure the datasets/ folder from the repo is intact."
        )
    texts = text_path.read_text(encoding="utf-8").splitlines()
    labels = [int(x) for x in label_path.read_text(encoding="utf-8").splitlines()]
    if len(texts) != len(labels):
        raise ValueError(
            f"Mismatched lengths: {len(texts)} texts vs {len(labels)} labels"
        )
    return texts, labels


def main(limit: int = None):
    print("Loading TweetEval sentiment test split...")
    texts, gold_labels = load_tweeteval_test_split()
    if limit:
        texts, gold_labels = texts[:limit], gold_labels[:limit]
    print(f"Loaded {len(texts)} labeled test examples.")

    print("Loading model (requires internet on first run)...")
    model = TextSentimentModel()
    model.load()

    label_to_idx = {"negative": 0, "neutral": 1, "positive": 2}
    predictions = []
    start = time.time()
    for i, text in enumerate(texts):
        label, _score, _conf = model.predict(text)
        predictions.append(label_to_idx[label])
        if (i + 1) % 200 == 0:
            print(f"  ...{i + 1}/{len(texts)}")
    elapsed = time.time() - start

    acc = accuracy_score(gold_labels, predictions)
    macro_f1 = f1_score(gold_labels, predictions, average="macro")
    report = classification_report(
        gold_labels, predictions,
        target_names=[LABEL_NAMES[i] for i in range(3)],
        output_dict=True,
    )
    cm = confusion_matrix(gold_labels, predictions).tolist()

    print("\n=== RESULTS (real, computed on TweetEval test set) ===")
    print(f"Examples evaluated : {len(texts)}")
    print(f"Accuracy           : {acc:.4f}")
    print(f"Macro F1           : {macro_f1:.4f}")
    print(f"Total inference time: {elapsed:.1f}s "
          f"({elapsed / len(texts) * 1000:.1f} ms/example)")
    print("\nPer-class report:")
    print(classification_report(
        gold_labels, predictions,
        target_names=[LABEL_NAMES[i] for i in range(3)],
    ))

    out = {
        "n_examples": len(texts),
        "accuracy": acc,
        "macro_f1": macro_f1,
        "classification_report": report,
        "confusion_matrix": cm,
        "labels_order": ["negative", "neutral", "positive"],
        "total_inference_seconds": elapsed,
        "ms_per_example": elapsed / len(texts) * 1000,
    }
    out_path = Path(__file__).resolve().parent / "evaluation_results.json"
    out_path.write_text(json.dumps(out, indent=2))
    print(f"\nSaved full results to {out_path}")


if __name__ == "__main__":
    # Pass a small --limit while iterating so you don't wait on the full
    # ~12k-example test set every run, e.g.: python evaluation_script.py 200
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else None
    main(limit=limit)
