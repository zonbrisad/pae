#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
#
#
#
# File:    escape.py
# Author:  Peter Malmberg <peter.malmberg@gmail.com>
# Date:    2022-05-22
# License: MIT
# Python:  3
#
# ----------------------------------------------------------------------------
# Pyplate
#   This file is generated from pyplate Python template generator.
#
# Pyplate is developed by:
#   Peter Malmberg <peter.malmberg@gmail.com>
#
# Available at:
#   https://github.com/zobrisad/pyplate.git
#
# ---------------------------------------------------------------------------
# References:
# https://en.wikipedia.org/wiki/ANSI_escape_code#3-bit_and_4-bit
# https://gist.github.com/fnky/458719343aabd01cfb17a3a4f7296797
# https://www.ditig.com/256-colors-cheat-sheet
# https://michurin.github.io/xterm256-color-picker/
# https://vt100.net/docs/vt510-rm/contents.html
#
#

from __future__ import annotations
from copy import copy
from dataclasses import dataclass, field
import logging


html_to_rgb_alphabetic_order = {
    "AliceBlue": (0xF0, 0xF8, 0xFF),
    "AntiqueWhite": (0xFA, 0xEB, 0xD7),
    "Aqua": (0x00, 0xFF, 0xFF),
    "Aquamarine": (0x7F, 0xFF, 0xD4),
    "Azure": (0xF0, 0xFF, 0xFF),
    "Beige": (0xF5, 0xF5, 0xDC),
    "Bisque": (0xFF, 0xE4, 0xC4),
    "Black": (0x00, 0x00, 0x00),
    "BlanchedAlmond": (0xFF, 0xEB, 0xCD),
    "Blue": (0x00, 0x00, 0xFF),
    "BlueViolet": (0x8A, 0x2B, 0xE2),
    "Brown": (0xA5, 0x2A, 0x2A),
    "BurlyWood": (0xDE, 0xB8, 0x87),
    "CadetBlue": (0x5F, 0x9E, 0xA0),
    "Chartreuse": (0x7F, 0xFF, 0x00),
    "Chocolate": (0xD2, 0x69, 0x1E),
    "Coral": (0xFF, 0x7F, 0x50),
    "CornflowerBlue": (0x64, 0x95, 0xED),
    "Cornsilk": (0xFF, 0xF8, 0xDC),
    "Crimson": (0xDC, 0x14, 0x3C),
    "Cyan": (0x00, 0xFF, 0xFF),
    "DarkBlue": (0x00, 0x00, 0x8B),
    "DarkCyan": (0x00, 0x8B, 0x8B),
    "DarkGoldenRod": (0xB8, 0x86, 0x0B),
    "DarkGray": (0xA9, 0xA9, 0xA9),
    "DarkGrey": (0xA9, 0xA9, 0xA9),
    "DarkGreen": (0x00, 0x64, 0x00),
    "DarkKhaki": (0xB5, 0x8B, 0x2E),
    "DarkMagenta": (0x8B, 0x00, 0x8B),
    "DarkOliveGreen": (0x55, 0x6B, 0x2F),
    "DarkOrange": (0xFF, 0x8C, 0x00),
    "DarkOrchid": (0x99, 0x32, 0xCC),
    "DarkRed": (0x8B, 0x00, 0x00),
    "DarkSalmon": (0xE9, 0x96, 0x7A),
    "DarkSeaGreen": (0x8F, 0xBC, 0x8F),
    "DarkSlateBlue": (0x48, 0x3D, 0x8B),
    "DarkSlateGray": (0x2F, 0x4F, 0x4F),
    "DarkSlateGrey": (0x2F, 0x4F, 0x4F),
    "DarkTurquoise": (0x00, 0xCE, 0xD1),
    "DarkViolet": (0x94, 0x00, 0xD3),
    "DeepPink": (0xFF, 0x14, 0x93),
    "DeepSkyBlue": (0x00, 0xBF, 0xFF),
    "DimGray": (0x69, 0x69, 0x69),
    "DimGrey": (0x69, 0x69, 0x69),
    "DodgerBlue": (0x1E, 0x90, 0xFF),
    "FireBrick": (0xB2, 0x22, 0x22),
    "FloralWhite": (0xFF, 0xFA, 0xF0),
    "ForestGreen": (0x22, 0x8B, 0x22),
    "Fuchsia": (0xFF, 0x00, 0xFF),
    "Gainsboro": (0xDC, 0xDC, 0xDC),
    "GhostWhite": (0xF8, 0xF8, 0xFF),
    "Gold": (0xFF, 0xD7, 0x00),
    "GoldenRod": (0xDA, 0xA5, 0x20),
    "Gray": (0x80, 0x80, 0x80),
    "Grey": (0x80, 0x80, 0x80),
    "Green": (0x00, 0x80, 0x00),
    "GreenYellow": (0xAD, 0xFF, 0x2F),
    "HoneyDew": (0xF0, 0xFF, 0xF0),
    "HotPink": (0xFF, 0x69, 0xB4),
    "IndianRed": (0xCD, 0x5C, 0x5C),
    "Indigo": (0x4B, 0x00, 0x82),
    "Ivory": (0xFF, 0xFF, 0xF0),
    "Khaki": (0xF0, 0xE6, 0x8C),
    "Lavender": (0xE6, 0xE6, 0xFA),
    "LavenderBlush": (0xFF, 0xF0, 0xF5),
    "LawnGreen": (0x7C, 0xFC, 0x00),
    "LemonChiffon": (0xFF, 0xFA, 0xCD),
    "LightBlue": (0xAD, 0xD8, 0xE6),
    "LightCoral": (0xF0, 0x80, 0x80),
    "LightCyan": (0xE0, 0xFF, 0xFF),
    "LightGoldenRodYellow": (0xFA, 0xFAD, 0x2),
    "LightGray": (0xD3, 0xD3, 0xD3),
    "LightGrey": (0xD3, 0xD3, 0xD3),
    "LightGreen": (0x90, 0xEE, 0x90),
    "LightPink": (0xFF, 0xB6, 0xC1),
    "LightSalmon": (0xFF, 0xA0, 0x7A),
    "LightSeaGreen": (0x20, 0xB2, 0xAA),
    "LightSkyBlue": (0x87, 0xCE, 0xFA),
    "LightSlateGray": (0x77, 0x88, 0x99),
    "LightSlateGrey": (0x77, 0x88, 0x99),
    "LightSteelBlue": (0xB0, 0xC4, 0xDE),
    "LightYellow": (0xFF, 0xFF, 0xE0),
    "Lime": (0x00, 0xFF, 0x00),
    "LimeGreen": (0x32, 0xCD, 0x32),
    "Linen": (0xFA, 0xF0, 0xE6),
    "Magenta": (0xFF, 0x00, 0xFF),
    "Maroon": (0x80, 0x00, 0x00),
    "MediumAquaMarine": (0x66, 0xCD, 0xAA),
    "MediumBlue": (0x00, 0x00, 0xCD),
    "MediumOrchid": (0xBA, 0x55, 0xD3),
    "MediumPurple": (0x93, 0x70, 0xDB),
    "MediumSeaGreen": (0x3C, 0xB3, 0x71),
    "MediumSlateBlue": (0x7B, 0x68, 0xEE),
    "MediumSpringGreen": (0x00, 0xFA, 0x9A),
    "MediumTurquoise": (0x48, 0xD1, 0xCC),
    "MediumVioletRed": (0xC7, 0x15, 0x85),
    "MidnightBlue": (0x19, 0x19, 0x70),
    "MintCream": (0xF5, 0xFF, 0xFA),
    "MistyRose": (0xFF, 0xE4, 0xE1),
    "Moccasin": (0xFF, 0xE4, 0xB5),
    "NavajoWhite": (0xFF, 0xDE, 0xAD),
    "Navy": (0x00, 0x00, 0x80),
    "OldLace": (0xFD, 0xF5, 0xE6),
    "Olive": (0x80, 0x80, 0x00),
    "OliveDrab": (0x6B, 0x8E, 0x23),
    "Orange": (0xFF, 0xA5, 0x00),
    "OrangeRed": (0xFF, 0x45, 0x00),
    "Orchid": (0xDA, 0x70, 0xD6),
    "PaleGoldenRod": (0xEE, 0xE8, 0xAA),
    "PaleGreen": (0x98, 0xFB, 0x98),
    "PaleTurquoise": (0xAF, 0xEE, 0xEE),
    "PaleVioletRed": (0xDB, 0x70, 0x93),
    "PapayaWhip": (0xFF, 0xEF, 0xD5),
    "PeachPuff": (0xFF, 0xDA, 0xB9),
    "Peru": (0xCD, 0x85, 0x3F),
    "Pink": (0xFF, 0xC0, 0xCB),
    "Plum": (0xDD, 0xA0, 0xDD),
    "PowderBlue": (0xB0, 0xE0, 0xE6),
    "Purple": (0x80, 0x00, 0x80),
    "RebeccaPurple": (0x66, 0x33, 0x99),
    "Red": (0xFF, 0x00, 0x00),
    "RosyBrown": (0xBC, 0x8F, 0x8F),
    "RoyalBlue": (0x41, 0x69, 0xE1),
    "SaddleBrown": (0x8B, 0x45, 0x13),
    "Salmon": (0xFA, 0x80, 0x72),
    "SandyBrown": (0xF4, 0xA4, 0x60),
    "SeaGreen": (0x2E, 0x8B, 0x57),
    "SeaShell": (0xFF, 0xF5, 0xEE),
    "Sienna": (0xA0, 0x52, 0x2D),
    "Silver": (0xC0, 0xC0, 0xC0),
    "SkyBlue": (0x87, 0xCE, 0xEB),
    "SlateBlue": (0x6A, 0x5A, 0xCD),
    "SlateGray": (0x70, 0x80, 0x90),
    "SlateGrey": (0x70, 0x80, 0x90),
    "Snow": (0xFF, 0xFA, 0xFA),
    "SpringGreen": (0x00, 0xFF, 0x7F),
    "SteelBlue": (0x46, 0x82, 0xB4),
    "Tan": (0xD2, 0xB4, 0x8C),
    "Teal": (0x00, 0x80, 0x80),
    "Thistle": (0xD8, 0xBF, 0xD8),
    "Tomato": (0xFF, 0x63, 0x47),
    "Turquoise": (0x40, 0xE0, 0xD0),
    "Violet": (0xEE, 0x82, 0xEE),
    "Wheat": (0xF5, 0xDE, 0xB3),
    "White": (0xFF, 0xFF, 0xFF),
    "WhiteSmoke": (0xF5, 0xF5, 0xF5),
    "Yellow": (0xFF, 0xFF, 0x00),
    "YellowGreen": (0x9A, 0xCD, 0x32),
}

