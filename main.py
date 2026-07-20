# -*- coding: utf-8 -*-
"""王朝 V1.10 入口：启动 PySide6 主窗口。

详细模块说明见 docs/modules/。
"""
import sys

from PySide6.QtWidgets import QApplication

from dynasty import DynastyApp, Person, roll_ability  # noqa: F401 — 兼容旧导入

__all__ = ["DynastyApp", "Person", "roll_ability", "main"]


def main():
    app = QApplication(sys.argv)
    window = DynastyApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
