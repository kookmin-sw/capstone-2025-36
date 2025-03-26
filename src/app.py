import json
import time
import streamlit as st

from parsers.image_ocr import ImageOCR
from parsers.table_parser import TableParser
from utils.logger import init_logger


logger = init_logger(__file__, "DEBUG")
image_ocr = ImageOCR()

st.cache_data.clear()
st.cache_resource.clear()

uploaded_file = st.file_uploader("JSON 파일을 업로드하세요", type=["json"], key="file_uploader")

if uploaded_file is not None:
    json_data = json.load(uploaded_file)

    if st.button("텍스트 추출"):
        with st.spinner("텍스트를 추출 중입니다..."):
            for curr_key, curr_json in json_data.items():
                logger.info('complete json loading')
        # table parsing
        # table_data = curr_json['tables']
        # table_parser = TableParser()

        # for table_name in table_data.keys():
        #     curr_json[table_name] = table_parser.parse_table_from_html(table_data[table_name])
    

                # image to text
                image_data = curr_json['images']
                logger.info('load image data')
                
                for image_name, image_byte in image_data.items():
                    logger.info(image_ocr.convert_img_to_txt(image_byte))
                    # curr_json[image_name] = 

    st.write("업로드된 JSON 데이터:")
    st.json(json_data)
