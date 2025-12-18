#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
#
# Ansi terminal decoder
#
# File:    terminal.py
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
from enum import Enum
from dataclasses import dataclass, field
import logging
from typing import Any

from escape import Ascii, Ansi
from terminal_colors import (
    PalettePutty,
    Palette256,
    PaletteDefault,
    PaletteVSCodeL,
    PaletteWinXPL,
    PaletteXtermL,
)


class PrivateSequence(Enum):

    # KAM=2 # (KAM) Keyboard Action Mode
    # IRM=4 - (IRM) Insert Replace Mode , h=insert mode, l=replace mode
    #  5 - (DECSCNM) Reverse video mode
    # 12 - (SRM) Send/receive .
    # 20 - Normal Linefeed (LNM

    # 47h - save screen
    # 47l - restore screen
    # AUTO_WRAP = 7  # default on
    # LINES_PER_SCREEN = 9  # l = 36, h = 24(default)
    CURSOR = 25  # Show/hide cursor, h=show, l=hide
    # REPORT_FOCUS = 1004
    # ALT_SCREEN_BUFFER = 1049 # h=on, l=off
    BRACKEDED_PASTE_MODE = 2004  # h=on, l=off
    UNSUPPORTED = 0xFFFF

    @staticmethod
    def decode(seq: int) -> PrivateSequence:
        for ps in PrivateSequence:
            if seq == ps.value:
                # logging.debug(f'Found: {ps}  "{seq}"')
                return ps

        # logging.debug(f'Found: {PrivateSequence.UNSUPPORTED}  "{seq}"')
        return PrivateSequence.UNSUPPORTED


class TextType(Enum):
    TEXT = 0
    C0 = 1
    C1 = 2  # Escape sequences


class C0Type(Enum):
    BELL = Ascii.BEL
    BACKSPACE = Ascii.BS
    TAB = Ascii.TAB
    LINEFEED = Ascii.LF
    FORMFEED = Ascii.FF
    CARRIAGE_RETURN = Ascii.CR
    ESCAPE = Ascii.ESC


class C1Type(Enum):
    CSI = "["  # Control Sequence Introducer
    # OSC = "]"  # Operating System Command
    # Fs (independet function) sequences 0x60-0x7E
    # RIS = "c"  # Reset to Initial State

    # Fp (private use) sequences 0x30-0x3F
    DECSC = "7"  # Save cursor position and character attributes
    DECRC = "8"  # Restore cursor and attributes to previously saved position

    DECPAM_NI = (
        "="  # Application Keypad Mode, switches numeric keypad into application mode
    )
    DECKPNM_NI = ">"  # Normal Keypad Mode

    # RESET = (
    #     "(B"  # Reset characterset to default ASCII character set (ISO 646 / US-ASCII).
    # )
    RESPONSE = "RESPONSE"  # Special response message (not in standard)

    # RESERVERD = "'"  # Reserved for future standardization
    UNSUPPORTED = "UNSUPPORTED"


class CSIType(Enum):
    """Control Sequence Introducer

    Args:
        Enum (_type_): _description_
    """

    CURSOR_UP = "A"
    CURSOR_DOWN = "B"
    CURSOR_FORWARD = "C"
    CURSOR_BACK = "D"
    CURSOR_NEXT_LINE = "E"
    CURSOR_PREVIOUS_LINE = "F"
    CURSOR_HORIZONTAL_ABSOLUTE = "G"
    CURSOR_POSITION = "H"
    ERASE_IN_DISPLAY = "J"
    ERASE_IN_LINE = "K"
    INSERT_LINE = "L"  # Insert line and move current line(s) down (VT102)
    DELETE_LINE = "M"  # Delete line and move lines up (VT102)
    DELETE_CHAR = "P"  # Delete character(s) from cursor position (VT102)
    SCROLL_UP = "S"  # "\e[2S" Move lines up, new lines at bottom
    SCROLL_DOWN = "T"

    PRIMARY_DEVICE_ATTRIBUTES = "c"  # (DA1) <https://vt100.net/docs/vt510-rm/DA1.html>

    CURSOR_VERTICAL_ABSOLUTE = "d"  # (VPA)
    HORIZONTAL_VERTICAL_POSITIONING = "f"  # (HVP) Horizontal and Vertical Position(depends on PUM=Positioning Unit Mode)

    # Private sequences
    ENABLE = "h"  # Enable/set
    DISABLE = "l"  # Disable/reset
    SAVE_CURSOR_POSITION = "s"  # (SCOSC) Save Current Cursor Position
    RESTORE_CURSOR_POSITION = "u"  # (SCORC) Restore Saved Cursor Position

    SGR = "m"  # Select graphics rendition (SGR)
    # AUX = "i"  # Enable/Disable aux serial port
    # DSR = "n"  # Device status report

    SET_SCROLLING_REGION = "r"
    # \e[12;24r  Set scrolling region between line 12 to 24
    # If sgr.code linefeed is received while on row 24 line 12 is removed and lines 13-24 is scrolled up
    # \e[r  Reset scrolling region to entire screen

    INSERT_CHARACTER = "@"  # (ICH) <https://vt100.net/docs/vt510-rm/ICH.html>

    UNSUPPORTED = "UNSUPPORTED"

    @staticmethod
    def decode(s: str) -> CSIType:
        if not s[0] == Ascii.ESC:
            return None

        tc = s[-1]  # termination character in Escape sequence

        for csi in CSIType:
            if tc == csi.value:
                logging.debug(f'Found: {csi}  "{Ansi.to_str(s)}"')
                return csi

        logging.debug(f'Found: {CSIType.UNSUPPORTED}  "{Ansi.to_str(s)}"')
        return CSIType.UNSUPPORTED


