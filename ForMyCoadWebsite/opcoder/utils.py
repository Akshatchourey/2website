from uuid import uuid4
from hashlib import sha256
from base64 import urlsafe_b64encode
from PIL import Image
from io import BytesIO
import os

# models functions

def img_preprocessing(photo):
    img = Image.open(photo)
    width, height = img.size

    target_ratio = 16 / 9.0
    current_ratio = width / float(height)
    if current_ratio > target_ratio:
        new_width = int(target_ratio * height)
        left = (width - new_width) // 2
        right = left + new_width
        top = 0
        bottom = height
    else:
        new_height = int(width / target_ratio)
        top = (height - new_height) // 2
        bottom = top + new_height
        left = 0
        right = width

    img = img.crop((left, top, right, bottom))
    output = BytesIO()
    img.save(output, format='PNG', optimize=True)  # Optimized PNG
    output.seek(0)

    return output

def generate_fixed_length_slug(title, length=18):
    random_id = str(uuid4())
    raw_input = f"{title}-{random_id}"
    digest = sha256(raw_input.encode('utf-8')).digest()
    base64_slug = urlsafe_b64encode(digest).decode('utf-8').rstrip('=')
    return base64_slug[:length]
