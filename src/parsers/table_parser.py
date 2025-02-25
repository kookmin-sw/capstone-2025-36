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

    return markdown_table
    