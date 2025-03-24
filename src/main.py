import os
import json
from pathlib import Path

from parsers.table_parser import TableParser
from parsers.image_ocr import ImageOCR
from parsers.json_formatter import save_json
from utils.file_handler import get_data_from_pickling, save_data_from_pickling
from utils.logger import init_logger
from utils.constants import DATA_DIR, OUTPUT_DIR


logger = init_logger(__file__, "DEBUG")


def main():
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
                
            del hwp_ctrl

        except ImportError:
            logger.error("please install pyhwpx")
    else:
        output_path = OUTPUT_DIR / "test" / "test4.pickle"
        components = get_data_from_pickling(output_path)

    # table parsing
    table_data = components['tables']
    table_parser = TableParser()

    for table_name in table_data.keys():
        table_data[table_name] = table_parser.parse_table_from_html(table_data[table_name])
    print(json.dumps(table_data, ensure_ascii=False, indent=4))

    # image to text
    image_data = components['images']
    image_ocr = ImageOCR()
    
    for image_data in image_data.keys():
        image_data[image_data] = image_ocr.convert_img_to_txt(image_data[image_data])
    print(json.dumps(image_data, ensure_ascii=False, indent=4))


if __name__ == "__main__":
    main()