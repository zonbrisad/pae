#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
#
# Temperature test with PAE
#
# File:     temptest
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
    NAME = "Temptest"
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
        self.terminal.setMinimumWidth(550)
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

        self.motor = PaeMotor()
        self.temp = self.motor.add_node(
            PaeNode(
                type=PaeType.Normal,
                name="Temp raw",
                id="temp_raw",
            )
        )
        self.motor.add_node(
            PaeNode(
                type=PaeType.Division,
                name="Temp",
                id="temp_d",
                source="temp_raw",
                divider=1000.0,
            )
        )
        self.motor.add_node(
            PaeNode(
                type=PaeType.Average,
                name="Temp filtered",
                id="temp",
                source="temp_d",
                average=10,
            )
        )
        self.motor.add_node(
            PaeNode(
                type=PaeType.Average,
                name="Temp minute average",
                id="temp_min",
                source="temp_d",
                average=60,
            )
        )
        self.motor.add_node(
            PaeNode(
                type=PaeType.Average,
                name="Temp hour average",
                id="temp_hour",
                source="temp_d",
                average=3600,
            )
        )

        self.motor.initiate()

        self.plots = []
        for plot_node in self.motor.plots:
            plot = PaePlot(node=plot_node)
            self.plotLayout.addWidget(plot)
            self.plots.append(plot)

        self.add_plot("temp_min", 60, 120, title="Minute (avg)")
        self.add_plot("temp_hour", 3600, 120, title="Hour (avg)")

        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.timerx)
        self.timer.start()

    def add_plot(
        self,
        node,
        intervall=1,
        dtp=1000,
        title="",
    ):
        if type(node) == str:
            nd = self.motor.find_node(node)
        plot = PaePlot(node=nd, title=title, datapoints=dtp, intervall=intervall)
        self.plotLayout.addWidget(plot)
        self.plots.append(plot)

    def read_val(self, file_name: str, row: int, col: int) -> float:
        if os.path.isfile(file_name):
            with open(file_name) as file:
                lines = file.readlines()
            line = lines[row - 1]
            d = line.split(" ")
            data = [x for x in d if x != ""]  # Remove empty strings
            # logging.debug(data)
            val = float(data[col - 1])
            # print(f"{file_name} {val} {row} {col}")
        return val

    def timerx(self) -> None:
        self.temp.value = self.read_val("/sys/class/hwmon/hwmon3/temp1_input", 1, 1)
        self.motor.update()
        for pl in self.plots:
            pl.update()

        d = str(self.motor)
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