class SGRType(Enum):
    """Select Graphic Rendition"""

    RESET = 0  # Reset all attributes
    BOLD = 1  # Bold/increased intensity
    DIM = 2  # Dim/decreased intensity
    ITALIC = 3
    UNDERLINE = 4
    SLOW_BLINK = 5
    RAPID_BLINK = 6
    REVERSE_VIDEO = 7
    CONCEAL = 8
    CROSSED = 9
    PRIMARY = 10  # Primary (default) font

    FRACTUR = 20  # Gothic
    DOUBLE_UNDERLINE = 21

    NORMAL_INTENSITY = 22
    NOT_ITALIC = 23
    NOT_UNDERLINED = 24
    NOT_BLINKING = 25
    NOT_REVERSED = 27
    REVEAL = 28
    NOT_CROSSED = 29
    FG_COLOR_BLACK = 30
    FG_COLOR_RED = 31
    FG_COLOR_GREEN = 32
    FG_COLOR_YELLOW = 33
    FG_COLOR_BLUE = 34
    FG_COLOR_MAGENTA = 35
    FG_COLOR_CYAN = 36
    FG_COLOR_WHITE = 37

    BG_COLOR_BLACK = 40
    BG_COLOR_RED = 41
    BG_COLOR_GREEN = 42
    BG_COLOR_YELLOW = 43
    BG_COLOR_BLUE = 44
    BG_COLOR_MAGENTA = 45
    BG_COLOR_CYAN = 46
    BG_COLOR_WHITE = 47

    OVERLINE = 53
    NOT_OVERLINE = 55

    SET_FG_COLOR_DEFAULT = 39  # Set default color foreground
    SET_BG_COLOR_DEFAULT = 49  # Set default color background

    SET_FG_COLOR = 38  # Select 256 color or RGB color foreground
    SET_BG_COLOR = 48  # Select 256 color or RGB color background
    SET_UL_COLOR = 58  # Select underline color
    FRAMED = 51

    SUPERSCRIPT = 73
    SUBSCRIPT = 74

    FG_COLOR_BR_BLACK = 90
    FG_COLOR_BR_RED = 91
    FG_COLOR_BR_GREEN = 92
    FG_COLOR_BR_YELLOW = 93
    FG_COLOR_BR_BLUE = 94
    FG_COLOR_BR_MAGENTA = 95
    FG_COLOR_BR_CYAN = 96
    FG_COLOR_BR_WHITE = 97

    BG_COLOR_BR_BLACK = 100
    BG_COLOR_BR_RED = 101
    BG_COLOR_BR_GREEN = 102
    BG_COLOR_BR_YELLOW = 103
    BG_COLOR_BR_BLUE = 104
    BG_COLOR_BR_MAGENTA = 105
    BG_COLOR_BR_CYAN = 106
    BG_COLOR_BR_WHITE = 107

    UNSUPPORTED = 0xFFFF

    @staticmethod
    def is_sgr(s: str) -> bool:
        if s[0] == Ascii.ESC and s[-1] == "m":
            return True
        return False

    @staticmethod
    def find_sgr(sgr_code: str) -> SGRType:
        for e in SGRType:
            if sgr_code == e.value:
                return e
        return SGRType.UNSUPPORTED


@dataclass
class SGR:
    """Select Graphic Rendition"""

    type: SGRType = SGRType.UNSUPPORTED
    color: str = None

    def decode(self, attrs: list[str]) -> int:
        """Decodes SGR attributes

        Args:
            attrs (list[str]): attributes

        Returns:
            int: nr of attributes used from attrs list
        """

        if len(attrs) == 0:
            self.type = SGRType.RESET
            return 0

        if attrs[0] == "":  # If no number present it is sgr.code reset(0)
            self.type = SGRType.RESET
            return 1

        attr = int(attrs[0])
        ret = 1

        self.type = SGRType.find_sgr(attr)

        # Extended(256/Truecolor) color management
        if self.type in [SGRType.SET_BG_COLOR, SGRType.SET_FG_COLOR]:
            color_mode = int(attrs[1])

            # 256 color mode
            if color_mode == 5:
                self.color = int(attrs[2])
                ret = 3

            # Truecolor mode
            if color_mode == 2:
                # xx.append({"SGR":SGR.find_sgr(c), "color":int(sp[2])})
                pass

        # Handle underline style
        if self.type == SGRType.UNDERLINE:
            pass

        # Handle underline color
        if self.type == SGRType.SET_UL_COLOR:
            pass

        return ret


