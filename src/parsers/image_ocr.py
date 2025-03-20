import io
import os
import cv2
import json
import numpy as np
import easyocr
import uuid
import requests
import time
from pathlib import Path
from dotenv import load_dotenv
from PIL import Image
from transformers import pipeline
from langchain_community.document_loaders import AzureAIDocumentIntelligenceLoader
from utils.logger import init_logger
from utils.constants import IMAGE_CATEGORY
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
import requests


load_dotenv()
logger = init_logger(__file__, "DEBUG")


class ImageOCR:
    def __init__(self) -> None:
        self.reader = easyocr.Reader(["en", "ko"])
        self.candidate_labels = [f'This is a photo of {label}' for label in IMAGE_CATEGORY]
        self.image_classifier = pipeline(model="openai/clip-vit-large-patch14", task="zero-shot-image-classification")

    def convert_img_to_txt(self, binary_image: bytes) -> str:
        image = Image.open(io.BytesIO(binary_image))
        image_type = self._classficate_image(image)
        
        if image_type == "Text":
            ocr_text = self._use_ocr_naver(binary_image)
            return ocr_text
        elif image_type == "Formula":
            return self._process_equation(image)
    
    def _classficate_image(self, image: Image.Image) -> str:
        """
        Image를 분류해주는 함수

        Args:

        Returns:
    
        """
        predictions = self.image_classifier(image, candidate_labels=self.candidate_labels)
        best_output = max(predictions, key=lambda x: x["score"])

        return best_output["label"]

    def _process_equation(self, image: Image.Image):
        pixel_values = self.processor(images=image.convert('RGB'), return_tensors="pt").pixel_values
        generated_ids = self.vision_model.generate(pixel_values)
        text = self.processor.batch_decode(generated_ids, skip_special_tokens=True)[0]

        return text

    def _use_ocr_naver(self, binary_img):
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


def _extract_text_from_img(jpg_path:str) -> str:
    OCRLoader = AzureAIDocumentIntelligenceLoader(
        api_endpoint=os.getenv("AZURE_COGNITIVE_API_ENDPOINT"), 
        api_key=os.getenv("AZURE_COGNITIVE_API_KEY"),  
        api_model="prebuilt-layout",
        file_path=jpg_path,
        mode="page"
    )
    documents = OCRLoader.load()
    texts = [doc.page_content for doc in documents]
    return "".join(texts)