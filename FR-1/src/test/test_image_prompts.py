from transformers import pipeline, AutoTokenizer


"""
siglip2 모델을 사용할 때 프롬프트의 토큰 길이가 동일해야 해서 그 길이를 확인하는 코드
"""
checkpoint = "google/siglip2-so400m-patch14-384"
image_classifier = pipeline(task="zero-shot-image-classification", model=checkpoint)

tokenizer = AutoTokenizer.from_pretrained("google/siglip2-so400m-patch14-384")

prompts = [
    'a sentence including Hangul',
    'a photo including Hangul',
    'a sentence including English word',
    'equilibrium expression for a chemical',
    'formula including fraction or symbols',
    'a picture including curve graph',
    'a picture including linear graph',
    'a picture including bar graph',
    'a picture including unexpected data',
    'a sentence including korean language',
]

tokenized = tokenizer(prompts, padding=False, add_special_tokens=False)
lengths = [len(ids) for ids in tokenized["input_ids"]]
print(lengths)