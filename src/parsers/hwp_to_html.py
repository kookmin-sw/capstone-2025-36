import os
import io
import pickle
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path
from time import sleep, time
from typing import List, Optional, Tuple
import pandas as pd
import win32clipboard as clipboard
from bs4 import BeautifulSoup
from pyhwpx import Hwp

from utils.logger import init_logger
from parsers.table_parser import Table


logger = init_logger(__file__, "DEBUG")


def _get_tag_from_clipboard(tag: str, max_retries: int = 10) -> Optional[str]:
    """
    클립보드에서 html table을 가져옵니다.

    :param max_retries: 클립보드에서 접근 시도하는 횟수 제한
    :return: 클립보드에서 가져온 HTML 테이블 문자열
    :raises Exception: 클립보드 접근 실패 시 예외 발생
    """
    for attempt in range(1, max_retries):
        try:
            clipboard.OpenClipboard()
            html_format = clipboard.RegisterClipboardFormat("HTML Format")
            html = clipboard.GetClipboardData(html_format)
            clipboard.EmptyClipboard()
            clipboard.CloseClipboard()

            html = html.decode("utf-8", errors="ignore")
            html_soup = BeautifulSoup(html, "html.parser")
            html_tag = html_soup.find("html").find(tag)

            if tag == 'img':
                img_src = html_tag['src']
                return img_src[8:] if img_src.startswith("file:///") else img_src
            
            html_tag = html_tag.encode().decode("utf-8")
            logger.info(f"Success to get {tag} from clipboard")

            return html_tag
        except Exception as e:
            if attempt < max_retries:
                sleep(0.1)
            else:
                logger.error(f"Failed to access clipboard after {max_retries} attempts")
                raise e
        finally:
            try:
                # 종종 clipboard가 닫히지 않는 경우가 있음.
                clipboard.CloseClipboard()
            except BaseException as e:  # noqa: F841
                pass

    return None


def _extract_html_table(hwp_dir_path: Path, output_dir_path, hwp: Hwp) -> Tuple[List[Table], List[str]]:
    table_ls = list()
    img_ls = list()

    output_dir_path = Path(output_dir_path) / hwp_dir_path.stem
    if not output_dir_path.exists():
        output_dir_path.mkdir(parents=True)

    for hwp_file_path in hwp_dir_path.glob("*.hwp"):
        logger.info(f"Hwp {hwp_file_path} 확인 중")
        hwp.open(hwp_file_path.as_posix())

        one_file_table_ls = list()

        ctrl = hwp.HeadCtrl
        while ctrl:
            if ctrl.UserDesc == "표" or ctrl.UserDesc == "그림":
                hwp.SetPosBySet(ctrl.GetAnchorPos(0))
                hwp.HAction.Run("SelectCtrlFront")
                hwp.HAction.Run("Copy")

                if ctrl.UserDesc == "표":
                    try:
                        html = _get_tag_from_clipboard(tag="table")
                        hwp.ShapeObjTableSelCell()
                        table_df = pd.read_html(io.StringIO(html))[0]
                        row_num, col_num = table_df.shape
                        
                    except BaseException as e:
                        logger.error(f"table 추출 중 다음과 같은 애러가 발생: {e}")
                        ctrl = ctrl.Next
                        continue

                    if not row_num or not col_num:
                        ctrl = ctrl.Next
                        continue

                    table = Table(html=html, col=col_num, row=row_num)

                    one_file_table_ls.append(table)
                elif ctrl.UserDesc == "그림":
                    try:
                        img_src = _get_tag_from_clipboard(tag="img")
                        img_save_path = output_dir_path / f"{hwp_file_path.stem}_{len(img_ls)+1}.jpg"
                        img_ls.append(img_save_path)
                        shutil.copy(img_src, img_save_path)

                    except BaseException as e:
                        logger.error(f"image 추출 중 다음과 같은 애러가 발생: {e}")
                        ctrl = ctrl.Next
                        continue

                ctrl = ctrl.Next

            else:
                ctrl = ctrl.Next
                continue

        table_ls.extend(one_file_table_ls)

        pickle_save_path = output_dir_path / f"{hwp_file_path.stem}.pickle"
        pickle_save_path.write_bytes(pickle.dumps(one_file_table_ls))

    return table_ls, img_ls
