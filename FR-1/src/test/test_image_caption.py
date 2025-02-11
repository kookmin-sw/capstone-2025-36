from transformers import AutoProcessor, Pix2StructForConditionalGeneration
from PIL import Image
import torch

model = Pix2StructForConditionalGeneration.from_pretrained("google/matcha-chartqa").to(0)
processor = AutoProcessor.from_pretrained("google/matcha-chartqa")

image = Image.open('assets/test.png')
inputs = processor(image, return_tensors="pt")

generated_ids = model.generate(**inputs, max_new_tokens=20)
generated_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0].strip()
print(generated_text)