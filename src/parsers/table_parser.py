import re
from typing import List, Dict
from bs4 import BeautifulSoup
from collections import deque
from langchain_ollama import ChatOllama
from dataclasses import dataclass
from utils.logger import init_logger


logger = init_logger(__file__, "DEBUG")


@dataclass
class Table:
    html: str
    row: int
    col: int


class TableParser:
    def __init__(self) -> None:
        pass

    def parse_table_from_html(self, html: str) -> Dict:
        """
        Table 객체를 Dict 형식으로 변환합니다.

        :param table: 변환할 Table 객체
        :return: 변환된 Dict
        :raises Exception: 변환 과정에서 오류 발생 시 예외 처리
        """
        row_len, col_len = self._get_row_and_column_length(html)

        table = Table(html, row_len, col_len)
        if not table:
            logger.warning("Table is Empty")

        matrix = self._html_to_matrix(table)
        if row_len == 1 and col_len == 1:  # 문자 하나만 존재할 경우
            return matrix[0][0]

        return self._convert_matrix_to_dict(matrix)
    
    def _convert_matrix_to_dict(self, matrix: List[List]) -> Dict:
        header_row = matrix[0]
        second_row = matrix[1]

        header_counts = set()
        has_duplicates = False

        for header in header_row:
            if header in header_counts:
                has_duplicates = True
                break
            else:
                header_counts.add(header)

        keys = []
        seen_keys = set()
        for i, (header, value) in enumerate(zip(header_row, second_row)):
            if has_duplicates:
                base_key = f"{value}_{header}" if value is not None and value != header else header
                key = base_key
                if key in seen_keys:
                    key = f"{base_key}_{i}"
            else:
                key = header

            keys.append(key)
            seen_keys.add(key)

        result = {key: [] for key in keys}
        start = 1 if not has_duplicates else 2
        for row in matrix[start:]:
            for i, value in enumerate(row):
                if i < len(keys):
                    result[keys[i]].append(value)

        return result
    
    def _get_row_and_column_length(self, html: str):
        soup = BeautifulSoup(html, "html.parser")
        table_html = soup.find("table")

        rows = table_html.find_all("tr")
        row_len = len(rows)

        col_lens = []

        for row in rows:
            col_len = 0
            for cell in row.find_all(["th", "td"]):
                colspan = int(cell.get("colspan", 1))
                if colspan > 1:
                    col_len += (colspan-1)
                col_len += 1
            col_lens.append(col_len)
        return row_len, max(col_lens)

    def _html_to_matrix(self, table: Table) -> List[List]:
        soup = BeautifulSoup(table.html, "html.parser")
        table_html = soup.find("table")

        if not table_html:
            return []
        
        matrix = []
        rowspan_tracker = {}

        for row in table_html.find_all("tr"):
            row_data = []
            col_idx = 0
                
            cells = deque(row.find_all(["th", "td"]))
            while col_idx < table.col:
                while col_idx in rowspan_tracker:
                    row_data.append(rowspan_tracker[col_idx]["value"])
                    rowspan_tracker[col_idx]["remaining_rows"] -= 1
                    if rowspan_tracker[col_idx]["remaining_rows"] == 0:
                        del rowspan_tracker[col_idx]
                    col_idx += 1
                
                if col_idx >= table.col:
                    break

                if cells:
                    cell = cells.popleft()

                    cell_value = cell.get_text(strip=True)
                    rowspan = int(cell.get("rowspan", 1))
                    colspan = int(cell.get("colspan", 1))

                    if colspan > 1:
                        for _ in range(colspan-1):
                            row_data.append(cell_value)
                            col_idx += 1

                    if rowspan > 1:
                        rowspan_tracker[col_idx] = {
                            "remaining_rows": rowspan - 1,
                            "value": cell_value
                        }

                    row_data.append(cell_value)

                else:
                    row_data.append(None)

                col_idx += 1
            
            matrix.append(row_data)
            
        return matrix


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
