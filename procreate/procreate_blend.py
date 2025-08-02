from enum import Enum

class ProcreateBlend(Enum):
    """
    Based off of `extendedBlend`, with just `blend` being commented next to the value.
    """ 
    MULTIPLY        = 1  # blend: 1
    DARKEN          = 19 # blend: 19
    COLOR_BURN      = 10 # blend: 10
    LINEAR_BURN     = 8  # blend: 8
    DARKER_COLOR    = 25 # blend: 0
    NORMAL          = 0  # blend: 0
    LIGHTEN         = 4  # blend: 4
    SCREEN          = 2  # blend: 2
    COLOR_DODGE     = 9  # blend: 9
    ADD             = 3  # blend: 3
    LIGHTER_COLOR   = 24 # blend: 0
    OVERLAY         = 11 # blend: 11
    SOFT_LIGHT      = 17 # blend: 17
    HARD_LIGHT      = 12 # blend: 12
    VIVID_LIGHT     = 21 # blend: 0
    LINEAR_LIGHT    = 22 # blend: 0
    PIN_LIGHT       = 23 # blend: 0
    HARD_MIX        = 20 # blend: 0
    DIFFERENCE      = 6  # blend: 6
    EXCLUSION       = 5  # blend: 5
    SUBTRACT        = 7  # blend: 7
    DIVIDE          = 26 # blend: 0
    HUE             = 15 # blend: 15
    SATURATION      = 16 # blend: 16
    COLOR           = 13 # blend: 13
    LUMINOSITY      = 14 # blend: 14

BLEND_MAP_TO_KRITA : dict = {
    ProcreateBlend.MULTIPLY:        "multiply",
    ProcreateBlend.DARKEN:          "darken",
    ProcreateBlend.COLOR_BURN:      "burn",
    ProcreateBlend.LINEAR_BURN:     "linear_burn",
    ProcreateBlend.DARKER_COLOR:    "darker color",
    ProcreateBlend.NORMAL:          "normal",
    ProcreateBlend.LIGHTEN:         "lighten",
    ProcreateBlend.SCREEN:          "screen",
    ProcreateBlend.COLOR_DODGE:     "dodge",        # check?
    ProcreateBlend.ADD:             "add",
    ProcreateBlend.LIGHTER_COLOR:   "lighter color",
    ProcreateBlend.OVERLAY:         "overlay",
    ProcreateBlend.SOFT_LIGHT:      "soft_light",
    ProcreateBlend.HARD_LIGHT:      "hard_light",
    ProcreateBlend.VIVID_LIGHT:     "vivid_light",
    ProcreateBlend.LINEAR_LIGHT:    "linear light",
    ProcreateBlend.PIN_LIGHT:       "pin_light",
    ProcreateBlend.HARD_MIX:        "hard_mix_photoshop",   # check?
    ProcreateBlend.DIFFERENCE:      "diff",
    ProcreateBlend.EXCLUSION:       "exclusion",
    ProcreateBlend.SUBTRACT:        "subtract",
    ProcreateBlend.DIVIDE:          "divide",
    ProcreateBlend.HUE:             "hue",
    ProcreateBlend.SATURATION:      "saturation",
    ProcreateBlend.COLOR:           "color",
    ProcreateBlend.LUMINOSITY:      "luminize",     # check?
}