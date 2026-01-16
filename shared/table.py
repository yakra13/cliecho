from dataclasses import dataclass
from typing import List, Literal, Optional

from .ansi import AnsiStyle
from .color import Color

@dataclass
class TableCell:
    text: str
    color: Optional[Color] = None
    style: Optional[AnsiStyle] = None

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

# region Table Style Constants

NO_LINES_TABLE_STYLE = TableStyle('', '', '', '', '', '', '', '', '', '', '', '', '', '', '')
DOUBLE_BORDER_TABLE_STYLE = TableStyle(t='═', tl='╔', tr='╗', tm='╤',
                                       b='═', bl='╚', br='╝', bm='╧',
                                       l='╟', lv='║', rv='║', r ='╢')
ASCII_TABLE_STYLE = TableStyle(t='-', tl='*',tr='*',tm='-',
                               b='-', bl='*',br='*',bm='-',
                               l='|', lv='|',rv='|',r ='|',
                               c='+', v='|', h='-')

# endregion

@dataclass
class TableConfig:
    cell_padding: int = 0
    table_width: int = 0
    cell_widths: List[int] = []
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
            text: str = cell.text

            match cell.align:
                case "center":
                    text = cell.text.center(width)
                case "left":
                    text = cell.text.ljust(width)
                case "right":
                    text = cell.text.rjust(width)

            parts.append(text)

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


if __name__ == "__main__":
    pass