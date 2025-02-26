import io
import pandas as pd
from dataclasses import dataclass
from utils.logger import init_logger

logger = init_logger(__file__, "DEBUG")

@dataclass
class Table:
    html: str
    row: int
    col: int


def get_json_from_table(table: Table):
    df = pd.read_html(io.StringIO(table.html))[0]
    markdown_table = df.to_markdown(index=False)

    is_row = True #TODO 첫번째 row를 Key로 설정 False인 경우 첫번쨰 column이 Key
    df.columns = df.iloc[0]

    if is_row:
        df = df[1:].reset_index(drop=True)
        json_data = df.to_dict(orient="list")
    else:
        df.set_index(df.columns[0], inplace=True)
        json_data = df.apply(lambda row: row.tolist(), axis=1).to_json(force_ascii=False, indent=4)

    # print(json_data)

    return markdown_table
    