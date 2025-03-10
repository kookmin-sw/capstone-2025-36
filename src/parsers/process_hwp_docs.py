import io
import time
from pathlib import Path
from typing import List, Dict
from pyhwpx import Hwp
import pandas as pd

from utils.logger import init_logger
from parsers.clipboard import get_table_from_clipboard, get_image_from_clipboard
from parsers.table_parser import Table
from parsers.equ_parser import extract_latex_list


logger = init_logger(__file__, "DEBUG")


class HwpController:
    def __init__(self) -> None:
        self.hwp = Hwp(visible=False)
        self.total_time = 0
        self.docs_count = 0
    

    def __del__(self) -> None:
        self._close_hwp_file()


    def get_tag_from_html(self, hwp_path: Path) -> Dict[str, List]:
        self._open_hwp_file(hwp_path)
    
        self.one_file_table_list = {}
        self.one_file_images = {}
        self.one_file_equations = []
        
        start = time.time()
        table_cnt = 0

        # Latex 수식을 우선 추출
        self.hwp_equation = []
        for ctrl in self.hwp.ctrl_list:
            if ctrl.UserDesc == "수식":
                self._copy_ctrl(ctrl)
                try: 
                    self.hwp_equation.append(ctrl.Properties.Item('VisualString'))
        
                except Exception as e:
                    logger.error(f"EqualationExtractionError: {str(e)}")
        
        self.one_file_equations = extract_latex_list(self.hwp, self.hwp_equation)

        for ctrl in self.hwp.ctrl_list:
            if ctrl.UserDesc == "표":
                self._copy_ctrl(ctrl)
                try:
                    html = get_table_from_clipboard()
                    table_df = pd.read_html(io.StringIO(html))[0]
                    row_num, col_num = table_df.shape
                        
                except BaseException as e:
                    logger.error(f"TableExtractionError: Failed to extract table: {e}")
                    continue

                if not row_num or not col_num:
                    continue
                
                table_cnt += 1
                self.one_file_table_list[table_cnt] = html
            
            elif ctrl.UserDesc == "그림":
                self._copy_ctrl(ctrl)
                try:
                    img_tmp_path = Path(get_image_from_clipboard())
                    if not img_tmp_path:
                        continue   
                    self.one_file_images[str(img_tmp_path)] = ''    

                except Exception as e:
                    logger.error(f"ImageExtractionError: {str(e)}")

        process_time = time.time()-start

        self.total_time += process_time

        logger.info(f"Success extract from hwp file: {process_time}")

        return {
            "tables": self.one_file_table_list,
            "images": self.one_file_images,
            "equals": self.one_file_equations
        }

    def get_process_time(self) -> int:
        return round(self.total_time / self.docs_count, 2)
    
    def _open_hwp_file(self, hwp_path: Path) -> None:
        self.hwp.open(hwp_path.as_posix())
        logger.info(f"Hwp {hwp_path} loading")
    
    def _close_hwp_file(self) -> None:
        self.hwp.Clear(option=1)
        self.hwp.quit()
    
    def _copy_ctrl(self, ctrl: 'Hwp.ctrl'):
        # 글자처럼 취급 적용 (속성 미적용시 표를 넘어가기도 함)
        prop = ctrl.Properties
        prop.SetItem("TreatAsChar", True)
        ctrl.Properties = prop

        # hwp로 현재 ctrl 위치에 있는 부분 복사
        self.hwp.SetPosBySet(ctrl.GetAnchorPos(0))
        self.hwp.HAction.Run("SelectCtrlFront")
        self.hwp.HAction.Run("Copy")

    def extract_text(self) -> str:
        txt = ""
        try:
        # 문서 전체를 텍스트 포함 모든 컨트롤을 탐색함
            self.hwp.InitScan(0x000F, 0x0077)

            while True:
                textdata = self.hwp.GetText()
                if textdata[0] == 1:
                    break

                # 201 = moveScanPos로 GetText 실행한 위치로 이동함
                self.hwp.MovePos(201, 0, 0)

                # 현재 위치의 상위 컨트롤을 구함
                parent_ctrl = self.hwp.ParentCtrl

                if not parent_ctrl:  # 일반 문장(paragraph)
                    txt = txt + textdata[1]
                    continue

                ctrlch = parent_ctrl.CtrlCh

                # 11 = 그리기 개체, 표
                if ctrlch == 11:
                # 상위 컨트롤이 '표'
                    if parent_ctrl.CtrlID == "tbl":
                        continue

                txt = txt + textdata[1]
        finally:
            self.hwp.ReleaseScan()

            return txt
    
