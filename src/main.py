import os
from pathlib import Path
from parsers.table_parser import get_json_from_tables
from parsers.image_ocr import convert_image_to_json
from utils.file_handler import get_table_from_pickling

if os.name == "nt":
    from pyhwpx import Hwp
    from parsers.hwp_to_html import extract_html_from_hwp

# DIR PATHS
ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "assets" / "input"
OUTPUT_DIR = ROOT_DIR / "assets" / "output"


def main():
    hwp = Hwp()
    table_ls, img_ls = extract_html_from_hwp(hwp_dir_path=DATA_DIR, output_dir_path=OUTPUT_DIR, hwp=hwp)
    
    # print(table_ls)

    # print(get_json_from_tables(table_ls, OUTPUT_DIR))

    
if __name__ == "__main__":
    main()