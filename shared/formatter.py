from dataclasses import dataclass
from enum import Enum
from typing import ClassVar, Final, Iterable, Literal, Optional


Style   = Literal['1','2','3','4','5','6','7','8']
FGColor = Literal['30','31','32','33','34','35','36','37','39']
BGColor = Literal['40','41','42','43','44','45','46','47','49']

class TextStyle(Enum):
    BOLD      = '1'
    DIM       = '2'
    ITALIC    = '3'
    UNDERLINE = '4'
    BLINK     = '5'
    REVERSE   = '6'
    HIDDEN    = '7'
    STRIKE    = '8'

class Color:
    class Style:
        BOLD:      Final[Style] = '1'
        DIM:       Final[Style] = '2'
        ITALIC:    Final[Style] = '3'
        UNDERLINE: Final[Style] = '4'
        BLINK:     Final[Style] = '5'
        REVERSE:   Final[Style] = '6'
        HIDDEN:    Final[Style] = '7'
        STRIKE:    Final[Style] = '8'

    class FG:
        BLACK:   Final[FGColor] = '30'
        RED:     Final[FGColor] = '31'
        GREEN:   Final[FGColor] = '32'
        YELLOW:  Final[FGColor] = '33'
        BLUE:    Final[FGColor] = '34'
        MAGENTA: Final[FGColor] = '35'
        CYAN:    Final[FGColor] = '36'
        WHITE:   Final[FGColor] = '37'
        DEFAULT: Final[FGColor] = '39'

    class BG:
        BLACK:   Final[BGColor] = '40'
        RED:     Final[BGColor] = '41'
        GREEN:   Final[BGColor] = '42'
        YELLOW:  Final[BGColor] = '43'
        BLUE:    Final[BGColor] = '44'
        MAGENTA: Final[BGColor] = '45'
        CYAN:    Final[BGColor] = '46'
        WHITE:   Final[BGColor] = '47'
        DEFAULT: Final[BGColor] = '49'

def _clamp_byte(value: int) -> int:
    return max(0, min(255, int(value)))

@dataclass(frozen=True)
class CColor:
    R: int
    G: int
    B: int

    Black: ClassVar["CColor"]
    White: ClassVar["CColor"]

    def __post_init__(self):
        object.__setattr__(self, 'R', _clamp_byte(self.R))
        object.__setattr__(self, 'G', _clamp_byte(self.G))
        object.__setattr__(self, 'B', _clamp_byte(self.B))
    
CColor.Black = CColor(0, 0, 0)
CColor.White = CColor(255, 255, 255)

def style_text(text: str,
               text_color: Optional[CColor] = None,
               back_color: Optional[CColor] = None,
               styles: Optional[Iterable[TextStyle]] = None) -> str:
    codes = []
    if styles:
        codes.extend(styles)
    
    if text_color:
        codes.append(['38', '2', str(text_color.R), str(text_color.G), str(text_color.B)])
    
    if back_color:
        codes.append(['38', '2', str(back_color.R), str(back_color.G), str(back_color.B)])

    seq = ';'.join(codes)

    return f"\033[{seq}m{text}\033[0m"

def color_text(text: str,
             text_color: FGColor=Color.FG.DEFAULT,
             back_color: BGColor=Color.BG.DEFAULT,
             styles: Optional[Iterable[Style]] = None) -> str:
    """TODO"""
    codes = [text_color, back_color]

    if styles:
        codes.extend(styles)

    seq = ";".join(codes)

    return f"\033[{seq}m{text}\033[0m"
