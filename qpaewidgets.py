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
from pae import PaeNode
from PyQt5.QtWidgets import (
    QHBoxLayout,
    QWidget,
    QPushButton,
    QTextEdit,
    QCheckBox,
    QSlider,
    QLineEdit,
)

pen = pg.mkPen(color="#ff00ff", width=1)


class QPaePlot(pg.PlotWidget):
    def __init__(self, node: PaeNode, datapoints=1000, intervall: int = 1):
        super().__init__(background="default")
        self.datapoints = datapoints
        self.node = node
        self.intervall = intervall
        self.tick = 0

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

        self.pl = QPaePlot(node=node)
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


def main() -> None:
    pass


if __name__ == "__main__":
    main()
