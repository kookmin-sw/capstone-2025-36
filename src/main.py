import os
import json
from pathlib import Path

from parsers.table_parser import TableParser
from parsers.image_ocr import ImageOCR
from parsers.json_formatter import save_json
from utils.file_handler import get_data_from_pickling, save_data_from_pickling
from utils.logger import init_logger
from utils.constants import DATA_DIR, OUTPUT_JSON, OUTPUT_PICKLE


logger = init_logger(__file__, "DEBUG")


def main():
    total_dict = dict()

    if os.name == "nt":
        try:
            # Linux나 macOS 환경에서는 import 안하도록
            from parsers.process_hwp_docs import HwpController

            
            hwp_ctrl = HwpController()

            for hwp_path in DATA_DIR.rglob("*.hwp"):
                output_path = OUTPUT_DIR / hwp_path.parent.stem

                components = hwp_ctrl.get_tag_from_html(hwp_path)
                components['content'] = hwp_ctrl.extract_text()
                
                if not output_path.exists():
                    os.makedirs(output_path)
                save_data_from_pickling(output_path / f'{hwp_path.stem}.pickle', components)
                
                total_dict[hwp_path] = components
            del hwp_ctrl

        except ImportError:
            logger.error("please install pyhwpx")
    else:
        total_dict = get_data_from_pickling(OUTPUT_PICKLE)
        logger.info(f"Open pickling file: {OUTPUT_PICKLE}")

    #table parsing
    table_parser = TableParser()

    for curr_doc in total_dict:
        for table_name in curr_doc['tables'].keys():
            curr_doc['tables'][table_name] = table_parser.parse_table_from_html(curr_doc['tables'][table_name])

        # image Text 변환
        for img_path in curr_doc['images'].keys():
            curr_doc['images'][img_path] = convert_image_to_json(Path(img_path))
    
        # Text 전처리
        curr_doc["texts"] = preprocess_markdown(curr_doc["texts"])

        # Metadata 추가
    
    try:
        with OUTPUT_JSON.open("w", encoding="utf-8") as json_file:
            json.dump(total_dict, json_file, ensure_ascii=False, indent=4)
        logger.info(f"Successfully save json file: {str(OUTPUT_JSON)}")
        
    except Exception as e:
        logger.error(f"Failed save json file: {e}")

    # image to text
    image_data = components['images']
    image_ocr = ImageOCR()
    
    for image_data in image_data.keys():
        image_data[image_data] = image_ocr.convert_img_to_txt(image_data[image_data])
    print(json.dumps(image_data, ensure_ascii=False, indent=4))


if __name__ == "__main__":
    main()