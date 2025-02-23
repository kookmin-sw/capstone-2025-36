import io
import pickle
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from time import sleep, time
from typing import List, Optional, Tuple

import datasets
import pandas as pd
import win32clipboard as clipboard
from bs4 import BeautifulSoup
from pyhwpx import Hwp


@dataclass
class Table:
    html: str
    row: int
    col: int


logger = datasets.logging.get_logger()


def _get_html_from_clipboard(max_retries: int = 10) -> Optional[str]:
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

            return html_table
        except Exception as e:
            if attempt < max_retries:
                sleep(0.1)
            else:
                logger.debug(
                    f"Failed to access clipboard after {max_retries} attempts"
                )
                raise e
        finally:
            try:
                # 종종 clipboard가 닫히지 않는 경우가 있음.
                clipboard.CloseClipboard()
            except BaseException as e:  # noqa: F841
                pass

    return None


def _extract_html_table(
    hwp_dir_path: Path, hwp: Hwp
) -> Tuple[List[Table], float]:
    def get_row_col_num(hwp: Hwp) -> Tuple[int, int]:
        # get_row_num, get_col_num의 기능은 겹침. 단순 RowCount냐, ColCount의 차이임. 속도 개선을 위해 이 부분을 간소화 함.
        cur_pos = hwp.get_pos()
        hwp.SelectCtrlFront()
        t = hwp.GetTextFile("HWPML2X", "saveblock")
        root = ET.fromstring(t)
        table = root.find(".//TABLE")
        row_count = int(table.get("RowCount"))
        col_count = int(table.get("ColCount"))
        hwp.set_pos(*cur_pos)
        return (row_count, col_count)

    table_ls = list()
    time_ls = list()
    for hwp_file_path in hwp_dir_path.glob("*.hwp"):
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

                # NOTE: 나중에 알게 되었는데, 이거 부정확 함.
                #       row 10개를 1개로 판단하거나 그럼, 이건 그냥 df로 해서 확인하는게 가장 정확할 듯.
                # row_num, col_num = get_row_col_num(hwp)

                # read_html으로 파싱 되는지 확인 한번 함.
            except BaseException as e:
                logger.debug(f"table 추출 중 다음과 같은 애러가 발생: {e}")
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

        pickle_save_path = hwp_file_path.parent.joinpath(
            f"{hwp_file_path.stem}.pickle"
        )
        pickle_save_path.write_bytes(pickle.dumps(one_file_table_ls))
        time_ls.extend(extract_time_ls)

    mean_time = sum(time_ls) / len(time_ls)
    return (table_ls, mean_time)
