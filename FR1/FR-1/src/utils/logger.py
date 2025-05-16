import logging

def init_logger(name: str, level: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # 이미 핸들러가 추가되어 있는지 확인
    if not logger.handlers:
        formatter = logging.Formatter('|%(asctime)s|==|%(levelname)s| %(funcName)s | %(message)s',
                                      datefmt='%Y-%m-%d %H:%M:%S')

        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

    # 부모 로거로의 전파 방지
    logger.propagate = False

    return logger