from confluent_kafka import Producer
import json, time, random
from faker import Faker

fake = Faker()
p = Producer({'bootstrap.servers': 'localhost:9092'})

def delivery(err, msg): pass

print("Producer started – press Ctrl+C to stop")
try:
    while True:
        tx = {
            "user_id": fake.uuid4(),
            "amount": round(random.expovariate(0.01), 2),
            "merchant": fake.company(),
            "country": random.choice(["US","GB","IN","CN","RU"]),
            "category": random.choice(["grocery","travel","online","luxury"]),
            "time_hour": time.localtime().tm_hour,
            "device": random.choice(["mobile","desktop"]),
            "timestamp": time.time()
        }
        p.produce("transactions", json.dumps(tx).encode(), callback=delivery)
        p.poll(0)
        time.sleep(0.005)  # ~2000 events/sec
except KeyboardInterrupt:
    p.flush()
    print("Stopped")
