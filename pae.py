#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# --------------------------------------------------------------------------
#
# Python automation engine
#
# File:    pae.py
# Author:  Peter Malmberg <peter.malmberg@gmail.com>
# Date:
# Version: 0.3
# Python:  >=3
# License: MIT
#
# ---------------------------------------------------------------------------

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from math import sin
from escape import Escape
import time

from random import random


# class PaeFType(Enum):
#     MovingAverage = 0
#     IIR = 1
#     FIR = 2


@dataclass
class PaeFilter:
    len: int = 10

    def __post_init__(self):
        self.data = []

    def update(self, new_val: float) -> float:
        self.data.append(new_val)
        if len(self.data) > self.len:
            self.data.pop(0)

        return sum(self.data) / len(self.data)


class PaeType(Enum):
    Normal = 0
    Max = 1
    Min = 2
    Count = 3
    Average = 4
    Integrate = 5
    Derivate = 6
    Counter = 7
    Limit = 8
    RateLimit = 9
    Addition = 10
    Subtract = 11
    Multiply = 12
    Division = 13
    Multiply_Add = 14

    Absolute = 40
    Above = 41
    Below = 42

    Sine = 100
    Square = 101
    Random = 102

    Alarm_above = 200
    Alarm_below = 201
    Alarm_between = 203


@dataclass
class PaeObject:
    tick: int = 0
    enabled: bool = True
    #   id: str = ""
    name: str = ""
    desc: str = ""
    unit: str = ""
    # plot: bool = True
    src_id: str = ""

    def enable(self, en: bool) -> None:
        self.enabled = en

    def is_enabled(self) -> bool:
        return self.enabled

    # def get_id(self) -> str:
    #     return self.id
    # if self.source is not None:
    #     return self.source.get_id()

    # return self.id

    def set_id(self, id) -> None:
        self.id = id

    def get_name(self) -> str:
        return self.name

    def set_description(self, description) -> None:
        self.description = description

    def get_description(self) -> str:
        return self.description

    def set_source(self, source: PaeNode) -> None:
        self.source = source

    def get_source(self) -> PaeNode:
        return self.source

    def update(self) -> None:
        pass


class PaeNode(PaeObject):
    def __init__(
        self,
        id: str = "",
        desc: str = "",
        name: str = "",
        type: PaeType = PaeType.Normal,
        source: PaeNode = None,
        max_limit: float = 0.0,
        min_limit: float = 0.0,
        term: float = 0.0,
        factor: float = 1.0,
        offset: float = 0.0,
        plot: bool = True,
        param: bool = False,
        threshold: float = 0.0,
        period: float = 1.0,
        amplitude: float = 1.0,
        average: int = 1,
        divider: float = 1.0,
    ) -> None:
        super().__init__(name=name)
        self.id = id
        self.value = 0.0
        self.last = 0.0
        self.type = type
        self.source = source
        self.invalid = False
        self.no_data = False
        self.out_of_range = False
        self.max_limit = max_limit
        self.min_limit = min_limit
        self.term = term
        self.offset = offset
        self.factor = factor
        self.threshold = threshold
        self.period = period
        self.amplitude = amplitude
        self.average = average
        self.divider = divider

        if self.type == PaeType.Average:
            self.filter = PaeFilter(self.average)

    def get_id(self) -> str:
        return self.id

    def get_value(self) -> float:
        return self.value

    def get(self, d) -> float:
        if type(d) == float:
            return d

        if type(d) == PaeNode:
            return d.get_value()

    def update(self) -> None:
        super().update()

        if not self.is_enabled():
            return

        if self.source is not None:
            sv = self.source.get_value()
        else:
            sv = self.value

        if self.type == PaeType.Normal:
            self.value = sv

        if self.type == PaeType.Min:
            if sv < self.value:
                self.value = sv

        if self.type == PaeType.Max:
            if sv > self.value:
                self.value = sv

        if self.type == PaeType.Counter:
            if self.source.value > 0.5 and self.last < 0.5:
                self.value += 1

            self.last = self.source.value

        if self.type == PaeType.Average:
            self.value = self.filter.update(sv)

        if self.type == PaeType.Sine:
            sv = self.get(self.amplitude) * sin(self.tick / 20) + self.get(self.offset)
            self.value = sv
            self.tick += 1

        if self.type == PaeType.Square:
            if self.tick > 0:
                self.value = 1
            else:
                self.value = 0
            self.tick += 1
            if self.tick > self.get(self.period):
                self.tick = -self.get(self.period)
            # if self.tick > 5:
            #     self.tick = -5

        if self.type == PaeType.Random:
            self.value = self.offset + (self.factor * random())

        if self.type == PaeType.Limit:
            if sv > self.max_limit:
                self.value = self.max_limit
                return
            if sv < self.min_limit:
                self.value = self.min_limit
                return
            self.value = sv

        if self.type == PaeType.RateLimit:
            self.last = self.source.value

        if self.type == PaeType.Multiply:
            self.value = sv * self.get(self.factor)

        if self.type == PaeType.Division:
            self.value = sv / self.get(self.divider)

        if self.type == PaeType.Multiply_Add:
            self.value = sv * self.get(self.factor) + self.get(self.term)

        if self.type == PaeType.Subtract:
            self.value = sv - self.get(self.term)

        if self.type == PaeType.Addition:
            self.value = sv + self.get(self.term)

        if self.type == PaeType.Absolute:
            self.value = abs(sv)

        if self.type == PaeType.Above:
            if sv > self.threshold:
                self.value = 1
            else:
                self.value = 0

        if self.type == PaeType.Below:
            if sv < self.threshold:
                self.value = 1
            else:
                self.value = 0

    def __str__(self) -> str:
        return (
            f"{self.get_name():24} {self.id:10} {self.type.name:16} {self.value:10.3f}"
        )


