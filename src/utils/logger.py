import logging


def init_logger(name:str, level:str) -> logging:
    logger = logging.getLogger(name=name)
    logger.setLevel(level=level)

    formatter = logging.Formatter("| %(levelname)s | %(funcName)s | %(message)s")
    
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    return logger