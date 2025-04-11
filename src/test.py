from numpy import asarray
from PIL import Image
from paddleocr import PaddleOCR
from utils.constants import DATA_DIR


ocr = PaddleOCR(lang='korean')

img_path = DATA_DIR / 'test.png'
image = Image.open(img_path)
numpydata = asarray(image)
result = ocr.ocr(numpydata, cls=False)

ocr_result = result[0]
for curr in ocr_result:
    word = curr[1][0]
    print(word)
