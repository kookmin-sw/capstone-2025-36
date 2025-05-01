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
