from pathlib import Path


# DIR PATHS
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = ROOT_DIR / "assets" / "input"
OUTPUT_DIR = ROOT_DIR / "assets" / "output"
OUTPUT_JSON = OUTPUT_DIR / "output.json"

# 추출할 Ctrl obj
CTRL_TYPES = ["표", "그림", "수식"]