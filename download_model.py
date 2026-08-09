import urllib.request
import os

# Create the models directory
os.makedirs("models", exist_ok=True)

# URL for an open-source lightweight face detection ONNX model
url = "https://github.com/onnx/models/raw/main/validated/vision/body_analysis/ultraface/models/version-RFB-320.onnx"

print("Downloading ONNX model... (this might take a few seconds)")
urllib.request.urlretrieve(url, "models/face_detection_lightweight.onnx")
print("Download complete! Model saved to models/face_detection_lightweight.onnx")