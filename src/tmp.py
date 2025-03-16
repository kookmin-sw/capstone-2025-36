from pathlib import Path

from utils.constants import OUTPUT_DIR
from parsers.image_ocr import ImageOCR

def get_img_with_binary(img_path: Path) -> bytes:
    """
    image Path를 토대로 binary 형태로 변환하는 코드

    Args:

    Returns:

    """
    with img_path.open("rb") as f:
        return f.read()

img_dir_path = OUTPUT_DIR / "ocr_test"
image_ocr = ImageOCR()


for img_path in img_dir_path.rglob("*.png"):
    binary_img = get_img_with_binary(img_path)
    # print(binary_img)
    result = image_ocr.convert_img_to_txt(binary_img)
    if result is not None:
        print(f"{str(img_path)}: {result}")
