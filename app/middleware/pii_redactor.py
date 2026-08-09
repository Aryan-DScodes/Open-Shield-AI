import os
import base64
import cv2
import numpy as np
import onnxruntime as ort
from typing import List, Dict, Any, Tuple

class VisualPIIRedactor:
    def __init__(self, model_path: str = "models/face_detection_lightweight.onnx"):
        self.session = None
        if os.path.exists(model_path):
            self.session = ort.InferenceSession(model_path, providers=['CPUExecutionProvider'])
            self.input_name = self.session.get_inputs()[0].name
        else:
            print("WARNING: ONNX model not found. Visual PII Redaction bypassed.")
        
    def _decode_base64_image(self, b64_str: str) -> np.ndarray:
        # Strip header if present (e.g., "data:image/jpeg;base64,...")
        if "," in b64_str:
            b64_str = b64_str.split(",")[1]
        
        img_data = base64.b64decode(b64_str)
        np_arr = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        return img

    def _encode_image_base64(self, img: np.ndarray, ext: str = ".jpg") -> str:
        _, buffer = cv2.imencode(ext, img)
        b64_str = base64.b64encode(buffer).decode("utf-8")
        return f"data:image/jpeg;base64,{b64_str}"

    def _detect_and_blur(self, image: np.ndarray) -> Tuple[np.ndarray, bool]:
        if not self.session:
            return image, False
            
        original_h, original_w = image.shape[:2]
        
        # 1. Preprocess image for ONNX model
        input_tensor = cv2.resize(image, (320, 240))
        input_tensor = input_tensor.astype(np.float32) / 255.0
        input_tensor = np.transpose(input_tensor, (2, 0, 1))
        input_tensor = np.expand_dims(input_tensor, axis=0)

        # 2. Run ONNX Inference
        outputs = self.session.run(None, {self.input_name: input_tensor})
        
        # Ultraface model outputs two separate arrays: scores and bounding boxes
        scores = outputs[0][0] if outputs[0].shape[-1] == 2 else outputs[1][0]
        boxes = outputs[1][0] if outputs[0].shape[-1] == 2 else outputs[0][0]

        redacted = False
        # 3. Apply blur to detected regions
        for i in range(len(scores)):
            confidence = scores[i][1]  # Index 1 is the 'face' probability
            if confidence > 0.6: 
                redacted = True
                box = boxes[i]
                
                # Convert normalized coordinates to actual image pixels
                x1 = max(0, int(box[0] * original_w))
                y1 = max(0, int(box[1] * original_h))
                x2 = min(original_w, int(box[2] * original_w))
                y2 = min(original_h, int(box[3] * original_h))
                
                roi = image[y1:y2, x1:x2]
                if roi.size != 0:
                    blurred_roi = cv2.GaussianBlur(roi, (99, 99), 30)
                    image[y1:y2, x1:x2] = blurred_roi
                    
        return image, redacted

    async def sanitize_payload(self, messages: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], bool]:
        """
        Iterates through the proxy payload. If a multimodal base64 image is found,
        it intercepts it, redacts PII locally, and replaces the string.
        """
        was_redacted = False
        
        for msg in messages:
            if isinstance(msg.get("content"), list):
                for block in msg["content"]:
                    if block.get("type") == "image_url":
                        url = block["image_url"].get("url", "")
                        
                        # Process only inline base64 images
                        if url.startswith("data:image"):
                            img = self._decode_base64_image(url)
                            safe_img, redacted = self._detect_and_blur(img)
                            
                            if redacted:
                                block["image_url"]["url"] = self._encode_image_base64(safe_img)
                                was_redacted = True
                                
        return messages, was_redacted