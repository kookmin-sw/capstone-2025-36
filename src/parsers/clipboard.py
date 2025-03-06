import io
import pickle
import shutil
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
from time import sleep, time
from typing import List, Optional, Tuple
import pandas as pd
from bs4 import BeautifulSoup
from pyhwpx import Hwp
import win32clipboard as clipboard
from utils.logger import init_logger
from parsers.table_parser import Table


logger = init_logger(__file__, "DEBUG")


def get_table_from_clipboard() -> Optional[str]:
    html = _get_html_from_clipboard()
    html_soup = BeautifulSoup(html, "html.parser")
    html_tag = html_soup.find("html").find("table")
    
    html_tag = html_tag.encode().decode("utf-8")
    logger.info("Success to get table from clipboard")

    return html_tag


def get_image_from_clipboard() -> Optional[str]:
    html = _get_html_from_clipboard()
    html_soup = BeautifulSoup(html, "html.parser")
    html_tag = html_soup.find("html").find("img")
    
    logger.info("Success to get image from clipboard")
    img_src = html_tag['src']

    return img_src[8:] if img_src.startswith("file:///") else img_src


def _get_html_from_clipboard(max_retries: int = 10) -> str:
    """
    클립보드에서 html을 가져옵니다.

    :param max_retries: 클립보드에서 접근 시도하는 횟수 제한
    :return: 클립보드에서 가져온 HTML 문자열
    :raises Exception: 클립보드 접근 실패 시 예외 발생
    """
    for attempt in range(1, max_retries):
        try:
            clipboard.OpenClipboard()
            html_format = clipboard.RegisterClipboardFormat("HTML Format")
            html = clipboard.GetClipboardData(html_format)
            clipboard.EmptyClipboard()
            clipboard.CloseClipboard()

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
    return html.decode("utf-8", errors="ignore")


def extract_text_exclude_table(hwp_app: Hwp) -> str:
  txt = ""
  try:
    # 문서 전체를 텍스트 포함 모든 컨트롤을 탐색함
    hwp_app.InitScan(0x000F, 0x0077)

    while True:
      textdata = hwp_app.GetText()
      if textdata[0] == 1:
        break

      # 201 = moveScanPos로 GetText 실행한 위치로 이동함
      hwp_app.MovePos(201, 0, 0)

      # 현재 위치의 상위 컨트롤을 구함
      parent_ctrl = hwp_app.ParentCtrl

      if parent_ctrl == None:  # 일반 문장(paragraph)
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
    hwp_app.ReleaseScan()

  return txt