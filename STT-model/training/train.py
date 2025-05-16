import torch
from transformers import (WhisperProcessor, WhisperForConditionalGeneration, Seq2SeqTrainingArguments, Seq2SeqTrainer, TrainerCallback)
from dataclasses import dataclass
from typing import Any, Dict, List, Union
from prepare_dataset import prepare_datasets
import evaluate


import os

os.environ["HF_HOME"] = "/data/seungmin/huggingface_cache"
os.environ["TRANSFORMERS_CACHE"] = "/data/seungmin/huggingface_cache"
os.environ["HF_DATASETS_CACHE"] = "/data/seungmin/huggingface_cache"


# gpu 사용 설ㅓ정
device = torch.device("cuda:1" if torch.cuda.is_available() else "cpu")
print("device : ", device)


'''
    학습을 이어서 재개하려면 checkpoint_path를 채워넣고 [A] 부분을 활성화, 새로운 모델로 학습하려면 [B] 부분을 활성화
'''
    # [A] : checkpoint 불러와서 학습 재개하기
# checkpoint_path = "/data/seungmin/test/0326_k12-5epoch/whisper_model/checkpoint-1473"
# model = WhisperForConditionalGeneration.from_pretrained(checkpoint_path).to(device)
# # processor는 백업 디렉토리에서 로드해야 함
# processor = WhisperProcessor.from_pretrained("/data/seungmin/모델백업/0326_k12-5epoch20250326_155303", language="Korean", task="transcribe")




    # [B] : 새로운 모델로 학습하기
# # Whisper 모델 로드 - 
# model_name = "SungBeom/whisper-small-ko"
model_name = "openai/whisper-large-v2"
model = WhisperForConditionalGeneration.from_pretrained(model_name).to(device) 
processor = WhisperProcessor.from_pretrained(model_name, language="Korean", task="transcribe")

# suppress_tokens을 None으로 설정하여 기본값을 유지 - Whisper 모델의 generation_config.suppress_tokens 리스트가 비어 있어서 [-2] 인덱스 접근 시 오류 발생하던 에러를 해결하는 코드
model.config.suppress_tokens = None # 하지만 이대로 하면 아래의 유의성 경고 창이 뜸(에러는 아님)

# model.generation_config.suppress_tokens = None

# 데이터셋 준비 - prepare_dataset.py를 통해서 가져옴
datasets = prepare_datasets()

# 데이터 전처리 함수 (Whisper input 맞추기)
def preprocess(batch):
    audio = batch["audio"]
    
    # 30초 이상 오디오 제거
    max_duration_sec = 30
    if len(audio["array"]) > max_duration_sec * audio["sampling_rate"]:
        return None  # datasets.map에서 None을 반환하면 자동 필터됨

    # Whisper 입력 feature 생성
    batch["input_features"] = processor.feature_extractor(
        audio["array"], sampling_rate=audio["sampling_rate"]
    ).input_features[0]

    # 텍스트 토큰화
    batch["labels"] = processor.tokenizer(batch["text"]).input_ids
    
    return batch

# 데이터셋 전처리 적용 (학습 데이터로써 사용하기 위해 map 형태로 변환하는데, 이 과정에서 CPU 코어 개수 따라 num_proc 조정 가능 - 데이터셋이 커질수록 병렬 처리 어려우니 참고)
datasets = datasets.map(preprocess, remove_columns=datasets["train"].column_names, num_proc=None) # num_proc > 1 --> multiprocessing

# 데이터 Collator 정의
@dataclass
class DataCollatorSpeechSeq2SeqWithPadding:
    processor: Any

    def __call__(self, features: List[Dict[str, Union[List[int], torch.Tensor]]]) -> Dict[str, torch.Tensor]:
        input_features = [{"input_features": f["input_features"]} for f in features]
        batch = self.processor.feature_extractor.pad(input_features, return_attention_mask=True, return_tensors="pt")

        label_features = [{"input_ids": f["labels"]} for f in features]
        labels_batch = self.processor.tokenizer.pad(label_features, return_tensors="pt")

        labels = labels_batch["input_ids"].masked_fill(labels_batch.attention_mask.ne(1), -100)

        if (labels[:, 0] == self.processor.tokenizer.bos_token_id).all().cpu().item():
            labels = labels[:, 1:]

        batch["labels"] = labels
        return batch

data_collator = DataCollatorSpeechSeq2SeqWithPadding(processor=processor)

# 평가 지표 로드 (CER 및 WER)
cer_metric = evaluate.load("cer")
wer_metric = evaluate.load("wer")

# 평가 지표 계산 함수
def compute_metrics(pred):
    pred_ids = pred.predictions
    label_ids = pred.label_ids
    
    # # 평가지표 gpu로 이동하여 계산
    # pred_ids = torch.tensor(pred.predictions).to(device)  
    # label_ids = torch.tensor(pred.label_ids).to(device)

    label_ids[label_ids == -100] = processor.tokenizer.pad_token_id

    pred_str = processor.tokenizer.batch_decode(pred_ids, skip_special_tokens=True)
    label_str = processor.tokenizer.batch_decode(label_ids, skip_special_tokens=True)
    
    print("Decoded Predictions:", pred_str[:3])
    print("Decoded Labels:", label_str[:3])

    cer = 100 * cer_metric.compute(predictions=pred_str, references=label_str)
    wer = 100 * wer_metric.compute(predictions=pred_str, references=label_str)

    return {"cer": cer, "wer": wer}


