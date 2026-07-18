# -*- coding: utf-8 -*-
"""王朝国运折线图：逐年国运走势，标注在位皇帝分段与年号更迭。"""
from __future__ import annotations

from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import QPainter, QPen, QColor, QFont, QBrush, QPolygonF
from PySide6.QtWidgets import (
    QWidget, QDialog, QVBoxLayout, QLabel, QScrollArea, QSizePolicy,
)

# 布局参数
PAD_LEFT = 46      # 左侧 Y 轴刻度区
PAD_RIGHT = 20
PAD_TOP = 64       # 顶部皇帝名条
PAD_BOTTOM = 56    # 底部年号条 + X 轴刻度
PX_PER_YEAR = 10   # 每年横向像素
MIN_PLOT_W = 560

# 古风配色（与 styles.py 主题呼应）
COL_BG = QColor("#faf6ec")
COL_PLOT_BG = QColor("#fffdf8")
COL_GRID = QColor("#e3d5b8")
COL_AXIS = QColor("#a67c3d")
COL_LINE = QColor("#b83a32")
COL_FILL = QColor(184, 58, 50, 26)
COL_TEXT = QColor("#5c4030")
COL_EMP_TEXT = QColor("#7a4e12")
COL_SEG_A = QColor(196, 165, 116, 26)   # 皇帝分段交替底色
COL_SEG_B = QColor(196, 165, 116, 0)
COL_SEG_LINE = QColor(166, 124, 61, 130)
COL_NIANHAO = QColor("#8b5a12")
COL_NIANHAO_TICK = QColor(139, 90, 18, 110)

FONT_FAMILY = "KaiTi"


