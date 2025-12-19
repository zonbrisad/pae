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

import pyqtgraph as pg
from pae import PaeNode

pen = pg.mkPen(color="#ff00ff", width=1)


class PaePlot(pg.PlotWidget):
    def __init__(self, node: PaeNode, title="", datapoints=1000, intervall: int = 1):
        super().__init__(background="default")
        self.datapoints = datapoints
        self.node = node
        self.intervall = intervall
        self.tick = 0

        if title != "":
            self.setTitle(title)
        else:
            self.setTitle(node.get_name())
            
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


def main() -> None:
    pass


if __name__ == "__main__":
    main()
