import io
import pandas as pd
from dataclasses import dataclass


@dataclass
class Table:
    html: str
    row: int
    col: int


def get_txt_from_table(table: Table):
    df = pd.read_html(io.StringIO(table.html))[0]

    markdown_table = df.to_markdown(index=False)

    print(markdown_table)