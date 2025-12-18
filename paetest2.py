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

import traceback
import os
import sys
import argparse
import logging
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QCloseEvent
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QMenu,
    QMenuBar,
    QAction,
    QStatusBar,
    QVBoxLayout,
    QHBoxLayout,
    QFileDialog,
    QMessageBox,
    QWidget,
    QPushButton,
    QTextEdit,
    QCheckBox,
    QSlider,
    QLineEdit,
)

from pae import PaeNode, PaeMotor, PaeType
from paeplot import PaePlot
from aboutdialog import AboutDialog


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
win_x_size = 1800
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


class NodeWidget(QWidget):
    def __init__(self, node: PaeNode, parent=None):
        super().__init__(parent)
        self.node = node
        self.layout = QHBoxLayout(self)
        self.layout.setSpacing(2)
        self.setLayout(self.layout)

        self.node_enabled = QCheckBox("", self)
        self.node_enabled.setChecked(self.node.enabled)
        self.node_enabled.stateChanged.connect(self.node_enable_changed)
        self.layout.addWidget(self.node_enabled)

        self.label = QLineEdit(self)
        self.label.setText(f"{self.node.get_name()}:")
        self.label.setReadOnly(True)
        self.label.setFixedWidth(150)
        self.layout.addWidget(self.label)

        self.id_label = QLineEdit(self)
        self.id_label.setText(f"{self.node.id}")
        self.id_label.setReadOnly(True)
        self.id_label.setFixedWidth(120)
        self.layout.addWidget(self.id_label)

        self.type_label = QLineEdit(self)
        self.type_label.setText(f"{self.node.type.name}")
        self.type_label.setReadOnly(True)
        self.type_label.setFixedWidth(140)
        self.layout.addWidget(self.type_label)

        self.flags_label = QLineEdit(self)
        self.flags_label.setReadOnly(True)
        self.flags_label.setFixedWidth(60)
        self.layout.addWidget(self.flags_label)

        self.value_label = QLineEdit(self)
        self.value_label.setReadOnly(True)
        self.value_label.setFixedWidth(100)
        self.layout.addWidget(self.value_label)

        self.pl = PaePlot(node=node)
        self.layout.addWidget(self.pl)
        self.update()

    def node_enable_changed(self, state: int) -> None:
        logging.debug(f"Node {self.node.get_name()} enabled state changed: {state}")
        if state == Qt.Checked:
            self.node.enable(True)
        else:
            self.node.enable(False)

    def update(self) -> None:

        self.value_label.setText(f"{self.node.value:.3f}")
        if self.node.is_enabled() is True:
            enabled = "E"
        else:
            enabled = "D"

        if self.node.source_enabled() is False:
            n_src = "SD"
        else:
            n_src = "  "

        self.flags_label.setText(
            f"{enabled:1} {n_src:2}"
        )

        self.pl.update()


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

        self.leftLayout = QVBoxLayout(self.centralwidget)
        self.leftLayout.setSpacing(2)
        self.mainLayout.addLayout(self.leftLayout)

        self.buttonLayout = QHBoxLayout(self.centralwidget)
        self.buttonLayout.setSpacing(2)
        self.buttonLayout.setContentsMargins(2, 2, 2, 2)
        self.leftLayout.addLayout(self.buttonLayout)

        self.plotLayout = QVBoxLayout(self.centralwidget)
        self.plotLayout.setSpacing(2)
        self.mainLayout.addLayout(self.plotLayout)

        self.triggerButton = QPushButton("Trigger timer", self.centralwidget)
        self.triggerButton.clicked.connect(self.trigger_timer)
        self.buttonLayout.addWidget(self.triggerButton)

        self.checkbox = QCheckBox("Checkbox", self.centralwidget)
        self.checkbox.stateChanged.connect(self.state_changed)
        self.buttonLayout.addWidget(self.checkbox)

        self.slider = QSlider(Qt.Horizontal, self.centralwidget)
        self.slider.setMinimum(0)
        self.slider.setMaximum(100)
        self.slider.valueChanged.connect(self.set_aslider)
        self.buttonLayout.addWidget(self.slider)

        self.buttonLayout.addStretch()

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
        self.actionAbout.triggered.connect(lambda: AboutDialog.about(about=about_html, title=App.NAME, parent=self))
        self.menuHelp.addAction(self.actionAbout)

        # Statusbar
        self.statusbar = QStatusBar(self)
        self.statusbar.setLayoutDirection(Qt.LeftToRight)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)

        self.motor = PaeMotor()
        self.node_sine = self.motor.add_node(
            PaeNode(
                type=PaeType.Sine,
                name="Sine",
                id="sin")
            )
        self.motor.add_node(
            PaeNode(
                type=PaeType.Square,
                name="Square",
                id="sqr",
                period=3.0
            )
        )
        self.motor.add_node(
            PaeNode(
                type=PaeType.Random,
                name="Random",
                id="rnd",
                offset=-0.25,
                factor=0.5,
            )
        )
        self.motor.add_node(
            PaeNode(
                type=PaeType.Min,
                name="Min",
                source="sin"),
            plot=False
        )
        self.motor.add_node(
            PaeNode(
                type=PaeType.Max,
                name="Max",
                source="sin"),
            plot=False
        )
        self.motor.add_node(
            PaeNode(
                type=PaeType.Counter,
                name="Counter",
                source="sqr"),
            plot=False
        )
        self.motor.add_node(
            PaeNode(
                type=PaeType.Limit,
                name="Limit",
                source="sin",
                min_limit=-0.5,
                max_limit=0.8,
            )
        )
        self.motor.add_node(
            PaeNode(
                type=PaeType.Absolute,
                name="Absolute",
                source="sin"
            )
        )
        self.motor.add_node(
            PaeNode(
                type=PaeType.Addition,
                name="Sine + random",
                source="sin",
                term="rnd",
                id="sinrnd",
            )
        )
        self.motor.add_node(
            PaeNode(
                type=PaeType.Average,
                name="Average sin+rnd",
                source="sinrnd",
                average=10,
            )
        )

        self.motor.add_node(
            PaeNode(
                type=PaeType.Multiply,
                name="Sine * Square",
                source="sin",
                factor="sqr",
            )
        )
        self.motor.add_node(
            PaeNode(
                type=PaeType.Sine,
                id="sint",
                name="Sine offset",
                amplitude=6.0,
                offset=8.0,
            )
        )
        self.motor.add_node(
            PaeNode(
                type=PaeType.Square,
                name="Square",
                id="sqr_v",
                period="sint")
        )
        self.motor.add_node(
            PaeNode(
                type=PaeType.Above,
                name="Sine above",
                source="sin",
                threshold=0.5,
            )
        )
        self.motor.add_node(
            PaeNode(
                type=PaeType.Below,
                name="Sine below",
                source="sin",
                threshold=0.0,
            )
        )
        self.cd_timer = self.motor.add_node(
            PaeNode(
                type=PaeType.CountDownTimer,
                name="Count down timer",
                source="",
                trigger=False
            )
        )
        self.on_off = self.motor.add_node(
            PaeNode(
                type=PaeType.Normal,
                name="On/Off",
                id="onoff")
        )
        self.aslider = self.motor.add_node(
            PaeNode(
                type=PaeType.Normal,
                name="Analog Slider",
                id="aslider")
        )
        self.motor.initiate()

        self.node_widgets = []
        for nd in self.motor.plots:
            nw = NodeWidget(node=nd)
            self.leftLayout.addWidget(nw)
            self.node_widgets.append(nw)

        self.timer = QTimer()
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.timerx)
        self.timer.start()

    def timerx(self) -> None:
        self.motor.update()
        for nw in self.node_widgets:
            nw.update()

    def trigger_timer(self) -> None:
        self.cd_timer.trigger = True

    def state_changed(self, state: int) -> None:
        logging.debug(f"Checkbox state changed: {state}")
        if state == Qt.Checked:
            self.on_off.set_value(1)
        else:
            self.on_off.set_value(0)

    def set_aslider(self, value: float) -> None:
        self.aslider.set_value(value)

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
