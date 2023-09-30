#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
#
# terminal window for qt5
#
# File:     terminalwin
# Author:   Peter Malmberg  <peter.malmberg@gmail.com>
# Org:      __ORGANISTATION__
# Date:     2022-12-02
# License:
# Python:   >= 3.0
#
# ----------------------------------------------------------------------------

# Imports --------------------------------------------------------------------

import logging

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTextCursor, QFont, QKeyEvent
from PyQt5.QtWidgets import QTextEdit, QPlainTextEdit

from escape import Escape, Ascii, TerminalState, CSI, SGR, EscapeObj

# Variables ------------------------------------------------------------------

# Code -----------------------------------------------------------------------

keys = {
    Qt.Key_Enter: ("\n", "Enter"),
    Qt.Key_Return: ("\n", "Return"),
    Qt.Key_Escape: ("", "Escape"),
    Qt.Key_Delete: ("", "Delete"),
    Qt.Key_Left: (Escape.BACK, "Left"),
    Qt.Key_Right: (Escape.FORWARD, "Right"),
    Qt.Key_Up: (Escape.UP, "Up"),
    Qt.Key_Down: (Escape.DOWN, "Down"),
    Qt.Key_Insert: ("", "Insert"),
    Qt.Key_Backspace: ("\b", "Backspace"),
    Qt.Key_Home: ("", "Home"),
    Qt.Key_End: ("", "End"),
    Qt.Key_PageDown: ("", "Page down"),
    Qt.Key_PageUp: ("", "Page up"),
    Qt.Key_F1: ("\x09", "F1"),
    Qt.Key_F2: ("", "F2"),
    Qt.Key_F3: ("", "F3"),
    Qt.Key_F4: ("", "F4"),
    Qt.Key_F5: ("", "F5"),
    Qt.Key_F6: ("", "F6"),
    Qt.Key_F7: ("", "F7"),
    Qt.Key_F8: ("", "F8"),
    Qt.Key_F9: ("", "F9"),
    Qt.Key_F10: ("", "F10"),
    Qt.Key_F11: ("", "F11"),
    Qt.Key_F12: ("", "F12"),
    Qt.Key_Control: ("", "Control"),
    Qt.Key_Shift: ("", "Shift"),
    Qt.Key_Alt: ("", "Alt"),
    Qt.Key_AltGr: ("", "Alt Gr"),
    Qt.Key_Space: (" ", "Space"),
    Qt.Key_Print: ("", "Print"),
    Qt.Key_ScrollLock: ("", "Scroll lock"),
    Qt.Key_CapsLock: ("", "Caps lock"),
    Qt.Key_Pause: ("", "Pause"),
    Qt.Key_Tab: (Ascii.TAB, "Tab"),
}


def get_description(key: QKeyEvent) -> str:
    for a, b in keys.items():
        if key.key() == a:
            return b[1]

    return key.text()


def get_key(key: QKeyEvent) -> str:
    for a, b in keys.items():
        if key.key() == a:
            return b[0]

    return key.text()


