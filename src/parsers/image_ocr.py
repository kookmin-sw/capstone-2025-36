import io
import os
import base64
import re
import base64
import uuid
import time
import json
import requests
from PIL import Image
from itertools import chain
from dotenv import load_dotenv
from transformers import pipeline
from langchain_community.document_loaders import AzureAIDocumentIntelligenceLoader

from transformers import AutoProcessor, AutoModelForImageTextToText
from utils.logger import init_logger
from utils.constants import IMAGE_CATEGORY, FORMULA_OCR_MESSAGE

import easyocr  # test용 OCR 모델


load_dotenv()
logger = init_logger(__file__, "DEBUG")


class ImageOCR:
    def __init__(self) -> None:
        # OCR Model init
        self.reader = easyocr.Reader(["en", "ko"])  # test용 ocr 모델
        
        # Classification Model
        checkpoint = "google/siglip2-so400m-patch14-384"  # openai/clip-vit-large-patch14
        self.image_classifier = pipeline(task="zero-shot-image-classification", model=checkpoint)
        
        # Formula Model
        self.formula_processor = AutoProcessor.from_pretrained("ds4sd/SmolDocling-256M-preview", use_fast=True)
        self.formula_model = AutoModelForImageTextToText.from_pretrained("ds4sd/SmolDocling-256M-preview").to("cpu")
        self.formula_prompt = self.formula_processor.apply_chat_template(FORMULA_OCR_MESSAGE, add_generation_prompt=True)


    def convert_img_to_txt(self, encode_image: str) -> str:
        '''
        이미지를 분류하고 각 카테고리에 따라서 str, latex, None으로 값을 리턴
        Args:
            encoding_image(str): encoding된 image 데이터
        Return:
            image_type(str): 이미지 형태 리턴 IMAGE_CATEGORY의 값 중 하나이다
            ocr_text(str|None): 이미지를 변환한 데이터 str 값
        '''
        try:
            binary_image = base64.b64decode(encode_image)
            image = Image.open(io.BytesIO(binary_image)).convert("RGB")
            logger.info("Success loading image")
        except Exception as e:
            logger.error(f"Failed loading image: {e}")
            return  
        
        try:
            image_type = self._classificate_image(image)

            if image_type in IMAGE_CATEGORY['Text']:
                return self._extract_text_from_img(binary_image)
            elif image_type in IMAGE_CATEGORY['Formula']:
                return fr"{self._extract_formula_from_img(image)}"
            else:
                return image_type
            
        except Exception as e:
            return encode_image

    def _classificate_image(self, image: Image.Image) -> str:
        '''
        이미지 분류 (그래프, 표, 텍스트로 구분)
        Args:
            image(Image.Image): pillow image data composed RGB
        Return:
            label: image label
        '''
        try:
            candidate_labels = list(chain(*IMAGE_CATEGORY.values()))
            outputs = self.image_classifier(image, candidate_labels=candidate_labels)
            best_output = max(outputs, key=lambda x: x["score"])['label']
            logger.info(f"classificate image: {best_output}")

            return best_output
        
        except Exception as e:
            logger.error(f"Failed classificate image: {e}")

    def _extract_formula_from_img(self, image: Image.Image) -> str:
        '''
        hugginface open ocr 모델을 활용해서 formula를 추출 합니다
        Args:
            image(Image.Image): pillow.Image.Image 타입의 image 데이터
        Return:
            latex_result(str): 추출된 latex를 str으로 변환하여 리턴
        '''
        
        inputs = self.formula_processor(text=self.formula_prompt, images=[image], return_tensors="pt").to("cpu")

        generated_ids = self.formula_model.generate(**inputs, max_new_tokens=500)
        generated_text = self.formula_processor.batch_decode(generated_ids, skip_special_tokens=True)[0]

        def extract_and_convert_to_latex(text: str) -> str:
            '''
            수식을 감지하고 LaTeX 형식으로 변환합니다.
            Args:
                text(str): LLM 답변 중 수식이 포함된 Text
            Return:
                latex_text(str): 유효한 수식 패턴이 감지되면 LaTeX 형식으로 반환하고, 그렇지 않으면 원본 텍스트를 반환합니다.
            '''
            text = re.sub(r"User:\s*Extract mathematical expressions in LaTeX format\s*Assistant: 0>0>500>500>", "", text)
            text = re.sub(r"\\, \.$", "", text)
            return f"${text}$"

        latex_result = extract_and_convert_to_latex(generated_text)
        return latex_result

    def _extract_text_from_img(self, binary_img: bytes) -> str:
        '''
        이미지에서 텍스트를 추출합니다
        Args:
            text(bytes): bytes 타입의 Text
        Return:
            text(str): image에서 추출한 text
        '''
        # OCRLoader = AzureAIDocumentIntelligenceLoader(
        #     api_endpoint=os.getenv("AZURE_COGNITIVE_API_ENDPOINT"), 
        #     api_key=os.getenv("AZURE_COGNITIVE_API_KEY"),  
        #     api_model="prebuilt-layout",
        #     bytes_source=binary_img,
        #     mode="page"
        # )
        # documents = OCRLoader.load()
        # texts = [doc.page_content for doc in documents]
        logger.info(f'Success extract text')
        result = self.reader.readtext(binary_img, detail = 0)
        
        texts = self.reader.readtext(binary_img)
        return " ".join([result[1] for result in texts])
