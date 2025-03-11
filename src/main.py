import os
from pathlib import Path

from parsers.table_parser import TableParser
from parsers.image_ocr import convert_image_to_json
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
        output_path = OUTPUT_DIR / "공업수학(KREYSZIG)_정진교" / "23강.pickle"
        components = get_data_from_pickling(output_path)

    # table parsing
    #TODO REMOVE test
    from test.test_table_template import tables

    table_parser = TableParser()
    for html_table in tables:
        table_parser.parse_table_from_html(html_table)

    # for table in components['tables']:
    #     print(dataframe_to_json(table))


if __name__ == "__main__":
    main()