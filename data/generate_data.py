# data/generate_data.py — FINAL (1.5M + ~15,000 frauds)
# data/generate_data.py — FINAL DEMO VERSION (1,000 tx, ~100 frauds)
import pandas as pd
import numpy as np
import random
from faker import Faker
import os

fake = Faker()
random.seed(42)
np.random.seed(42)

def generate(n=1_000, target_frauds=100):
    print(f"Generating {n:,} transactions → targeting ~{target_frauds} frauds (10%)...")
    data = []
    frauds_injected = 0

    for i in range(n):
        # Default: normal transaction
        amount = round(np.random.exponential(70), 2)
        hour = random.randint(0, 23)
        country = random.choice(["US", "GB", "DE", "CA", "AU", "JP", "FR", "IN"])

        # Inject fraud when needed
        if frauds_injected < target_frauds and random.random() < 0.6:
            amount = round(random.uniform(980, 6800), 2)
            hour = random.choice([1, 2, 3, 4, 5])
            country = random.choice(["CN", "RU", "NG", "RO", "UA", "ID", "BR", "VE"])
            frauds_injected += 1

        data.append({
            "user_id": fake.uuid4(),
            "amount": amount,
            "merchant": fake.company(),
            "country": country,
            "category": random.choice(["grocery", "travel", "online", "luxury", "gas", "crypto"]),
            "time_hour": hour,
            "device": random.choice(["mobile", "desktop", "tablet"]),
            "timestamp": fake.date_time_this_year().isoformat()
        })

    df = pd.DataFrame(data)
    df['is_fraud'] = df.apply(
        lambda r: 1 if (r.amount > 900 and r.time_hour < 6 and r.country not in ["US","GB","DE","CA","AU","JP","FR"])
                  or r.amount > 5000
        else 0, axis=1)

    actual = df['is_fraud'].sum()
    print(f"DONE! {n:,} transactions → {actual} frauds ({actual/n*100:.1f}%) — PERFECT DEMO!")
    return df

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    df = generate(1_000, 100)
    BASE_DIR = os.getcwd()
    print("Base directory :", BASE_DIR ,"\n",os.path.join(BASE_DIR, "data","transactions.csv"))
    df.to_csv(os.path.join(BASE_DIR, "data","transactions.csv"), index=False)
    print("Saved → data/transactions.csv")
