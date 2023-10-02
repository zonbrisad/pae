#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
#
# asdf asdf asdf
#
# File:     xx
# Author:   Peter Malmberg  <peter.malmberg@gmail.com>
# Org:      __ORGANISTATION__
# Date:     2023-09-21
# License:
# Python:   >= 3.0
#
# ----------------------------------------------------------------------------

from ast import Add
import traceback
import os
import sys
import logging
import argparse
from PyQt5.QtCore import Qt, QTimer, QSettings, QIODevice
from PyQt5.QtGui import QIcon, QCloseEvent
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QMenu,
    QMenuBar,
    QAction,
    QStatusBar,
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QTextEdit,
    QDialogButtonBox,
    QPushButton,
    QMessageBox,
    QWidget,
    QLabel,
    QFileDialog,
    QSpacerItem,
    QSizePolicy,
)

from qterminalwidget import QTerminalWidget
from pae import PaeNode, PaeMotor, PaeType
from simpleplot import SimplePlot
from paeplot import PaePlot


class App:
    NAME = "Paetest"
    VERSION = "0.01"
    DESCRIPTION = "Program for testing pae graphicly"
    LICENSE = ""
    AUTHOR = "Peter Malmberg"
    EMAIL = "<peter.malmberg@gmail.com>"
    ORG = "__ORGANISATION__"
    HOME = ""
    ICON = ""


# Qt main window settings
win_title = App.NAME
win_x_size = 800
win_y_size = 240


def cmd_cmd1():
    pass


about_html = f"""
<center><h2>{App.NAME}</h2></center>
<br>
<b>Version: </b>{App.VERSION}
<br>
<b>Author: </b>{App.AUTHOR}
<br>
<hr>
<br>
{App.DESCRIPTION}
<br>
"""


