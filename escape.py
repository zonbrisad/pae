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


class Ascii:
    NUL = "\x00"  # Null character
    SOH = "\x01"  # Start of heading
    STX = "\x02"  # Start of text
    ETX = "\x03"  # End of text (Ctrl-C)
    EOT = "\x04"  # End of transmition (Ctrl-D)
    ENQ = "\x05"  # Enquiry
    ACK = "\x06"  # Acknowledge
    BEL = "\x07"  # Bell, Alert
    BS = "\x08"  # Backspace
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
