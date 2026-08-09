import requests
import base64
import urllib.request
import io
from PIL import Image

print("1. Downloading & compressing test image...")
img_url = "https://raw.githubusercontent.com/opencv/opencv/master/samples/data/lena.jpg"
urllib.request.urlretrieve(img_url, "test_face.jpg")

# Downsample image to conserve vision tokens
with Image.open("test_face.jpg") as img:
    img.thumbnail((150, 150))
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=60)
    base64_image = base64.b64encode(buffer.getvalue()).decode('utf-8')

print("2. Forwarding through Open Shield Gateway...\n")
payload = {
    "model": "gemini-2.0-flash-lite",  # Uses the flash-lite quota pool
    "user_id": "aryan_pii_test",
    "messages": [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Describe this image in one brief sentence."},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
            ]
        }
    ]
}

res = requests.post("http://127.0.0.1:8000/v1/chat/completions", json=payload)
data = res.json()

print("=" * 45)
print(f"Status Code  : {res.status_code}")
print(f"Cache Hit    : {data.get('x_cache_hit')}")
print(f"PII Redacted : {data.get('x_pii_redacted')}")
print("=" * 45)

if res.status_code == 200:
    content = data.get('choices', [{}])[0].get('message', {}).get('content', '')
    print(f"\nAI Response:\n{content}")
else:
    print("\nError Details:")
    print(data)