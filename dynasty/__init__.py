# -*- coding: utf-8 -*-
"""王朝（Dynasty）游戏包：按功能拆分的 PySide6 桌面模拟。"""
from dynasty.models import Person, roll_ability

__all__ = ["DynastyApp", "Person", "roll_ability"]


def __getattr__(name):
    if name == "DynastyApp":
        from dynasty.app import DynastyApp
        return DynastyApp
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
