import streamlit as st
from PIL import Image

from parsers.image_ocr import ImageOCR
from utils.logger import init_logger


logger = init_logger(__file__, "DEBUG")


st.title("이미지 OCR 추출기")

uploaded_file = st.file_uploader("이미지를 업로드 하세요", type=["jpg", "png", "jpeg"])
if uploaded_file is not None:
    file_bytes = uploaded_file.getvalue()
    image = Image.open(uploaded_file)
    st.image(image, caption='업로드한 이미지', use_container_width=True)
image_ocr = ImageOCR()

if st.button("텍스트 추출"):
    image_type, image_text = image_ocr.convert_img_to_txt(file_bytes)    
    
st.write("추출된 텍스트:")
st.text_area("OCR 결과", image_text, height=200)
