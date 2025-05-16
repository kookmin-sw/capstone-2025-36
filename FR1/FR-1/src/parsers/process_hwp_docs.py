import io
import time
import re
import base64
from pathlib import Path
from typing import List, Dict
from pyhwpx import Hwp
import pandas as pd
import json

from utils.logger import init_logger
from parsers.clipboard import get_table_from_clipboard, get_image_from_clipboard
from parsers.equ_parser import extract_latex_list
from utils.window_asciimath import modify_init_py

logger = init_logger(__file__, "DEBUG")


class HwpController:
    def __init__(self) -> None:

        modify_init_py()
        self.hwp = Hwp(visible=False)
        self.total_time = 0
        self.docs_count = 0
    

    def __del__(self) -> None:
        self._close_hwp_file()


    def get_tag_from_html(self, hwp_path: Path) -> Dict[str, List]:
        
        self._open_hwp_file(hwp_path)
    
        self.one_file_table_list = {}
        self.one_file_images = {}
        self.one_file_equations = {}

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
        
        for idx, latex in enumerate(extract_latex_list(self.hwp, self.hwp_equation)):
            self.one_file_equations[f"equation_{idx+1}"] = latex

        self.delete_file("eq.mml")

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

                self.one_file_table_list[f"table_{self.table_cnt}"] = html
            
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
                        img_data = base64.b64encode(f.read()).decode("utf-8")
                    self.one_file_images[f"image_{self.image_cnt}"] = img_data
                    
                    self.hwp.move_to_ctrl(ctrl)
                    self.hwp.insert_text(f'{{image_{self.image_cnt}}}')  

                except Exception as e:
                    pass
                    #logger.info(f"Success to get image from clipboard")
        

        process_time = time.time()-start

        self.total_time += process_time

        logger.info(f"확인된 수식 개수 : {self.equation_cnt} / 추출된 수식 개수 : {len(self.one_file_equations)}")
        logger.info(f"확인된 표 개수 : {self.table_cnt} / 추출된 표 개수 : {len(self.one_file_table_list)}")
        logger.info(f"확인된 이미지 개수 : {self.image_cnt} / 추출된 이미지 개수 : {len(self.one_file_images)}")

        logger.info(f"Success extract from hwp file: {process_time}")

        components = {
            "texts": self.extract_text(),
            "equations": self.one_file_equations,
            "tables": self.one_file_table_list,
            "images": self.one_file_images
        }

        return components


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
            try:
                self.hwp.InitScan(0x000F, 0x0077)
            except Exception as e:
                print(f"[Critical Error] InitScan 실패: {e}")
                return ""  # InitScan 안 되면 더 진행 불가, 바로 빠져나가기

            while True:
                try:
                    textdata = self.hwp.GetText()
                except Exception as e:
                    print(f"[Warning] GetText 실패: {e}")
                    break  # 텍스트를 못 읽으면 루프 중단

                if not textdata or textdata[0] == 1:
                    break

                try:
                    self.hwp.MovePos(201, 0, 0)
                except Exception as e:
                    print(f"[Warning] MovePos 실패: {e}")
                    continue  # 다음으로

                try:
                    parent_ctrl = self.hwp.ParentCtrl
                except Exception as e:
                    print(f"[Warning] ParentCtrl 접근 실패: {e}")
                    parent_ctrl = None

                if not parent_ctrl:
                    txt += textdata[1]
                    continue

                try:
                    ctrlch = parent_ctrl.CtrlCh
                    if ctrlch == 11 and parent_ctrl.CtrlID == "tbl":
                        continue  # 표는 건너뛰기
                except Exception as e:
                    print(f"[Warning] Ctrl 정보 읽기 실패: {e}")

                txt += textdata[1]

        except Exception as e:
            print(f"[Critical Error] extract_text 전체 실패: {e}")

        finally:
            try:
                self.hwp.ReleaseScan()
            except Exception as e:
                print(f"[Warning] ReleaseScan 실패: {e}")

        return re.sub(r'(\n\s*){3,}', '\n\n\n', txt)
    
    def delete_file(self, file_path):
        """파일을 삭제하는 함수 (예외 처리 포함)"""
        path = Path(file_path)
        try:
            if path.exists():
                path.unlink()  # 파일 삭제
                logger.info(f"✅ 파일 삭제 완료: {file_path}")
            else:
                logger.error(f"⚠ 파일이 존재하지 않음: {file_path}")
        except PermissionError:
            logger.exception(f"❌ 삭제 실패: {file_path} (권한 문제)")
        except Exception as e:
            logger.exception(f"❌ 삭제 실패: {file_path} (Error: {e})")
