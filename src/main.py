import os
from pathlib import Path
from parsers.table_parser import get_json_from_table
from parsers.image_ocr import convert_image_to_json
from utils.file_handler import get_table_from_pickling

if os.name == "nt":
    from pyhwpx import Hwp
    from parsers.hwp_to_html import extract_html_from_hwp

# DIR PATHS
ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(ROOT_DIR, "assets", "input")
OUTPUT_DIR = os.path.join(ROOT_DIR, "assets", "output")

TEST_DIR = os.path.join(DATA_DIR, "test")
TEST_HWP_PATH = os.path.join(TEST_DIR, "test1.hwp")
TEST_PICKLE_PATH = os.path.join(TEST_DIR, "test1.pickle")
TEST_IMG_MATH_PATH = os.path.join(TEST_DIR, "test1_2.jpg")
TEST_IMG_PATH = os.path.join(TEST_DIR, "test4_32.jpg")

def main():
    # hwp = Hwp()
    # table_ls, img_ls = extract_html_from_hwp(hwp_dir_path=Path(TEST_DIR), output_dir_path=Path(OUTPUT_DIR), hwp=hwp)
    
    #TODO TEST용 코드
    table_ls = get_table_from_pickling(TEST_PICKLE_PATH)
    print(get_json_from_table(table_ls[0]))
    print(convert_image_to_json([Path(TEST_IMG_PATH)]))

    # for img_path in img_ls:
    #     print(str(img_path))
    
if __name__ == "__main__":
    main()