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
