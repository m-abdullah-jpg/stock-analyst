import sys, os
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch.nn.functional as F

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from backend.utils.database import SessionLocal, NewsHeadline

MODEL_NAME = "ProsusAI/finbert"

class SentimentScorer:
    """
    Wraps FinBERT for financial sentiment scoring.
    Scores: positive=+1, negative=-1, neutral=0 (weighted by probability).
    """
    def __init__(self):
        print("  Loading FinBERT model...", end=" ", flush=True)
        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        self.model     = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
        self.model.eval()
        # Use GPU if available, otherwise CPU
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model.to(self.device)
        print(f"ready (device: {self.device})")

        # FinBERT label order: positive=0, negative=1, neutral=2
        self.label_map = {0: 1.0, 1: -1.0, 2: 0.0}

    def score(self, text: str) -> tuple[float, str]:
        """
        Score a single headline.
        Returns (score, label) where score is -1.0 to +1.0.
        """
        inputs = self.tokenizer(
            text, return_tensors="pt",
            truncation=True, max_length=512,
            padding=True
        ).to(self.device)

        with torch.no_grad():
            logits = self.model(**inputs).logits
            probs  = F.softmax(logits, dim=-1)[0]

        pos, neg, neu = probs[0].item(), probs[1].item(), probs[2].item()

        # Weighted score: positive pulls toward +1, negative toward -1
        score = (pos * 1.0) + (neg * -1.0) + (neu * 0.0)

        # Human-readable label
        if score > 0.15:
            label = "positive"
        elif score < -0.15:
            label = "negative"
        else:
            label = "neutral"

        return round(score, 4), label

    def score_batch(self, texts: list[str]) -> list[tuple[float, str]]:
        """Score a list of headlines efficiently."""
        return [self.score(t) for t in texts]


def score_unscored_headlines(batch_size: int = 32) -> int:
    """Find all headlines with no sentiment score, score them, save back to DB."""
    scorer = SentimentScorer()

    with SessionLocal() as session:
        unscored = session.query(NewsHeadline).filter(
            NewsHeadline.sentiment == None
        ).all()

        if not unscored:
            print("  All headlines already scored.")
            return 0

        print(f"  Scoring {len(unscored)} headlines...")
        updated = 0

        for i in range(0, len(unscored), batch_size):
            batch = unscored[i:i+batch_size]
            for row in batch:
                score, label = scorer.score(row.headline)
                row.sentiment = score
                updated += 1

            session.commit()
            print(f"    {min(i+batch_size, len(unscored))}/{len(unscored)} scored...", end="\r")

        print(f"\n  Done. {updated} headlines scored.")
        return updated

if __name__ == "__main__":
    print("Running FinBERT sentiment scorer...")
    score_unscored_headlines()
