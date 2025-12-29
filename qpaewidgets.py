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
import sys
import time
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QCloseEvent
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QDialog,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
    QLabel,
    QPushButton,
    QCheckBox,
    QLineEdit,
)
import pyqtgraph as pg
from pae import PaeNode, PaeType, PaeMotor

pen = pg.mkPen(color="#ff00ff", width=0.6)
pen_default = pg.mkPen(color="#00ff00", width=0.6)

pg_color_red = "#ff0000"
pg_color_green = "#00ff00"
pg_color_blue = "#0000ff"
pg_color_white = "#ffffff"
pg_color_yellow = "#ffff00"
pg_color_cyan = "#00ffff"
pg_color_magenta = "#ff00ff"

class QPaePlot(pg.PlotWidget):
    def __init__(self, node: PaeNode, datapoints=1000, intervall: int = 1, parent=None):
        super().__init__(background="default",
                         parent=parent,
                         axisItems={"bottom": pg.DateAxisItem()})
        self.datapoints = datapoints
        self.node = node
        self.intervall = intervall
        self.tick = 0
        # self.setTitle(node.get_name())
        self.x = [time.time() - (self.datapoints - i)*self.intervall for i in range(self.datapoints)]
        self.y = [0 for _ in range(self.datapoints)]

        self.line = self.plot(self.x, self.y, pen=pen)

    def update(self):
        self.tick += 1
        if self.tick >= self.intervall:
            self.update_plot(self.node.value)
            self.tick = 0

    def update_plot(self, new_val):
        self.x.pop(0)
        self.x.append(time.time())
        self.y.pop(0)
        self.y.append(new_val)
        self.line.setData(self.x, self.y)


class QPaePlots(pg.PlotWidget):
    def __init__(self, nodes: PaeNode, datapoints=1000, intervall: int = 1, parent=None):
        super().__init__(background="default",
                         parent=parent,
                         axisItems={"bottom": pg.DateAxisItem()})
        self.datapoints = datapoints
        self.nodes = []
        self.intervall = intervall
        self.tick = 0
        # self.setTitle(node.get_name())
        self.x = [time.time() - (self.datapoints - i)*self.intervall for i in range(self.datapoints)]

    def add_node(self, node: PaeNode, color="#00ff00") -> None:   
        y = [0 for _ in range(self.datapoints)]
        pen = pg.mkPen(color=color, width=0.6)
        line = self.plot(self.x, y, pen=pen)

        self.nodes.append((node, y, line))

    def update(self):
        self.tick += 1
        self.x.pop(0)
        self.x.append(time.time())
        if self.tick >= self.intervall:
            for (node, y, line) in self.nodes:
                y.pop(0)
                y.append(node.value)
                line.setData(self.x, y)

            self.tick = 0


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
        self.main_layout.setContentsMargins(1, 1, 1, 1)
        self.setLayout(self.main_layout)

        self.node_layout = QVBoxLayout()
        self.main_layout.addLayout(self.node_layout)

        self.data_layout = QHBoxLayout()
        self.node_layout.addLayout(self.data_layout)

        self.name_label = self.add_label(f"{self.node.get_name()}", 150)
        self.id_label = self.add_label(f"{self.node.id}", 120)
        self.type_label = self.add_label(f"{self.node.type.name}", 140)
        self.flags_label = self.add_label("", 60)
        self.value_label = self.add_label("", 100)
        self.data_layout.addStretch()
        #self.data_layout.setStretchFactor(self.data_layout.itemAt(5), 1)

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

        self.control_layout.addStretch()

        self.plot = QPaePlot(node=node, datapoints=500, intervall=0.1)
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


