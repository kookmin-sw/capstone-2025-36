import io
from PIL import Image
from ollama import Client
from datasets import load_dataset


def convert_image(image: Image.Image):
    buf = io.BytesIO()
    image.save(buf, format='WEBP', quality=85)
    return buf.getvalue()


client = Client(host='http://localhost:11434')

dataset = load_dataset("naver-clova-ix/synthdog-ko", split=f"train[:10]")

image = dataset['image'][0]
bytes_image = convert_image(image)

response = client.chat(
    model='llama3.2',
    messages=[{'role': 'user', 'content': 'Why is the sky blue?'}]
)

print(response)
