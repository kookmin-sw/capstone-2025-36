from pathlib import Path
import easyocr
import io
from PIL import Image
from transformers import pipeline
from PIL import Image

# load pipe

# from utils.constants import ROOT_DIR


jpg_path = Path("/Users/jeong-uihyeon/capstone-data/assets/output/output.png")


class ImageOCR:
    def __init__(self) -> None:
        self.reader = easyocr.Reader(["en", "ko"])
        self.image_classifier = pipeline(
            task="zero-shot-image-classification",
            model="google/siglip2-base-patch16-224",
        )

    def convert_img_to_txt(self, binary_image: bytes) -> str:
        image_stream = io.BytesIO(binary_image)
        image = Image.open(image_stream)
        self._classficate_image(image_stream)

        # ocr_text = "".join(self.reader.readtext(str(img_path), detail=0))
        # return ocr_text
    
    def _classficate_image(self, image: Image.Image) -> str:
        candidate_labels = ["Table", "Graph", "Text"]
        outputs = self.image_classifier(image, candidate_labels=candidate_labels)
        outputs = [{"score": round(output["score"], 4), "label": output["label"] } for output in outputs]
        print(outputs)
        # return outputs["label"]

    def get_img_with_binary(self, img_path: Path) -> bytes:
        """
        image Path를 토대로 binary 형태로 변환하는 코드

        Args:

        Returns:
    
        """
        with img_path.open("rb") as f:
            return f.read()


if __name__ == "__main__":
    image_ocr = ImageOCR()
    binary_img = image_ocr.get_img_with_binary(jpg_path)
    print(image_ocr.convert_img_to_txt(binary_img))
