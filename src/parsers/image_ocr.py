import os
import easyocr
from pathlib import Path
from typing import List, Dict
from dotenv import load_dotenv
from langchain_community.document_loaders import AzureAIDocumentIntelligenceLoader
from utils.logger import init_logger


load_dotenv()
reader = easyocr.Reader(["en", "ko"])
logger = init_logger(__file__, "DEBUG")


def convert_image_to_json(img_path:Path) -> str:
    """
    image를 JSON으로 변환하여 리턴
    """
    if not img_path.exists():
        logger.error(f"이미지 파일이 존재하지 않습니다: {img_path}")

    # TODO: OCR 모델 선정
    # ocr_text = _extract_text_from_img(str(img_path))
    ocr_text = "".join(reader.readtext(str(img_path), detail=0))

    return ocr_text


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