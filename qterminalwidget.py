#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
#
# Ansi terminal window for Qt5
#
# File:     terminalwin
# Author:   Peter Malmberg  <peter.malmberg@gmail.com>
# Org:
# Date:     2022-12-02
# License:
# Python:   >= 3.0
#
# ----------------------------------------------------------------------------

# Imports --------------------------------------------------------------------

import logging
import sys
from typing import Callable

from escape import Ansi, Ascii
from terminal import EscapeObj, TerminalState, TerminalLine

from PyQt5.QtCore import Qt
from PyQt5.QtGui import (
    QTextCursor,
    QKeyEvent,
    QKeyEvent,
    QCloseEvent,
)
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QPlainTextEdit,
    QVBoxLayout,
    QHBoxLayout,
    QMenu,
    QMenuBar,
    QAction,
    QPushButton,
    QWidget,
)

# Variables ------------------------------------------------------------------

# Code -----------------------------------------------------------------------

keys = {
    Qt.Key_Enter: (Ascii.LF, "Enter"),
    Qt.Key_Return: (Ascii.LF, "Return"),
    Qt.Key_Escape: (Ascii.ESC, "Escape"),
    Qt.Key_Delete: (Ansi.KEY_DELETE, "Delete"),
    Qt.Key_Left: (Ansi.BACK, "Left"),
    Qt.Key_Right: (Ansi.FORWARD, "Right"),
    Qt.Key_Up: (Ansi.UP, "Up"),
    Qt.Key_Down: (Ansi.DOWN, "Down"),
    Qt.Key_Insert: (Ansi.KEY_INSERT, "Insert"),
    Qt.Key_Backspace: ("\b", "Backspace"),
    Qt.Key_Home: (Ansi.KEY_HOME, "Home"),
    Qt.Key_End: (Ansi.KEY_END, "End"),
    Qt.Key_PageDown: (Ansi.KEY_PGDN, "Page down"),
    Qt.Key_PageUp: (Ansi.KEY_PGUP, "Page up"),
    Qt.Key_F1: (Ansi.KEY_F1, "F1"),
    Qt.Key_F2: (Ansi.KEY_F2, "F2"),
    Qt.Key_F3: (Ansi.KEY_F3, "F3"),
    Qt.Key_F4: (Ansi.KEY_F4, "F4"),
    Qt.Key_F5: (Ansi.KEY_F5, "F5"),
    Qt.Key_F6: (Ansi.KEY_F6, "F6"),
    Qt.Key_F7: (Ansi.KEY_F7, "F7"),
    Qt.Key_F8: (Ansi.KEY_F8, "F8"),
    Qt.Key_F9: (Ansi.KEY_F9, "F9"),
    Qt.Key_F10: (Ansi.KEY_F10, "F10"),
    Qt.Key_F11: (Ansi.KEY_F11, "F11"),
    Qt.Key_F12: (Ansi.KEY_F12, "F12"),
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
    """QTerminalWidget implements a limited ANSI terminal into a QPlainTextEdit widget."""

    def __init__(self, parent=None, init="") -> None:
        super().__init__(parent)

        self.cur = QTextCursor(self.document())
        self.terminal_state = TerminalState(rows=24, columns=80)
        # self.terminal_state = TerminalState(rows=50, columns=120)
        self.data_list = []
        self.setCursorWidth(2)
        self.ensureCursorVisible()
        self.setReadOnly(True)
        self.clear()

        #
        # https://stackoverflow.com/questions/10250533/set-line-spacing-in-qtextedit
        #
        # bf = self.cur.blockFormat()
        # bf.setLineHeight(10, QTextBlockFormat.LineHeightTypes.SingleHeight)
        # bf.setLineHeight(30, QTextBlockFormat.LineHeightTypes.FixedHeight)
        # bf.setLineHeight(50, QTextBlockFormat.LineHeightTypes.LineDistanceHeight)
        # self.cur.setBlockFormat(bf)

        # self.setFocusPolicy(Qt.NoFocus)
        # https://developer.mozilla.org/en-US/docs/Web/CSS/line-height

        self.setStyleSheet(  # Working, but row distance long
            """
        color : White;
        background-color: rgb(0, 0, 0);
        font-family:Monospace;
        font-size:12pt;
        line-height:1.0;
        """
        )

        self.max_lines = 100
        self.last_id = 0

    def setMaxLines(self, max_lines) -> None:
        self.max_lines = max_lines

    def clear(self) -> None:
        super().clear()
        self.terminal_state.reset()
        self.moveCursor(QTextCursor.End)

    def printpos(self, newPos: QTextCursor.MoveOperation) -> None:
        pos = self.cur.position()
        bpos = self.cur.positionInBlock()
        logging.debug(f"Cursor moved: abs:{pos}  block:{bpos}  newpos: {newPos}")

    def insert(self, html: str) -> None:
        self.cur.insertHtml(html)

    def move(self, direction: QTextCursor, anchor: QTextCursor, steps: int = 1) -> None:
        self.cur.movePosition(direction, anchor, n=steps)

    def remove_rows_alt(self, lines) -> None:
        logging.debug(f"Removing {lines} lines")
        cursor = self.textCursor()  # QTextCursor(self.document())

        for _ in range(lines):
            cursor.movePosition(QTextCursor.Start, QTextCursor.MoveAnchor)
            cursor.select(QTextCursor.LineUnderCursor)
            cursor.removeSelectedText()
            cursor.deleteChar()

        self.setTextCursor(cursor)

    def limit_lines(self) -> None:
        """Limit the number of lines in the terminal widget."""
        lines = self.document().lineCount()
        # logging.debug(f"Lines: {lines}  Maxlines: {self.max_lines}")
        if lines > self.max_lines:
            self.remove_rows_alt(lines - self.max_lines)

    def insert_html(self, html: str) -> None:
        self.cur.insertHtml(html)
        self.cur.movePosition(QTextCursor.Right, len(html))

    def append_html_text(self, html: str) -> None:
        self.move(QTextCursor.End, QTextCursor.MoveAnchor)
        self.insert(html)
        self.limit_lines()

    def append_ansi_text(self, data: str) -> None:
        """Append ANSI text to the terminal. Return EscapeObj if escape sequence detected."""

        if type(data) is str:
            lines = self.terminal_state.update(data)
            self.data_list.extend(lines)

        for i in range(len(self.data_list)):
            obj = self.data_list.pop(0)
            if type(obj) is TerminalLine:
                if obj.id > self.last_id:  # a new line detected
                    self.last_id = obj.id
                    self.move(QTextCursor.End, QTextCursor.MoveAnchor)
                    self.cur.insertHtml("<br>")

                if obj.id == self.last_id:  # last row
                    self.move(QTextCursor.End, QTextCursor.MoveAnchor)
                    self.move(QTextCursor.StartOfLine, QTextCursor.KeepAnchor)

                if obj.id < self.last_id:
                    self.move(QTextCursor.End, QTextCursor.MoveAnchor)
                    self.move(
                        QTextCursor.Up, QTextCursor.MoveAnchor, self.last_id - obj.id
                    )
                    self.move(QTextCursor.StartOfLine, QTextCursor.MoveAnchor)
                    self.move(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)

                self.cur.insertHtml(obj.line_to_html())
                # print(f"HTML id={obj.id}")

            if type(obj) is EscapeObj:
                return obj

        self.limit_lines()
        return None

    def scroll_down(self) -> None:
        """Scroll down to the last line."""
        vsb = self.verticalScrollBar()
        vsb.setValue(vsb.maximum())


space_test_string = f"""{Ansi.BOLD}1234{Ansi.RESET}5678\n"""


class MainForm(QMainWindow):
    # Handle windows close event
    def closeEvent(self, a0: QCloseEvent) -> None:
        return super().closeEvent(a0)

    def exitProgram(self, e) -> None:
        self.close()

    def add_button(self, label: str, text: str) -> None:
        pb = QPushButton(label, self.centralwidget)
        pb.pressed.connect(lambda: self.terminal.append_ansi_text(text))
        self.button_layout.addWidget(pb)

    def add_func_button(self, label: str, func: Callable) -> None:
        pb = QPushButton(label, self.centralwidget)
        pb.pressed.connect(func)
        self.button_layout.addWidget(pb)

    def __init__(self, args, parent=None) -> None:
        super(MainForm, self).__init__(parent)

        self.centralwidget = QWidget(self)
        self.setCentralWidget(self.centralwidget)
        self.resize(850, 500)

        # Layouts
        self.vertical_layout = QVBoxLayout(self.centralwidget)
        self.vertical_layout.setContentsMargins(2, 2, 2, 2)
        self.vertical_layout.setSpacing(2)

        self.main_layout = QHBoxLayout(self.centralwidget)
        self.button_layout = QVBoxLayout(self.centralwidget)
        self.button_layout.addSpacing(10)
        self.main_layout.addLayout(self.button_layout)
        self.right_layout = QVBoxLayout(self.centralwidget)
        self.main_layout.addLayout(self.right_layout)
        self.vertical_layout.addLayout(self.main_layout)

        self.terminal = QTerminalWidget(self.centralwidget)
        self.terminal.setMaxLines(500)
        self.right_layout.addWidget(self.terminal)

        self.add_func_button("Clear terminal", lambda: self.terminal.clear())
        self.add_button("Font Attributes", Ansi.test())
        self.add_button("Colors 256", Ansi.color_test())
        self.add_button("Cursor up", Ansi.UP)
        self.add_button("Cursor down", Ansi.DOWN)
        self.add_button("Cursor back", Ansi.BACK)
        self.add_button("Cursor forward", Ansi.FORWARD)
        self.add_button("Erase in line", "\x1b[K")
        self.add_button("Spacetest", space_test_string)
        self.add_button("Ö", "Ö")
        self.add_button("🐍", "🐍")
        self.add_button("&#8731;", "&#8731;")
        self.add_button("\xf0\x9f\x90\x8d", "\xf0\x9f\x90\x8d")
        self.add_button("&#F09F908D;", "&#F09F908D;")
        self.add_button("&#4036989069;", "&#4036989069;")

        self.button_layout.addStretch()

        # Menu bar
        self.menubar = QMenuBar(self)
        self.setMenuBar(self.menubar)

        # Menu
        self.menuFile = QMenu(self.menubar, title="&File")
        self.menubar.addAction(self.menuFile.menuAction())

        self.actionExit = QAction("Quit", self, triggered=self.exitProgram)
        self.actionExit.setToolTip("Quit")
        self.actionExit.setShortcutContext(Qt.WidgetShortcut)
        self.menuFile.addAction(self.actionExit)

        self.terminal.append_html_text(
            """<div style="font-size:20px;line-height:40px;color:green;">
                Line 1 <br>
                Line 2 <br>
              </div>"""
        )


def main() -> None:
    logging.basicConfig(
        format="[%(levelname)s] Line: %(lineno)d %(message)s", level=logging.DEBUG
    )
    app = QApplication(sys.argv)
    mainForm = MainForm(sys.argv)
    mainForm.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
