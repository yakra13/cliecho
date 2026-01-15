import math
import os
import re
import shutil
import sys

from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, ClassVar, Final, Iterable, List, Literal, Optional


# Regex to remove ANSI escape characters from a string
ANSI_RE = re.compile(r'\x1b\[[0-9;]*m')

class ColorSupport(Enum):
    NONE      = auto()
    ANSI_16   = auto()
    ANSI_256  = auto()
    TRUECOLOR = auto()

def _detect_color_support() -> ColorSupport:
    # stdout must be a TTY
    if not sys.stdout.isatty():
        return ColorSupport.NONE

    # check explicit user override
    if os.environ.get("NO_COLOR"):
        return ColorSupport.NONE

    if os.environ.get("FORCE_COLOR"):
        return ColorSupport.TRUECOLOR
    
    term = os.environ.get("TERM", "").lower()
    colorterm = os.environ.get("COLORTERM", "").lower()

    # truecolor detection
    if colorterm in ("truecolor", "24bit"):
        return ColorSupport.TRUECOLOR

    if "truecolor" in term or "24bit" in term:
        return ColorSupport.TRUECOLOR

    if "256color" in term:
        return ColorSupport.ANSI_256

    # Windows
    if sys.platform == "win32":
        # Terminal, VS code, conhost
        if os.environ.get("WT_SESSION") or os.environ.get("TERM_PROGRAM"):
            return ColorSupport.TRUECOLOR
        return ColorSupport.ANSI_16

    return ColorSupport.ANSI_16

COLOR_SUPPORT = _detect_color_support()

class TextStyle(Enum):
    BOLD      = '1'
    DIM       = '2'
    ITALIC    = '3'
    UNDERLINE = '4'
    BLINK     = '5'
    REVERSE   = '6'
    HIDDEN    = '7'
    STRIKE    = '8'

def _clamp_byte(value: int) -> int:
    return max(0, min(255, int(value)))

@dataclass(frozen=True, slots=True)
class Color:
    """ 24-bit Color RGB Dataclass"""
    R: int
    G: int
    B: int
    
    # region Colors

    Black:         ClassVar["Color"]
    White:         ClassVar["Color"]
    Gray:          ClassVar["Color"]
    DarkGray:      ClassVar["Color"]
    LightGray:     ClassVar["Color"]
    Red:           ClassVar["Color"]
    DarkRed:       ClassVar["Color"]
    Crimson:       ClassVar["Color"]
    Firebrick:     ClassVar["Color"]
    Pink:          ClassVar["Color"]
    LightPink:     ClassVar["Color"]
    HotPink:       ClassVar["Color"]
    Orange:        ClassVar["Color"]
    DarkOrange:    ClassVar["Color"]
    Coral:         ClassVar["Color"]
    OrangeRed:     ClassVar["Color"]
    Brown:         ClassVar["Color"]
    Sienna:        ClassVar["Color"]
    Chocolate:     ClassVar["Color"]
    Tan:           ClassVar["Color"]
    Yellow:        ClassVar["Color"]
    LightYellow:   ClassVar["Color"]
    Goldenrod:     ClassVar["Color"]
    Gold:          ClassVar["Color"]
    Khaki:         ClassVar["Color"]
    DarkKhaki:     ClassVar["Color"]
    Green:         ClassVar["Color"]
    DarkGreen:     ClassVar["Color"]
    LightGreen:    ClassVar["Color"]
    PaleGreen:     ClassVar["Color"]
    Lime:          ClassVar["Color"]
    LimeGreen:     ClassVar["Color"]
    ForestGreen:   ClassVar["Color"]
    SeaGreen:      ClassVar["Color"]
    SpringGreen:   ClassVar["Color"]
    Olive:         ClassVar["Color"]
    YellowGreen:   ClassVar["Color"]
    Cyan:          ClassVar["Color"]
    LightCyan:     ClassVar["Color"]
    Aqua:          ClassVar["Color"]
    Aquamarine:    ClassVar["Color"]
    Turquoise:     ClassVar["Color"]
    DarkTurquoise: ClassVar["Color"]
    LightSeaGreen: ClassVar["Color"]
    DarkCyan:      ClassVar["Color"]
    Teal:          ClassVar["Color"]
    Blue:          ClassVar["Color"]
    DarkBlue:      ClassVar["Color"]
    LightBlue:     ClassVar["Color"]
    SkyBlue:       ClassVar["Color"]
    LightSkyBlue:  ClassVar["Color"]
    DeepSkyBlue:   ClassVar["Color"]
    SteelBlue:     ClassVar["Color"]
    RoyalBlue:     ClassVar["Color"]
    MediumBlue:    ClassVar["Color"]
    MidnightBlue:  ClassVar["Color"]
    Navy:          ClassVar["Color"]
    SlateBlue:     ClassVar["Color"]
    DarkSlateBlue: ClassVar["Color"]
    Purple:        ClassVar["Color"]
    Magenta:       ClassVar["Color"]
    Fuchsia:       ClassVar["Color"]
    Violet:        ClassVar["Color"]
    Plum:          ClassVar["Color"]
    Orchid:        ClassVar["Color"]
    DarkOrchid:    ClassVar["Color"]
    BlueViolet:    ClassVar["Color"]
    DarkViolet:    ClassVar["Color"]
    Snow:          ClassVar["Color"]
    MintCream:     ClassVar["Color"]
    Azure:         ClassVar["Color"]
    WhiteSmoke:    ClassVar["Color"]
    Beige:         ClassVar["Color"]
    Ivory:         ClassVar["Color"]
    Lavender:      ClassVar["Color"]

    #endregion

    def __post_init__(self):
        object.__setattr__(self, 'R', _clamp_byte(self.R))
        object.__setattr__(self, 'G', _clamp_byte(self.G))
        object.__setattr__(self, 'B', _clamp_byte(self.B))

