import torch
from transformers import (WhisperProcessor, WhisperForConditionalGeneration, Seq2SeqTrainingArguments, Seq2SeqTrainer)
from dataclasses import dataclass
from typing import Any, Dict, List, Union
from prepare_dataset import prepare_datasets
import evaluate

from transformers import TrainerCallback 


# gpu 사용 설ㅓ정
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("device : ", device)


'''
    학습을 이어서 재개하려면 checkpoint_path를 채워넣고 [A] 부분을 활성화, 새로운 모델로 학습하려면 [B] 부분을 활성화ㄴ
'''
    # [A]
checkpoint_path = "/data/seungmin/모델백업/kr_univ-5epoch-CER20/checkpoint-1065"
model = WhisperForConditionalGeneration.from_pretrained(checkpoint_path).to(device)

model_name = "SungBeom/whisper-small-ko"
processor = WhisperProcessor.from_pretrained(model_name, language="Korean", task="transcribe")



export_dir = f"/data/seungmin/모델백업/kr_univ-5epoch-CER20/backup"
# export_dir = "/data/seungmin/deployment_model3_only_k12"  # 원하는 저장 경로 - 지정된 디렉토리가 존재하지 않으면 자동으로 생성해주니 걱정ㄴ / 이미 존재하면 overwrite

model.save_pretrained(export_dir) # model : 모델 아키텍처 + 가중치
processor.save_pretrained(export_dir) # processor : tokenizer + feature extractor

print(f"Hugging Face 포맷으로 방금 학습한 모델을 {export_dir}에 저장하였음")

'''---------------------------저장------------------- '''

'''
이건 checkpoint를 Trainer()가 아닌 수동으로 저장하는 것인데, 이렇게 하면 latest 모델만 불러올 수 있고 최고 성능의 모델은 불러올 수 없음

# 모델 가중치(.pt) 추가 저장 - Trainer()를 통해서 저장되긴하는데,
model.to("cpu")  # 저장 전에 CPU로 이동하고
torch.save(model.state_dict(), "/data/seungmin/test/whisper_model/test/whisper_finetuned.pt") # 훈련이 끝난 후의 모델 가중치만 .pt 형태로 저장 - inference-only 용도로 쓰기 위하여
os.makedirs("/data/seungmin/test/whisper_model/test", exist_ok=True) # 디렉토리 없으면 생성
'''

print("학습 완료 및 모델 저장 완료.")
