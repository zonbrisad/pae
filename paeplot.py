#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
#
# a simple plot widget for qt5
#
# File:     simpleplot
# Author:   Peter Malmberg  <peter.malmberg@gmail.com>
# Org:      __ORGANISTATION__
# Date:     2023-09-30
# License:
# Python:   >= 3.0
#
# ----------------------------------------------------------------------------

from dataclasses import dataclass
import pyqtgraph as pg
from pae import PaeNode

# pen = pg.mkPen(color=(255, 0, 100), width=1)
pen = pg.mkPen(color="#ff00ff", width=1)


@dataclass
class AvgFilter:
    len: int = 10

    def __post_init__(self):
        self.data = []

    def update(self, new_val: float) -> float:
        self.data.append(new_val)
        if len(self.data) > self.len:
            self.data.pop(0)

        return sum(self.data) / len(self.data)


class PaePlot(pg.PlotWidget):
    def __init__(self, node: PaeNode, parent=None, datapoints=1000, average=1):
        super().__init__(parent=parent, background="default", plotItem=None)
        self.datapoints = datapoints
        self.node = node
        self.filter = AvgFilter(average)

        self.setTitle(node.id)

        self.x = list(range(self.datapoints))
        self.y = [0 for _ in range(self.datapoints)]
        self.line = self.plot(self.x, self.y, pen=pen)

    def update(self):
        self.update_plot(self.node.value)

    def update_plot(self, new_val):
        val = self.filter.update(new_val)

        self.x = self.x[1:]
        self.x.append(self.x[-1] + 1)
        self.y = self.y[1:]
        self.y.append(val)
        self.line.setData(self.x, self.y)


def main() -> None:
    pass


if __name__ == "__main__":
    main()
