import io
import os
import cv2
import numpy as np
import easyocr
import pytesseract
from pathlib import Path
from dotenv import load_dotenv
from PIL import Image
from transformers import pipeline
from langchain_community.document_loaders import AzureAIDocumentIntelligenceLoader
from utils.logger import init_logger
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
import requests


load_dotenv()
logger = init_logger(__file__, "DEBUG")


class ImageOCR:
    def __init__(self) -> None:
        self.reader = easyocr.Reader(["en", "ko"])
        self.type_list = ["Graph", "Diagram", "Text", "Formula"]
        self.detector = pipeline(model="openai/clip-vit-large-patch14", task="zero-shot-image-classification")
        pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        self.processor = TrOCRProcessor.from_pretrained("microsoft/trocr-base-handwritten")
        self.vision_model = VisionEncoderDecoderModel.from_pretrained("microsoft/trocr-base-handwritten")

    def convert_img_to_txt(self, binary_image: bytes) -> str:
        image = Image.open(io.BytesIO(binary_image))
        image_type = self._classficate_image(image)
        if image_type == "Text":
            # binary_image = self._preprocess_image(binary_image)
            ocr_text = pytesseract.image_to_string(image, lang="kor")
            return ocr_text
        elif image_type == "Formula":
            return self._process_equation(image)
    
    def _classficate_image(self, image: Image.Image) -> str:
        """
        Image를 분류해주는 함수

        Args:

        Returns:
    
        """
        predictions = self.detector(image, candidate_labels=self.type_list)
        pred_max = 0
        pred_val = None

        for pred in predictions:
            if pred['score'] > pred_max:
                pred_max = pred['score']
                pred_val = pred['label']

        return pred_val
    
    def _preprocess_image(self, image_bytes: bytes):
        """이미지 전처리 (흑백 변환 + 이진화)"""
        image = Image.open(io.BytesIO(image_bytes)).convert("L") 
        img_array = np.array(image)
        _, binary_img = cv2.threshold(img_array, 150, 255, cv2.THRESH_BINARY)  # 이진화
        return Image.fromarray(binary_img)

    def _process_equation(self, image: Image.Image):
        pixel_values = self.processor(images=image.convert('RGB'), return_tensors="pt").pixel_values
        generated_ids = self.vision_model.generate(pixel_values)
        text = self.processor.batch_decode(generated_ids, skip_special_tokens=True)[0]

        return text


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