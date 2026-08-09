# 🛡️ Open Shield AI Gateway

An enterprise-grade, privacy-first AI Gateway built to securely proxy, manage, and monitor traffic between client applications and upstream Large Language Models (LLMs). 

Built with **FastAPI**, **Redis**, and **Docker**, Open Shield acts as a secure middleware layer that intercepts requests, scrubs visual PII locally, enforces rate limits, and dramatically reduces latency via semantic caching.

---

## ✨ Core Features

* **Visual PII Redaction (Privacy by Design):** Intercepts image payloads and utilizes a local, lightweight vision model to detect and blur human faces (Gaussian blur) *before* the data ever leaves your network. 
* **Semantic Caching:** Uses Redis to cache responses for identical or highly similar queries, reducing duplicate upstream LLM calls and dropping response latency to **< 50ms**.
* **Distributed Rate Limiting:** Enforces user-level API quotas (429 Too Many Requests) to prevent abuse and manage upstream costs.
* **Upstream Resilience:** Gracefully handles upstream quota limits or API outages by falling back to synthetic mock responses, ensuring continuous system availability.
* **Real-Time Observability:** Emits live metrics to a Prometheus and Grafana stack for monitoring cache hit rates, PII interventions, latency, and HTTP status codes.

---

## 🏗️ Architecture & Tech Stack

* **Core Framework:** FastAPI (Python)
* **Data Store & Caching:** Redis
* **Computer Vision:** OpenCV / Pillow (Local processing)
* **Containerization:** Docker & Docker Compose
* **Observability:** Prometheus & Grafana
* **Upstream Compatibility:** OpenAI-compatible REST endpoints (Configured for Google AI Studio / Gemini)

---

## 🚀 Getting Started

### Prerequisites
* [Docker](https://docs.docker.com/get-docker/) and Docker Compose
* Python 3.10+ (for running local test scripts)

### 1. Clone & Configure
```bash
git clone [https://github.com/yourusername/open-shield.git](https://github.com/Aryan-DScodes/open-shield.git)
cd open-shield
Create a .env file in the root directory and add your upstream API key:

Ini, TOML
UPSTREAM_API_KEY=your_google_ai_studio_api_key
REDIS_URL=redis://redis:6379/0
2. Launch the Stack
Spin up the Gateway, Redis, Prometheus, and Grafana containers:

Bash
docker-compose up --build -d
The API Gateway will be live at: http://localhost:8000

Grafana Dashboard will be live at: http://localhost:3000

🧪 Testing the Gateway
The repository includes dedicated test scripts to verify the core gateway functionality.

1. Test Visual PII Redaction
Downloads a test image, base64 encodes it, and sends it through the gateway to verify local facial blurring.

Bash
python test_pii.py
Expected Output: Status Code: 200 | PII Redacted: True

2. Test Semantic Caching & Rate Limiting
Sends rapid requests to test cache latency drops and token-bucket throttling.

Bash
python test_gateway.py
Expected Output:

Request 1: Cache Miss (~1000ms)

Request 2: Cache Hit (< 50ms)

Request 3+: 429 Too Many Requests (Gateway Blocked)

📊 Observability
Open Shield ships with a pre-configured Grafana dashboard. Navigate to http://localhost:3000 to view live traffic metrics, including:

Total Requests & Error Rates

Cache Hit vs. Miss Ratios

PII Redaction Triggers

Average Gateway Latency

#🎥 Demo
[Insert a link or GIF of your 60-second Loom/MP4 demo here]

👤 Author
Aryan


### Your Final Action Items:
1. Copy the text above and save it as `README.md` in your project folder.
2. Replace `[https://github.com/yourusername/open-shield.git](https://github.com/yourusername/open-shield.git)` with your actual GitHub link.
3. Record that quick 60-second demo we discussed and paste the link in the `## 🎥 Demo` section.
4. Push everything to GitHub!
