from dataclasses import dataclass
from enum import Enum
from typing import List, Literal, Optional

class TextStyle(Enum):
    BOLD      = '1'
    DIM       = '2'
    ITALIC    = '3'
    UNDERLINE = '4'
    BLINK     = '5'
    REVERSE   = '6'
    HIDDEN    = '7'
    STRIKE    = '8'

@dataclass(frozen=True, slots=True)
class Color:
    """ 24-bit Color RGB Dataclass"""
    R: int
    G: int
    B: int

@dataclass
class TableCell:
    text: str
    style: Optional[TextStyle] = None
    align: Literal["left", "right", "center"] = "left"

@dataclass
class TableStyle:
    t: str  = '─'
    tl: str = '┌'
    tr: str = '┐'
    tm: str = '┬'
    b: str  = '─'
    bl: str = '└'
    br: str = '┘'
    bm: str = '┴'
    l: str  = '├'
    lv: str = '│'
    rv: str = '│'
    r: str  = '┤'
    c: str  = '┼'
    v: str  = '│'
    h: str  = '─'

@dataclass
class TableConfig:
    cell_padding: int = 0
    table_width: int = 0
    # cell_widths: List[int] = []
    content_truncate: bool = False
    multi_line_cells: bool = False
    styling: TableStyle = TableStyle()


class Table:
    def __init__(self, 
                 rows: List[List[TableCell]],
                 config: TableConfig = TableConfig()) -> None:
        self.rows: List[List[TableCell]] = rows
        self.config: TableConfig = config
    
    def _rule_line(self, left: str, fill: str, join: str, right: str, width: int, columns: int) -> str:
        parts = [left]

        for i in range(columns):
            parts.append(fill * width)
            if i < columns - 1:
                parts.append(join)

        parts.append(right)

        return "".join(parts) + "\n"

    def _render_row(self, cells: List[TableCell], width: int) -> str:
        parts = [self.config.styling.lv]
        for i, cell in enumerate(cells):
            parts.append(cell.text.center(width))
            if i < len(cells) - 1:
                parts.append(self.config.styling.v)
        parts.append(self.config.styling.rv)
        return "".join(parts) + "\n"

    def print_table(self) -> str:

        col_width = 9 + (self.config.cell_padding * 2)
        col_count = len(self.rows[0])

        lines: List[str] = []

        style = self.config.styling

        border_top = self._rule_line(style.tl, style.t, style.tm, style.tr, col_width, col_count)
        header_bottom = self._rule_line(style.l, style.h, style.c, style.r, col_width, col_count)
        border_bottom = self._rule_line(style.bl, style.b, style.bm, style.br, col_width, col_count)
        separator = header_bottom # header_bottom could be differnt than cell separator later

        lines.append(border_top)

        for i, row in enumerate(self.rows):
            if i < len(self.rows) - 1:
                lines.append(self._render_row(row, col_width))
            if i < len(self.rows) - 2:
                # TODO: logic to insert the header bottom if it is diff from separator
                lines.append(separator)

        lines.append(border_bottom)

        return "".join(lines)


DOUBLE_BORDER_TABLE_STYLE = TableStyle(
    t  = '═',
    tl = '╔',
    tr = '╗',
    tm = '╤',
    b  = '═',
    bl = '╚',
    br = '╝',
    bm = '╧',
    l  = '╟',
    lv = '║',
    rv = '║',
    r  = '╢')

NO_LINES_TABLE_STYLE = TableStyle('', '', '', '', '', '', '', '', '', '', '', '', '', '', '')
ASCII_TABLE_STYLE = TableStyle(t='-', tl='@',tr='@',tm='|',
                               b='-', bl='@',br='@',bm='|',
                               l='|', lv='|',rv='|',r ='|',
                               c='|', v='|', h='-')

if __name__ == '__main__':

    tconfig: TableConfig = TableConfig()
    tconfig.styling = DOUBLE_BORDER_TABLE_STYLE
    # tconfig.styling = NO_LINES_TABLE_STYLE
    # tconfig.styling = ASCII_TABLE_STYLE

    data: List[List[TableCell]] = [[]]
    for row in range(5):
        data.append([])
        for col in range(3):
            if row == 0:
                # headers
                data[row].append(TableCell(f"Column_{col}"))
            else:
                data[row].append(TableCell(f'{row}, {col}', style=None, align='center'))

    table = Table(rows=data, config=tconfig)

    print(table.print_table())