@dataclass
class EscapeObj:
    """Escape object"""

    type: C1Type = C1Type.UNSUPPORTED
    private_sequence: PrivateSequence = PrivateSequence.UNSUPPORTED
    csitype: CSIType = CSIType.UNSUPPORTED
    sgrs: list[SGR] = field(default_factory=list)
    n: int = 1
    m: int = 1
    is_text: bool = False
    text: str = ""

    def decode(self, seq: str) -> None:
        if not seq[0] == Ascii.ESC:
            return None

        self.text = Ansi.to_str(seq)

        for type in C1Type:
            if seq[1] == type.value:
                self.type = type

        if self.type == C1Type.UNSUPPORTED:
            logging.debug(f"{str(self)}")
            return None

        if self.type == C1Type.CSI:
            self.decode_csi(seq)
            return None

    def decode_csi(self, seq: str) -> None:

        for csi in CSIType:
            if seq[-1] == csi.value:
                self.csitype = csi

        if self.csitype == CSIType.UNSUPPORTED:
            logging.debug(f"{str(self)}")
            return None

        # The following CSI's has 0 as default for n
        if self.csitype in [CSIType.ERASE_IN_DISPLAY, CSIType.ERASE_IN_LINE]:
            self.n = 0

        # remove questionmark "?" if private sequence
        if self.csitype in (CSIType.ENABLE, CSIType.DISABLE):
            seq = seq.replace("?", "")

        params = seq[2:-1].replace(":", ";").split(";")
        params = [param for param in params if param != ""]  # removing empty strings

        if len(params) > 0:
            self.n = int(params[0])
        if len(params) > 1:
            self.m = int(params[1])

        # Decode SGR (Select Graphic Rendition)
        if self.csitype == CSIType.SGR:
            self.decode_sgr(seq)

        if self.csitype in (CSIType.ENABLE, CSIType.DISABLE):
            self.private_sequence = PrivateSequence.decode(self.n)

        logging.debug(f"{str(self)}")
        if self.csitype == CSIType.SGR:
            for sgr in self.sgrs:
                logging.debug(f"            {sgr}")

    def decode_sgr(self, attr_string: str) -> None:

        x = attr_string[2:-1]
        attributes = x.replace(":", ";").split(";")

        while len(attributes) > 0:
            sgr = SGR()
            x = sgr.decode(attributes)
            for _ in range(x):
                attributes.pop(0)

            self.sgrs.append(sgr)

    def __str__(self) -> str:
        if self.type != C1Type.CSI:
            return f"{self.type:20} {str(self.text):12}"

        if self.csitype in (CSIType.ENABLE, CSIType.DISABLE):
            return f"{self.csitype:20} {str(self.text):12} {self.private_sequence:12}"

        if self.csitype == CSIType.SGR:
            return f"{self.csitype:20} {str(self.text):12}"

        return f"{self.csitype:20} {str(self.text):12}n={self.n:<2} m={self.m:<2}"
        # return f"{self.csi:20} n={self.n:<2} m={self.m:<2}"


class EscapeTokenizer:
    """Tokenize escape sequences"""

    def __init__(self):
        self.clear()

    def clear(self):
        self.seq = ""
        self.lbuf = []

    def append_string(self, data: str) -> None:
        self.lbuf.extend(list(data))

    def append_bytearray(self, data: bytearray) -> None:
        utf = data.decode("utf-8")
        self.lbuf.extend(list(utf))

    def is_csi(self) -> bool:
        """Check if sequence string is CSI terminated"""

        if self.seq[1] != C1Type.CSI.value:
            return False

        lc = ord(self.seq[-1])
        if lc == 0x5B:  # "[" is excluded as terminator, possibly wrong
            return False

        if lc >= 0x40 and lc <= 0x7E:
            return True

        return False

    def is_Fp(self) -> bool:
        """Check if independent function dequence"""

        lc = ord(self.seq[1])
        if (lc >= 0x60) and (lc <= 0x7E):
            return True

    def is_Fs(self) -> bool:
        """Check if private two character sequence"""

        lc = ord(self.seq[-1])
        if (lc >= 0x30) and (lc <= 0x3F):
            return True

    def is_terminated(self) -> bool:
        """Check if Escape sequence is terminated"""

        seq_len = len(self.seq)

        if seq_len <= 1:
            return False

        if seq_len == 2:
            if self.is_Fp() is True:
                return True

            if self.is_Fs() is True:
                return True

        if seq_len == 3 and self.seq[1] == "(":
            return True

        if self.is_csi() is True:
            return True

        return False

    def __iter__(self):
        self.i = 0
        return self

    def __next__(self) -> str:
        try:
            while True:
                ch = self.lbuf.pop(0)  # get next character from buffer

                if ch in [Ascii.LF, Ascii.BEL, Ascii.BS, Ascii.CR]:
                    if len(self.seq) > 0:
                        ret = self.seq
                        self.seq = ""
                        self.lbuf.insert(0, ch)
                        return ret
                    return ch

                if ch == Ascii.ESC:  # Escape sequence start character found
                    if len(self.seq) > 0:
                        ret = self.seq
                        self.seq = ch
                        return ret

                    self.seq = ch
                    continue

                self.seq += ch

                if self.seq[0] == Ascii.ESC:
                    if self.is_terminated() is True:
                        ret = self.seq
                        self.seq = ""
                        return ret

        except IndexError:
            if len(self.seq) == 0:
                raise StopIteration

            if self.seq[0] == Ascii.ESC:
                raise StopIteration

            ret = self.seq
            self.seq = ""
            return ret


