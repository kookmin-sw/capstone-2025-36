import pickle
from pathlib import Path
from typing import List
from utils.logger import init_logger


logger = init_logger(__file__, "DEBUG")


def save_data_from_pickling(data_path: Path, data: List) -> None:
    try:
        with data_path.open("wb") as f:
            pickle.dump(data, f)
        logger.info(f"Success save {data_path}")
    except Exception as e:
        logger.error(f"Failed save {data_path}: {str(e)}")


def get_data_from_pickling(data_path: Path) -> List:
    try:
        with data_path.open("rb") as f:
            loaded_data = pickle.load(f)
        logger.info(f"Success load {data_path}")
    except Exception as e:
        logger.error(f"Failed load {data_path}: {str(e)}")

    return loaded_data