class PaeMotor(PaeObject):
    def __init__(self) -> None:
        super().__init__()
        self.nodes = []
        self.first = False
        self.plots = []

    def add_node(self, node: PaeNode, plot: bool = True) -> PaeNode:
        self.nodes.append(node)
        if plot is True:
            self.plots.append(node)
        return node

    def find_node(self, id: str) -> PaeNode:
        for node in self.nodes:
            if node.id == id:
                return node
        return None

    def initiate(self):
        for node in self.nodes:
            if type(node.source) == str:
                node.source = self.find_node(node.source)

            if type(node.term) == str:
                node.term = self.find_node(node.term)

            if type(node.factor) == str:
                node.factor = self.find_node(node.factor)

            if type(node.divider) == str:
                node.divider = self.find_node(node.divider)

            if type(node.max_limit) == str:
                node.max_limit = self.find_node(node.max_limit)

            if type(node.min_limit) == str:
                node.min_limit = self.find_node(node.min_limit)

            if type(node.offset) == str:
                node.offset = self.find_node(node.offset)

            if type(node.threshold) == str:
                node.threshold = self.find_node(node.threshold)

            if type(node.period) == str:
                node.period = self.find_node(node.period)

            if type(node.amplitude) == str:
                node.amplitude = self.find_node(node.amplitude)

    def update(self) -> None:
        for node in self.nodes:
            node.update()

    def printout(self) -> None:
        print(self, end="")

    def __str__(self) -> str:
        out = ""
        if self.first is not True:
            for _ in self.nodes:
                out += "\n"
            self.first = True

        for _ in self.nodes:
            out += Escape.UP

        for x in self.nodes:
            out += f"{str(x)}\n"
        return out


def main() -> None:
    n_sin = PaeNode(type=PaeType.Sine, id="sin")
    n_square = PaeNode(type=PaeType.Square, id="square")
    n_min = PaeNode(type=PaeType.Min, source=n_sin)
    n_max = PaeNode(type=PaeType.Max, source=n_sin)
    n_count = PaeNode(type=PaeType.Counter, source=n_square)

    motor = PaeMotor()

    motor.add_node(n_sin)
    motor.add_node(n_square)
    motor.add_node(n_min)
    motor.add_node(n_max)
    motor.add_node(n_count)

    for i in range(1, 100):
        motor.update()
        motor.printout()
        # p = motor.__printout()

        time.sleep(0.1)


if __name__ == "__main__":
    main()