# region Color Constants
 
Color.Black         = Color(0, 0, 0)
Color.White         = Color(255, 255, 255)
Color.Gray          = Color(128, 128, 128)
Color.DarkGray      = Color(105, 105, 105)
Color.LightGray     = Color(211, 211, 211)
Color.Red           = Color(255, 0, 0)
Color.DarkRed       = Color(139, 0, 0)
Color.Crimson       = Color(220, 20, 60)
Color.Firebrick     = Color(178, 34, 34)
Color.Pink          = Color(255, 192, 203)
Color.LightPink     = Color(255, 182, 193)
Color.HotPink       = Color(255, 105, 180)
Color.Orange        = Color(255, 165, 0)
Color.DarkOrange    = Color(255, 140, 0)
Color.Coral         = Color(255, 127, 80)
Color.OrangeRed     = Color(255, 69, 0)
Color.Brown         = Color(165, 42, 42)
Color.Sienna        = Color(160, 82, 45)
Color.Chocolate     = Color(210, 105, 30)
Color.Tan           = Color(210, 180, 140)
Color.Yellow        = Color(255, 255, 0)
Color.LightYellow   = Color(255, 255, 224)
Color.Goldenrod     = Color(250, 250, 210)
Color.Gold          = Color(255, 215, 0)
Color.Khaki         = Color(240, 230, 140)
Color.DarkKhaki     = Color(189, 183, 107)
Color.Green         = Color(0, 128, 0)
Color.DarkGreen     = Color(0, 100, 0)
Color.LightGreen    = Color(144, 238, 144)
Color.PaleGreen     = Color(152, 251, 152)
Color.Lime          = Color(0, 255, 0)
Color.LimeGreen     = Color(50, 205, 50)
Color.ForestGreen   = Color(34, 139, 34)
Color.SeaGreen      = Color(46, 139, 87)
Color.SpringGreen   = Color(0, 255, 127)
Color.Olive         = Color(128, 128, 0)
Color.YellowGreen   = Color(154, 205, 50)
Color.Cyan	        = Color(0, 255, 255)
Color.LightCyan	    = Color(224, 255, 255)
Color.Aqua	        = Color(0, 255, 255)
Color.Aquamarine    = Color(127, 255, 212)
Color.Turquoise	    = Color(64, 224, 208)
Color.DarkTurquoise	= Color(0, 206, 209)
Color.LightSeaGreen	= Color(32, 178, 170)
Color.DarkCyan	    = Color(0, 139, 139)
Color.Teal	        = Color(0, 128, 128)
Color.Blue          = Color(0, 0, 255)
Color.DarkBlue      = Color(0, 0, 139)
Color.LightBlue     = Color(173, 216, 230)
Color.SkyBlue       = Color(135, 206, 235)
Color.LightSkyBlue  = Color(135, 206, 250)
Color.DeepSkyBlue   = Color(0, 191, 255)
Color.SteelBlue     = Color(70, 130, 180)
Color.RoyalBlue     = Color(65, 105, 225)
Color.MediumBlue    = Color(0, 0, 205)
Color.MidnightBlue  = Color(25, 25, 112)
Color.Navy          = Color(0, 0, 128)
Color.SlateBlue     = Color(106, 90, 205)
Color.DarkSlateBlue = Color(72, 61, 139)
Color.Purple        = Color(128, 0, 128)
Color.Magenta       = Color(255, 0, 255)
Color.Fuchsia       = Color(255, 0, 255)
Color.Violet        = Color(238, 130, 238)
Color.Plum          = Color(221, 160, 221)
Color.Orchid        = Color(218, 112, 214)
Color.DarkOrchid    = Color(153, 50, 204)
Color.BlueViolet    = Color(138, 43, 226)
Color.DarkViolet    = Color(148, 0, 211)
Color.Snow          = Color(255, 250, 250)
Color.MintCream     = Color(245, 255, 250)
Color.Azure         = Color(240, 255, 255)
Color.WhiteSmoke    = Color(245, 245, 245)
Color.Beige         = Color(245, 245, 220)
Color.Ivory         = Color(255, 255, 240)
Color.Lavender      = Color(230, 230, 250)

#endregion

_ANSI_COLORS = {
    30: (0, 0, 0),         # black
    31: (205, 49, 49),     # red
    32: (13, 188, 121),    # green
    33: (229, 229, 16),    # yellow
    34: (36, 114, 200),    # blue
    35: (188, 63, 188),    # magenta
    36: (17, 168, 205),    # cyan
    37: (229, 229, 229)    # white
}