class QTerminalWidget(QPlainTextEdit):
    def __init__(self, parent=None, serialPort=None, init=""):
        super().__init__(parent)
        self.serialPort = serialPort
        # self.setObjectName("textEdit")

        font = QFont()
        font.setFamily("Monospace")
        font.setPointSize(10)
        self.setFont(font)
        # self.maximumBlockCount = 100
        # self.setMaximumBlockCount(10)

        # self.setFocusPolicy(Qt.NoFocus)
        self.setStyleSheet(
            "background-color: rgb(0, 0, 0); color : White; font-family:Monospace; font-size:10pt; line-height:1.5;"
        )
        # self.setStyleSheet("background-color: rgb(0, 0, 0); color : White; line-height:20pt; font-family:Monospace")

        self.cur = QTextCursor(self.document())

        # self.insert(init)
        # self.setPlaceholderText("asdfasdfasdf")
        # doc = self.document()
        # settings = QTextOption()
        # settings.setFlags(QTextOption.IncludeTrailingSpaces | QTextOption.ShowTabsAndSpaces )
        # doc.setDefaultTextOption(settings)
        # p = self.viewport().palette()
        # p.setColor(self.viewport().backgroundRole(), QColor(0,0,0))
        # self.viewport().setPalette(p)

        self.ts = TerminalState()

        self.setReadOnly(True)
        self.clear()

        self.ensureCursorVisible()
        self.setCursorWidth(2)
        self.overwrite = False
        self.idx = 0
        self.maxLines = 100
        self.cr = False

    def setMaxLines(self, maxLines):
        self.maxLines = maxLines

    def clear(self):
        super().clear()
        self.ts.reset()
        self.moveCursor(QTextCursor.End)

    def update(self, s: str) -> str:
        self.ts.update(s)
        # b = template + self.ts.get_buf()
        self.buf += b
        logging.debug(b)

    def printpos(self, newPos: QTextCursor.MoveOperation) -> None:
        pos = self.cur.position()
        bpos = self.cur.positionInBlock()
        logging.debug(f"Cursor moved: abs:{pos}  block:{bpos}  newpos: {newPos}")

    def insert(self, html):
        self.cur.insertHtml(html)
        # self.printpos(None)

    def move(self, newPos: QTextCursor) -> None:
        self.cur.movePosition(newPos)
        # self.printpos(newPos)

    def remove_rows_alt(self, lines):
        logging.debug(f"Removing {lines} lines")
        cursor = self.textCursor()  # QTextCursor(self.document())

        for x in range(lines):
            cursor.movePosition(QTextCursor.Start, QTextCursor.MoveAnchor)
            cursor.select(QTextCursor.LineUnderCursor)
            cursor.removeSelectedText()
            cursor.deleteChar()

        self.setTextCursor(cursor)

    def limit_lines(self):
        lines = self.document().lineCount()
        logging.debug(f"Lines: {lines}  Maxlines: {self.maxLines}")
        if lines > self.maxLines:
            self.remove_rows_alt(lines - self.maxLines)

    def append_html(self, html):
        self.move(QTextCursor.End)
        self.insert(html)
        self.limit_lines()

    def insertHtml(self, html):
        l = len(html)
        self.cur.insertHtml(html)
        self.cur.movePosition(QTextCursor.Right, l)

    def append_terminal_text(self, s: str) -> None:
        lines = self.ts.update(s)

        # lines = self.document().lineCount()

        for line in lines:
            if type(line) == EscapeObj:
                if line.csi == CSI.CURSOR_UP:
                    self.move(QTextCursor.Up)
                    continue

                if line.csi == CSI.CURSOR_DOWN:
                    self.move(QTextCursor.Down)
                    continue

                if line.csi == CSI.CURSOR_NEXT_LINE:
                    continue

                if line.csi == CSI.ERASE_IN_DISPLAY:
                    self.clear()
                    continue

                if line.csi == CSI.ERASE_IN_LINE:
                    continue

                if line.csi == CSI.CURSOR_POSITION:
                    self.move(QTextCursor.End)
                    self.move(QTextCursor.StartOfLine)
                    for a in range(0, 25 - line.n):
                        self.move(QTextCursor.Up)

                    logging.debug(f"Cursor position: n: {line.n}  m: {line.m}")
                    # self.cur.ro
                    continue

                if line.csi == CSI.CURSOR_PREVIOUS_LINE:
                    logging.debug("Cursor previous line")
                    self.move(QTextCursor.StartOfLine)
                    self.move(QTextCursor.Up)
                    continue

            if line == Ascii.BS:
                logging.debug("Backspace")
                # self.cur.deletePreviousChar()
                self.move(QTextCursor.Left)
                continue

            if line == Ascii.CR:
                logging.debug("Carriage return")
                self.move(QTextCursor.StartOfLine)
                self.cr = True
                continue

            if line == Ascii.NL:
                logging.debug("Newline")
                if self.cr:
                    self.move(QTextCursor.EndOfLine)
                    self.cr = False
                self.cur.insertHtml("<br>")
                continue

            # self.append_html(line)
            # text = line.replace("<", "&lt;")
            text = line
            l = len(text)
            if not self.cur.atEnd():
                self.cur.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, l)
                # print(f"Distance to end: {l}")
                # self.cur.setPosition()
                # self.cur.removeSelectedText()
                self.cur.insertHtml(text)
                self.cur.movePosition(QTextCursor.Right, l)
                continue

            # text = text.replace("<", "&lt;")
            self.cur.insertHtml(text)
            self.cur.movePosition(QTextCursor.Right, l)
            self.cr = False

        self.limit_lines()

    # def keyPressEvent(self, e: QKeyEvent) -> None:
    #     logging.debug(f"  {e.key():x}  {get_description(e)}")
    #     self.sp.send_string(get_key(e))
    #     #super().keyPressEvent(e)

    def scroll_down(self):
        vsb = self.verticalScrollBar()
        vsb.setValue(vsb.maximum())


def main() -> None:
    pass


if __name__ == "__main__":
    main()
