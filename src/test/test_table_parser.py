from bs4 import BeautifulSoup
from typing import Dict, List
import pandas as pd


def build_matrix(html_table: str):
    soup = BeautifulSoup(html_table, "html.parser")
    table = soup.find("table")
    if not table:
        return []
    
    rows = table.find_all("tr")
    matrix = []
    rowspan_tracker = {}  # {col_idx: {remaining_rows: N, value: "cell value"}}
    
    # Process each row
    for row_idx, row in enumerate(rows):
        row_data = []
        col_idx = 0
        cells = row.find_all(["th", "td"])
        
        # Fill in cells from rowspan_tracker
        while col_idx in rowspan_tracker and rowspan_tracker[col_idx]["remaining_rows"] > 0:
            row_data.append(rowspan_tracker[col_idx]["value"])
            rowspan_tracker[col_idx]["remaining_rows"] -= 1
            if rowspan_tracker[col_idx]["remaining_rows"] == 0:
                del rowspan_tracker[col_idx]
            col_idx += 1
        
        # Process actual cells in current row
        for cell in cells:
            while col_idx in rowspan_tracker and rowspan_tracker[col_idx]["remaining_rows"] > 0:
                row_data.append(rowspan_tracker[col_idx]["value"])
                rowspan_tracker[col_idx]["remaining_rows"] -= 1
                if rowspan_tracker[col_idx]["remaining_rows"] == 0:
                    del rowspan_tracker[col_idx]
                col_idx += 1
            
            cell_value = cell.get_text(strip=True)
            rowspan = int(cell.get("rowspan", 1))
            colspan = int(cell.get("colspan", 1))
            
            if rowspan > 1:
                rowspan_tracker[col_idx] = {
                    "remaining_rows": rowspan - 1,
                    "value": cell_value
                }
            
            for _ in range(colspan):
                row_data.append(cell_value)
                col_idx += 1
        
        matrix.append(row_data)
    return matrix


if __name__ == "__main__":
    html_table = """
    <table border="1">
    <thead>
        <tr>
        <th rowspan="2">이름</th>
        <th colspan="2">인적사항</th>
        <th rowspan="2">메모</th>
        </tr>
        <tr>
        <th>나이</th>
        <th>직업</th>
        </tr>
    </thead>
    <tbody>
        <tr>
        <td>김철수</td>
        <td>28</td>
        <td>개발자</td>
        <td rowspan="2">우수 사원</td>
        </tr>
        <tr>
        <td>이영희</td>
        <td>32</td>
        <td>디자이너</td>
        </tr>
        <tr>
        <td>박지민</td>
        <td>25</td>
        <td>마케터</td>
        <td>신입</td>
        </tr>
    </tbody>
    </table>
    """
    print(build_matrix(html_table))