html_to_rgb = {
    "RebeccaPurple": (0x66, 0x33, 0x99),
    "Purple": (0x80, 0x00, 0x80),
    "MediumVioletRed": (0xC7, 0x15, 0x85),
    "DeepPink": (0xFF, 0x14, 0x93),
    "Magenta": (0xFF, 0x00, 0xFF),
    "Fuchsia": (0xFF, 0x00, 0xFF),
    "PaleVioletRed": (0xDB, 0x70, 0x93),
    "HotPink": (0xFF, 0x69, 0xB4),
    "LightPink": (0xFF, 0xB6, 0xC1),
    "Pink": (0xFF, 0xC0, 0xCB),
    "MistyRose": (0xFF, 0xE4, 0xE1),
    "Indigo": (0x4B, 0x00, 0x82),
    "BlueViolet": (0x8A, 0x2B, 0xE2),
    "DarkViolet": (0x94, 0x00, 0xD3),
    "DarkOrchid": (0x99, 0x32, 0xCC),
    "MediumOrchid": (0xBA, 0x55, 0xD3),
    "Orchid": (0xDA, 0x70, 0xD6),
    "Violet": (0xEE, 0x82, 0xEE),
    "Plum": (0xDD, 0xA0, 0xDD),
    "Thistle": (0xD8, 0xBF, 0xD8),

    "DarkSlateBlue": (0x48, 0x3D, 0x8B),
    "MediumPurple": (0x93, 0x70, 0xDB),
    "MediumSlateBlue": (0x7B, 0x68, 0xEE),
    "SlateBlue": (0x6A, 0x5A, 0xCD),
    "MidnightBlue": (0x19, 0x19, 0x70),
    "Navy": (0x00, 0x00, 0x80),
    "DarkBlue": (0x00, 0x00, 0x8B),
    "MediumBlue": (0x00, 0x00, 0xCD),
    "Blue": (0x00, 0x00, 0xFF),
    "RoyalBlue": (0x41, 0x69, 0xE1),
    "CornflowerBlue": (0x64, 0x95, 0xED),
    "DodgerBlue": (0x1E, 0x90, 0xFF),
    "DeepSkyBlue": (0x00, 0xBF, 0xFF),
    "SkyBlue": (0x87, 0xCE, 0xEB),
    "LightSkyBlue": (0x87, 0xCE, 0xFA),
    "LightBlue": (0xAD, 0xD8, 0xE6),
    "PowderBlue": (0xB0, 0xE0, 0xE6),
    "PaleTurquoise": (0xAF, 0xEE, 0xEE),
    "Teal": (0x00, 0x80, 0x80),
    "DarkCyan": (0x00, 0x8B, 0x8B),
    "LightSeaGreen": (0x20, 0xB2, 0xAA),
    "DarkTurquoise": (0x00, 0xCE, 0xD1),
    "MediumTurquoise": (0x48, 0xD1, 0xCC),
    "Turquoise": (0x40, 0xE0, 0xD0),
    "Aqua": (0x00, 0xFF, 0xFF),
    "Cyan": (0x00, 0xFF, 0xFF),
    "LightCyan": (0xE0, 0xFF, 0xFF),
    "SteelBlue": (0x46, 0x82, 0xB4),
    "LightSteelBlue": (0xB0, 0xC4, 0xDE),
    "Lavender": (0xE6, 0xE6, 0xFA),
    "CadetBlue": (0x5F, 0x9E, 0xA0),
    "MediumAquaMarine": (0x66, 0xCD, 0xAA),
    "Aquamarine": (0x7F, 0xFF, 0xD4),
    "MintCream": (0xF5, 0xFF, 0xFA),
    "Azure": (0xF0, 0xFF, 0xFF),
    "AliceBlue": (0xF0, 0xF8, 0xFF),

    "DarkSlateGray": (0x2F, 0x4F, 0x4F),
    "DarkSlateGrey": (0x2F, 0x4F, 0x4F),
    "SlateGray": (0x70, 0x80, 0x90),
    "SlateGrey": (0x70, 0x80, 0x90),
    "LightSlateGray": (0x77, 0x88, 0x99),
    "LightSlateGrey": (0x77, 0x88, 0x99),
    "Black": (0x00, 0x00, 0x00),
    "DimGray": (0x69, 0x69, 0x69),
    "DimGrey": (0x69, 0x69, 0x69),
    "Gray": (0x80, 0x80, 0x80),
    "Grey": (0x80, 0x80, 0x80),
    "DarkGray": (0xA9, 0xA9, 0xA9),
    "DarkGrey": (0xA9, 0xA9, 0xA9),
    "Silver": (0xC0, 0xC0, 0xC0),
    "LightGray": (0xD3, 0xD3, 0xD3),
    "LightGrey": (0xD3, 0xD3, 0xD3),
    "Gainsboro": (0xDC, 0xDC, 0xDC),
    "White": (0xFF, 0xFF, 0xFF),
    "Snow": (0xFF, 0xFA, 0xFA),
    "Ivory": (0xFF, 0xFF, 0xF0),
    "FloralWhite": (0xFF, 0xFA, 0xF0),
    "GhostWhite": (0xF8, 0xF8, 0xFF),
    "WhiteSmoke": (0xF5, 0xF5, 0xF5),
    "OldLace": (0xFD, 0xF5, 0xE6),
    "SeaShell": (0xFF, 0xF5, 0xEE),
    "LavenderBlush": (0xFF, 0xF0, 0xF5),
    "Linen": (0xFA, 0xF0, 0xE6),
    "Beige": (0xF5, 0xF5, 0xDC),
    "Cornsilk": (0xFF, 0xF8, 0xDC),
    "PapayaWhip": (0xFF, 0xEF, 0xD5),
    "AntiqueWhite": (0xFA, 0xEB, 0xD7),
    "Khaki": (0xF0, 0xE6, 0x8C),

    "RosyBrown": (0xBC, 0x8F, 0x8F),
    "SaddleBrown": (0x8B, 0x45, 0x13),
    "Brown": (0xA5, 0x2A, 0x2A),
    "Sienna": (0xA0, 0x52, 0x2D),
    "Chocolate": (0xD2, 0x69, 0x1E),
    "Peru": (0xCD, 0x85, 0x3F),
    "SandyBrown": (0xF4, 0xA4, 0x60),
    "Tan": (0xD2, 0xB4, 0x8C),
    "BurlyWood": (0xDE, 0xB8, 0x87),
    "NavajoWhite": (0xFF, 0xDE, 0xAD),

    "Maroon": (0x80, 0x00, 0x00),
    "DarkRed": (0x8B, 0x00, 0x00),
    "FireBrick": (0xB2, 0x22, 0x22),
    "Crimson": (0xDC, 0x14, 0x3C),
    "Red": (0xFF, 0x00, 0x00),
    "Tomato": (0xFF, 0x63, 0x47),

    "LightSalmon": (0xFF, 0xA0, 0x7A),
    "DarkSalmon": (0xE9, 0x96, 0x7A),
    "IndianRed": (0xCD, 0x5C, 0x5C),
    "LightCoral": (0xF0, 0x80, 0x80),
    "Salmon": (0xFA, 0x80, 0x72),
    "Coral": (0xFF, 0x7F, 0x50),

    "OrangeRed": (0xFF, 0x45, 0x00),
    "DarkOrange": (0xFF, 0x8C, 0x00),
    "Orange": (0xFF, 0xA5, 0x00),
    "Yellow": (0xFF, 0xFF, 0x00),
    "Gold": (0xFF, 0xD7, 0x00),
    "GoldenRod": (0xDA, 0xA5, 0x20),
    "DarkGoldenRod": (0xB8, 0x86, 0x0B),
    "DarkKhaki": (0xB5, 0x8B, 0x2E),

    "LemonChiffon": (0xFF, 0xFA, 0xCD),
    "LightGoldenRodYellow": (0xFA, 0xFA, 0xd2),
    "LightYellow": (0xFF, 0xFF, 0xE0),

    "DarkGreen": (0x00, 0x64, 0x00),
    "Green": (0x00, 0x80, 0x00),
    "ForestGreen": (0x22, 0x8B, 0x22),
    "LimeGreen": (0x32, 0xCD, 0x32),
    "Lime": (0x00, 0xFF, 0x00),
    "LawnGreen": (0x7C, 0xFC, 0x00),
    "Chartreuse": (0x7F, 0xFF, 0x00),
    "YellowGreen": (0x9A, 0xCD, 0x32),
    "GreenYellow": (0xAD, 0xFF, 0x2F),

    "DarkOliveGreen": (0x55, 0x6B, 0x2F),
    "OliveDrab": (0x6B, 0x8E, 0x23),
    "Olive": (0x80, 0x80, 0x00),
    "MediumSpringGreen": (0x00, 0xFA, 0x9A),
    "SpringGreen": (0x00, 0xFF, 0x7F),
    "SeaGreen": (0x2E, 0x8B, 0x57),
    "MediumSeaGreen": (0x3C, 0xB3, 0x71),
    "DarkSeaGreen": (0x8F, 0xBC, 0x8F),
    "LightGreen": (0x90, 0xEE, 0x90),
    "PaleGreen": (0x98, 0xFB, 0x98),

    "PaleGoldenRod": (0xEE, 0xE8, 0xAA),
    "Bisque": (0xFF, 0xE4, 0xC4),
    "Moccasin": (0xFF, 0xE4, 0xB5),
    "PeachPuff": (0xFF, 0xDA, 0xB9),
    "Wheat": (0xF5, 0xDE, 0xB3),
    "BlanchedAlmond": (0xFF, 0xEB, 0xCD),
    "HoneyDew": (0xF0, 0xFF, 0xF0),
}