@dataclass
class TerminalCoordinate:
    row: int = 1
    column: int = 1


@dataclass
class TerminalAttributeState:
    """Terminal attribute state class"""

    BOLD: bool = False
    DIM: bool = False
    ITALIC: bool = False
    CROSSED: bool = False
    UNDERLINE: bool = False
    SUPERSCRIPT: bool = False
    SUBSCRIPT: bool = False
    REVERSE: bool = False
    OVERLINE: bool = False
    CURSOR: bool = False
    FG_COLOR: str = ""
    BG_COLOR: str = ""
    DEFAULT_FG_COLOR: str = ""
    DEFAULT_BG_COLOR: str = ""
    palette: list = None

    def __post_init__(self) -> None:
        self.DEFAULT_FG_COLOR = self.palette[7]
        self.DEFAULT_BG_COLOR = self.palette[0]
        self.FG_COLOR = self.DEFAULT_FG_COLOR
        self.BG_COLOR = self.DEFAULT_BG_COLOR

    def reset(self):
        """Reset all attributes to default"""
        self.BOLD = False
        self.DIM = False
        self.ITALIC = False
        self.CROSSED = False
        self.UNDERLINE = False
        self.SUPERSCRIPT = False
        self.SUBSCRIPT = False
        self.REVERSE = False
        self.OVERLINE = False
        self.FG_COLOR = self.DEFAULT_FG_COLOR
        self.BG_COLOR = self.DEFAULT_BG_COLOR
        self.CURSOR = False

    def __str__(self) -> str:
        state: int = 0
        if self.BOLD is True:
            state += 1
        if self.DIM is True:
            state += 2
        if self.ITALIC is True:
            state += 4
        if self.CROSSED is True:
            state += 8
        if self.UNDERLINE is True:
            state += 16
        if self.SUPERSCRIPT is True:
            state += 32
        if self.SUBSCRIPT is True:
            state += 64
        if self.REVERSE is True:
            state += 128
        if self.OVERLINE is True:
            state += 256
        if self.CURSOR is True:
            state += 512
        return f"{state:010b}"


class TerminalCharacter:
    def __init__(self, ch: str, tas: TerminalAttributeState):
        self.tas = copy(tas)
        self.ch = ch
        self.cursor: bool = False

    def __str__(self) -> str:
        return f"{self.tas} {self.ch}"


