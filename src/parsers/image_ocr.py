import io
import os
import re
import uuid
import time
import json
import requests
from sympy import sympify, latex 
from PIL import Image
from typing import Tuple
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
        self.image_classifier = pipeline(model="openai/clip-vit-large-patch14", task="zero-shot-image-classification", use_fast=True)
        
        # Formula Model
        self.formula_processor = AutoProcessor.from_pretrained("ds4sd/SmolDocling-256M-preview")
        self.formula_model = AutoModelForImageTextToText.from_pretrained("ds4sd/SmolDocling-256M-preview").to("cpu")
        self.formula_prompt = self.formula_processor.apply_chat_template(FORMULA_OCR_MESSAGE, add_generation_prompt=True)


    def convert_img_to_txt(self, binary_image: bytes) -> Tuple[str, str]:
        '''
        이미지를 분류하고 각 카테고리에 따라서 str, latex, None으로 값을 리턴
        Args:
            binary_image(bytes): image data
        Return:
            image_type(str): 이미지 형태 리턴 IMAGE_CATEGORY의 값 중 하나이다
            ocr_text(str|None): 이미지를 변환한 데이터 str 값
        '''
        image = Image.open(io.BytesIO(binary_image))
        logger.info("success loading image")
        
        image_type = self._classificate_image(image)
        logger.info(f"classificate image: {image_type}")

        if image_type == IMAGE_CATEGORY[2]:
            return image_type, self._extract_text_from_img(binary_image)
        elif image_type == IMAGE_CATEGORY[0]:
            return image_type, fr"{self._extract_formula_from_img(image)}"
        else:
            return image_type, None
    
    def _classificate_image(self, image: Image.Image) -> str:
        '''
        이미지 분류 (그래프, 표, 텍스트로 구분)
        Args:
            image(Image.Image): pillow image data composed RGB
            category(str): image label
            labels: label types
        Return:
            label: image label
        '''
        outputs = self.image_classifier(image, candidate_labels=IMAGE_CATEGORY)

        best_output = max(outputs, key=lambda x: x["score"])
        return best_output["label"]

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

        latex_result = self._extract_and_convert_to_latex(generated_text)

        return latex_result

    def _extract_and_convert_to_latex(self, text: str):
            '''
            수식을 감지하고 LaTeX 형식으로 변환합니다.
            Args:
                text(str): LLM 답변 중 수식이 포함된 Text
            Return:
                latex_text(str): 유효한 수식 패턴이 감지되면 LaTeX 형식으로 반환하고, 그렇지 않으면 원본 텍스트를 반환합니다.
            '''
            math_pattern = r"[0-9a-zA-Z\s\+\-\*/=\(\)\^\{\}]+"
            equations = re.findall(math_pattern, text)

            latex_expressions = []
            for eq in equations:
                try:
                    sympy_expr = sympify(eq)
                    latex_expr = latex(sympy_expr)
                    latex_expressions.append(f"${latex_expr}$")
                except Exception:
                    latex_expressions.append(f"${eq}$")

            return "\n".join(latex_expressions)

    def _extract_text_from_img(self, binary_img: bytes, ocr_model="easyocr") -> str:
        '''
        이미지에서 텍스트를 추출합니다
        Args:
            text(bytes): bytes 타입의 Text
        Return:
            text(str): image에서 추출한 text
        '''
        if ocr_model == "azure":
            OCRLoader = AzureAIDocumentIntelligenceLoader(
                api_endpoint=os.getenv("AZURE_COGNITIVE_API_ENDPOINT"), 
                api_key=os.getenv("AZURE_COGNITIVE_API_KEY"),  
                api_model="prebuilt-layout",
                bytes_source=binary_img,
                mode="page"
            )
            documents = OCRLoader.load()
            texts = [doc.page_content for doc in documents]

        elif ocr_model == "easyocr":
            texts = self.reader.readtext(binary_img)[1]

        else:
            secret_key = os.getenv('NAVER_API_KEY')
            api_url = os.getenv('AZURE_COGNITIVE_API_KEY')

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

            texts = response.text.encode('utf8')
        return texts
