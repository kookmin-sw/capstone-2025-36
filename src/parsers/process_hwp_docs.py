import io
import time
import re
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

        self.image_cnt = 0
        self.table_cnt = 0
        self.equation_cnt = 0
        
        table_cnt = 1
        image_count = 1

        # Latex 수식을 우선 추출
        self.hwp_equation = []
        for ctrl in self.hwp.ctrl_list:
            if ctrl.UserDesc == "수식":
                self.equation_cnt += 1
                self._copy_ctrl(ctrl)
                try:
                    self.hwp_equation.append(ctrl.Properties.Item('VisualString'))
                    
                    self.hwp.move_to_ctrl(ctrl)
                    self.hwp.insert_text(f'{{equation_{self.equation_cnt}}}')
        
                except Exception as e:
                    logger.error(f"EquationExtractionError: {str(e)}")
        
        self.one_file_equations = extract_latex_list(self.hwp, self.hwp_equation)

        for ctrl in self.hwp.ctrl_list:
            if ctrl.UserDesc == "표":
                self.table_cnt += 1
                self.hwp.move_to_ctrl(ctrl)
                self.hwp.insert_text(f'{{table_{self.table_cnt}}}')
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

                self.one_file_table_list[self.table_cnt] = html
            
            elif ctrl.UserDesc == "그림":
                # 이미지가 '글과 겹치게 하여 글 뒤로'로 설정 되어 있으면 워터마크이기 때문에 추출하지 않는다.
                if ctrl.Properties.Item("TextWrap") == 2:
                    continue

                self.image_cnt += 1
                self._copy_ctrl(ctrl)
                try:
                    img_tmp_path = Path(get_image_from_clipboard())
                    if not img_tmp_path:
                        continue   
                    with img_tmp_path.open("rb") as f:
                        img_data = f.read()
    
                    self.one_file_images[f"image_{self.image_cnt}"] = img_data
                    
                    self.hwp.move_to_ctrl(ctrl)
                    self.hwp.insert_text(f'{{image_{self.image_cnt}}}')  

                except Exception as e:
                    logger.error(f"ImageExtractionError: {str(e)}")
        

        process_time = time.time()-start

        self.total_time += process_time

        logger.info(f"확인된 수식 개수 : {self.equation_cnt} / 추출된 수식 개수 : {len(self.one_file_equations)}")
        logger.info(f"확인된 표 개수 : {self.table_cnt} / 추출된 표 개수 : {len(self.one_file_table_list)}")
        logger.info(f"확인된 이미지 개수 : {self.image_cnt} / 추출된 이미지 개수 : {len(self.one_file_images)}")

        logger.info(f"Success extract from hwp file: {process_time}")

        return {
            "tables": self.one_file_table_list,
            "images": self.one_file_images,
            "equals": self.one_file_equations,
            "content": self.extract_text()
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
    
    def get_img_with_binary(img_path: Path) -> bytes:
        """
        image Path를 토대로 binary 형태로 변환하는 코드

        Args:

        Returns:

        """


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

            return re.sub(r'(\n\s*){3,}', '\n\n\n', txt)
    
