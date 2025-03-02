import io
from pathlib import Path

import win32clipboard as clipboard
from pyhwpx import Hwp
import pandas as pd

from utils.logger import init_logger
from parsers.table_parser import Table, dataframe_to_json
from parsers.image_ocr import convert_image_to_json
from parsers.clipboard import get_table_from_clipboard, get_image_from_clipboard
from parsers.json_formatter import save_json

from utils.file_handler import get_table_from_pickling
from utils.logger import init_logger


# DIR PATHS
ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "assets" / "test"
OUTPUT_DIR = ROOT_DIR / "assets" / "output"
OUTPUT_PATH = OUTPUT_DIR / "output.json"


logger = init_logger(__file__, "DEBUG")

def main():
    hwp = Hwp()
    
    total_dict = dict()
    ctrls = ["표", "그림"]

    # 결과를 담을 DIR 생성
    if not OUTPUT_DIR.exists():
        OUTPUT_DIR.mkdir(parents=True)

    for HWP_PATH in DATA_DIR.rglob("*.hwp"):
        hwp.open(HWP_PATH.as_posix())
        logger.info(f"Hwp {HWP_PATH} loding")

        doc_name = HWP_PATH.stem

        curr_data = dict()
        table_cnt = 0

        for ctrl in hwp.ctrl_list:
            if ctrl.UserDesc in ctrls:
                # 글자처럼 취급 적용 (속성 미적용시 표를 넘어가기도 함)
                prop = ctrl.Properties
                prop.SetItem("TreatAsChar", True)
                ctrl.Properties = prop

                # hwp로 현재 ctrl 위치에 있는 부분 복사
                hwp.SetPosBySet(ctrl.GetAnchorPos(0))
                hwp.HAction.Run("SelectCtrlFront")
                hwp.HAction.Run("Copy")

                if ctrl.UserDesc == "표":
                    try:
                        html = get_table_from_clipboard()
                        table_df = pd.read_html(io.StringIO(html))[0]
                        row_num, col_num = table_df.shape
                            
                    except BaseException as e:
                        logger.error(f"TableExtractionError: Failed to extract table: {e}")
                        continue

                    if not row_num or not col_num:
                        continue

                    table = Table(html=html, col=col_num, row=row_num)
                    curr_data[f"table_{table_cnt}"] = dataframe_to_json(table)
                    table_cnt += 1
            
                elif ctrl.UserDesc == "그림":
                    try:
                        img_tmp_path = Path(get_image_from_clipboard())
                        if not img_tmp_path:
                            continue
                        
                    except Exception as e:
                        logger.error(f"Image Error: {str(e)}")
                    
                    curr_data[f"image_{img_tmp_path.stem}"] = convert_image_to_json(img_tmp_path)

        total_dict[doc_name] = curr_data        

    save_json(total_dict, OUTPUT_PATH)


if __name__ == "__main__":
    main()