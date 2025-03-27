from PIL import Image
from transformers import pipeline

from utils.constants import OUTPUT_DIR

checkpoint = "google/siglip2-so400m-patch14-384"
image_classifier = pipeline(task="zero-shot-image-classification", model=checkpoint)

image_path = OUTPUT_DIR / "ocr_test/Formula/Formula2.png"

basic_prompt = "Chart"
another_prompt = "Formula"
other_prompt = f"Something other than a {basic_prompt} or {another_prompt}"

candidate_labels = [basic_prompt, another_prompt, other_prompt]

image = Image.open(str(image_path))
outputs = image_classifier(image, candidate_labels=candidate_labels)
best_output = max(outputs, key=lambda x: x["score"])
print(best_output)