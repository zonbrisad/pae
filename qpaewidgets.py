#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
#
# Plotwidget for Pae
#
# File:     paeplot
# Author:   Peter Malmberg  <peter.malmberg@gmail.com>
# Org:      __ORGANISTATION__
# Date:     2023-09-30
# License:
# Python:   >= 3.0
#
# ----------------------------------------------------------------------------

import logging
from PyQt5.QtCore import Qt
import pyqtgraph as pg
from pae import PaeNode, PaeType
from PyQt5.QtWidgets import (
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
    QPushButton,
    QTextEdit,
    QCheckBox,
    QSlider,
    QLineEdit,
)

pen = pg.mkPen(color="#ff00ff", width=1)


class QPaePlot(pg.PlotWidget):
    def __init__(self, node: PaeNode, datapoints=1000, intervall: int = 1, parent=None):
        # super().__init__(background="default")
        super().__init__(background="default", parent=parent)
        self.datapoints = datapoints
        self.node = node
        self.intervall = intervall
        self.tick = 0
        #self.setTitle(node.get_name())
        self.x = list(range(self.datapoints))
        self.y = [0 for _ in range(self.datapoints)]
        self.line = self.plot(self.x, self.y, pen=pen)

    def update(self):
        self.tick += 1
        if self.tick >= self.intervall:
            self.update_plot(self.node.value)
            self.tick = 0

    def update_plot(self, new_val):
        self.x = self.x[1:]
        self.x.append(self.x[-1] + 1)
        self.y = self.y[1:]
        self.y.append(new_val)
        self.line.setData(self.x, self.y)


class QPaeNode(QWidget):

    def add_label(self, text: str, width: int = 100) -> QLineEdit:
        label = QLineEdit(self)
        label.setText(text)
        label.setReadOnly(True)
        label.setFixedWidth(width)
        self.data_layout.addWidget(label)
        return label

    def __init__(self, node: PaeNode, parent=None):
        super().__init__(parent)
        self.node = node

        self.main_layout = QHBoxLayout(self)
        self.main_layout.setSpacing(1)
        self.setLayout(self.main_layout)

        self.node_layout = QVBoxLayout()
        self.main_layout.addLayout(self.node_layout)

        self.data_layout = QHBoxLayout()
        self.node_layout.addLayout(self.data_layout)

        self.name_label = self.add_label(f"{self.node.get_name()}:", 150)
        self.id_label = self.add_label(f"{self.node.id}", 120)
        self.type_label = self.add_label(f"{self.node.type.name}", 140)
        self.flags_label = self.add_label("", 60)
        self.value_label = self.add_label("", 100)

        self.control_layout = QHBoxLayout()
        self.node_layout.addLayout(self.control_layout)

        self.node_enabled = QCheckBox("")
        self.node_enabled.setChecked(self.node.enabled)
        self.node_enabled.stateChanged.connect(self.node_enable_changed)
        self.control_layout.addWidget(self.node_enabled)

        if self.node.type == PaeType.CountDownTimer:
            self.reset_button = QPushButton("Reset")
            self.reset_button.clicked.connect(lambda: self.node.trigger())
            self.control_layout.addWidget(self.reset_button)

        self.plot = QPaePlot(node=node)
        self.main_layout.addWidget(self.plot)
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

        self.plot.update()


def main() -> None:
    pass


if __name__ == "__main__":
    main()
