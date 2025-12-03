from confluent_kafka import Consumer
import json
import joblib
import xgboost as xgb
import pandas as pd
import os

# --- Load models with correct paths ---
# BASE_DIR = os.getcwd()
# #rf = joblib.load(os.path.join(BASE_DIR, "models", "rf_fraud.pkl"))
# rf = joblib.load("/home/shewa/projects/StreamGuard-Kafka-ML/models/rf_fraud.pkl")
# #xgb_model = xgb.XGBClassifier()
# #xgb_model.load_model(os.path.join(BASE_DIR, "models", "xgb_fraud.json"))
# xgb_model = xgb.XGBClassifier()
# xgb_model.load_model("/home/shewa/projects/StreamGuard-Kafka-ML/models/xgb_fraud.json")

BASE_DIR = os.getcwd()
print("Base directory :", BASE_DIR)
rf = joblib.load(os.path.join(BASE_DIR, "models", "rf_fraud.pkl"))
xgb_model = xgb.XGBClassifier()
xgb_model.load_model(os.path.join(BASE_DIR, "models", "xgb_fraud.json"))

# --- Kafka consumer ---
c = Consumer({
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'fraud-team',
    'auto.offset.reset': 'latest'
})
c.subscribe(['transactions'])

print("Fraud detector LIVE – waiting for transactions...")

while True:
    msg = c.poll(1.0)
    if msg is None:
        continue
    if msg.error():
        continue

    tx = json.loads(msg.value().decode('utf-8'))

    # Build feature DataFrame
    df = pd.DataFrame([{
        "amount": tx["amount"],
        "time_hour": tx["time_hour"],
        "country": tx["country"],
        "category": tx["category"],
        "device": tx["device"]
    }])
    df = pd.get_dummies(df, columns=["country", "category", "device"])

    # Align columns exactly like training
    for col in rf.feature_names_in_:
        if col not in df.columns:
            df[col] = 0
    df = df[rf.feature_names_in_]

    # --- SAFE predict_proba (handles single-class case) ---
    rf_prob = rf.predict_proba(df)[0][1] if rf.predict_proba(df).shape[1] > 1 else 1.0

    xgb_proba = xgb_model.predict_proba(df)
    xgb_prob = xgb_proba[0][1] if xgb_proba.shape[1] > 1 else 1.0

    prob = (rf_prob + xgb_prob) / 2

    if prob >= 0.1:
        print(f"FRAUD → {tx['user_id'][:8]} | ${tx['amount']:.2f} | {prob:.3f} | Country: {tx['country']}")
    else:
        print(f"Clean → ${tx['amount']:.2f} | Prob: {prob:.3f}")
