import torch
import torchaudio
import torchaudio.transforms as T
from transformers import WhisperProcessor, WhisperForConditionalGeneration
import time


processor = WhisperProcessor.from_pretrained("SungBeom/whisper-small-ko")
model = WhisperForConditionalGeneration.from_pretrained("SungBeom/whisper-small-ko")

# .pth 파일에서 가중치 로드
checkpoint_path = "/data/seungmin/0412temp/best_model.pth"
state_dict = torch.load(checkpoint_path, map_location="cpu")
model.load_state_dict(state_dict)

# 디바이스 설정 및 eval
model.to("cuda" if torch.cuda.is_available() else "cpu")
model.eval()

mp4_path = "/data/jinwoo/target_data/emjjk_23.mp4"

def load_audio(mp4_path, target_sample_rate=16000):
    waveform, sample_rate = torchaudio.load(mp4_path)
    if waveform.size(0) > 1:  # Stereo → Mono
        waveform = waveform.mean(dim=0, keepdim=True)
    if sample_rate != target_sample_rate:
        waveform = T.Resample(orig_freq=sample_rate, new_freq=target_sample_rate)(waveform)
    return waveform.squeeze(), target_sample_rate

def chunk_audio(waveform, sample_rate, chunk_duration=30):
    """30초 단위로 오디오를 자르고, 마지막 청크는 패딩을 붙임"""
    chunk_length = sample_rate * chunk_duration
    chunks = []
    for i in range(0, len(waveform), chunk_length):
        chunk = waveform[i : i + chunk_length]
        if len(chunk) < chunk_length:
            padding = torch.zeros(chunk_length - len(chunk))
            chunk = torch.cat([chunk, padding])  # 패딩
        chunks.append(chunk)
    return chunks

start_time = time.time()

waveform, sampling_rate = load_audio(mp4_path)
chunks = chunk_audio(waveform, sampling_rate)

full_transcription = []

# 2) forced_decoder_ids 설정
forced_decoder_ids = processor.get_decoder_prompt_ids(
    language="ko", task="transcribe"
)
# get_decoder_prompt_ids()가 비어 있으면, 모델 설정의 forced_decoder_ids를 사용
if not forced_decoder_ids or len(forced_decoder_ids) == 0:
    forced_decoder_ids = model.config.forced_decoder_ids

for chunk in chunks:
    # feature 추출
    inputs = processor.feature_extractor(
        chunk.numpy(), sampling_rate=sampling_rate, return_tensors="pt"
    )
    input_features = inputs.input_features.to(model.device)

    with torch.no_grad():
        # 3) generate() 시 forced_decoder_ids 적용
        predicted_ids = model.generate(
            input_features,
            forced_decoder_ids=forced_decoder_ids,
            no_repeat_ngram_size=2,
            repetition_penalty=1.2,
            suppress_tokens=None  # 이전 코드처럼 억제토큰 해제하려면 None
        )

    # 4) 디코딩
    transcription = processor.batch_decode(predicted_ids, skip_special_tokens=True)[0]
    full_transcription.append(transcription)

final_text = " ".join(full_transcription)

with open("/data/seungmin/test/inference/result/k12_5epoch.txt", "w", encoding="utf-8") as f:
    print("저장 시작")
    f.write(final_text)

end_time = time.time()
print(f"저장 완료, 소요 시간: {end_time - start_time:.2f}초)")
