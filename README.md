# Distributed Event Processing System
### Real-time Credit Card Fraud Detection with Kafka + ML

**Live fraud detection** using Apache Kafka, Python, and an ensemble of Random Forest + XGBoost models.  
Features a real-time web dashboard and terminal alerts — similar to how modern fintech companies (Stripe, Revolut, Nubank) detect fraud in production.

## Demo


https://github.com/user-attachments/assets/23d7c582-bb72-4d39-83dc-9462627baa66


*(Fraud alerts flying in terminal + live dashboard updating every second)*

## Features
- Real-time transaction streaming with **Apache Kafka**
- Synthetic dataset: **1,000 transactions with ~100 labeled frauds**
- **Ensemble ML model** (Random Forest + XGBoost) trained offline
- **Sub-300ms end-to-end latency** fraud scoring
- Live fraud alerts in **terminal**
- Real-time web dashboard[](http://localhost:8000)
- Multiple producers supported — scale to 10k+ tx/sec easily
- Fully containerized with **Docker Compose** (Kafka + Zookeeper)


## Tech Stack
| Component              | Technology                          | Why Chosen |
|-----------------------|-------------------------------------|----------|
| Streaming Platform     | Apache Kafka + Zookeeper            | Industry standard for high-throughput, fault-tolerant streams |
| ML Models              | Random Forest + XGBoost (ensemble)  | Best accuracy on tabular fraud data |
| Language               | Python 3.12                         | Rapid ML prototyping + huge ecosystem |
| Web Dashboard          | FastAPI + Uvicorn + Pure HTML/CSS   | Lightweight, async |
| Data Generation        | Faker + Pandas                      | Realistic synthetic transactions |
| Serialization          | joblib (RF) + JSON (XGBoost)        | Fast model loading |
| Containerization       | Docker + Docker Compose             | One-click reproducible environment |

## Prerequisites
**Prerequisites**
- Docker & Docker Compose (installed on Arch via `sudo pacman -S docker docker-compose`)
- Python 3.12
- Git

## Getting Started

```bash
# 1. Clone the repo
git clone https://github.com/shhvva/StreamGuard-Kafka-ML.git
cd StreamGuard

# 2. Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Generate data + train models (1,000 tx, ~100 frauds)
python data/generate_data.py
python src/trainer/train_models.py

# 5. Start everything with ONE command
./run_demo.sh start
```
- Open your browser → http://localhost:8000
- Watch frauds get caught in real time!

## To stop
```bash
# 1. Stop all python scripts
pkill -f python

# 2. Stop docker
docker-compose down -v
```
## Contributing

- Fork the repo
- Create your branch (git checkout -b feature/amazing)
- Commit (git commit -m 'Add amazing feature')
- Push (git push origin feature/amazing)
- Open a Pull Request
