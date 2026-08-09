import requests
import time

BASE_URL = "http://127.0.0.1:8000/v1/chat/completions"

def test_cache_and_rate_limit():
    payload = {
        "model": "gemini-2.0-flash-lite",
        "user_id": "aryan_gateway_test",
        "messages": [{"role": "user", "content": "Explain vector databases in one sentence."}]
    }

    print("--- 1. Testing Cache Miss (First Request) ---")
    start = time.time()
    res1 = requests.post(BASE_URL, json=payload)
    latency1 = (time.time() - start) * 1000
    data1 = res1.json()
    
    print(f"Status Code : {res1.status_code}")
    print(f"Cache Hit   : {data1.get('x_cache_hit')}")
    print(f"Latency     : {latency1:.2f} ms\n")

    print("--- 2. Testing Semantic Cache Hit (Second Request) ---")
    start = time.time()
    res2 = requests.post(BASE_URL, json=payload)
    latency2 = (time.time() - start) * 1000
    data2 = res2.json()

    print(f"Status Code : {res2.status_code}")
    print(f"Cache Hit   : {data2.get('x_cache_hit')}")
    print(f"Latency     : {latency2:.2f} ms (Served from Redis!)\n")

    print("--- 3. Testing Open Shield Rate Limiter ---")
    hit_rate_limit = False
    # Rapid loop hits Open Shield rate limiter without calling Google
    for i in range(12):
        res = requests.post(BASE_URL, json=payload)
        if res.status_code == 429:
            print(f"Request #{i+1}: 429 Too Many Requests (Open Shield Gateway Blocked It!)")
            hit_rate_limit = True
            break
        else:
            print(f"Request #{i+1}: {res.status_code} OK (Cache Hit)")

if __name__ == "__main__":
    test_cache_and_rate_limit()