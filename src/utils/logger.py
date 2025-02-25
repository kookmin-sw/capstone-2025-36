import logging


def init_logger(name:str, level:str) -> logging:
    logger = logging.getLogger(name=name)
    logger.setLevel(level=level)

    formatter = logging.Formatter('|%(asctime)s|==|%(levelname)s| %(funcName)s | %(message)s',
                                datefmt='%Y-%m-%d %H:%M:%S'
                                )
    
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    return logger