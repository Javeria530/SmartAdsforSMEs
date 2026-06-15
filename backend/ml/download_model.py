"""Download a Hugging Face model and save it to `backend/models/roberta-sentiment`.

Usage:
  python download_model.py --model_id cardiffnlp/twitter-roberta-base-sentiment-latest
"""
import argparse
import os

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_id", default="cardiffnlp/twitter-roberta-base-sentiment-latest")
    parser.add_argument("--output_dir", default=os.path.join("..", "models", "roberta-sentiment"))
    args = parser.parse_args()

    model_id = args.model_id
    outdir = os.path.abspath(args.output_dir)
    os.makedirs(outdir, exist_ok=True)

    print(f"Downloading model {model_id} to {outdir} ...")
    try:
        from transformers import AutoTokenizer, AutoModelForSequenceClassification
        tokenizer = AutoTokenizer.from_pretrained(model_id)
        model = AutoModelForSequenceClassification.from_pretrained(model_id)

        tokenizer.save_pretrained(outdir)
        model.save_pretrained(outdir)
        print("Model saved to", outdir)
    except Exception as e:
        print("Failed to download/save model:", e)

if __name__ == '__main__':
    main()
