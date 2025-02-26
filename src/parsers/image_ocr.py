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


def convert_image_to_json(img_paths:List[Path]) -> Dict[str, str]:
    """
    image를 JSON으로 변환하여 리턴
    """
    img_json = dict()

    for img_path in img_paths:
        img_path = str(img_path)
        try:
            if not os.path.exists(img_path):
                raise FileNotFoundError(f"이미지 파일이 존재하지 않습니다: {img_path}")
            # TODO: OCR 모델 선정
            # ocr_text = _extract_text_from_img(img_path)
            ocr_text = "".join(reader.readtext(img_path, detail=0))
            img_json[img_path] = ocr_text
            
            logger.info(f"이미지 Text 변환: {ocr_text}")

            if ocr_text is None:
                raise ValueError("OCR 결과가 None입니다.")
        
        except AttributeError as e:
            #TODO 수식 전용 OCR 이용
            continue

    return img_json


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