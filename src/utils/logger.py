import logging


def init_logger(name:str, level:str) -> logging:
    logger = logging.getLogger(name=name)
    logger.setLevel(level)

    formatter = logging.Formatter('|%(asctime)s|==|%(levelname)s| %(funcName)s | %(message)s',
                                datefmt='%Y-%m-%d %H:%M:%S'
                                )

    stream_handler = logging.StreamHandler() ## 스트림 핸들러 생성
    stream_handler.setFormatter(formatter) ## 텍스트 포맷 설정
    
    logger.addHandler(stream_handler) ## 핸들러 등록


    return logger