def print_html_colors() -> None:
    """Print all HTML colors to the terminal using ANSI escape codes."""

    htb = list(html_to_rgb.items())
    step = 37
    for x in range(0, step):
        color1, hex_value1 = htb[x]
        r1, g1, b1 = hex_value1
        print(f"{Ansi.bg_24bit_color(r1, g1, b1)}       {Ansi.RESET}  {color1:21} ", end="")

        color2, hex_value2 = htb[x + step]
        r2, g2, b2 = hex_value2
        print(f"{Ansi.bg_24bit_color(r2, g2, b2)}       {Ansi.RESET}  {color2:21} ", end="")

        color3, hex_value3 = htb[x + step * 2]
        r3, g3, b3 = hex_value3
        print(f"{Ansi.bg_24bit_color(r3, g3, b3)}       {Ansi.RESET}  {color3:21} ", end="")

        try:
            color4, hex_value4 = htb[x + step * 3]
            r4, g4, b4 = hex_value4
            print(f"{Ansi.bg_24bit_color(r4, g4, b4)}       {Ansi.RESET}  {color4:21}")
        except IndexError:
            print()


class Ascii:
    NUL = "\x00"  # Null character
    SOH = "\x01"  # Start of heading
    STX = "\x02"  # Start of text
    ETX = "\x03"  # End of text (Ctrl-C)
    EOT = "\x04"  # End of transmition (Ctrl-D)
    ENQ = "\x05"  # Enquiry
    ACK = "\x06"  # Acknowledge
    BEL = "\x07"  # Bell, Alert
    BS = "\x08"   # Backspace
    TAB = "\x09"
    LF = "\x0a"
    VT = "\x0b"
    FF = "\x0c"
    CR = "\x0d"
    SO = "\x0e"
    SI = "\x0f"
    DLE = "\x10"
    DC1 = "\x11"
    DC2 = "\x12"
    DC3 = "\x13"
    DC4 = "\x14"
    NAK = "\x15"
    SYN = "\x16"
    ETB = "\x17"
    CAN = "\x18"
    EM = "\x19"
    SUB = "\x1a"
    ESC = "\x1b"
    FS = "\x1c"
    GS = "\x1d"
    RS = "\x1e"
    US = "\x1f"

    @staticmethod
    def is_newline(ch: str) -> bool:
        if ch in ("\n", "\r\n", "\r"):
            return True
        return False

    @staticmethod
    def symbol(ch: int) -> str:
        if ch >= 0x20:
            return chr(ch)

        for x in dir(Ascii):
            if x.isupper():
                if chr(ch) == getattr(Ascii, x):
                    return x

    @staticmethod
    def table() -> str:
        chars = []
        for i in range(128):
            if i < 0x20:
                chars.append(f"{i:02x} {Ascii.symbol(i):3}   ")
            else:
                chars.append(f"{i:02x} '{Ascii.symbol(i)}'   ")

        rows = []
        for i in range(32):
            row = []
            rows.append(row)

        i = 0
        for char in chars:
            try:
                rows[i].append(char)
                i = i + 1
            except IndexError:
                rows[0].append(char)
                i = 1

        lines = []
        for row in rows:
            line = f"{''.join(row)}\n"
            lines.append(line)

        return "".join(lines)


