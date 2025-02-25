import io
import pickle
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


def _get_html_from_clipboard(max_retries: int = 10) -> Optional[str]:
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
            html_table = html_soup.find("html").find("table")
            html_table = html_table.encode().decode("utf-8")

            logger.info("Success to get html from clipboard")

            return html_table
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


def _extract_html_table(hwp_dir_path: Path, hwp: Hwp) -> Tuple[List[Table], float]:
    table_ls = list()
    time_ls = list()

    for hwp_file_path in hwp_dir_path.glob("*.hwp"):
        logger.info(f"Hwp {hwp_file_path} 확인 중")
        hwp.open(hwp_file_path.as_posix())

        extract_time_ls = list()
        one_file_table_ls = list()

        ctrl = hwp.HeadCtrl
        while ctrl:
            if ctrl.UserDesc != "표":
                ctrl = ctrl.Next
                continue

            start_time = time()

            hwp.SetPosBySet(ctrl.GetAnchorPos(0))
            hwp.HAction.Run("SelectCtrlFront")
            hwp.HAction.Run("Copy")

            try:
                html = _get_html_from_clipboard()
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
            ctrl = ctrl.Next

            end_time = time()

            extract_time_ls.append(end_time - start_time)
        table_ls.extend(one_file_table_ls)

        #TODO pickling 하는 이유?
        pickle_save_path = hwp_file_path.parent.joinpath(
            f"{hwp_file_path.stem}.pickle"
        )
        pickle_save_path.write_bytes(pickle.dumps(one_file_table_ls))
        time_ls.extend(extract_time_ls)

    mean_time = sum(time_ls) / len(time_ls)
    return (table_ls, mean_time)
