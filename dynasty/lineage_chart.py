# -*- coding: utf-8 -*-
"""直观的男系世系图：以中心人物 ±2 代窗口展示，边缘可展开，支持全屏。"""
from __future__ import annotations

from PySide6.QtCore import Qt, QRectF, QPointF, QSize, Signal
from PySide6.QtGui import QPainter, QPen, QColor, QFont, QBrush, QPainterPath
from PySide6.QtWidgets import (
    QWidget, QSizePolicy, QVBoxLayout, QHBoxLayout, QPushButton,
    QScrollArea, QDialog, QLabel,
)


NODE_W = 108
NODE_H = 56
H_GAP = 18
V_GAP = 48
PAD = 28
EXPAND_R = 11  # 展开按钮半径
WINDOW = 2     # 上下各展示代数


class _Node:
    __slots__ = (
        "person", "children", "x", "y", "width",
        "can_expand_up", "can_expand_down",
    )

    def __init__(self, person):
        self.person = person
        self.children = []
        self.x = 0.0
        self.y = 0.0
        self.width = NODE_W
        self.can_expand_up = False
        self.can_expand_down = False


class LineageChartWidget(QWidget):
    """以 center 为中心、上下各 WINDOW 代的男系世系图。"""

    personActivated = Signal(int)
    centerChanged = Signal(int)  # 展开后中心人物变化

    def __init__(
        self,
        get_person_by_id,
        center_person,
        focus_id=None,
        current_emperor_pid=None,
        parent=None,
    ):
        super().__init__(parent)
        self._get = get_person_by_id
        self._focus_id = focus_id
        self._emperor_pid = current_emperor_pid
        self._center_id = center_person.id if center_person else None
        self._nodes = []
        self._tree = None
        self._expand_hits = []  # (QRectF, "up"|"down", person_id)

        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setMouseTracking(True)
        self.setObjectName("lineage_chart")
        self._rebuild()

    def set_center(self, person):
        if not person:
            return
        self._center_id = person.id
        self._rebuild()
        self.centerChanged.emit(person.id)

    def _rebuild(self):
        self._nodes = []
        self._tree = None
        self._expand_hits = []
        center = self._get(self._center_id) if self._center_id is not None else None
        if not center:
            self.setFixedSize(200, 200)
            self.update()
            return

        root_person = self._window_root(center)
        max_gen = center.generation + WINDOW
        self._tree = self._build(root_person, max_gen)
        self._mark_expand(self._tree, root_person, center)
        self._layout(self._tree, 0, PAD)
        self._collect(self._tree)
        self._build_expand_hits()

        content_w = max(int(self._max_right(self._tree) + PAD), 200)
        depth = self._max_depth(self._tree)
        content_h = PAD * 2 + (depth + 1) * NODE_H + depth * V_GAP + EXPAND_R * 2
        self.setFixedSize(content_w, max(content_h, 200))
        self.update()

    def _window_root(self, center):
        """从中心向上最多 WINDOW 代，得到可见树根。"""
        root = center
        steps = 0
        while steps < WINDOW and root.father_id is not None:
            father = self._get(root.father_id)
            if not father or father.gender != "M":
                break
            root = father
            steps += 1
        return root

    def _male_sons(self, person):
        sons = []
        for cid in person.children:
            child = self._get(cid)
            if child and child.gender == "M":
                sons.append(child)
        sons.sort(key=lambda c: (c.birth_year, c.id))
        return sons

    def _build(self, person, max_gen):
        node = _Node(person)
        if person.generation >= max_gen:
            return node
        for son in self._male_sons(person):
            if son.generation <= max_gen:
                node.children.append(self._build(son, max_gen))
        return node

    def _mark_expand(self, tree, root_person, center):
        """顶行可上展、底行（相对中心 +WINDOW 且仍有子）可下展。"""
        if not tree:
            return
        # 上：根之上还有父亲
        father = None
        if root_person.father_id is not None:
            father = self._get(root_person.father_id)
        tree.can_expand_up = bool(father and father.gender == "M")

        # 下：generation == center.gen + WINDOW 且有男嗣
        floor_gen = center.generation + WINDOW

        def walk(n):
            p = n.person
            if p.generation >= floor_gen and self._male_sons(p):
                n.can_expand_down = True
            for ch in n.children:
                walk(ch)

        walk(tree)

    def _layout(self, node, depth, x_left):
        y = PAD + EXPAND_R + depth * (NODE_H + V_GAP)
        node.y = y
        if not node.children:
            node.x = x_left + NODE_W / 2
            node.width = NODE_W
            return x_left + NODE_W + H_GAP

        cursor = x_left
        for ch in node.children:
            cursor = self._layout(ch, depth + 1, cursor)
        first_x = node.children[0].x
        last_x = node.children[-1].x
        node.x = (first_x + last_x) / 2
        node.width = cursor - x_left - H_GAP
        return cursor

    def _collect(self, node):
        self._nodes.append(node)
        for ch in node.children:
            self._collect(ch)

    def _max_right(self, node):
        r = node.x + NODE_W / 2
        for ch in node.children:
            r = max(r, self._max_right(ch))
        return r

    def _max_depth(self, node, d=0):
        if not node.children:
            return d
        return max(self._max_depth(ch, d + 1) for ch in node.children)

    def _node_rect(self, node):
        return QRectF(node.x - NODE_W / 2, node.y, NODE_W, NODE_H)

    def _expand_rect_up(self, node):
        cx, cy = node.x, node.y - EXPAND_R - 2
        return QRectF(cx - EXPAND_R, cy - EXPAND_R, EXPAND_R * 2, EXPAND_R * 2)

    def _expand_rect_down(self, node):
        cx, cy = node.x, node.y + NODE_H + EXPAND_R + 2
        return QRectF(cx - EXPAND_R, cy - EXPAND_R, EXPAND_R * 2, EXPAND_R * 2)

    def _build_expand_hits(self):
        self._expand_hits = []
        for node in self._nodes:
            if node.can_expand_up:
                self._expand_hits.append((self._expand_rect_up(node), "up", node.person.id))
            if node.can_expand_down:
                self._expand_hits.append((self._expand_rect_down(node), "down", node.person.id))

    # ── 绘制 ──────────────────────────────────────────────

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.TextAntialiasing)
        painter.fillRect(self.rect(), QColor("#fffdf8"))

        if not self._tree:
            painter.setPen(QColor("#6b4e2e"))
            painter.drawText(self.rect(), Qt.AlignCenter, "暂无世系")
            return

        line_pen = QPen(QColor("#a67c3d"), 1.4)
        painter.setPen(line_pen)
        for node in self._nodes:
            if not node.children:
                continue
            px, py = node.x, node.y + NODE_H
            mid_y = py + V_GAP / 2
            painter.drawLine(QPointF(px, py), QPointF(px, mid_y))
            if len(node.children) == 1:
                cx = node.children[0].x
                painter.drawLine(QPointF(px, mid_y), QPointF(cx, mid_y))
                painter.drawLine(QPointF(cx, mid_y), QPointF(cx, node.children[0].y))
            else:
                left = node.children[0].x
                right = node.children[-1].x
                painter.drawLine(QPointF(left, mid_y), QPointF(right, mid_y))
                for ch in node.children:
                    painter.drawLine(QPointF(ch.x, mid_y), QPointF(ch.x, ch.y))

        name_font = QFont(self.font())
        name_font.setPointSize(11)
        name_font.setBold(True)
        sub_font = QFont(self.font())
        sub_font.setPointSize(9)

        for node in self._nodes:
            self._paint_card(painter, node, name_font, sub_font)
            if node.can_expand_up:
                self._paint_expand(painter, self._expand_rect_up(node))
            if node.can_expand_down:
                self._paint_expand(painter, self._expand_rect_down(node))

    def _paint_expand(self, painter, rect):
        painter.setBrush(QBrush(QColor("#c4453c")))
        painter.setPen(QPen(QColor("#b5893f"), 1.2))
        painter.drawEllipse(rect)
        painter.setPen(QPen(QColor("#fff8e7"), 2.0))
        cx = rect.center().x()
        cy = rect.center().y()
        arm = EXPAND_R * 0.45
        painter.drawLine(QPointF(cx - arm, cy), QPointF(cx + arm, cy))
        painter.drawLine(QPointF(cx, cy - arm), QPointF(cx, cy + arm))

    def _paint_card(self, painter, node, name_font, sub_font):
        p = node.person
        rect = self._node_rect(node)
        is_focus = self._focus_id is not None and p.id == self._focus_id
        is_center = self._center_id is not None and p.id == self._center_id
        is_emp = self._emperor_pid is not None and p.id == self._emperor_pid

        # 卡片背景一律浅色（规范见 docs/modules/04-styles.md），身份差异靠边框区分
        if is_focus:
            bg = QColor("#f5e6c8")
            border = QColor("#b83a32")
            border_w = 2.2
        elif is_center:
            bg = QColor("#f8edd8")
            border = QColor("#a67c3d")
            border_w = 1.8
        elif is_emp:
            bg = QColor("#f8edd8")
            border = QColor("#8b5a12")
            border_w = 1.8
        elif not p.is_alive:
            bg = QColor("#f3ead8")
            border = QColor("#b0a090")
            border_w = 1.2
        else:
            bg = QColor("#fffdf8")
            border = QColor("#c4a574")
            border_w = 1.4

        path = QPainterPath()
        path.addRoundedRect(rect, 6, 6)
        painter.fillPath(path, QBrush(bg))
        painter.setPen(QPen(border, border_w))
        painter.drawPath(path)

        name = p.name
        if is_emp:
            name = "★ " + name
        title = (p.title or "").strip()
        if len(title) > 8:
            title = title[:7] + "…"
        status = "在世" if p.is_alive else "已故"
        if p.extinct:
            status += "·绝"
        if p.is_heir:
            status += "·世子"
        sub = f"{title} · {status}" if title else status

        text_color = QColor("#2c1810") if p.is_alive else QColor("#6b5a4a")
        if is_focus:
            text_color = QColor("#7a1a14")

        name_rect = QRectF(rect.x() + 4, rect.y() + 6, rect.width() - 8, 22)
        sub_rect = QRectF(rect.x() + 4, rect.y() + 28, rect.width() - 8, 20)

        painter.setPen(text_color)
        painter.setFont(name_font)
        painter.drawText(name_rect, Qt.AlignHCenter | Qt.AlignVCenter, name)
        painter.setFont(sub_font)
        painter.setPen(QColor("#6b4e2e") if p.is_alive else QColor("#8a7a6a"))
        painter.drawText(sub_rect, Qt.AlignHCenter | Qt.AlignTop, sub)

    # ── 交互 ──────────────────────────────────────────────

    def mouseMoveEvent(self, event):
        pos = event.position()
        if self._hit_expand(pos) or self._hit_person(pos) is not None:
            self.setCursor(Qt.PointingHandCursor)
        else:
            self.setCursor(Qt.ArrowCursor)

    def mousePressEvent(self, event):
        if event.button() != Qt.LeftButton:
            return
        hit = self._hit_expand(event.position())
        if not hit:
            return
        _rect, direction, pid = hit
        person = self._get(pid)
        if not person:
            return
        # 以边缘人物为新中心，再展开 ±2 代
        self.set_center(person)

    def mouseDoubleClickEvent(self, event):
        if self._hit_expand(event.position()):
            return
        pid = self._hit_person(event.position())
        if pid is not None:
            self.personActivated.emit(pid)

    def _hit_expand(self, pos):
        for rect, direction, pid in self._expand_hits:
            if rect.contains(pos):
                return (rect, direction, pid)
        return None

    def _hit_person(self, pos):
        for node in self._nodes:
            if self._node_rect(node).contains(pos):
                return node.person.id
        return None


