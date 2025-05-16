import json
import os
from datasets import Dataset, DatasetDict, Audio

# sample
# train_dir = "/data/seungmin/dataset/sample/training/"
# valid_dir = "/data/seungmin/dataset/sample/validation/"

k12_train_dir = "/data/seungmin/dataset/k12_training_processed/number_and_english/"
k12_valid_dir = "/data/seungmin/dataset/k12_validation_processed/number_and_english/"

# 추가된 데이터셋 경로
univ_train_dir = "/data/seungmin/dataset/kr_univ_training_processed/number_and_english/"
univ_valid_dir = "/data/seungmin/dataset/kr_univ_validation_processed/number_and_english/"


# txt 파일을 학습 데이터로 쓸 때
def load_txt_label_data(data_dir):
    audio_paths = []
    texts = []

    for file in os.listdir(data_dir):
        if file.endswith(".wav"):
            audio_file = os.path.join(data_dir, file)
            text_file = audio_file.replace(".wav", ".txt")
            if os.path.exists(text_file):
                with open(text_file, "r", encoding="utf-8") as f:
                    text = f.read().strip()
                audio_paths.append(audio_file)
                texts.append(text)

    return Dataset.from_dict({"audio": audio_paths, "text": texts})

# json 파일을 학습 데이터로 쓸 때
def load_json_label_data(data_dir):
    audio_paths = []
    texts = []

    for file in os.listdir(data_dir):
        if file.endswith(".wav"):
            audio_file = os.path.join(data_dir, file)
            json_file = audio_file.replace(".wav", ".json")
            if os.path.exists(json_file):
                with open(json_file, "r", encoding="utf-8") as f:
                    json_data = json.load(f)
                text = json_data.get("06_transcription", {}).get("1_text", "").strip()
                if text:
                    audio_paths.append(audio_file)
                    texts.append(text)

    return Dataset.from_dict({"audio": audio_paths, "text": texts})


def prepare_datasets(use_k12=True, use_univ=False):
    train_audio = []
    train_text = []
    valid_audio = []
    valid_text = []

    if use_k12:
        print("k12 훈련 데이터 로딩 중")
        k12_train = load_txt_label_data(k12_train_dir)
        train_audio += k12_train["audio"]
        train_text += k12_train["text"]

        print("k12 검증 데이터 로딩 중")
        k12_valid = load_txt_label_data(k12_valid_dir)
        valid_audio += k12_valid["audio"]
        valid_text += k12_valid["text"]

    if use_univ:
        print("univ 훈련 데이터 로딩 중")
        univ_train = load_json_label_data(univ_train_dir)
        train_audio += univ_train["audio"]
        train_text += univ_train["text"]

        print("univ 검증 데이터 로딩 중")
        univ_valid = load_json_label_data(univ_valid_dir)
        valid_audio += univ_valid["audio"]
        valid_text += univ_valid["text"]

    train_dataset = Dataset.from_dict({"audio": train_audio, "text": train_text}).cast_column("audio", Audio(sampling_rate=16000))
    valid_dataset = Dataset.from_dict({"audio": valid_audio, "text": valid_text}).cast_column("audio", Audio(sampling_rate=16000))

    return DatasetDict({"train": train_dataset, "validation": valid_dataset})


if __name__ == "__main__":
    
    
    # 사용하고자 하는 데이터에 True로하면 됨. 둘 다 사용하려면 T/T
    datasets = prepare_datasets(use_k12=True, use_univ=False)
    # pytorch의 dataloader는 기본적으로 shuffle = True를 사용해서 학습 시에는 데이터 순서를 무작위로 섞음
    print("데이터셋 로딩 완료")
    print(datasets)