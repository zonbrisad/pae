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

    Sine = 100
    Square = 101
    Noise = 200


@dataclass
class PaeObject:
    tick: int = 0
    enabled: bool = True
    id: str = ""
    name: str = ""
    desc: str = ""
    unit: str = ""

    def enable(self, en: bool) -> None:
        self.enabled = en

    def is_enabled(self) -> bool:
        return self.enabled

    def get_id(self) -> str:
        if self.source is not None:
            return self.source.get_id()

        return self.id

    def set_id(self, id) -> None:
        self.id = id

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
        id: str = None,
        desc: str = "",
        type: PaeType = PaeType.Normal,
        source: PaeNode = None,
    ) -> None:
        super().__init__(id=id)
        self.value = 0.0
        self.last = 0.0
        self.type = type
        self.source = source
        self.invalid = False
        self.no_data = False
        self.out_of_range = False

    def get_id(self) -> str:
        if self.source is not None:
            return self.source.get_id()

        return self.id

    def get_value(self) -> float:
        return self.value

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
            pass

        if self.type == PaeType.Sine:
            sv = sin(self.tick / 20)
            self.value = sv
            self.tick += 1

        if self.type == PaeType.Square:
            if self.tick > 0:
                self.value = 1
            else:
                self.value = 0
            self.tick += 1
            if self.tick > 5:
                self.tick = -5

    def __str__(self) -> str:
        return f"{self.get_id():8} {self.type.name:10} {self.value:8.3f}"


class PaeAlarm(PaeObject):
    def __init__(self) -> None:
        super().__init__()


class PaeMotor(PaeObject):
    def __init__(self) -> None:
        super().__init__()
        self.nodes = []
        self.alarms = []
        self.first = False

    def add_node(self, node: PaeNode) -> None:
        self.nodes.append(node)

    def add_alarm(self, alarm: PaeAlarm) -> None:
        self.alarms.append(alarm)

    def update(self) -> None:
        for node in self.nodes:
            node.update()

        for alarm in self.alarms:
            alarm.update()
        pass

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


class PaeFType:
    MovingAverage = 0
    IIR = 1
    FIR = 2


class PaeFilter(PaeObject):
    def __init__(self) -> None:
        super().__init__()


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
