import sys, os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from backend.data_pipeline.fetch_prices       import run_all as fetch_prices
from backend.data_pipeline.fetch_fundamentals import run_all as fetch_fundamentals
from backend.data_pipeline.compute_indicators import run_all as compute_indicators
from backend.data_pipeline.fetch_news         import run_all as fetch_news
from backend.models.sentiment                 import score_unscored_headlines
from backend.models.features                  import build_feature_matrix
from backend.models.train                     import run_training

def run_pipeline():
    start = datetime.now()
    print(f"=== Stock Analyst Pipeline ===\nStarted: {start.strftime('%Y-%m-%d %H:%M')}\n")
    print("1/7 Prices");       fetch_prices()
    print("\n2/7 Fundamentals"); fetch_fundamentals()
    print("\n3/7 Indicators");   compute_indicators()
    print("\n4/7 News");         fetch_news()
    print("\n5/7 Sentiment");    score_unscored_headlines()
    print("\n6/7 Features")
    df = build_feature_matrix()
    df.to_csv("data/processed/feature_matrix.csv", index=False)
    print("\n7/7 Training");     run_training()
    print(f"\n=== Done in {(datetime.now()-start).seconds}s ===")

if __name__ == "__main__":
    run_pipeline()