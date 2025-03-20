import uuid
import json
import time
import requests
from pathlib import Path

from utils.constants import OUTPUT_DIR
from parsers.image_ocr import ImageOCR

def get_img_with_binary(img_path: Path) -> bytes:
    """
    image Path를 토대로 binary 형태로 변환하는 코드

    Args:

    Returns:

    """
    with img_path.open("rb") as f:
        return f.read()

img_dir_path = OUTPUT_DIR / "ocr_test"
test_img_path = OUTPUT_DIR / "Formula/Formula1.png"
image_ocr = ImageOCR()


binary_img = get_img_with_binary(test_img_path)
secret_key = "bXFGVWN6ZlN6a3VieW5oZHVRQVN4QmhlUVhwenhZeUw="
api_url = "http://clovaocr-api-kr.ncloud.com/external/v1/39574/0abdca05b34ecdb1edf0cd4f0039b45f569d3d0bd6be8707b9b7c577b60eb876"

request_json = {
    'images': [
        {
            'format': 'jpg',
            'name': 'demo'
        }
    ],
    'requestId': str(uuid.uuid4()),
    'version': 'V2',
    'timestamp': int(round(time.time() * 1000))
}

payload = {'message': json.dumps(request_json).encode('UTF-8')}
files = [
('file', binary_img)
]
headers = {
'X-OCR-SECRET': secret_key
}

response = requests.request("POST", api_url, headers=headers, data = payload, files = files)

print(response.text.encode('utf8'))

