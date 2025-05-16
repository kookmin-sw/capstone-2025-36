import os
import json
from pathlib import Path

from parsers.table_parser import TableParser
from parsers.image_ocr import ImageOCR
from utils.logger import init_logger
from utils.constants import DATA_DIR, OUTPUT_DIR, OUTPUT_JSON


logger = init_logger(__file__, "DEBUG")


def main():
    total_dict = dict()

    table_parser = TableParser()
    image_ocr = ImageOCR()

    if os.name == "nt":
        try:
            # Linux나 macOS 환경에서는 import 안하도록
            from parsers.process_hwp_docs import HwpController

            
            hwp_ctrl = HwpController()

            for hwp_path in DATA_DIR.rglob("*.hwp"):
                output_path = OUTPUT_DIR / hwp_path.parent.stem

                components = hwp_ctrl.get_tag_from_html(hwp_path)
                
                if not output_path.exists():
                    os.makedirs(output_path)
                # save_data_from_pickling(output_path / f'{hwp_path.stem}.pickle', components)
                
                total_dict[str(hwp_path)] = components
            del hwp_ctrl
            
            try:
                parsing_data_path = DATA_DIR / "parsing.json"
                with parsing_data_path.open("w", encoding="utf-8") as json_file:
                    json.dump(total_dict, json_file, ensure_ascii=False, indent=4)
                logger.info(f"Successfully save json file: {str(parsing_data_path)}")
            
            except Exception as e:
                logger.error(f"Failed save json file: {e}")

        except ImportError:
            logger.error("please install pyhwpx")

    # 이 아래부분만 UI로 구현
    for curr_name, curr_document in total_dict.items():
        #table parsing
        for table_name, table_data in curr_document['tables'].items():
            total_dict[curr_name]['tables'][table_name] = table_parser.parse_table_from_html(table_data)

        # image OCR 
        for image_key, image_data in curr_document['images'].items():
            total_dict[curr_name]['images'][image_key] = image_ocr.convert_img_to_txt(image_data)
    
    try:
        with OUTPUT_JSON.open("w", encoding="utf-8") as json_file:
            json.dump(total_dict, json_file, ensure_ascii=False, indent=4)
        logger.info(f"Successfully save json file: {str(OUTPUT_JSON)}")
        
    except Exception as e:
        logger.error(f"Failed save json file: {e}")


if __name__ == "__main__":
    main()