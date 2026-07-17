# -*- coding: utf-8 -*-
"""古风主题 QSS 样式（宣纸底、朱漆金边）。"""
from PySide6.QtWidgets import QApplication


class StylesMixin:
    """古风主题 QSS 样式（宣纸底、朱漆金边）。"""

    def apply_stylesheet(self):
        app = QApplication.instance()
        qss = """
        /* ===== 全局：宣纸明堂 · 朱漆金边 ===== */
        QWidget {
            background-color: #f5efe3;
            color: #2c1810;
            font-family: "KaiTi", "STKaiti", "楷体", "FangSong", "仿宋", "SimSun", "宋体", serif;
            font-size: 14px;
        }
        QMainWindow, QDialog {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #faf6ec, stop:0.5 #f5efe3, stop:1 #ebe0cc);
        }

        /* 标题 / 匾额 */
        QLabel#title_label {
            font-size: 42px;
            font-weight: bold;
            color: #8b5a12;
            letter-spacing: 14px;
            padding: 14px 0 6px 14px;
            qproperty-alignment: AlignCenter;
        }
        QLabel#subtitle_label {
            color: #6b4e2e;
            font-size: 15px;
            letter-spacing: 4px;
            padding-bottom: 10px;
            qproperty-alignment: AlignCenter;
        }
        QLabel#reign_banner {
            font-size: 26px;
            font-weight: bold;
            color: #fff8e7;
            letter-spacing: 6px;
            padding: 10px 0;
            border: 2px solid #c9a24b;
            border-radius: 6px;
            background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                stop:0 #b83a32, stop:1 #8f2420);
            qproperty-alignment: AlignCenter;
        }
        QLabel#section_label {
            color: #7a4e12;
            font-size: 16px;
            font-weight: bold;
            padding: 6px 0 2px 0;
            border-bottom: 1px solid #c4a574;
            margin-bottom: 6px;
            letter-spacing: 3px;
        }

        /* 输入框 */
        QLineEdit {
            background-color: #fffdf8;
            border: 1px solid #c4a574;
            border-radius: 4px;
            padding: 6px 8px;
            color: #2c1810;
            selection-background-color: #d45a4a;
            selection-color: #fff8e7;
        }
        QLineEdit:focus {
            border: 1px solid #a67c3d;
            background-color: #ffffff;
        }

        /* 按钮 —— 朱漆玉印 */
        QPushButton {
            background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                stop:0 #c4453c, stop:1 #9a2e28);
            border: 1px solid #b5893f;
            border-radius: 5px;
            color: #fff8e7;
            padding: 7px 16px;
            font-size: 15px;
            letter-spacing: 2px;
        }
        QPushButton:hover {
            background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                stop:0 #d9554a, stop:1 #b83a32);
            border: 1px solid #d4af37;
            color: #ffffff;
        }
        QPushButton:pressed {
            background: #8f2420;
        }

        /* 标签页 */
        QTabWidget::pane {
            border: 1px solid #c4a574;
            border-radius: 4px;
            background: #faf6ec;
            top: -1px;
        }
        QTabBar::tab {
            background: #ebe0cc;
            color: #5c4030;
            padding: 8px 18px;
            border: 1px solid #c4a574;
            border-bottom: none;
            border-top-left-radius: 5px;
            border-top-right-radius: 5px;
            letter-spacing: 2px;
        }
        QTabBar::tab:selected {
            background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                stop:0 #c4453c, stop:1 #9a2e28);
            color: #fff8e7;
            border: 1px solid #b5893f;
            border-bottom: 1px solid #9a2e28;
        }
        QTabBar::tab:hover:!selected {
            background: #f0e6d2;
            color: #8b5a12;
        }

        /* 表格 / 树 */
        QTableWidget, QTreeWidget {
            background-color: #fffdf8;
            gridline-color: #d4c4a8;
            border: 1px solid #c4a574;
            border-radius: 4px;
            color: #2c1810;
            selection-background-color: #c4453c;
            selection-color: #fff8e7;
        }
        QHeaderView::section {
            background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                stop:0 #c4453c, stop:1 #9a2e28);
            color: #fff8e7;
            padding: 6px;
            border: 1px solid #a67c3d;
            font-weight: bold;
            letter-spacing: 1px;
        }
        QTableWidget::item, QTreeWidget::item {
            padding: 4px;
        }
        QTableWidget::item:alternate, QTreeWidget::item:alternate {
            background-color: #f3ead8;
        }

        /* 滑块 */
        QSlider::groove:horizontal {
            border: 1px solid #c4a574;
            height: 6px;
            border-radius: 3px;
            background: #ebe0cc;
        }
        QSlider::sub-page:horizontal {
            background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                stop:0 #c4453c, stop:1 #c9a24b);
            border-radius: 3px;
        }
        QSlider::handle:horizontal {
            background: qradialgradient(cx:0.5,cy:0.5,radius:0.5,
                stop:0 #fff8e7, stop:1 #c9a24b);
            border: 1px solid #a67c3d;
            width: 16px;
            height: 16px;
            border-radius: 8px;
            margin: -6px 0;
        }

        /* 滚动条 */
        QScrollBar:vertical {
            background: #ebe0cc;
            width: 12px;
            border-radius: 6px;
        }
        QScrollBar::handle:vertical {
            background: #c4a574;
            border-radius: 6px;
            min-height: 20px;
        }
        QScrollBar::handle:vertical:hover { background: #b5893f; }
        QScrollBar:horizontal {
            background: #ebe0cc;
            height: 12px;
            border-radius: 6px;
        }
        QScrollBar::handle:horizontal {
            background: #c4a574;
            border-radius: 6px;
            min-width: 20px;
        }

        /* 表单标签 */
        QLabel {
            color: #3d2914;
        }

        /* ===== 宗藩页：紧凑列表 + 世系主区 ===== */
        QLabel#fief_title {
            color: #7a4e12;
            font-size: 15px;
            font-weight: bold;
            letter-spacing: 4px;
            padding: 0;
            border: none;
            margin: 0;
        }
        QLabel#fief_count_label {
            color: #6b4e2e;
            font-size: 12px;
            letter-spacing: 1px;
            padding: 0 2px;
        }
        QLabel#fief_panel_caption {
            color: #8b5a12;
            font-size: 12px;
            letter-spacing: 2px;
            padding: 2px 4px;
            border: none;
            margin: 0;
        }
        QLabel#fief_detail_banner {
            color: #fff8e7;
            font-size: 13px;
            letter-spacing: 1px;
            padding: 6px 10px;
            border: 1px solid #c9a24b;
            border-radius: 4px;
            background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                stop:0 #b83a32, stop:1 #8f2420);
        }
        QLabel#fief_lineage_hint {
            color: #6b4e2e;
            font-size: 11px;
            letter-spacing: 1px;
            padding: 0 2px 2px 2px;
            qproperty-alignment: AlignLeft;
        }
        QWidget#fief_list_panel {
            background: transparent;
        }
        QWidget#fief_lineage_panel {
            background: transparent;
        }
        QTableWidget#fief_table {
            font-size: 12px;
            background-color: #fffdf8;
            border: 1px solid #c4a574;
            border-radius: 4px;
            gridline-color: transparent;
        }
        QTableWidget#fief_table::item {
            padding: 2px 4px;
        }
        QTableWidget#fief_table QHeaderView::section {
            font-size: 12px;
            padding: 4px 4px;
            letter-spacing: 0px;
        }
        QTreeWidget#fief_lineage_tree {
            font-size: 13px;
            border: 1px solid #c4a574;
            border-radius: 4px;
        }
        QSplitter#fief_splitter::handle {
            background: #d4c4a8;
            width: 4px;
            margin: 2px 0;
            border-radius: 2px;
        }
        QSplitter#fief_splitter::handle:hover {
            background: #b5893f;
        }
        """
        app.setStyleSheet(qss)