class Ansi:
    CSI = "\x1b["  # CSI introducer

    """ANSI foreground colors codes"""

    BLACK = "\x1b[30m"  # Black
    RED = "\x1b[31m"  # Red
    GREEN = "\x1b[32m"  # Green
    YELLOW = "\x1b[33m"  # Yellow
    BLUE = "\x1b[34m"  # Blue
    MAGENTA = "\x1b[35m"  # Magenta
    CYAN = "\x1b[36m"  # Cyan
    WHITE = "\x1b[37m"  # Gray
    DARKGRAY = "\x1b[1;30m"  # Dark Gray
    BR_RED = "\x1b[1;31m"  # Bright Red
    BR_GREEN = "\x1b[1;32m"  # Bright Green
    BR_YELLOW = "\x1b[1;33m"  # Bright Yellow
    BR_BLUE = "\x1b[1;34m"  # Bright Blue
    BR_MAGENTA = "\x1b[1;35m"  # Bright Magenta
    BR_CYAN = "\x1b[1;36m"  # Bright Cyan
    BR_WHITE = "\x1b[1;37m"  # White

    # ANSI background color codes
    #
    BG_BLACK = "\x1b[40m"  # Black
    BG_RED = "\x1b[41m"  # Red
    BG_GREEN = "\x1b[42m"  # Green
    BG_YELLOW = "\x1b[43m"  # Yellow
    BG_BLUE = "\x1b[44m"  # Blue
    BG_MAGENTA = "\x1b[45m"  # Magenta
    BG_CYAN = "\x1b[46m"  # Cyan
    BG_WHITE = "\x1b[47m"  # White

    # ANSI Text attributes
    RESET = "\x1b[0m"  # Reset attributes
    BOLD = "\x1b[1m"  # bold font
    DIM = "\x1b[2m"  # Low intensity/faint/dim
    ITALIC = "\x1b[3m"  # Low intensity/faint/dim
    UNDERLINE = "\x1b[4m"  # Underline
    SLOWBLINK = "\x1b[5m"  # Slow blink
    FASTBLINK = "\x1b[6m"  # Fast blink
    REVERSE = "\x1b[7m"  # Reverse video
    HIDE = "\x1b[8m"
    CROSSED = "\x1b[9m"  # Crossed text
    FRACTUR = "\x1b[20m"  # Gothic
    FRAMED = "\x1b[51m"  # Framed
    OVERLINE = "\x1b[53m"  # Overlined
    SUPERSCRIPT = "\x1b[73m"  # Superscript
    SUBSCRIPT = "\x1b[74m"  # Subscript
    NORMAL = "\x1b[22m"  # Normal intensity
    NOT_ITALIC = "\x1b[23m"
    NOT_UNDERLINED = "\x1b[24m"
    NOT_BLINKING = "\x1b[25m"
    NOT_REVERSED = "\x1b[27m"
    REVEAL = "\x1b[28m"
    NOT_CROSSED = "\x1b[29m"
    NOT_SSCRIPT = "\x1b[75m"
    NOT_OVERLINE = "\x1b[55m"

    END = "\x1b[m"  # Clear Attributes
    CLEAR = "\x1b[2J"

    WONR = "\x1b[1;47\x1b[1;31m"

    # ANSI cursor operations
    #
    UP = "\x1b[A"  # Move cursor one line up
    DOWN = "\x1b[B"  # Move cursor one line down
    FORWARD = "\x1b[C"  # Move cursor forward
    BACK = "\x1b[D"  # Move cursor backward
    RETURN = "\x1b[F"  # Move cursor to begining of line
    HOME = "\x1b[1;1H"  # Move cursor to home position
    HIDE = "\x1b[?25l"  # Hide cursor
    SHOW = "\x1b[?25h"  # Show cursor

    KEY_HOME = "\x1b[1~"  # Home
    KEY_INSERT = "\x1b[2~"  #
    KEY_DELETE = "\x1b[3~"  #
    KEY_END = "\x1b[4~"  #
    KEY_PGUP = "\x1b[5~"  #
    KEY_PGDN = "\x1b[6~"  #
    KEY_HOME = "\x1b[7~"  #
    KEY_END = "\x1b[8~"  #
    KEY_F0 = "\x1b[10~"  # F0
    KEY_F1 = "\x1b[11~"  # F1
    KEY_F2 = "\x1b[12~"  # F2
    KEY_F3 = "\x1b[13~"  # F3
    KEY_F4 = "\x1b[14~"  # F4
    KEY_F5 = "\x1b[15~"  # F5
    KEY_F6 = "\x1b[17~"  # F6
    KEY_F7 = "\x1b[18~"  # F7
    KEY_F8 = "\x1b[19~"  # F8
    KEY_F9 = "\x1b[20~"  # F9
    KEY_F10 = "\x1b[21~"  # F10
    KEY_F11 = "\x1b[23~"  # F11
    KEY_F12 = "\x1b[24~"  # F12
    KEY_F13 = "\x1b[25~"  # F13
    KEY_F14 = "\x1b[26~"  # F14
    KEY_F15 = "\x1b[28~"  # F15
    KEY_F16 = "\x1b[29~"  # F16

    E_RET = 100
    E_UP = 101
    E_DOWN = 102

    x = [RETURN, UP, DOWN]
    y = {E_RET: RETURN, E_UP: UP, E_DOWN: DOWN}

    @staticmethod
    def fg_8bit_color(c: int) -> str:
        return f"\x1b[38;5;{c}m"

    @staticmethod
    def fg_24bit_color(r: int, g: int, b: int) -> str:
        return f"\x1b[38;2;{r};{g};{b}m"

    @staticmethod
    def bg_8bit_color(c: int) -> str:
        return f"\x1b[48;5;{c}m"

    @staticmethod
    def bg_24bit_color(r: int, g: int, b: int) -> str:
        return f"\x1b[48;2;{r};{g};{b}m"

    @staticmethod
    def findEnd(data, idx):
        i = idx
        while (i - idx) < 12:
            ch = data.at(i)
            if ch.isalpha():
                return i
            else:
                i += 1
        return -1

    @staticmethod
    def is_escape_seq(s: str) -> bool:
        if s[0] == Ascii.ESC:
            return True
        else:
            return False

    @staticmethod
    def to_str(s: str) -> str:
        return (
            s.replace("\x1b", "\\e")
            .replace("\x0a", "\\n")
            .replace("\x0d", "\\r")
            .replace("\x08", "\\b")
        )

    @staticmethod
    def row_add(a, b, c) -> str:
        return f"{a}{b:28}{c}Not {b}{Ansi.RESET}"

    @staticmethod
    def row_add_c(c1, cs1, c2, cs2) -> str:
        return f"{c1}{cs1:26}{Ansi.RESET}{c2}{cs2:22}{Ansi.RESET}"

    @staticmethod
    def test() -> str:
        """Font attribute tests"""
        s = []
        s.append(f"{Ansi.UNDERLINE}Font attributes{Ansi.END}")
        s.append(Ansi.row_add(Ansi.BOLD, "Bold text", Ansi.NORMAL))
        s.append(Ansi.row_add(Ansi.DIM, "Dim text", Ansi.NORMAL))
        s.append(Ansi.row_add(Ansi.ITALIC, "Italic text", Ansi.NOT_ITALIC))
        s.append(Ansi.row_add(Ansi.UNDERLINE, "Underline text", Ansi.NOT_UNDERLINED))
        s.append(Ansi.row_add(Ansi.SLOWBLINK, "Slow blinking  text", Ansi.NOT_BLINKING))
        s.append(Ansi.row_add(Ansi.FASTBLINK, "Fast blinking text", Ansi.NOT_BLINKING))
        s.append(Ansi.row_add(Ansi.FRAMED, "Framed text", Ansi.RESET))
        s.append(Ansi.row_add(Ansi.SUBSCRIPT, "Subscript text", Ansi.NOT_SSCRIPT))
        s.append(Ansi.row_add(Ansi.SUPERSCRIPT, "Superscript text", Ansi.NOT_SSCRIPT))
        s.append(Ansi.row_add(Ansi.FRACTUR, "Fractur/Gothic text", Ansi.RESET))
        s.append(Ansi.row_add(Ansi.CROSSED, "Crossed text", Ansi.NOT_CROSSED))
        s.append(Ansi.row_add(Ansi.OVERLINE, "Overlined text", Ansi.NOT_OVERLINE))
        s.append(Ansi.row_add(Ansi.REVERSE, "Reversed text", Ansi.NOT_REVERSED))
        s.append(f"\n{Ansi.UNDERLINE}Standard foreground color attributes{Ansi.END}")
        s.append(Ansi.row_add_c(Ansi.BLACK, "Black", Ansi.DARKGRAY, "Dark Gray"))
        s.append(Ansi.row_add_c(Ansi.RED, "Red", Ansi.BR_RED, "Bright Red"))
        s.append(Ansi.row_add_c(Ansi.GREEN, "Green", Ansi.BR_GREEN, "Bright Green"))
        s.append(Ansi.row_add_c(Ansi.YELLOW, "Yellow", Ansi.BR_YELLOW, "Bright Yellow"))
        s.append(Ansi.row_add_c(Ansi.BLUE, "Blue", Ansi.BR_BLUE, "Bright Blue"))
        s.append(
            Ansi.row_add_c(Ansi.MAGENTA, "Magenta", Ansi.BR_MAGENTA, "Bright Magenta")
        )
        s.append(Ansi.row_add_c(Ansi.CYAN, "Cyan", Ansi.BR_CYAN, "Bright Cyan"))
        s.append(Ansi.row_add_c(Ansi.WHITE, "White", Ansi.BR_WHITE, "Bright White"))

        s.append(f"\n{Ansi.UNDERLINE}Standard background color attributes{Ansi.END}")
        s.append(f"{Ansi.BG_BLACK} Black {Ansi.RESET}")
        s.append(f"{Ansi.BG_RED} Red {Ansi.RESET}")
        s.append(f"{Ansi.BG_GREEN} Green {Ansi.RESET}")
        s.append(f"{Ansi.BG_YELLOW} Yellow {Ansi.RESET}")
        s.append(f"{Ansi.BG_BLUE} Blue {Ansi.RESET}")
        s.append(f"{Ansi.BG_MAGENTA} Magenta {Ansi.RESET}")
        s.append(f"{Ansi.BG_CYAN} Cyan {Ansi.RESET}")

        return "\n".join(s)

    def color_test() -> str:
        """Color attribute test"""
        buf = ""
        for c in range(0, 8):
            buf += f"{Ansi.fg_8bit_color(c)}{c:^7}"

        buf += "\n"
        for c in range(8, 16):
            buf += f"{Ansi.fg_8bit_color(c)}{c:^7}"
        buf += "\n\n"
        for r in range(0, 36):
            x = 16 + r * 6
            buf2 = ""
            for c in range(x, x + 6):
                buf += f"{Ansi.fg_8bit_color(c)}{c:>5}"
                buf2 += f"{Ansi.BLACK}{Ansi.bg_8bit_color(c)}{c:^5}{Ansi.RESET} "

            buf += "  " + buf2

            buf += "\n"

        buf += "\n"

        for c in range(232, 244):
            buf += f"{Ansi.fg_8bit_color(c)}{c:>3} "
        buf += "\n"
        for c in range(244, 256):
            buf += f"{Ansi.fg_8bit_color(c)}{c:>3} "
        buf += "\n"

        return buf


FLAG_BLUE = "\x1b[48;5;20m"
FLAG_YELLOW = "\x1b[48;5;226m"

flag = f"""
{FLAG_BLUE}     {FLAG_YELLOW}  {FLAG_BLUE}          {Ansi.END}
{FLAG_BLUE}     {FLAG_YELLOW}  {FLAG_BLUE}          {Ansi.END}
{FLAG_YELLOW}                 {Ansi.END}
{FLAG_BLUE}     {FLAG_YELLOW}  {FLAG_BLUE}          {Ansi.END}
{FLAG_BLUE}     {FLAG_YELLOW}  {FLAG_BLUE}          {Ansi.END}
"""


def main() -> None:
    logging.basicConfig(
        format="[%(levelname)s] Line: %(lineno)d %(message)s", level=logging.DEBUG
    )
    print(Ansi.color_test())
    print(Ansi.test())


if __name__ == "__main__":
    main()
