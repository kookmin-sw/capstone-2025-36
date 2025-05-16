from transformers import WhisperForConditionalGeneration, WhisperProcessor

def load_model_and_processor(model_path="/data/seungmin/모델백업/kr_univ-5epoch-CER20"):
    model = WhisperForConditionalGeneration.from_pretrained(model_path)
    processor = WhisperProcessor.from_pretrained(model_path)

    # generation_config 업데이트: no_timestamps_token_id 설정
    if not hasattr(model.generation_config, "no_timestamps_token_id"):
        try:
            no_ts_token = processor.tokenizer.no_timestamps_token
        except AttributeError:
            no_ts_token = "<|notimestamps|>"
        model.generation_config.no_timestamps_token_id = processor.tokenizer.convert_tokens_to_ids(no_ts_token)

    return model, processor
