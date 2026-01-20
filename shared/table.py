from dataclasses import dataclass, field
from typing import Iterable, List, Literal, Optional

from shared.ansi import AnsiStyle
from shared.color import Color
from shared.formatter import style_text


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

_TABLE_STYLE_NONE = TableStyle('', '', '', '', '', '', '', '', '', '', '', '', '', '', '')
_TABLE_STYLE_DOUBLE = TableStyle(t='═', tl='╔', tr='╗', tm='╤',
                                 b='═', bl='╚', br='╝', bm='╧',
                                 l='╟', lv='║', rv='║', r ='╢')
_TABLE_STYLE_ASCII = TableStyle(t='-', tl='*',tr='*',tm='-',
                                b='-', bl='*',br='*',bm='-',
                                l='|', lv='|',rv='|',r ='|',
                                c='+', v='|', h='-')

# endregion
CellAlignment = Literal["left", "right", "center"]
@dataclass
class TableCell:
    text: str
    align: Optional[CellAlignment] = None
    padding: Optional[int] = None
    fore_color: Optional[Color] = None
    back_color: Optional[Color] = None
    styles: Optional[Iterable[AnsiStyle]] = None

@dataclass
class TableRow:
    cells: List[TableCell] = field(default_factory=list)
    height: int = 1
    align: CellAlignment = "left"
    padding: Optional[int] = None
    fore_color: Optional[Color] = None
    back_color: Optional[Color] = None
    styles: Optional[Iterable[AnsiStyle]] = None

    def add_cell(self,
                 text: str,
                 align: Optional[CellAlignment] = None,
                 padding: Optional[int] = None,
                 fore_color: Optional[Color] = None,
                 back_color: Optional[Color] = None,
                 styles: Optional[Iterable[AnsiStyle]] = None):
        
        self.cells.append(TableCell(text=text,
                                    align=align,
                                    padding=padding,
                                    fore_color=fore_color,
                                    back_color=back_color,
                                    styles=styles))

@dataclass
class TableHeader(TableRow):
    pass

@dataclass
class TableConfig:
    cell_padding: int = 0
    table_width: int = 0
    cell_widths: List[int] = field(default_factory=list)
    content_truncate: bool = True
    multi_line_cells: bool = False
    styling: Literal['single', 'double', 'ascii', 'none'] = 'single'

class Table:
    def __init__(self,
                 header: TableHeader,
                 config: TableConfig = TableConfig()) -> None:

        self.column_count = len(header.cells)
        self.header = header
        self.rows: List[TableRow] = [] #rows
        self.config: TableConfig = config
        self.widest_column: int = 0
        self.column_content_width: List[int] = []
        self.table_style: TableStyle = TableStyle()

        match config.styling:
            case 'ascii':
                self.table_style = _TABLE_STYLE_ASCII
            case 'double':
                self.table_style = _TABLE_STYLE_DOUBLE
            case 'single':
                self.table_style = TableStyle()
            case 'none':
                self.table_style = _TABLE_STYLE_NONE

        for cell in header.cells:
            padding = cell.padding or header.padding or self.config.cell_padding
            self.column_content_width.append(len(cell.text) + padding)

    def add_row(self, row: TableRow) -> None:
        # track each columns widest text
        for i in range(self.column_count):
            # Determine which padding setting to use
            padding = row.cells[i].padding or row.padding or self.config.cell_padding
            self.column_content_width[i] = max(self.column_content_width[i],
                                               len(row.cells[i].text) + padding)
        self.rows.append(row)

    def _rule_line(self, left: str, fill: str, join: str, right: str) -> str:
        columns = self.column_count
        parts = [left]

        for i in range(columns):
            width = self.column_content_width[i]
            if self.config.content_truncate and width > self.config.cell_widths[i]:
                width = self.config.cell_widths[i]
            parts.append(fill * width)
            if i < columns - 1:
                parts.append(join)

        parts.append(right)

        return "".join(parts) + "\n"

    def _render_row(self, row: TableRow) -> str:
        parts = [self.table_style.lv]

        for i in range(self.column_count):
        # for i, cell in enumerate(row.cells):
            cell = row.cells[i]
            text: str = cell.text
            # select the lowest level padding
            padding = cell.padding or row.padding or self.config.cell_padding
            col_width = self.column_content_width[i]
            fore_color = cell.fore_color or row.fore_color
            back_color = cell.back_color or row.back_color
            align = cell.align or row.align
            styles = cell.styles or row.styles

            if self.config.content_truncate and col_width > self.config.cell_widths[i]:
                if len(text) > self.config.cell_widths[i] - padding: 
                    text = text[:self.config.cell_widths[i] - padding - 3]
                    text += "..."

            match align:
                case "center":
                    text = text.center(min(col_width, self.config.cell_widths[i]))
                case "left":
                    text = text.ljust(min(col_width, self.config.cell_widths[i]))
                case "right":
                    text = text.rjust(min(col_width, self.config.cell_widths[i]))

            parts.append(style_text(text,
                                    fore_color,
                                    back_color,
                                    styles))

            if i < self.column_count - 1:
                parts.append(self.table_style.v)

        parts.append(self.table_style.rv)

        return "".join(parts) + "\n"

    def render(self) -> str:
        lines: List[str] = []
        style: TableStyle = self.table_style

        border_top = self._rule_line(style.tl, style.t, style.tm, style.tr)
        header_bottom = self._rule_line(style.l, style.h, style.c, style.r)
        border_bottom = self._rule_line(style.bl, style.b, style.bm, style.br)
        # TODO: header_bottom could be differnt than cell separator later
        separator = header_bottom

        lines.append(border_top)

        lines.append(self._render_row(self.header))
        lines.append(header_bottom)

        for i, row in enumerate(self.rows):
            lines.append(self._render_row(row))
            if i < len(self.rows) - 1:
                lines.append(separator)
        
        lines.append(border_bottom)

        return "".join(lines)


if __name__ == "__main__":
    pass
