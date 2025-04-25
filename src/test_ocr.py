# OCR TEST
import io
import ast
import logging
import nlptutti as metrics
from PIL import Image
from datasets import load_dataset
from parsers.image_ocr import ImageOCR


def get_score(refs: str, preds: str):
    cer_result = metrics.get_cer(refs, preds)
    wer_result = metrics.get_wer(refs, preds)

    return (cer_result['cer'], wer_result['wer'])


def convert_image(image: Image.Image):
    buf = io.BytesIO()
    image.save(buf, format='WEBP', quality=85)
    return buf.getvalue()


logging.disable(logging.DEBUG)
dataset = load_dataset("naver-clova-ix/synthdog-ko", split="train", streaming=True)
image_ocr = ImageOCR()

LIMIT = 10
count = 0

print(next(iter(dataset)))

#     image = data[count]['image']
#     image = image.convert('L')

#     image_caption = ast.literal_eval(dataset[count]['ground_truth'])
#     image_caption = image_caption['gt_parse']['text_sequence']

#     image_bytes = convert_image(image)
#     del image

#     ocr_text = image_ocr._extract_text_from_image_with_paddle(image_bytes)
#     del image_bytes

#     cer, wer = get_score(refs=image_caption, preds=ocr_text)
#     print(f"CER: {cer}, WER: {wer}")
#     count += 1