class FortuneChartWidget(QWidget):
    """按 dynasty_hp_history 绘制的国运折线图，顶部标皇帝、底部标年号。"""

    def __init__(self, history, parent=None):
        super().__init__(parent)
        self._history = list(history or [])
        self._emperor_segments = self._build_segments("emperor_id", "emperor")
        self._nianhao_segments = self._build_segments("nianhao", "nianhao")
        n = max(len(self._history), 1)
        plot_w = max(MIN_PLOT_W, n * PX_PER_YEAR)
        self.setFixedSize(PAD_LEFT + plot_w + PAD_RIGHT, 420)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setMouseTracking(True)
        self._hover_idx = None

    def _build_segments(self, key, label_key):
        """把逐年记录按 key 连续段聚合 → [(start_idx, end_idx, label)]。"""
        segs = []  # [start, end, value, label]
        for i, rec in enumerate(self._history):
            val = rec.get(key)
            if segs and segs[-1][2] == val:
                segs[-1][1] = i
            else:
                segs.append([i, i, val, rec.get(label_key, "")])
        return [(s, e, lbl) for s, e, _v, lbl in segs]

    # ---- 坐标换算 ----

    def _plot_rect(self):
        return QRectF(PAD_LEFT, PAD_TOP,
                      self.width() - PAD_LEFT - PAD_RIGHT,
                      self.height() - PAD_TOP - PAD_BOTTOM)

    def _x(self, idx, rect):
        n = len(self._history)
        if n <= 1:
            return rect.left() + rect.width() / 2
        return rect.left() + rect.width() * idx / (n - 1)

    def _y(self, hp, rect):
        return rect.bottom() - rect.height() * max(0.0, min(100.0, hp)) / 100.0

    # ---- 绘制 ----

    def paintEvent(self, _event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.fillRect(self.rect(), COL_BG)

        rect = self._plot_rect()
        p.fillRect(rect, COL_PLOT_BG)

        if not self._history:
            p.setPen(COL_TEXT)
            p.setFont(QFont(FONT_FAMILY, 14))
            p.drawText(self.rect(), Qt.AlignCenter, "尚无国运记录")
            return

        self._draw_emperor_bands(p, rect)
        self._draw_grid(p, rect)
        self._draw_line(p, rect)
        self._draw_nianhao(p, rect)
        self._draw_axes(p, rect)
        self._draw_hover(p, rect)
        p.end()

    def _draw_grid(self, p, rect):
        p.setPen(QPen(COL_GRID, 1, Qt.DashLine))
        p.setFont(QFont(FONT_FAMILY, 9))
        for hp in (0, 20, 40, 60, 80, 100):
            y = self._y(hp, rect)
            p.drawLine(QPointF(rect.left(), y), QPointF(rect.right(), y))
            p.setPen(COL_TEXT)
            p.drawText(QRectF(0, y - 8, PAD_LEFT - 6, 16),
                       Qt.AlignRight | Qt.AlignVCenter, str(hp))
            p.setPen(QPen(COL_GRID, 1, Qt.DashLine))

    def _draw_emperor_bands(self, p, rect):
        """皇帝在位分段：交替底色 + 分界线 + 顶部名条。"""
        p.setFont(QFont(FONT_FAMILY, 10, QFont.Bold))
        for i, (s, e, name) in enumerate(self._emperor_segments):
            x0 = self._x(s, rect) if s > 0 else rect.left()
            x1 = self._x(e, rect) if e < len(self._history) - 1 else rect.right()
            band = QRectF(x0, rect.top(), x1 - x0, rect.height())
            p.fillRect(band, COL_SEG_A if i % 2 == 0 else COL_SEG_B)
            if s > 0:
                p.setPen(QPen(COL_SEG_LINE, 1, Qt.DashDotLine))
                p.drawLine(QPointF(x0, rect.top() - 6), QPointF(x0, rect.bottom()))
            # 顶部皇帝名（段太窄则省略）
            label_rect = QRectF(x0, 6, max(x1 - x0, 1), PAD_TOP - 12)
            p.setPen(COL_EMP_TEXT)
            fm = p.fontMetrics()
            if fm.horizontalAdvance(name) <= label_rect.width():
                p.drawText(label_rect, Qt.AlignHCenter | Qt.AlignTop, name)
            elif label_rect.width() >= fm.horizontalAdvance("帝"):
                p.drawText(label_rect, Qt.AlignHCenter | Qt.AlignTop, "…")

    def _draw_nianhao(self, p, rect):
        """底部年号条：每个年号段起点小三角 + 名称（窄段省略名称）。"""
        p.setFont(QFont(FONT_FAMILY, 9))
        base_y = rect.bottom() + 18
        for s, e, name in self._nianhao_segments:
            x0 = self._x(s, rect)
            x1 = self._x(e, rect) if e < len(self._history) - 1 else rect.right()
            # 起点小三角标记
            p.setPen(Qt.NoPen)
            p.setBrush(QBrush(COL_NIANHAO_TICK))
            tri = QPolygonF([QPointF(x0, rect.bottom() + 3),
                             QPointF(x0 - 4, rect.bottom() + 10),
                             QPointF(x0 + 4, rect.bottom() + 10)])
            p.drawPolygon(tri)
            p.setPen(COL_NIANHAO)
            fm = p.fontMetrics()
            w = max(x1 - x0, 1)
            if fm.horizontalAdvance(name) <= w + 8:
                p.drawText(QRectF(x0 - 4, base_y - 6, w + 8, 16),
                           Qt.AlignLeft | Qt.AlignVCenter, name)

    def _draw_line(self, p, rect):
        pts = [QPointF(self._x(i, rect), self._y(rec["hp"], rect))
               for i, rec in enumerate(self._history)]
        if len(pts) >= 2:
            # 填充
            poly = QPolygonF(pts)
            poly.append(QPointF(pts[-1].x(), rect.bottom()))
            poly.append(QPointF(pts[0].x(), rect.bottom()))
            p.setPen(Qt.NoPen)
            p.setBrush(QBrush(COL_FILL))
            p.drawPolygon(poly)
            # 折线
            p.setPen(QPen(COL_LINE, 2))
            p.setBrush(Qt.NoBrush)
            p.drawPolyline(QPolygonF(pts))
        # 单点或点稀疏时描点
        if len(pts) <= 60:
            p.setPen(Qt.NoPen)
            p.setBrush(QBrush(COL_LINE))
            for pt in pts:
                p.drawEllipse(pt, 2.4, 2.4)

    def _draw_axes(self, p, rect):
        p.setPen(QPen(COL_AXIS, 1.4))
        p.drawLine(rect.bottomLeft(), rect.bottomRight())
        p.drawLine(rect.topLeft(), rect.bottomLeft())
        # X 轴国祚年刻度（约每 10 年）
        p.setFont(QFont(FONT_FAMILY, 8))
        n = len(self._history)
        step = max(1, round(n / (rect.width() / 56)))
        step = max(step, 5) if n > 20 else step
        p.setPen(COL_TEXT)
        for i in range(0, n, step):
            x = self._x(i, rect)
            p.drawLine(QPointF(x, rect.bottom()), QPointF(x, rect.bottom() + 3))
            p.drawText(QRectF(x - 24, rect.bottom() + 34, 48, 14),
                       Qt.AlignCenter, f"{self._history[i]['year']}年")

    def _draw_hover(self, p, rect):
        idx = self._hover_idx
        if idx is None or not (0 <= idx < len(self._history)):
            return
        rec = self._history[idx]
        x = self._x(idx, rect)
        y = self._y(rec["hp"], rect)
        p.setPen(QPen(COL_SEG_LINE, 1, Qt.DotLine))
        p.drawLine(QPointF(x, rect.top()), QPointF(x, rect.bottom()))
        p.setPen(QPen(COL_LINE, 1.6))
        p.setBrush(QBrush(QColor("#fff8e7")))
        p.drawEllipse(QPointF(x, y), 4, 4)

        text = (f"{rec.get('time', '')}（国祚{rec['year']}年）　"
                f"{rec.get('emperor', '')}　国运 {rec['hp']:.0f}")
        p.setFont(QFont(FONT_FAMILY, 10))
        fm = p.fontMetrics()
        tw = fm.horizontalAdvance(text) + 16
        th = fm.height() + 8
        tx = min(max(x - tw / 2, rect.left()), rect.right() - tw)
        ty = rect.top() + 6 if y > rect.top() + th + 12 else y + 10
        tip = QRectF(tx, ty, tw, th)
        p.setPen(QPen(COL_AXIS, 1))
        p.setBrush(QBrush(QColor(255, 253, 248, 235)))
        p.drawRoundedRect(tip, 4, 4)
        p.setPen(COL_TEXT)
        p.drawText(tip, Qt.AlignCenter, text)

    # ---- 交互 ----

    def mouseMoveEvent(self, event):
        rect = self._plot_rect()
        n = len(self._history)
        idx = None
        if n and rect.left() - 6 <= event.position().x() <= rect.right() + 6:
            if n == 1:
                idx = 0
            else:
                frac = (event.position().x() - rect.left()) / rect.width()
                idx = int(round(frac * (n - 1)))
                idx = max(0, min(n - 1, idx))
        if idx != self._hover_idx:
            self._hover_idx = idx
            self.update()

    def leaveEvent(self, _event):
        if self._hover_idx is not None:
            self._hover_idx = None
            self.update()


class FortuneChartDialog(QDialog):
    """承载国运折线图的对话框（横向滚动，适配长国祚）。"""

    def __init__(self, history, dynasty_name="", parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"{dynasty_name}朝国运图" if dynasty_name else "王朝国运图")
        self.resize(860, 540)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)

        title = QLabel(f"— {dynasty_name} 朝 国 运 —" if dynasty_name else "— 国 运 —")
        title.setObjectName("section_label")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        hint = QLabel("上标在位皇帝，下标年号更迭（▲ 为改元），移动鼠标查看逐年国运")
        hint.setAlignment(Qt.AlignCenter)
        layout.addWidget(hint)

        chart = FortuneChartWidget(history)
        scroll = QScrollArea()
        scroll.setWidget(chart)
        scroll.setWidgetResizable(False)
        scroll.setAlignment(Qt.AlignCenter)
        layout.addWidget(scroll, 1)
        # 默认滚到最右（最新年份）
        scroll.horizontalScrollBar().setValue(scroll.horizontalScrollBar().maximum())
