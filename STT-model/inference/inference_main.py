# main_inference.py

import os
import torch
from model import load_model_and_processor
from inference_on import inference_on

def main():
    # 모델 및 processor 로드 (수정된 model.py를 통해 fine-tuned 모델 로딩)
    model, processor = load_model_and_processor()

    # 추론 시작
    input_path = "/data/jinwoo/target_data/emjjk_23.mp4"  # mp4 입력 파일
    result_dir = "/data/seungmin/test/inference/result"
    os.makedirs(result_dir, exist_ok=True)

    print("Inference 시작")
    full_transcription = inference_on(input_path, model, processor, segment_length_sec=30)

    result_path = os.path.join(result_dir, "emjjk_23_univ-5epoch.txt")
    with open(result_path, "w", encoding="utf-8") as f:
        f.write(full_transcription)
        
    print(f"Inference 결과 저장 완료: {result_path}")


if __name__ == "__main__":
    main()
