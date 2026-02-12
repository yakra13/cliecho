
from dataclasses import dataclass
from typing import ClassVar

from shared.util import UINT8_MAX, UINT8_MIN, clamp, lerp

@dataclass(frozen=True, slots=True)
class Color:
    """24-bit Color RGB dataclass"""
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
        object.__setattr__(self, 'R', clamp(self.R, UINT8_MIN, UINT8_MAX))
        object.__setattr__(self, 'G', clamp(self.G, UINT8_MIN, UINT8_MAX))
        object.__setattr__(self, 'B', clamp(self.B, UINT8_MIN, UINT8_MAX))

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

def estimate_ansi_color(color: Color, is_background: bool = False) -> int:
    """
    Estimate the ANSI_16 color code that most closely matches the 24bit color.
    
    Args:
        color: The color to estimate the ANSI 16 color from.
        is_background: Set to true if the color is used as the ANSI background color.
    
    Returns:
        The integer value ANSI color code closest to the provided color.

    Raises:
        None
    """
    r, g, b = color.R, color.G, color.B
    # Calculate luminance (brightness)
    luma = 0.2126 * r + 0.7152 * g + 0.0722 * b
    # The color is "bright" if it falls into the upper range (128-255)
    is_bright: bool = luma >= 128

    final_code = 30 # black
    best_dist = float("inf")
    # Determine the "distance" the color is from each possible
    # ansi color and choose the closest one
    for code, (cr, cg, cb) in _ANSI_COLORS.items():
        distance = (r - cr) ** 2 + (g - cg) ** 2 + (b - cb) ** 2
        if distance < best_dist:
            best_dist = distance
            final_code = code

    # Convert the code to the bright version if required
    if is_bright:
        final_code += 60
    
    if is_background:
        final_code += 10
    
    return final_code

def lerp_color(start_color: Color, end_color: Color, t: float) -> Color:
    """
    Performs a lerp operation between two colors.

    Args:
        start_color: The starting color. t == 0.0
        end_color: The ending color. t == 1.0
        t: The step size between the start and end color.
    
    Returns:
        The color that falls between the start and end colors.
    
    Raises:
        None
    """
    return Color(round(lerp(start_color.R, end_color.R, t)),
                 round(lerp(start_color.G, end_color.G, t)),
                 round(lerp(start_color.B, end_color.B, t)))