class LineageChartPanel(QWidget):
    """带全屏按钮的世系图面板（详情弹窗 / 全屏共用）。"""

    personActivated = Signal(int)

    def __init__(
        self,
        get_person_by_id,
        center_person,
        focus_id=None,
        current_emperor_pid=None,
        parent=None,
        compact=True,
    ):
        super().__init__(parent)
        self._get = get_person_by_id
        self._focus_id = focus_id
        self._emperor_pid = current_emperor_pid
        self._compact = compact

        self.setObjectName("lineage_chart_panel")
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(4)

        bar = QHBoxLayout()
        bar.setContentsMargins(2, 0, 2, 0)
        self._hint = QLabel("以中心 ±2 代　·　点击 ⊕ 展开两代　·　双击查看详情")
        self._hint.setObjectName("lineage_chart_hint")
        bar.addWidget(self._hint, 1)

        self._fs_btn = QPushButton("⛶")
        self._fs_btn.setObjectName("lineage_fullscreen_btn")
        self._fs_btn.setToolTip("全屏展示家族树")
        self._fs_btn.setFixedSize(32, 28)
        self._fs_btn.setCursor(Qt.PointingHandCursor)
        self._fs_btn.clicked.connect(self._open_fullscreen)
        bar.addWidget(self._fs_btn, 0, Qt.AlignTop)
        outer.addLayout(bar)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(False)
        self._scroll.setObjectName("lineage_chart_scroll")
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self._scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        if compact:
            self._scroll.setMinimumHeight(280)
            self._scroll.setMaximumHeight(360)

        self._chart = LineageChartWidget(
            get_person_by_id=get_person_by_id,
            center_person=center_person,
            focus_id=focus_id,
            current_emperor_pid=current_emperor_pid,
        )
        self._chart.personActivated.connect(self.personActivated.emit)
        self._scroll.setWidget(self._chart)
        outer.addWidget(self._scroll, 1)

    def _open_fullscreen(self):
        center = self._get(self._chart._center_id) if self._chart._center_id is not None else None
        if not center:
            return
        dlg = QDialog(self.window())
        dlg.setWindowTitle("家族树 · 全屏")
        dlg.setWindowFlag(Qt.Window)
        dlg.resize(1000, 720)
        lay = QVBoxLayout(dlg)
        lay.setContentsMargins(10, 10, 10, 10)

        panel = LineageChartPanel(
            get_person_by_id=self._get,
            center_person=center,
            focus_id=self._focus_id,
            current_emperor_pid=self._emperor_pid,
            compact=False,
        )
        # 全屏面板隐藏再开全屏，避免嵌套
        panel._fs_btn.setVisible(False)
        panel._hint.setText("以中心 ±2 代　·　点击 ⊕ 展开两代　·　双击查看详情　·　Esc 关闭")
        panel.personActivated.connect(self.personActivated.emit)
        lay.addWidget(panel, 1)

        close_btn = QPushButton("关闭全屏")
        close_btn.clicked.connect(dlg.accept)
        lay.addWidget(close_btn, 0, Qt.AlignRight)

        dlg.showMaximized()
        dlg.exec()
        # 同步全屏中可能改变的中心
        if panel._chart._center_id is not None:
            p = self._get(panel._chart._center_id)
            if p:
                self._chart.set_center(p)
