# dashboard/app.py
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn
import json
from confluent_kafka import Consumer
import threading
import pandas as pd
import joblib
import xgboost as xgb
import os

app = FastAPI(title="StreamGuard – Live Fraud Detection")

# Shared state
stats = {"total": 0, "frauds": 0, "clean": 0, "recent_frauds": []}

# Load models
BASE_DIR = os.getcwd()
print("Base directory :", BASE_DIR)
rf = joblib.load(os.path.join(BASE_DIR, "models", "rf_fraud.pkl"))
xgb_model = xgb.XGBClassifier()
xgb_model.load_model(os.path.join(BASE_DIR, "models", "xgb_fraud.json"))

def kafka_consumer_loop():
    c = Consumer({'bootstrap.servers': 'localhost:9092', 'group.id': 'dashboard-group', 'auto.offset.reset': 'latest'})
    c.subscribe(['transactions'])
    while True:
        msg = c.poll(0.1)
        if msg and not msg.error():
            tx = json.loads(msg.value().decode())
            df = pd.DataFrame([{k: tx.get(k) for k in ["amount","time_hour","country","category","device"]}])
            df = pd.get_dummies(df, columns=["country","category","device"])
            for col in rf.feature_names_in_:
                if col not in df.columns: df[col] = 0
            df = df[rf.feature_names_in_]

            rf_prob = rf.predict_proba(df)[0][1] if rf.predict_proba(df).shape[1] > 1 else 0.0
            xgb_prob = xgb_model.predict_proba(df)[0][1] if xgb_model.predict_proba(df).shape[1] > 1 else 0.0
            prob = (rf_prob + xgb_prob) / 2

            stats["total"] += 1
            if prob >=0.1:
                stats["frauds"] += 1
                fraud = {**tx, "prob": round(prob, 3), "country": tx["country"]}
                stats["recent_frauds"].append(fraud)
                if len(stats["recent_frauds"]) > 10:
                    stats["recent_frauds"].pop(0)
            else:
                stats["clean"] += 1

# Start consumer in background
threading.Thread(target=kafka_consumer_loop, daemon=True).start()

@app.get("/", response_class=HTMLResponse)
async def home():
    fraud_rate = stats["frauds"] / max(stats["total"], 1) * 100
    return f"""
    <html>
        <head>
            <title>StreamGuard – Live Fraud Detection</title>
            <meta http-equiv="refresh" content="2">
            <style>
                body {{ font-family: 'Segoe UI', sans-serif; background: #0f1620; color: #00ff9d; text-align: center; padding: 20px; }}
                .card {{ background: #1a2332; padding: 20px; margin: 20px auto; border-radius: 15px; max-width: 900px; box-shadow: 0 0 20px #00ff9d33; }}
                .big {{ font-size: 4em; margin: 10px; }}
                .fraud {{ color: #ff3366; }}
                .recent {{ background: #2a3444; padding: 15px; border-radius: 10px; text-align: left; margin: 20px; }}
                h1 {{ text-shadow: 0 0 10px #00ff9d; }}
            </style>
        </head>
        <body>
            <h1>StreamGuard – Real-time Fraud Detection</h1>
            <div class="card">
                <h2>Live Stats</h2>
                <div class="big">{stats["total"]:,}</div> Total Transactions<br>
                <div class="big fraud">{stats["frauds"]:,}</div> Frauds Detected<br>
                <div class="big">{stats["clean"]:,}</div> Clean<br><br>
                <h2>Fraud Rate: <span class="fraud">{fraud_rate:.3f}%</span></h2>
            </div>
            <div class="card recent">
                <h2>Latest Fraud Alerts</h2>
                {''.join([f"<p><b>FRAUD</b> ${f['amount']:.2f} from {f['country']} (Prob: {f['prob']}) – {f['user_id'][:8]}</p>" for f in stats["recent_frauds"]])}
                { "<p>No frauds yet – waiting...</p>" if not stats["recent_frauds"] else "" }
            </div>
            <footer>Powered by Kafka + XGBoost + Random Forest | 1.5M training records</footer>
        </body>
    </html>
    """

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