class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super(AboutDialog, self).__init__(parent)

        self.setWindowTitle(App.NAME)
        self.setWindowModality(Qt.ApplicationModal)
        self.resize(400, 300)

        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.setSpacing(2)
        self.setLayout(self.verticalLayout)

        # TextEdit
        self.textEdit = QTextEdit(self)
        self.textEdit.setReadOnly(True)
        self.verticalLayout.addWidget(self.textEdit)
        self.textEdit.insertHtml(about_html)

        # Buttonbox
        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Ok)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.setCenterButtons(True)
        self.verticalLayout.addWidget(self.buttonBox)

    @staticmethod
    def about(parent=None):
        dialog = AboutDialog(parent)
        result = dialog.exec_()
        return result == QDialog.Accepted


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.resize(win_x_size, win_y_size)
        self.setWindowTitle(win_title)
        # self.setWindowIcon(QIcon(App.ICON))

        # Create central widget
        self.centralwidget = QWidget(self)
        self.setCentralWidget(self.centralwidget)
        self.mainLayout = QHBoxLayout(self.centralwidget)
        self.mainLayout.setSpacing(2)
        self.mainLayout.setContentsMargins(2, 2, 2, 2)

        # # TextEdit
        # self.textEdit = QTextEdit(self.centralwidget)
        # self.plotLayout.addWidget(self.textEdit)

        self.terminal = QTerminalWidget()
        self.terminal.setMinimumWidth(450)
        self.mainLayout.addWidget(self.terminal)

        self.plotLayout = QVBoxLayout(self.centralwidget)
        self.plotLayout.setSpacing(2)
        self.mainLayout.addLayout(self.plotLayout)

        # Menubar
        self.menubar = QMenuBar(self)
        self.setMenuBar(self.menubar)

        # Menus
        self.menuFile = QMenu("File", self.menubar)
        self.menubar.addAction(self.menuFile.menuAction())

        self.menuHelp = QMenu("Help", self.menubar)
        self.menubar.addAction(self.menuHelp.menuAction())

        self.actionOpen = QAction("Open", self)
        self.actionOpen.setStatusTip("Open file")
        self.actionOpen.setShortcut("Ctrl+O")
        self.actionOpen.triggered.connect(self.open)
        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addSeparator()

        self.actionQuit = QAction("Quit", self)
        self.actionQuit.setStatusTip("Quit application")
        self.actionQuit.setShortcut("Ctrl+Q")
        self.actionQuit.triggered.connect(self.exit)
        self.menuFile.addAction(self.actionQuit)

        self.actionAbout = QAction("About", self)
        self.actionAbout.setStatusTip("About")
        self.actionAbout.triggered.connect(lambda: AboutDialog.about())
        self.menuHelp.addAction(self.actionAbout)

        # Statusbar
        self.statusbar = QStatusBar(self)
        self.statusbar.setLayoutDirection(Qt.LeftToRight)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)

        self.xmotor = PaeMotor()
        self.xmotor.add_node(PaeNode(type=PaeType.Sine, name="Sine", id="sin"))
        self.xmotor.add_node(
            PaeNode(type=PaeType.Square, name="Square", id="sqr", period=3.0)
        )
        self.xmotor.add_node(
            PaeNode(
                type=PaeType.Random,
                name="Random",
                id="rnd",
                offset=-0.125,
                factor=0.25,
            )
        )
        self.xmotor.add_node(
            PaeNode(type=PaeType.Min, name="Min", source="sin", plot=False)
        )
        self.xmotor.add_node(
            PaeNode(type=PaeType.Max, name="Max", source="sin", plot=False)
        )
        self.xmotor.add_node(
            PaeNode(type=PaeType.Counter, name="Counter", source="sqr", plot=False)
        )
        self.xmotor.add_node(
            PaeNode(
                type=PaeType.Limit,
                name="Limit",
                source="sin",
                min_limit=-0.5,
                max_limit=0.8,
            )
        )
        self.xmotor.add_node(
            PaeNode(type=PaeType.Absolute, name="Absolute", source="sin")
        )
        self.xmotor.add_node(
            PaeNode(
                type=PaeType.Addition,
                name="Sine + random",
                source="sin",
                term="rnd",
            )
        )
        self.xmotor.add_node(
            PaeNode(
                type=PaeType.Multiply,
                name="Sin chopped",
                source="sin",
                factor="sqr",
            )
        )
        self.xmotor.add_node(
            PaeNode(
                type=PaeType.Sine,
                id="sint",
                name="Sine offset",
                source="sin",
                amplitude=6.0,
                offset=8.0,
            )
        )
        self.xmotor.add_node(
            PaeNode(type=PaeType.Square, name="Square", id="sqr_v", period="sint")
        )
        self.xmotor.add_node(
            PaeNode(
                type=PaeType.Above,
                name="Sine above",
                source="sin",
                threshold=0.5,
            )
        )
        self.xmotor.add_node(
            PaeNode(
                type=PaeType.Below,
                name="Sine below",
                source="sin",
                threshold=0.0,
            )
        )
        self.xmotor.initiate()

        self.plots = []
        for nd in self.xmotor.nodes:
            if nd.plot is False:
                continue
            pl = PaePlot(node=nd)
            self.plotLayout.addWidget(pl)
            self.plots.append(pl)

        self.timer = QTimer()
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.timerx)
        self.timer.start()

    def timerx(self) -> None:
        self.xmotor.update()
        for pl in self.plots:
            pl.update()

        d = str(self.xmotor)
        self.terminal.append_terminal_text(d)

    def exit(self):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Information)
        msgBox.setWindowTitle("Quit")
        msgBox.setText("Are you sure you want to quit?")
        msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        if msgBox.exec() == QMessageBox.Ok:
            self.close()

    def open(self):
        files = QFileDialog.getOpenFileNames(self, "Open file", ".", "*.*")

    def closeEvent(self, event: QCloseEvent) -> None:
        self.exit()
        return super().closeEvent(event)


def main() -> None:
    logging_format = "[%(levelname)s] %(lineno)d %(funcName)s() : %(message)s"
    # logging.basicConfig(format=logging_format, level=logging.DEBUG)

    p_parser = argparse.ArgumentParser(add_help=False)
    p_parser.add_argument(
        "--debug", action="store_true", default=False, help="Print debug messages"
    )
    p_parser.add_argument(
        "--version",
        action="version",
        help="Print version information",
        version=f"{App.NAME} {App.VERSION}",
    )

    parser = argparse.ArgumentParser(
        prog=App.NAME, description=App.DESCRIPTION, epilog="", parents=[p_parser]
    )
    subparsers = parser.add_subparsers(title="Commands", help="", description="")

    cmd1 = subparsers.add_parser("cmd1", parents=[p_parser], help="Command 1")
    cmd1.set_defaults(func=cmd_cmd1)

    args = parser.parse_args()

    if hasattr(args, "func"):
        args.func()
        exit(0)

    parser.print_help()
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    try:
        main()
        sys.exit(0)
    except KeyboardInterrupt as e:  # Ctrl-C
        raise e
    except SystemExit as e:  # sys.exit()
        raise e
    except Exception as e:
        print("ERROR, UNEXPECTED EXCEPTION")
        print(str(e))
        traceback.print_exc()
        os._exit(1)
