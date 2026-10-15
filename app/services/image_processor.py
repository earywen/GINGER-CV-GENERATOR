# -*- coding: utf-8 -*-
import io
import os
import base64
from PIL import Image

import cv2
import numpy as np

# Load Haar cascade once
_CASCADE_PATH = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
_FACE_CASCADE = cv2.CascadeClassifier(_CASCADE_PATH) if os.path.exists(_CASCADE_PATH) else None

def crop_studio_bust(image_bytes: bytes) -> str:
    # Decode with OpenCV for fast face detection
    np_arr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    
    if img is None:
        # Fallback to PIL decode if OpenCV fails
        im = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        w, h = im.size
        crop_size = min(w, h)
        x0 = max(0, int((w - crop_size) * 0.5))
        y0 = max(0, int((h - crop_size) * 0.1))
        cropped = im.crop((x0, y0, x0 + crop_size, y0 + crop_size)).resize((800, 800), Image.Resampling.LANCZOS)
        buf = io.BytesIO()
        cropped.save(buf, format="JPEG", quality=98)
        return base64.b64encode(buf.getvalue()).decode("utf-8")
        
    h, w = img.shape[:2]
    faces = []
    if _FACE_CASCADE is not None:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = _FACE_CASCADE.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(int(w * 0.08), int(w * 0.08)))
        if len(faces) == 0:
            faces = _FACE_CASCADE.detectMultiScale(gray, scaleFactor=1.05, minNeighbors=3, minSize=(int(w * 0.05), int(w * 0.05)))
            
    if len(faces) > 0:
        # Pick the largest detected face (subject)
        fx, fy, fw, fh = max(faces, key=lambda f: f[2] * f[3])
        cx = fx + fw / 2.0
        cy = fy + fh / 2.0
        
        # Desired bust framing: face occupies ~40-44% of circular avatar diameter
        crop_size = int(fh * 2.35)
        
        # In a circular avatar, the face optical center should sit at ~44% from top
        ideal_y0 = int(cy - crop_size * 0.44)
        pad_top = 0
        if ideal_y0 < 0:
            # Replicate studio backdrop at the top so the hair has natural headroom
            pad_top = abs(ideal_y0) + int(h * 0.03)
            img = cv2.copyMakeBorder(img, pad_top, 0, 0, 0, cv2.BORDER_REPLICATE)
            cy += pad_top
            h += pad_top
            
        y0 = int(cy - crop_size * 0.44)
        x0 = int(cx - crop_size * 0.5)
        
        # Clamp within image bounds
        if x0 < 0:
            x0 = 0
        elif x0 + crop_size > w:
            x0 = max(0, w - crop_size)
            
        if y0 < 0:
            y0 = 0
        elif y0 + crop_size > h:
            y0 = max(0, h - crop_size)
            
        final_size = min(crop_size, w - x0, h - y0)
        cropped_bgr = img[y0:y0+final_size, x0:x0+final_size]
        cropped_rgb = cv2.cvtColor(cropped_bgr, cv2.COLOR_BGR2RGB)
        im_pil = Image.fromarray(cropped_rgb)
    else:
        # Fallback centered framing
        crop_size = min(w, int(h * 0.72))
        x0 = max(0, int((w - crop_size) * 0.5))
        y0 = max(0, int(h * 0.05))
        cropped_bgr = img[y0:y0+crop_size, x0:x0+crop_size]
        cropped_rgb = cv2.cvtColor(cropped_bgr, cv2.COLOR_BGR2RGB)
        im_pil = Image.fromarray(cropped_rgb)
        
    resized = im_pil.resize((800, 800), Image.Resampling.LANCZOS)
    buf = io.BytesIO()
    resized.save(buf, format="JPEG", quality=98)
    return base64.b64encode(buf.getvalue()).decode("utf-8")