def _estimate_ansi_color(color: Color) -> int:
    """Estimate the ANSI_16 color code that most closely matches the 24bit color."""
    r, g, b = color.R, color.G, color.B
    # Calculate luminance (brightness)
    luma = 0.2126 * r + 0.7152 * g + 0.0722 * b
    # The color is "bright" if it falls into the upper range (128-255)
    bright: bool = luma >= 128

    best_code = 30
    best_dist = float("inf")
    # Determine the "distance" the color is from each possible
    # ansi color and choose the closest one
    for code, (cr, cg, cb) in _ANSI_COLORS.items():
        distance = (r - cr) ** 2 + (g - cg) ** 2 + (b - cb) ** 2
        if distance < best_dist:
            best_dist = distance
            best_code = code

    # Convert the code to the bright version if required
    if bright:
        best_code += 60
    
    return best_code

def _to_column_major(items: List[str], columns: int) -> List[str]:
    if not items or columns <= 0:
        return items
    
    rows = math.ceil(len(items) / columns)

    grid: List[List[Optional[str]]] = [[None] * columns for _ in range(rows)]

    # Fill column-major
    idx = 0
    for c in range(columns):
        for r in range(rows):
            if idx < len(items):
                grid[r][c] = items[idx]
                idx += 1

    result: List[str] = []
    for row in grid:
        for item in row:
            result.append(item if item is not None else '')
    
    return result

def _visible_len(ansi_text: str) -> int:
    """Ignores ANSI encoding and returns the length of the text."""
    return len(ANSI_RE.sub('', ansi_text))

def lerp(a: float, b: float, t: float) -> float:
    t = max(0.0, min(1.0, t))
    return a + (b - a) * t

def lerp_color(c1: Color, c2: Color, t: float) -> Color:
    return Color(round(lerp(c1.R, c2.R, t)),
                 round(lerp(c1.G, c2.G, t)),
                 round(lerp(c1.B, c2.B, t)))

def style_text(text: str,
               text_color: Optional[Color] = None,
               back_color: Optional[Color] = None,
               styles: Optional[Iterable[TextStyle]] = None) -> str:
    """
    Apply ANSI color and text styling to a string.

    If the current terminal does not support the requested formatting,
    the original text is returned unmodified.

    Args:
        text: The text to be styled.
        text_color: Optional foreground color.
        back_color: Optional background color.
        styles: Optional iterable of text styles (e.g. bold, underline).

    Returns:
        The stylized text if supported; otherwise, the original text.

    Raises:
        None

    """
    if COLOR_SUPPORT == ColorSupport.NONE:
        # NOTE: We assume that even styling is not supported (bold, underline, etc)
        return text

    codes = []

    if styles:
        codes.extend([s.value for s in styles])

    if text_color:
        if COLOR_SUPPORT == ColorSupport.TRUECOLOR:
            codes.extend(['38', '2', str(text_color.R), str(text_color.G), str(text_color.B)])
        else:
            # If truecolor is not supported we default to ANSI_16 currently
            fg = _estimate_ansi_color(text_color)
            codes.extend([str(fg)])
    
    if back_color:
        if COLOR_SUPPORT == ColorSupport.TRUECOLOR:
            codes.extend(['38', '2', str(back_color.R), str(back_color.G), str(back_color.B)])
        else:
            # If truecolor is not supported we default to ANSI_16 currently
            bg = _estimate_ansi_color(back_color)
            # Add ten to shift from foreground ansi color to background
            bg += 10
            codes.extend([str(bg)])

    seq = ';'.join(codes)

    return f"\033[{seq}m{text}\033[0m"

def format_list_as_grid(items: List[str],
                        columns: int = 1,
                        auto_size: bool = False,
                        column_major: bool = True,
                        left_padding: int = 4) -> str:
    """
    Formats a list of strings into a grid. Maintains any ANSI encoding.
    
    Args:
        items: List of strings to be formatted into a grid
        columns: The explicit number of columns the grid should contain if possible.
        auto_size: If true the grid will be sized automatically and ignore the columns arg
        column_major: Determines if the grid will fill top to bottom then left to right
        left_padding: the number of padding spaces to insert before each row

    Returns:
        Returns a string formatted to be printed in a grid.
        If there are no items an empty string is returned.

    Raises:
        None
    """
    if not items:
        return ''

    # Find the length of the longest item add 2 for spacing
    column_width = max(_visible_len(item) for item in items) + 2

    if auto_size:
        terminal_width, _ = shutil.get_terminal_size()
        columns = max(1, terminal_width // column_width)

    if column_major:
        items = _to_column_major(items, columns)

    # Print formatted
    lines = []

    for i in range(0, len(items), columns):
        row_items = items[i:i + columns]
        line = ''.join(item.ljust(column_width) for item in row_items)
        lines.append(f"{' ' * left_padding}{line.rstrip()}")  # remove trailing spaces

    return '\n'.join(lines)


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

# region Table Style Constants

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

# endregion