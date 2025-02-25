import os
from pyhwpx import Hwp
from utils.file_handler import get_filenames_with_type

# DIR PATHS
ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(ROOT_DIR, "assets", "input")
OUTPUT_DIR = os.path.join(ROOT_DIR, "assets", "output")

TEST_HWP_PATH = os.path.join(DATA_DIR, "test", "test.hwp")


def main():
    hwp_file_paths = get_filenames_with_type(DATA_DIR, "hwp")
    print(hwp_file_paths)
    # hwp = Hwp()
    # hwp.open(TEST_HWP_PATH)


if __name__ == "__main__":
    main()