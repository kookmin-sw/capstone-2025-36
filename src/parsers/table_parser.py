import io
import re
import json
import pandas as pd
from pandas.api.types import is_integer_dtype
from langchain_ollama import ChatOllama
from dataclasses import dataclass
from utils.logger import init_logger

logger = init_logger(__file__, "DEBUG")

@dataclass
class Table:
    html: str
    row: int
    col: int


def get_json_from_table(table: Table):
    """
    Table 객체를 JSON으로 변환

    - 'index': 개별 행을 키로 변환 (RAG 시스템 및 DB 최적)
    - 'columns': 속성 중심 변환 (분석 및 머신러닝 최적)
    - 'records': 일반적인 JSON 리스트 (REST API 최적)
    """
    df = pd.read_html(io.StringIO(table.html))[0]
    df.columns = df.iloc[0]

    if _get_orient(df) == 'index':
        df = df[1:].reset_index(drop=True)
        json_data = df.to_dict(orient="list")
    elif _get_orient(df) == 'columns':
        df.set_index(df.columns[0], inplace=True)
        json_data = df.apply(lambda row: row.tolist(), axis=1).to_json(force_ascii=False, indent=4)
    else:
        json_data = _extract_tables_from_text(table)

    return json_data


def _get_orient(df: pd.DataFrame) -> str:
    if df.index.is_unique and not is_integer_dtype(df.index):
        return "index"
    elif df.shape[0] > df.shape[1] * 3:
        return 'index'
    elif df.shape[1] > df.shape[0] * 5:
        return 'columns'
    elif (df.dtypes == object).sum() / df.shape[1] > 0.5:
        return 'index'
    else:
        return None


def _extract_tables_from_text(table: Table):
    messages = [
        {"role": "system", "content": """
            아래 문서에서 테이블 데이터를 JSON으로 변환해주세요. JSON 형식은 다음과 같이 유지되어야 합니다:
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