class TerminalLine:
    def __init__(
        self, tas: TerminalAttributeState, id: int = 0, columns: int = 80
    ) -> None:
        self.line: list[TerminalCharacter] = []
        for i in range(0, columns):
            self.line.append(TerminalCharacter(" ", tas))
        self.tas = tas
        self.id: int = id
        self.text: str = ""
        self.changed: bool = False
        self.cursor = None
        self.old_cursor = None

    def __str__(self) -> str:
        tchars = []
        for tc in self.line:
            # tchars.append(str(tc))
            tchars.append(tc.ch)

        return f"Id={self.id} {"".join(tchars)}"

    def clear(self):
        """Clear all character to " " and set attributes do default"""
        for ch in self.line:
            ch.tas = self.tas
            ch.ch = " "

    def reset(self):
        self.changed = False
        self.old_cursor = self.cursor
        self.cursor = None

        for ch in self.line:
            ch.tas.CURSOR = False

    def set_cursor(self, cursor: TerminalCoordinate) -> None:
        """Calling set_cursor indicates that the cursor i located on this particular line"""
        # print(f"Cursor on id: {self.id} line: {cursor}")
        self.cursor = cursor
        try:
            self.line[cursor.column - 1].tas.CURSOR = True
        except IndexError:
            logging.debug(f"IndexError: {cursor=} {len(self.line)}")

        self.changed = True

    def has_changed(self, cursor: TerminalCoordinate = None) -> bool:
        """Check if line has changed since last update"""

        # if cursor is not None it means that the cursor is present on this particular row
        # self.cursor = cursor
        if self.old_cursor != self.cursor:
            self.changed = True

        return self.changed

    def is_reversed(self, tas: TerminalAttributeState) -> bool:
        """Check if text is reversed"""
        # print(f"Cursor on id: {self.id} line: {self.cursor}")
        if tas.CURSOR is True:
            # print("cursor")
            return not tas.REVERSE

        return tas.REVERSE

    def attr_to_html(self, data: str, tas: TerminalAttributeState) -> str:
        """Convert terminal attributes to htmltags"""

        if self.is_reversed(tas):
            bg_color = tas.FG_COLOR
            fg_color = tas.BG_COLOR
        else:
            fg_color = tas.FG_COLOR
            bg_color = tas.BG_COLOR

        b = f'<span style="color:{fg_color};background-color:{bg_color};font-size:12pt;'

        if tas.BOLD:
            b += "font-weight:bold;"
        if tas.ITALIC:
            b += "font-style:italic;"
        if tas.UNDERLINE:
            b += "text-decoration:underline;"
        if tas.CROSSED:
            b += "text-decoration:line-through;"
        if tas.OVERLINE:
            b += "text-decoration:overline;"

        b += '">'
        b += data.replace(" ", "&nbsp;").replace("<", "&lt;").replace(">", "&gt;")
        b += "</span>"
        return b

    def line_to_html(self) -> str:
        """Convert line to html, including attributes and cursor"""
        line_text = []
        line_text.append('<div style="line-height:30px;">')
        text = ""
        for idx, tc in enumerate(self.line):
            if idx == 0:
                tas = tc.tas

            # if self.cursor is not None:
            #     if idx == (self.cursor.column - 1):
            #         tas.CURSOR = True
            #     else:
            #         tas.CURSOR = False

            # else:
            #     tas.CURSOR = False

            if tas == tc.tas:
                text += tc.ch
            else:
                line_text.append(self.attr_to_html(text, tas))
                text = tc.ch
                tas = tc.tas

        if len(text) > 0:
            line_text.append(self.attr_to_html(text, tas))

        line_text.append("</div>")

        # if self.cursor is not None:
        #     print(f"Cursor on id: {self.id} line: {self.cursor}")

        return "".join(line_text)

    def append(self, text: str, column: int) -> int:
        """Append text to line at position column"""

        i = column - 1
        for ch in text:
            tc = TerminalCharacter(ch, self.tas)
            try:
                self.line[i] = tc
            except IndexError:
                self.line.append(tc)
            i += 1
        self.update()
        return i + 1

    def insert_char(self, column: int, n: int) -> None:
        """Insert n space(s) at position column"""
        for i in range(n):
            tc = TerminalCharacter(" ", self.tas)
            self.line.insert(column - 1, tc)
        self.update()

    def delete_char(self, column: int, n: int) -> None:
        """Delete n characters at position column"""
        for i in range(column, column + n):
            # print(f"Deleting: {self.line[i-1].ch}")
            self.line.pop(i - 1)
        self.update()

    def erase_in_line(self, column: int, mode: int) -> None:
        """Remove characters in line.

        Args:
            column (int): Position in line
            mode (int):  0 = erase after column
                         1 = erase before column
                         3 = erase entire line
        """
        if mode == 0:  # erase after column
            erase_range = range(column - 1, len(self.line))
        elif mode == 1:  # erase before column
            erase_range = range(0, column)
        elif mode == 2:  # erase entire line
            erase_range = range(0, len(self.line))

        for i in erase_range:
            try:
                self.line[i] = TerminalCharacter(" ", self.tas)
            except IndexError:
                self.line.append(TerminalCharacter(" ", self.tas))
        self.update()

    def update(self):
        """Update line status"""
        self.changed = True
        self.text = str(self)


