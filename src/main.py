import os
from pathlib import Path
from pyhwpx import Hwp
from parsers.hwp_to_html import _extract_html_table
from parsers.table_parser import get_txt_from_table

# DIR PATHS
ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(ROOT_DIR, "assets", "input")
OUTPUT_DIR = os.path.join(ROOT_DIR, "assets", "output")

TEST_DIR = os.path.join(DATA_DIR, "test")


def main():
    hwp = Hwp()
    table_ls, mean_time = _extract_html_table(hwp_dir_path=Path(TEST_DIR), hwp=hwp)
    get_txt_from_table(table_ls[0])
    
if __name__ == "__main__":
    main()