# 학습 중 train loss, eval loss, CER, WER 출력
class CustomCallback(TrainerCallback):
    def on_log(self, args, state, control, logs=None, **kwargs):
        if logs is not None:
            train_loss = logs.get("loss", "N/A")
            eval_loss = logs.get("eval_loss", "N/A")
            cer = logs.get("eval_cer", "N/A")
            wer = logs.get("eval_wer", "N/A")

            print(f"Step {state.global_step}:")
            print(f"Train Loss: {train_loss}")
            print(f"Validation Loss: {eval_loss}")
            
            # 타입 체크해서 CER, WER가 존재할 때만 출력
            if isinstance(cer, float) and isinstance(wer, float):
                print(f"CER: {cer:.3f} | WER: {wer:.3f}")
            else:
                print("CER: N/A | WER: N/A")
                
            print("-" * 50)
            
            

# 학습 설정 (TrainingArguments)
training_args = Seq2SeqTrainingArguments(
    
    # 기본적인 설정들
    output_dir="/data/seungmin/test/0501/whisper_model", # if) 첫 학습시, 저장 할 경로 / if) 재개 시, 이어서 학습을 하고자 할 때 참조가 되는 경로임
    per_device_train_batch_size=8, # 한 개의 GPU(디바이스)당 학습에 사용하는 배치 크기
    gradient_accumulation_steps=4, #  그래디언트 업데이트를 2번의 미니 배치 동안 누적한 후 한 번의 옵티마이저 업데이트를 수행 --> 실질적인 배치 크기 : per_device_train_batch_size × gradient_accumulation_steps = 32
    num_train_epochs=1,
    
    # 평가, 로깅
    eval_strategy="steps", # 학습 도중 언제마다 평가할지 - 스텝마다 평가 
    eval_steps=100, # 
    logging_steps=10, # n스텝마다 로깅 정보 출력 - [loss 값 / lr / mem usage]
    
    
    # 학습 
    fp16=True, # 32 bit fp가 아닌 16 bit fp로 불러와서 mem usage 개선, 학습 속도 개선
    learning_rate=5e-5,
    warmup_steps=500, # 학습 초반 n스텝동안 linear하게 lr을 증가시켜서 급격한 weight 변화를 방지
    
    
    # checkpoint, 모델 저장
    save_steps=100, # 모델 저장 스텝 주기기
    save_total_limit=7, # 최신 n개만 유지하고 오래된 모델 삭제 - storage 절약
    load_best_model_at_end=True, #  학습이 끝난 후 가장 좋은 성능을 보인 모델
    
    
    # 생성 기반 모델 설정 - whisper
    predict_with_generate=True, # 평가 시 generate()를 사용하여 시퀀스를 생성 - whipser는 s2s이라서 필요
    generation_max_length=225,
    
    # best model 선정 기준
    metric_for_best_model="cer", # WER도 사용하지만, CER을 우선으로 함(이유는 찾아보기~)
    greater_is_better=False, # CER는 에러율이므로, 낮을수록 == 좋은 값
    
    # 이전에 저장된 체크포인트에서 재시작 - trainer.train() 실행 시 output_dir 안에 있는 가장 최근의 checkpoint에서 자동으로 학습을 재개함
    resume_from_checkpoint=True, 
        # output_dir에 checkpoint가 없으면, resume_from_checkpoint=True는 무시됨 → 처음부터 학습 시작
        # 반대로 checkpoint는 있는데 resume_from_checkpoint=False면 → 새로 덮어쓰기 시작하니 주의하기
        # 새로운 데이터셋으로 학습하려면 False
)

# Trainer 정의
trainer = Seq2SeqTrainer(
    model=model,
    args=training_args,
    train_dataset=datasets["train"],
    eval_dataset=datasets["validation"],
    tokenizer=processor.feature_extractor,
    data_collator=data_collator,
    compute_metrics=compute_metrics,
    callbacks=[CustomCallback()],
)



# # 학습 시작
    # 학습 전 캐시 정리
torch.cuda.empty_cache()
# if 학습 처음 시)
trainer.train()

# if 학습 재개 시) 학습 재개를 명시적으로 지정
# trainer.train(resume_from_checkpoint=checkpoint_path)



'''--------------------------- 최종 모델만 따로 깔끔하게 추론/배포 용도로 저장------------------- '''



from datetime import datetime # 현재 날짜 및 시간 기반 디렉토리 생성
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")  # ex) 20250321_1043
print("timestamp : ", timestamp)
export_dir = f"/data/seungmin/모델백업/0326_k12-5epoch{timestamp}"
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