class TerminalState:
    """Terminal state class"""

    def __init__(self, rows: int = 24, columns: int = 80) -> None:
        self.tokenizer = EscapeTokenizer()
        self.line_id: int = 0
        # self.palette = PaletteVSCodeL
        # self.palette = PaletteXtermL
        # self.palette = PaletteWinXPL
        self.palette = PalettePutty
        self.tas = TerminalAttributeState(palette=self.palette)
        self.cursor_visible: bool = False
        self.terminal_response_list: list[Any] = []
        self.set_terminal(rows, columns)
        self.reset()

    def set_cursor_visible(self, visible: bool) -> None:
        self.cursor_visible = visible

    def set_cursor(self, column=None, row=None) -> None:
        """Set cursor position"""
        if column is not None:
            self.cursor.column = column
            if self.cursor.column < 1:
                self.cursor.column = 1

        if row is not None:
            self.cursor.row = row
            if self.cursor.row < 1:
                self.cursor.row = 1
            if self.cursor.row > self.max.row:
                self.cursor.row = self.max.row

    def set_cursor_rel(self, column=None, row=None) -> None:
        """Set cursor with relative cursor movements"""

        if column is not None:
            new_column = self.cursor.column + column
        else:
            new_column = None

        if row is not None:
            new_row = self.cursor.row + row
        else:
            new_row = None

        self.set_cursor(column=new_column, row=new_row)

    def fg_color(self, color: SGRType) -> str:
        """Return foreground color"""
        color_id = color.value - 30
        if self.tas.BOLD is True:
            color_id += 8

        return self.palette[color_id]

    def bg_color(self, color: SGRType) -> str:
        """Return background color"""
        return self.palette[color.value - 40]

    def get_256_color(self, color: int) -> str:
        """Return 256 color"""
        if color < 16:
            return self.palette[color]

        return Palette256[color]["hex"]

    def set_terminal(self, rows: int, columns: int) -> None:
        """Set terminal size"""
        self.rows = rows
        self.columns = columns

    def reset(self):
        self.cursor = TerminalCoordinate()
        self.saved_cursor = TerminalCoordinate()
        self.max = TerminalCoordinate(self.rows, self.columns)
        self.lines: list[TerminalLine] = []
        for _ in range(0, self.max.row):
            self.new_line()
        self.tokenizer.clear()
        self.reset_attr()

    def reset_attr(self):
        self.tas.reset()

    def pos_str(self) -> str:
        """Return cursor position as string"""
        ps = f"{self.cursor}"
        return ps

    def new_line(self) -> TerminalLine:

        nl = TerminalLine(tas=self.tas, id=self.line_id, columns=self.max.column)
        nl.append(" ", 0)  # For some reason needed
        self.line_id += 1
        self.lines.insert(0, nl)
        return nl

    def delete_line(self, n: int = 1) -> None:
        """Delete n row(s) at cursor, existing rows scroll up"""
        for i in range(self.max.row - self.cursor.row, -1, -1):
            self.lines[i].line = self.lines[i - 1].line
            self.lines[i].changed = True

        self.clear_line(self.max.row)

    def clear_line(self, line: int) -> None:
        """Clear line at position line"""
        self.lines[self.max.row - line].clear()

        # For some reason the following line is needed.
        # A guess is that it might have with html rendering to do
        self.lines[self.max.row - line].append(" ", 1)

    def insert_line(self, n: int = 1) -> None:
        """insert n row(s) at cursor, existing rows scroll down"""

        pos = self.max.row - self.cursor.row
        logging.debug(f"Insert at: {pos}")

        for i in range(0, pos + 1):
            self.lines[i].line = self.lines[i + 1].line
            self.lines[i].changed = True

        self.clear_line(self.cursor.row)

    def insert_char(self, n: int = 1) -> None:
        """Insert n characters at cursor position"""
        self.lines[self.max.row - self.cursor.row].insert_char(self.cursor.column, n)

    def delete_char(self, n: int = 1) -> None:
        """Delete n characters at cursor position"""
        self.lines[self.max.row - self.cursor.row].delete_char(self.cursor.column, n)

    def erase_in_line(self, mode: int) -> None:
        """Erase in line"""
        logging.debug(
            f"Erase in line: {self.cursor.row=}  {self.cursor.column=} {mode=}"
        )
        self.lines[self.max.row - self.cursor.row].erase_in_line(
            self.cursor.column, mode
        )

    def erase_in_display(self, mode: int) -> None:
        """Erase in display"""
        if mode == 0:  # Clear from cursor to end of screen
            for line in range(self.cursor.row, self.max.row + 1):
                self.lines[self.max.row - line].erase_in_line(1, 2)
        elif mode == 1:  # Clear from cursor to beginning of screen
            for line in range(1, self.cursor.row):
                self.lines[self.max.row - line].erase_in_line(1, 2)
        elif mode == 2:  # Clear entire screen
            for line in range(1, self.max.row):
                self.lines[self.max.row - line].erase_in_line(1, 2)
        elif mode == 3:  # Clear saved lines
            logging.debug(f"UNSUPPORTED: Erase in display mode 3 not implemented")

    def append(self, text: str) -> None:
        """Append text to terminal line"""
        self.cursor.column = self.lines[self.max.row - self.cursor.row].append(
            text, self.cursor.column
        )
        tok_str = f'"{text}"'
        logging.debug(f"(Text): {tok_str}")

    def handle_sgr(self, eo: EscapeObj) -> None:
        """Handle Select Graphic Rendition (SGR)"""
        for sgr in eo.sgrs:
            if sgr.type == SGRType.BOLD:
                self.tas.BOLD = True

            elif sgr.type == SGRType.ITALIC:
                self.tas.ITALIC = True

            elif sgr.type == SGRType.NOT_ITALIC:
                self.tas.ITALIC = False

            elif sgr.type == SGRType.UNDERLINE:
                self.tas.UNDERLINE = True

            elif sgr.type == SGRType.NOT_UNDERLINED:
                self.tas.UNDERLINE = False

            elif sgr.type == SGRType.CROSSED:
                self.tas.CROSSED = True

            elif sgr.type == SGRType.NOT_CROSSED:
                self.tas.CROSSED = False

            elif sgr.type == SGRType.SUPERSCRIPT:
                self.tas.SUPERSCRIPT = True

            elif sgr.type == SGRType.SUBSCRIPT:
                self.tas.SUBSCRIPT = True

            elif sgr.type == SGRType.OVERLINE:
                self.tas.OVERLINE = True
                self.tas.UNDERLINE = False
                self.tas.CROSSED = False

            elif sgr.type == SGRType.NOT_OVERLINE:
                self.tas.OVERLINE = False

            elif sgr.type == SGRType.NORMAL_INTENSITY:
                self.tas.BOLD = False
                self.tas.DIM = False

            elif sgr.type == SGRType.REVERSE_VIDEO:
                self.tas.REVERSE = True

            elif sgr.type == SGRType.NOT_REVERSED:
                self.tas.REVERSE = False

            elif sgr.type == SGRType.RESET:
                self.tas.reset()

            elif sgr.type == SGRType.SLOW_BLINK:
                self.BLINKING = True

            elif sgr.type == SGRType.NOT_BLINKING:
                self.BLINKING = False

            elif sgr.type in [
                SGRType.FG_COLOR_BLACK,
                SGRType.FG_COLOR_RED,
                SGRType.FG_COLOR_GREEN,
                SGRType.FG_COLOR_YELLOW,
                SGRType.FG_COLOR_BLUE,
                SGRType.FG_COLOR_MAGENTA,
                SGRType.FG_COLOR_CYAN,
                SGRType.FG_COLOR_WHITE,
            ]:

                self.tas.FG_COLOR = self.fg_color(sgr.type)

            elif sgr.type in [
                SGRType.BG_COLOR_BLACK,
                SGRType.BG_COLOR_RED,
                SGRType.BG_COLOR_GREEN,
                SGRType.BG_COLOR_YELLOW,
                SGRType.BG_COLOR_BLUE,
                SGRType.BG_COLOR_MAGENTA,
                SGRType.BG_COLOR_CYAN,
                SGRType.BG_COLOR_WHITE,
            ]:
                self.tas.BG_COLOR = self.bg_color(sgr.type)

            elif sgr.type == SGRType.SET_FG_COLOR:
                self.tas.FG_COLOR = self.get_256_color(sgr.color)

            elif sgr.type == SGRType.SET_BG_COLOR:
                self.tas.BG_COLOR = self.get_256_color(sgr.color)

            elif sgr.type == SGRType.SET_FG_COLOR_DEFAULT:
                self.tas.FG_COLOR = self.tas.DEFAULT_FG_COLOR

            elif sgr.type == SGRType.SET_BG_COLOR_DEFAULT:
                self.tas.BG_COLOR = self.tas.DEFAULT_BG_COLOR

            elif sgr.type in [
                SGRType.FG_COLOR_BR_BLACK,
                SGRType.FG_COLOR_BR_RED,
                SGRType.FG_COLOR_BR_GREEN,
                SGRType.FG_COLOR_BR_YELLOW,
                SGRType.FG_COLOR_BR_BLUE,
                SGRType.FG_COLOR_BR_MAGENTA,
                SGRType.FG_COLOR_BR_CYAN,
                SGRType.FG_COLOR_BR_WHITE,
            ]:
                self.tas.FG_COLOR = self.get_256_color(sgr.type.value - 90 + 8)

            elif sgr.type in [
                SGRType.BG_COLOR_BR_BLACK,
                SGRType.BG_COLOR_BR_RED,
                SGRType.BG_COLOR_BR_GREEN,
                SGRType.BG_COLOR_BR_YELLOW,
                SGRType.BG_COLOR_BR_BLUE,
                SGRType.BG_COLOR_BR_MAGENTA,
                SGRType.BG_COLOR_BR_CYAN,
                SGRType.BG_COLOR_BR_WHITE,
            ]:
                self.tas.BG_COLOR = self.get_256_color(sgr.type.value - 100 + 8)

    def handle_csi(self, eo: EscapeObj) -> None:
        """Handle Control Sequence Introducer (CSI)"""
        if eo.csitype == CSIType.CURSOR_UP:
            self.set_cursor(row=(self.cursor.row - eo.n))

        if eo.csitype == CSIType.CURSOR_DOWN:
            self.set_cursor(row=(self.cursor.row + eo.n))

        if eo.csitype == CSIType.CURSOR_FORWARD:
            self.set_cursor(column=(self.cursor.column + eo.n))

        if eo.csitype == CSIType.CURSOR_BACK:
            self.set_cursor(column=(self.cursor.column - eo.n))

        if eo.csitype == CSIType.CURSOR_NEXT_LINE:
            self.set_cursor(column=1, row=(self.cursor.row + eo.n))

        if eo.csitype == CSIType.CURSOR_PREVIOUS_LINE:
            self.set_cursor(column=1, row=(self.cursor.row - eo.n))

        if eo.csitype == CSIType.CURSOR_POSITION:
            self.set_cursor(column=eo.m, row=eo.n)

        if eo.csitype == CSIType.CURSOR_HORIZONTAL_ABSOLUTE:
            self.set_cursor(column=eo.n)

        if eo.csitype == CSIType.CURSOR_VERTICAL_ABSOLUTE:
            self.set_cursor(row=eo.n)

        # Horizontal and Vertical Position(depends on PUM)
        if eo.csitype == CSIType.HORIZONTAL_VERTICAL_POSITIONING:
            self.set_cursor(column=eo.m, row=eo.n)

        if eo.csitype == CSIType.ERASE_IN_DISPLAY:
            self.erase_in_display(eo.n)

        if eo.csitype == CSIType.ERASE_IN_LINE:
            self.erase_in_line(eo.n)

        if eo.csitype == CSIType.SAVE_CURSOR_POSITION:
            self.saved_cursor = copy(self.cursor)

        if eo.csitype == CSIType.RESTORE_CURSOR_POSITION:
            self.cursor = copy(self.saved_cursor)

        if eo.csitype == CSIType.INSERT_LINE:
            self.insert_line(eo.n)

        if eo.csitype == CSIType.DELETE_LINE:
            self.delete_line(eo.n)

        if eo.csitype == CSIType.DELETE_CHAR:
            self.delete_char(eo.n)

        if eo.csitype == CSIType.SET_SCROLLING_REGION:
            logging.debug(f"{eo.csitype.name} is UNSUPPORTED")

        if eo.csitype == CSIType.INSERT_CHARACTER:
            self.insert_char(eo.m)

        if eo.csitype == CSIType.SGR:
            self.handle_sgr(eo)

        if eo.csitype == CSIType.PRIMARY_DEVICE_ATTRIBUTES:
            rsp = f"{Ansi.CSI}?64;c"  # 64 = service class for VT510
            response = EscapeObj(type=C1Type.RESPONSE, text=rsp)
            self.terminal_response_list.append(response)

        if eo.csitype == CSIType.ENABLE:
            self.handle_private_sequence(eo, True)

        if eo.csitype == CSIType.DISABLE:
            self.handle_private_sequence(eo, False)

    def handle_private_sequence(self, eo: EscapeObj, state: bool) -> None:
        """Handle private sequence"""

        if eo.private_sequence == PrivateSequence.CURSOR:
            # self.cursor_visible = state
            self.set_cursor_visible(state)

        if eo.private_sequence == PrivateSequence.BRACKEDED_PASTE_MODE:
            logging.debug(f"{eo.private_sequence} is UNSUPPORTED")

    def update(self, data: str) -> list:
        """Update terminal state with data"""
        self.terminal_response_list.clear()
        last_line_id = self.lines[0].id
        self.tokenizer.append_string(data)
        for line in self.lines:
            line.reset()
        # for i in range(0, self.max.row):
        #     self.lines[i].reset()

        for token in self.tokenizer:
            if Ansi.is_escape_seq(token):
                eo = EscapeObj()
                eo.decode(token)

                if eo.type == C1Type.DECSC:  # Save cursor and attributes
                    self.saved_cursor = copy(self.cursor)
                    self.saved_tas = copy(self.tas)

                if eo.type == C1Type.DECRC:  # Restore cursor and attributes
                    self.cursor = copy(self.saved_cursor)
                    self.tas = copy(self.saved_tas)

                if eo.type == C1Type.CSI:
                    self.handle_csi(eo)

                continue

            if token == Ascii.CR:  # carriage return
                self.set_cursor(column=1)
                logging.debug(f"(CR)    Carriage Return {self.pos_str()}")
                continue

            if token == Ascii.BS:  # backspace
                self.set_cursor(column=(self.cursor.column - 1))
                logging.debug(f"(BS)    Backspace       {self.pos_str()}")
                continue

            if token == Ascii.LF:  # newline
                if (self.cursor.row) >= self.max.row:
                    self.new_line()

                self.set_cursor(column=1, row=(self.cursor.row + 1))

                logging.debug(f"(LF)    Linefeed        {self.pos_str()}")
                continue

            if token in [Ascii.BEL]:  # bell
                continue

            # Adding normal text
            self.append(token)

        # Find rows that need to be updated
        lines_to_update = self.lines[0].id - (last_line_id) + 24
        for i in range(lines_to_update - 1, -1, -1):

            if self.lines[i].has_changed(None) is True:
                self.terminal_response_list.append(self.lines[i])

        if self.cursor_visible is True:
            self.lines[24 - self.cursor.row].set_cursor(self.cursor)
            self.terminal_response_list.append(self.lines[24 - self.cursor.row])

        logging.debug(
            f"Changed lines:{len(self.terminal_response_list)}  Last Id={self.line_id-1}  Cursor={self.cursor}"
        )
        return self.terminal_response_list


