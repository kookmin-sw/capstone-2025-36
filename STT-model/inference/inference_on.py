# inference_on.py
import torch
import numpy as np
import re
import io
import ffmpeg
import soundfile as sf

def load_audio_wav(file_path):
    audio, sr = sf.read(file_path)
    if audio.ndim > 1:
        audio = np.mean(audio, axis=1)  # stereo → mono
    return audio, sr

def load_audio_ffmpeg(file_path, target_sr=16000):
    try:
        out, err = (
            ffmpeg
            .input(file_path)
            .output('pipe:', format='wav', acodec='pcm_s16le', ac=1, ar=target_sr)
            .run(capture_stdout=True, capture_stderr=True)
        )
    except ffmpeg.Error as e:
        print("FFmpeg error:", e)
        raise e
    audio, sr = sf.read(io.BytesIO(out))
    return audio, sr

def format_time(seconds: float) -> str:
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"

def split_sentences_with_timestamps(text: str, seg_start: float, seg_end: float, chunk_size: int = 10):
    sentences = re.split(r'(?<=[.?!])\s+', text.strip())
    if len(sentences) == 1:
        words = text.split()
        if len(words) > chunk_size:
            sentences = [
                ' '.join(words[i:i+chunk_size]) 
                for i in range(0, len(words), chunk_size)
            ]
    if not sentences or sentences == ['']:
        return []

    total_length = sum(len(s) for s in sentences)
    if total_length == 0:
        total_length = len(sentences)

    seg_duration = seg_end - seg_start
    sentence_boundaries = []
    cumulative = 0
    for s in sentences:
        s_len = len(s)
        start_time = seg_start + (cumulative / total_length) * seg_duration
        cumulative += s_len
        end_time = seg_start + (cumulative / total_length) * seg_duration
        sentence_boundaries.append({
            "start": start_time,
            "end": end_time,
            "text": s
        })
    return sentence_boundaries

def inference_on(file_path, model, processor, segment_length_sec=30):
    sampling_rate = 16000

    # 1) 로드
    if file_path.endswith(".wav"):
        audio, sr = load_audio_wav(file_path)
    else:
        audio, sr = load_audio_ffmpeg(file_path, target_sr=sampling_rate)

    if audio.ndim > 1:
        audio = np.mean(audio, axis=0)

    num_samples = len(audio)
    segment_samples = segment_length_sec * sampling_rate

    print(f"Inference 시작: {file_path}")
    print("전체 오디오 길이(샘플):", num_samples)
    print("세그먼트당 샘플 수:", segment_samples)

    # 2) forced_decoder_ids
    forced_decoder_ids = processor.get_decoder_prompt_ids(language="ko", task="transcribe")
    if not forced_decoder_ids or len(forced_decoder_ids) == 0:
        print("processor.get_decoder_prompt_ids() is empty. Use model.config.forced_decoder_ids instead.")
        forced_decoder_ids = model.config.forced_decoder_ids

    sentence_results = []
    seg_index = 1

    # 3) 30초(기본) 단위로 반복
    for start in range(0, num_samples, segment_samples):
        end = min(start + segment_samples, num_samples)
        segment = audio[start:end]

        # whisper processor로 변환
        inputs = processor(segment, sampling_rate=sampling_rate, return_tensors="pt")
        input_features = inputs["input_features"].to(model.device)

        with torch.no_grad():
            predicted_ids = model.generate(
                input_features,
                forced_decoder_ids=forced_decoder_ids,
                suppress_tokens=None
            )

        transcription = processor.tokenizer.decode(predicted_ids[0], skip_special_tokens=True)

        seg_start = start / sampling_rate
        seg_end = end / sampling_rate
        print(f"Segment {seg_index} 완료. ({format_time(seg_start)} ~ {format_time(seg_end)})")
        seg_index += 1

        # 문장 단위 분리, timestamps
        sentences = split_sentences_with_timestamps(transcription, seg_start, seg_end)
        sentence_results.extend(sentences)

    # 4) 출력 정리
    lines = []
    for sent in sentence_results:
        st = format_time(sent["start"])
        en = format_time(sent["end"])
        txt = sent["text"]
        lines.append(f"({st} ~ {en}) {txt}")
    final_transcription = "\n".join(lines)

    print("\nInference 결과:")
    print(final_transcription)
    return final_transcription
