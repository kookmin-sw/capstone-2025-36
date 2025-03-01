import io
import re
import json
from pathlib import Path
from typing import List, Dict
import pandas as pd
from bs4 import BeautifulSoup
from langchain_ollama import ChatOllama
from dataclasses import dataclass
from utils.logger import init_logger

logger = init_logger(__file__, "DEBUG")

@dataclass
class Table:
    html: str
    row: int
    col: int


def get_json_from_tables(tables: List[Table], output_dir: Path) -> List[dict]:
    json_list = []
    for table in tables:
        json_data = _dataframe_to_json(table)
        if json_data:
            json_list.append(json_data)
            _save_table_with_json(json_data, output_dir / "table.json")
    
    return json_list


def _table_to_dataframe(table: Table) -> pd.DataFrame:
    """
    HTML 테이블을 파싱하여 rowspan 정보를 반영한 DataFrame을 반환합니다.

    :param table_html: HTML 형식의 테이블 문자열
    :return: 병합된 행이 반영된 pandas DataFrame
    """
    soup = BeautifulSoup(table.html, "html.parser")
    table = soup.find("table")

    rows = table.find_all("tr")
    data = []
    rowspan_tracker = {}

    for row in rows:
        cols = row.find_all(["td", "th"])
        row_data = []
        col_idx = 0

        for col in cols:
            while col_idx in rowspan_tracker and rowspan_tracker[col_idx] > 0:
                row_data.append(data[-1][col_idx])  # 이전 행 값 복사
                rowspan_tracker[col_idx] -= 1
                col_idx += 1

            rowspan = int(col.get("rowspan", 1))
            text = col.get_text(strip=True)

            row_data.append(text)

            if rowspan > 1:
                rowspan_tracker[col_idx] = rowspan - 1

            col_idx += 1

        data.append(row_data)

    df = pd.DataFrame(data)
    return df


def _dataframe_to_json(table: Table) -> json:
    """
    Table 객체를 JSON 형식으로 변환합니다.

    :param table: 변환할 Table 객체
    :return: 변환된 JSON 문자열
    :raises Exception: 변환 과정에서 오류 발생 시 예외 처리
    """
    df = _table_to_dataframe(table)

    keys = df.iloc[0].astype(str).tolist()
    df = df.iloc[1:].reset_index(drop=True)
    
    empty_ratio = df.isnull().mean().max()

    try:
        json_data = {keys[i]: df.iloc[:, i].astype(str).tolist() for i in range(len(keys))}
        
    except Exception:
        try:
            json_data = _extract_tables_with_llm(table)

        except Exception as e:
            logger.error(f"failed dataframe to json. {e}")

    return json.dumps(json_data, ensure_ascii=False, indent=4)


def _save_table_with_json(json_data: Dict, output_path: Path) -> None:
    """
    JSON 데이터를 파일로 저장하는 함수.
    
    :param json_data: 저장할 JSON 데이터 (Dict 형태)
    :param output_path: 저장할 파일 경로 (Path 객체)
    """
    if output_path.exists():
        with output_path.open('r', encoding='utf-8') as f:
            try:
                existing_data = json.load(f)
            except json.JSONDecodeError:
                existing_data = {}
    else:
        existing_data = {}
    
    table_number = len(existing_data) + 1
    table_key = f"table{table_number}"
    existing_data[table_key] = json_data
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open('w', encoding='utf-8') as f:
        json.dump(existing_data, f, ensure_ascii=False, indent=4)


def _extract_tables_with_llm(table: Table):
    """LLM을 이용하여 table parsing"""
    messages = [
        {"role": "system", "content": """
            아래 html문서에서 테이블 데이터를 JSON으로 변환해주세요. JSON 형식은 다음과 같이 유지되어야 합니다:
            {
                "tables": [
                    {
                        "name": "테이블 제목",
                        "headers": ["열 제목1", "열 제목2", "열 제목3"],
                        "rows": [
                            ["값1", "값2", "값3"],
                            ["값4", "값5", "값6"]
                        ]
                    }
                ]
            }
            JSON 형식 이외의 불필요한 설명은 포함하지 말고 순수한 JSON 데이터만 출력하세요.
        """},
        {"role": "user", "content": f"""
            === 원본 텍스트 ===
            {table.html}
            ==================
            위 html 문서에서 모든 테이블을 JSON으로 변환해줘.
        """}
    ]

    llm = ChatOllama(model="deepseek-r1:8b")

    ai_msg = llm.invoke(messages)
    response_content = ai_msg.content if hasattr(ai_msg, "content") else ai_msg
    if not response_content:
        logger.error("답변을 받지 못했습니다.")
    logger.info(response_content)

    json_pattern = r"```json\n(.*?)\n```"
    match = re.search(json_pattern, response_content, re.DOTALL)
    json_content = match.group(1) if match else None
    return json_content