def main() -> None:
    logging.basicConfig(
        format="[%(levelname)s] Line: %(lineno)d %(message)s", level=logging.DEBUG
    )
    # print(Ansi.color_test())
    print(Ansi.test())

    incomplete_escape_sequence = f"""
    {Ansi.BR_MAGENTA}Some colored text{Ansi.END}
    {Ansi.GREEN}Some more text with incomplete escape sequence \x1b["""

    end_with_newline = "Some text with newline end\n"

    test_string = f"Normal color {Ansi.RED}Red color {Ansi.END}More normal color {Ansi.BLUE}Blue angels {Ansi.END}White end"

    et = EscapeTokenizer()
    et.append_string(test_string)
    for token in et:
        print(f"{token=}")

    ts = TerminalState()
    ts.update(Ansi.RESET)
    ts.update(Ansi.END)
    ts.update(Ansi.RED)

    # dec4 = EscapeDecoder()
    # dec4.append_string(incomplete_escape_sequence)
    # for x in dec4:
    #     pass

    # dec5 = EscapeDecoder()
    # dec5.append_string(end_with_newline)
    # for x in dec5:
    #     pass

    # dec6 = EscapeDecoder()
    # dec6.append_string(cursor_test)
    # for x in dec6:
    #     pass

    # dec6 = EscapeTokenizer()
    # dec6.append_string(cursor_test)
    # for x in dec6:
    #     pass

    # et = TerminalState()
    # et.update(escape_attribute_test)
    # print("Buf:\n" + et.html_buf)

    # print(dir(Ascii))
    # print(ascii_table())


if __name__ == "__main__":
    main()