class QPaeMonitorNode(QWidget):

    def add_label(self, text: str, width: int = 100) -> QLineEdit:
        label = QLineEdit(self, text=text)
        label.setReadOnly(True)
        # label.setFixedWidth(width)
        label.setMinimumWidth(width)
        self.main_layout.addWidget(label)
        return label

    def add_qlabel(self, text: str, width: int = 100) -> QLabel:
        label = QLabel(f"<b>{text}</b>", self)
        label.setMinimumWidth(width)
        self.main_layout.addWidget(label)
        return label

    def __init__(self, node: PaeNode, parent=None, header: bool = False):
        super().__init__(parent)

        self.node = node
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setSpacing(1)
        self.main_layout.setContentsMargins(1, 1, 1, 1)
        self.setLayout(self.main_layout)

        if header is True:
            self.name_label = self.add_qlabel("Name", 150)
            self.id_label = self.add_qlabel("ID", 120)
            self.type_label = self.add_qlabel("Type", 140)
            self.source_id = self.add_qlabel("Source ID", 120)
            self.flags_label = self.add_qlabel("Flags", 60)
            self.value_label = self.add_qlabel("Value", 100)
            return

        self.name_label = self.add_label(f"{self.node.get_name()}", 150)
        self.id_label = self.add_label(f"{self.node.id}", 120)
        self.type_label = self.add_label(f"{self.node.type.name}", 140)
        if self.node.source is not None:
            self.source_id = self.add_label(f"{self.node.source.id}", 120)
        else:
            self.source_id = self.add_label("", 120)
        
        self.flags_label = self.add_label("", 60)
        self.value_label = self.add_label("", 100)

        self.update()

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


class QPaeMonitor(QDialog):
    def __init__(self, motor: PaeMotor, parent=None):
        super().__init__(parent)
        self.motor = motor
        self.setWindowTitle("Pae Node Monitor")
        self.setModal(False)
        self.setWindowModality(Qt.WindowModal)
        #self.setWindowModality(Qt.ApplicationModal)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(1, 1, 1, 1)
        self.main_layout.setSpacing(1)
        self.setLayout(self.main_layout)

        self.main_layout.addWidget(QPaeMonitorNode(node=None, header=True))

        self.node_widgets = []
        for nd in self.motor.nodes:
            nw = QPaeMonitorNode(node=nd)
            self.main_layout.addWidget(nw)
            self.node_widgets.append(nw)

    def update(self) -> None:
        for nw in self.node_widgets:
            nw.update()

    @staticmethod
    def monitor(motor: PaeMotor) -> None:
        monitor = QPaeMonitor(motor)
        monitor.show()
        return monitor


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.resize(1200, 200)
        self.setWindowTitle("QPaeWidgetTest")

        # Create central widget
        self.centralwidget = QWidget(self)
        self.setCentralWidget(self.centralwidget)

        self.main_layout = QVBoxLayout(self.centralwidget)
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self.motor = PaeMotor()
        sin_node = self.motor.add_node(
            PaeNode(
                type=PaeType.Sine,
                name="Sine",
                id="sin")
            )
        sqr_node = self.motor.add_node(
            PaeNode(
                type=PaeType.Square,
                name="Square",
                id="sqr",
                period=12.0
            )
        )
        sin_sqr_node = self.motor.add_node(
            PaeNode(
                type=PaeType.Multiply,
                name="Sine*Square",
                id="sin_sqr",
                source=sin_node,
                factor="sqr"
            )
        )
            
        self.motor.initiate()

        self.node_widgets = []
        for nd in self.motor.nodes:
            nw = QPaePlot(node=nd, datapoints=500, intervall=0.1)
            self.main_layout.addWidget(nw)
            self.node_widgets.append(nw)

        self.multi_plot = QPaePlots(nodes=self.motor.nodes, datapoints=500, intervall=0.1)
        self.multi_plot.add_node(sin_node, pg_color_cyan)
        self.multi_plot.add_node(sqr_node, pg_color_red)
        self.main_layout.addWidget(self.multi_plot)

        self.monitor = None

        self.timer = QTimer()
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.timerx)
        self.timer.start()

    def timerx(self) -> None:
        if self.monitor is None:
            # self.monitor = QPaeMonitor(self.motor, self)
            # self.monitor.show()
            self.monitor = QPaeMonitor.monitor(self.motor)
        
        self.motor.update()
        for nw in self.node_widgets:
            nw.update()

        self.multi_plot.update()

        if self.monitor is not None:
            self.monitor.update()

    def exit(self):
        return super().close()  # Placeholder for any cleanup actions

    def closeEvent(self, event: QCloseEvent) -> None:
        self.monitor.close()
        self.exit()
        return super().closeEvent(event)


def main() -> None:
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
