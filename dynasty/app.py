# -*- coding: utf-8 -*-
"""主窗口、各界面 Tab、对话框与 UI 刷新；编排年度循环。"""
from PySide6.QtWidgets import (
    QMainWindow, QStackedWidget, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QLineEdit, QPushButton, QFormLayout, QDialog,
    QHeaderView, QTabWidget, QTableWidget, QSlider, QTableWidgetItem,
    QTreeWidget, QTreeWidgetItem, QComboBox, QSplitter, QAbstractItemView,
    QPlainTextEdit, QApplication,
)
from PySide6.QtCore import Qt, QTimer

from dynasty.lineage_chart import LineageChartPanel
from dynasty.fortune_chart import FortuneChartDialog
from dynasty.mixins.dynasty_logic import DynastyLogicMixin
from dynasty.mixins.emperor import EmperorMixin
from dynasty.mixins.events import EventsMixin
from dynasty.mixins.family import FamilyMixin
from dynasty.mixins.history_prompt import HistoryPromptMixin
from dynasty.mixins.naming import NamingMixin
from dynasty.mixins.succession import SuccessionMixin
from dynasty.mixins.titles import TitlesMixin
from dynasty.resources import ResourcesMixin
from dynasty.state import GameStateMixin
from dynasty.styles import StylesMixin


class DynastyApp(
    ResourcesMixin,
    GameStateMixin,
    StylesMixin,
    NamingMixin,
    TitlesMixin,
    FamilyMixin,
    SuccessionMixin,
    EventsMixin,
    EmperorMixin,
    DynastyLogicMixin,
    HistoryPromptMixin,
    QMainWindow,
):
    """王朝模拟主窗口：组合各功能 Mixin，负责界面与年度主循环编排。"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("王朝 V1.00")
        self.resize(1000, 700)

        # Initialize Game State
        self.init_game_state()

        # Central stacked widget
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # Start Screen
        self.start_screen = QWidget()
        self.setup_start_screen()
        self.stacked_widget.addWidget(self.start_screen)

        # Main Game Screen
        self.main_game_screen = QWidget()
        self.setup_main_game_screen()
        self.stacked_widget.addWidget(self.main_game_screen)

        # Initially show start screen
        self.stacked_widget.setCurrentIndex(0)

        # Dialogs
        self.setup_dialogs()

        # 古风主题样式（墨底金边 · 朱漆宫墙）
        self.apply_stylesheet()

        # Auto-run timer
        self.auto_run = False
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.auto_run_step)

    def setup_dialogs(self):
        # End Game Dialog
        self.end_game_dialog = QDialog(self)
        self.end_game_dialog.setWindowTitle("结束")
        self.end_game_dialog.resize(600, 400)
        end_game_layout = QVBoxLayout()

        self.end_game_tabs = QTabWidget()

        # Emperor List Tab
        self.end_game_emp_tab = QWidget()
        end_game_emp_layout = QVBoxLayout()
        self.dialog_emperor_list_table = QTableWidget()
        self.dialog_emperor_list_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.dialog_emperor_list_table.setColumnCount(9)
        self.dialog_emperor_list_table.setHorizontalHeaderLabels(["序号", "庙号", "谥号", "姓名", "年龄", "年号", "纪年", "治国手腕", "史书评价"])
        self.dialog_emperor_list_table.verticalHeader().setVisible(False)
        self.dialog_emperor_list_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        end_game_emp_layout.addWidget(self.dialog_emperor_list_table)
        self.end_game_emp_tab.setLayout(end_game_emp_layout)

        # Events Tab
        self.end_game_event_tab = QWidget()
        end_game_event_layout = QVBoxLayout()
        self.dialog_event_table = QTableWidget()
        self.dialog_event_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.dialog_event_table.setColumnCount(3)
        self.dialog_event_table.setHorizontalHeaderLabels(["时间", "皇帝", "事件"])
        self.dialog_event_table.verticalHeader().setVisible(False)
        self.dialog_event_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        end_game_event_layout.addWidget(self.dialog_event_table)
        self.end_game_event_tab.setLayout(end_game_event_layout)

        self.end_game_tabs.addTab(self.end_game_emp_tab, "皇帝列表")
        self.end_game_tabs.addTab(self.end_game_event_tab, "王朝纪事")
        end_game_layout.addWidget(self.end_game_tabs)

        end_btn_row = QHBoxLayout()
        self.end_game_restart_btn = QPushButton("重新开始")
        self.end_game_browse_btn = QPushButton("翻阅国史")
        self.end_game_export_btn = QPushButton("导出提示词")
        end_btn_row.addWidget(self.end_game_restart_btn)
        end_btn_row.addWidget(self.end_game_browse_btn)
        end_btn_row.addWidget(self.end_game_export_btn)
        end_game_layout.addLayout(end_btn_row)

        self.end_game_dialog.setLayout(end_game_layout)
        self.end_game_restart_btn.clicked.connect(self.dio2)
        # 「翻阅国史」与点 X 关闭同走 rejected：留在主界面翻阅本局史料
        self.end_game_browse_btn.clicked.connect(self.end_game_dialog.reject)
        self.end_game_export_btn.clicked.connect(self.show_history_prompt_dialog)
        self.end_game_dialog.rejected.connect(self.enter_history_browse_mode)

    def enter_history_browse_mode(self):
        """亡国后翻阅国史：主界面下方显示「重新开始」与「一键导出国史提示词」。"""
        self.auto_run_btn.hide()
        self.export_prompt_btn.show()
        self.restart_btn.show()

    def exit_history_browse_mode(self):
        self.restart_btn.hide()
        self.auto_run_btn.show()
        self.export_prompt_btn.show()

    def setup_start_screen(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 30, 40, 30)

        # 醒目标题，增强代入感
        title = QLabel("王 朝")
        title.setObjectName("title_label")
        subtitle = QLabel("—— 一代天骄，执掌乾坤 ——")
        subtitle.setObjectName("subtitle_label")
        layout.addWidget(title)
        layout.addWidget(subtitle)

        form_layout = QFormLayout()

        # Dynasty input
        self.dynasty_input = QLineEdit()
        self.dynasty_input.setReadOnly(True)
        self.dynasty_btn = QPushButton("刷新")
        dynasty_layout = QHBoxLayout()
        dynasty_layout.addWidget(self.dynasty_input)
        dynasty_layout.addWidget(self.dynasty_btn)
        form_layout.addRow("朝代:", dynasty_layout)

        # Emperor input
        self.emperor_input = QLineEdit()
        self.emperor_input.setReadOnly(True)
        self.emperor_btn = QPushButton("刷新")
        emperor_layout = QHBoxLayout()
        emperor_layout.addWidget(self.emperor_input)
        emperor_layout.addWidget(self.emperor_btn)
        form_layout.addRow("皇帝:", emperor_layout)

        # Year number input
        self.year_number_input = QLineEdit()
        self.year_number_input.setReadOnly(True)
        self.year_number_btn = QPushButton("刷新")
        year_number_layout = QHBoxLayout()
        year_number_layout.addWidget(self.year_number_input)
        year_number_layout.addWidget(self.year_number_btn)
        form_layout.addRow("年号:", year_number_layout)

        # 字辈：下拉备选 + 可手改 + 刷新随机
        self.zibei_combo = QComboBox()
        self.zibei_combo.setEditable(False)
        self.zibei_combo.addItems(self.zibei_options)
        self.zibei_combo.setCurrentIndex(0)
        self.zibei_btn = QPushButton("刷新")
        zibei_layout = QHBoxLayout()
        zibei_layout.addWidget(self.zibei_combo)
        zibei_layout.addWidget(self.zibei_btn)
        form_layout.addRow("字辈:", zibei_layout)

        layout.addLayout(form_layout)

        # Start Button
        self.start_btn = QPushButton("开始游戏")
        layout.addWidget(self.start_btn)

        self.start_screen.setLayout(layout)
        # Connect signals
        self.dynasty_btn.clicked.connect(self.dynasty_change_name)
        self.emperor_btn.clicked.connect(self.emperor_change_name)
        self.year_number_btn.clicked.connect(self.yearNumber_change_name)
        self.zibei_btn.clicked.connect(self.zibei_change_poem)
        self.start_btn.clicked.connect(self.start_game_from_ui)

    def start_game_from_ui(self):
        self.zibei_poem = self.zibei_combo.currentText().strip() or self.zibei_options[0]
        if not self.dynasty_input.text().strip():
            self.dynasty_change_name()
        if not self.emperor_input.text().strip():
            self.emperor_change_name()
        if not self.year_number_input.text().strip():
            self.yearNumber_change_name()

        self.dynasty = self.dynasty_input.text()
        self.emperor = self.emperor_input.text()
        self.yearNumber = self.year_number_input.text()
        self.gamestart()

    def achange(self, value):
        self.amuse = value
        self.hardworking = 100 - self.amuse
        self.hardworking_slider.setValue(self.hardworking)

    def bchange(self, value):
        self.hardworking = value
        self.amuse = 100 - self.hardworking
        self.amuse_slider.setValue(self.amuse)

    def gamemin(self):
        self.year += 1
        self.event_happen()
        self.gamemin_family_aging_death()
        self.gamemin_emperor()
        self.gamemin_dynasty()
        if not self.ongame:
            self.update_ui()
            return

        if self.emperor_die and self.next_emperor_pid is not None:
            self.auto_accession()

        self.gamemin_family_marriage_birth()
        self.update_crown_prince() # Calls update_heirs internally
        self.gamemin_family_shihao_titles()
        self.prune_unimportant_people()
        self.dynasty_function_st()
        self.update_ui()

    def update_ui(self):

        # 朝代年号匾额
        reign_text = f"　{self.dynasty}　·　{self.yearNumber}　"
        self.reign_banner.setText(reign_text)

        # Update Tab 1
        self.dynasty_label.setText(self.dynasty)
        self.emperor_label.setText(self.emperor)
        self.year_number_label.setText(self.yearNumber)
        self.jinian_label.setText("元" if self.jinian == 1 else str(self.jinian))
        self.dynasty_st_label.setText(self.dynasty_st)
        self.emperor_hp_label.setText(str(round(self.emperor_hp)))

        # Event Table：仅显示最新 50 条；完整历史仍保留在 event_happened（结束界面展示全部）
        events = self.event_happened[1:]
        display_events = events[-50:] if len(events) > 50 else events
        shown = self.event_table.rowCount()
        need_rebuild = shown > len(display_events)
        if not need_rebuild and shown > 0 and display_events:
            first = self.event_table.item(0, 0)
            first_ev = self.event_table.item(0, 2)
            # 时间可能重复（同年改元记两条），需连事件文本一并比对
            if (first is None or first.text() != display_events[0].get("time", "")
                    or first_ev is None or first_ev.text() != display_events[0].get("event", "")):
                need_rebuild = True
        if need_rebuild:
            self.event_table.setRowCount(0)
            shown = 0
        for i in range(shown, len(display_events)):
            ev = display_events[i]
            self.event_table.insertRow(i)
            self.event_table.setItem(i, 0, QTableWidgetItem(ev.get("time", "")))
            self.event_table.setItem(i, 1, QTableWidgetItem(ev.get("emperor", "")))
            self.event_table.setItem(i, 2, QTableWidgetItem(ev.get("event", "")))
        if display_events:
            self.event_table.scrollToBottom()

        # Update Tab 2
        self.emp_name_label.setText(self.emperor)
        self.emp_zunhao_label.setText(self.emperor_zunhao)
        self.emp_age_label.setText(str(self.emperor_age))
        self.emp_hp_label.setText(str(round(self.emperor_hp)))
        self.emp_ab_label.setText(str(self.emperor_ab))

        # Update Tab 3
        self.dyn_name_label.setText(self.dynasty)
        self.dyn_age_label.setText(str(self.dynasty_age))
        self.dyn_st_label.setText(self.dynasty_st)

        self.emperor_list_table.setRowCount(0)
        for i, emp in enumerate(self.listjson):
            self.emperor_list_table.insertRow(i)
            self.emperor_list_table.setItem(i, 0, QTableWidgetItem(str(emp["id"])))
            self.emperor_list_table.setItem(i, 1, QTableWidgetItem(emp["miaohao"]))
            self.emperor_list_table.setItem(i, 2, QTableWidgetItem(emp["shihao"]))
            self.emperor_list_table.setItem(i, 3, QTableWidgetItem(emp["name"]))
            self.emperor_list_table.setItem(i, 4, QTableWidgetItem(str(emp["age"])))
            self.emperor_list_table.setItem(i, 5, QTableWidgetItem(emp["nianhao"]))
            self.emperor_list_table.setItem(i, 6, QTableWidgetItem(str(emp["jinian"])))
            self.emperor_list_table.setItem(i, 7, QTableWidgetItem(str(emp["ab"])))
            self.emperor_list_table.setItem(i, 8, QTableWidgetItem(emp["verdict"]))

        # 宗亲/宗藩 UI 较重：仅当前 Tab 或每 5 年全量刷新
        tab_idx = self.tabs.currentIndex() if hasattr(self, "tabs") else 0
        need_family = tab_idx in (3, 4) or (self.year % 5 == 0)
        if need_family and hasattr(self, "family_table"):
            self.family_table.setUpdatesEnabled(False)
            self.family_table.setRowCount(0)
            # 在世 + 有爵/谥/帝系；未封已故支系不入表
            males = [
                p for p in self.people
                if p.gender == "M" and self.is_important_person(p)
            ]
            males.sort(key=lambda p: (
                0 if self.get_guobie(p) != "未封" else 1,
                self.get_guobie(p),
                p.generation,
                -p.age,
            ))
            for row_idx, p in enumerate(males):
                self.family_table.insertRow(row_idx)
                self.family_table.setItem(row_idx, 0, QTableWidgetItem(str(p.id)))
                self.family_table.setItem(row_idx, 1, QTableWidgetItem(p.name))
                self.family_table.setItem(row_idx, 2, QTableWidgetItem(str(p.age)))
                self.family_table.setItem(row_idx, 3, QTableWidgetItem(p.title))
                self.family_table.setItem(row_idx, 4, QTableWidgetItem(self.get_guobie(p)))
                self.family_table.setItem(row_idx, 5, QTableWidgetItem("存活" if p.is_alive else "已故"))
                self.family_table.setItem(row_idx, 6, QTableWidgetItem(p.shihao))
                self.family_table.setItem(row_idx, 7, QTableWidgetItem(str(p.generation)))
                self.family_table.setItem(row_idx, 8, QTableWidgetItem("绝嗣" if p.extinct else ""))
            self.family_table.setUpdatesEnabled(True)
            self.update_family_tree()

        if need_family:
            self.update_fief_list()

    def update_family_tree(self):
        tree = self.family_tree_widget
        tree.setUpdatesEnabled(False)
        tree.clear()

        # 树只展示重要人物（在世/有爵/帝系），避免未封已故支系撑爆 UI
        males = [
            p for p in self.people
            if p.gender == "M" and self.is_important_person(p)
        ]
        if not males:
            tree.setUpdatesEnabled(True)
            return

        # 补全祖先链，保证树不断档
        id_all = {p.id: p for p in self.people if p.gender == "M"}
        shown = {p.id: p for p in males}
        for p in list(males):
            cur = p
            while cur and cur.father_id is not None and cur.father_id not in shown:
                father = id_all.get(cur.father_id)
                if not father:
                    break
                shown[father.id] = father
                cur = father
        males = list(shown.values())

        # 按父系构建世系树（开国皇帝为根）
        id_map = {p.id: p for p in males}
        children_map = {p.id: [] for p in males}
        roots = []
        for p in males:
            fid = p.father_id
            if fid in id_map:
                children_map[fid].append(p)
            else:
                roots.append(p)

        for cid in children_map:
            children_map[cid].sort(key=lambda x: (x.birth_year, x.id))

        def make_node(parent, person, depth=0):
            is_now = (person.id == self.current_emperor_pid)
            title_str = f" {person.title}" if person.title else ""
            name_str = ("★ " if is_now else "") + person.name + ("（今上）" if is_now else "") + title_str
            status = "存活" if person.is_alive else "已故"
            if person.extinct:
                status += "·绝嗣"
            shimiao = ""
            if person.miaohao:
                shimiao = f"庙号 {person.miaohao}"
            elif person.shihao:
                shimiao = person.shihao
            if person.zunhao and person.is_alive:
                shimiao = (shimiao + "　" if shimiao else "") + f"尊号 {person.zunhao}"
            node = QTreeWidgetItem(parent, [
                name_str,
                self.get_guobie(person),
                status,
                shimiao,
                str(person.generation),
            ])
            node.setData(0, Qt.UserRole, person.id)
            # 默认只展开前两代，减少布局开销
            node.setExpanded(depth < 2)
            for child in children_map.get(person.id, []):
                make_node(node, child, depth + 1)

        # 开国皇帝（无父者）为根；其余旁支归入“旁系”
        roots.sort(key=lambda x: (0 if x.father_id is None else 1, x.generation, x.birth_year, x.id))
        main_root = None
        side_roots = []
        for r in roots:
            if r.father_id is None and main_root is None:
                main_root = r
            else:
                side_roots.append(r)

        if main_root is not None:
            make_node(tree, main_root)
        if side_roots:
            side_item = QTreeWidgetItem(tree, ["旁系 / 来源不详", "", "", "", ""])
            side_item.setExpanded(True)
            for r in side_roots:
                make_node(side_item, r)

        tree.setUpdatesEnabled(True)

    def update_fief_list(self):
        if not hasattr(self, "fief_table"):
            return
        fiefs = self.collect_fiefs()
        alive_fiefs = sum(1 for f in fiefs if not f["extinct"])
        if hasattr(self, "fief_count_label"):
            self.fief_count_label.setText(
                f"存续 {alive_fiefs}　·　共计 {len(fiefs)}"
            )
        self.fief_table.setRowCount(0)
        for i, fief in enumerate(fiefs):
            self.fief_table.insertRow(i)
            current = fief["current"]
            current_name = current.name if current else "—"
            rank_label = self.get_rank_label(fief["rank"])
            rank_short = self.get_rank_short(fief["rank"]) if fief["rank"] else "—"
            full_title = self.format_enfeoffed_title(fief["name"], fief["rank"]) if fief["rank"] else fief["name"]
            status = "绝" if fief["extinct"] else "存"
            items = [fief["name"], rank_short, current_name, status]
            for col, text in enumerate(items):
                item = QTableWidgetItem(text)
                if col == 0:
                    item.setData(Qt.UserRole, fief["name"])
                    tip = full_title or fief["name"]
                    if current:
                        tip += f"　国主 {current.name}"
                    tip += f"　在世 {fief['alive_count']}/{fief['total_count']}"
                    item.setToolTip(tip)
                if col == 3 and fief["extinct"]:
                    item.setForeground(Qt.GlobalColor.darkRed)
                self.fief_table.setItem(i, col, item)
        # 若当前选中的封国仍在，刷新右侧世系；否则清空
        if hasattr(self, "_selected_fief_name") and self._selected_fief_name:
            names = {f["name"] for f in fiefs}
            if self._selected_fief_name in names:
                self.show_fief_lineage(self._selected_fief_name)
            else:
                self.fief_lineage_tree.clear()
                self.fief_detail_label.setText("点选左侧封国，查看该支世系")
                self._selected_fief_name = None

    def build_lineage_tree_widget(self, root_person, fief_name=None):
        """构建以 root 为根的男系世系树。"""
        tree = QTreeWidget()
        tree.setColumnCount(4)
        tree.setHeaderLabels(["姓名 / 称号", "状态", "谥号", "代数"])
        tree.setColumnWidth(0, 220)
        tree.setColumnWidth(1, 80)
        tree.setColumnWidth(2, 140)
        tree.setColumnWidth(3, 50)
        tree.setAlternatingRowColors(True)

        if not root_person:
            return tree

        def node_label(p):
            title_str = f" {p.title}" if p.title else ""
            mark = ""
            if p.id == self.current_emperor_pid:
                mark = "★ "
            if fief_name and p.is_alive and p.has_title and p.title_name == fief_name:
                mark = "◆ " + mark
            return mark + p.name + title_str

        def status_of(p):
            s = "存活" if p.is_alive else "已故"
            if p.extinct:
                s += "·绝嗣"
            if p.is_heir:
                s += "·世子"
            return s

        def shimiao_of(p):
            if p.miaohao:
                return f"庙号 {p.miaohao}"
            return p.shihao or ""

        def add_node(parent_item, person, depth=0):
            item = QTreeWidgetItem(parent_item, [
                node_label(person),
                status_of(person),
                shimiao_of(person),
                str(person.generation),
            ])
            item.setData(0, Qt.UserRole, person.id)
            item.setExpanded(depth < 6)
            sons = []
            for cid in person.children:
                child = self.get_person_by_id(cid)
                if child and child.gender == "M":
                    sons.append(child)
            sons.sort(key=lambda c: (c.birth_year, c.id))
            for son in sons:
                add_node(item, son, depth + 1)

        add_node(tree, root_person)
        tree.itemDoubleClicked.connect(self.on_lineage_tree_person_clicked)
        return tree

    def on_lineage_tree_person_clicked(self, item, column):
        pid = item.data(0, Qt.UserRole)
        if pid is None:
            return
        self.show_person_detail_dialog(int(pid))

    def on_family_tree_item_clicked(self, item, column):
        pid = item.data(0, Qt.UserRole)
        if pid is None:
            return
        self.show_person_detail_dialog(int(pid))

    def on_family_table_clicked(self, row, column):
        pid_item = self.family_table.item(row, 0)
        if not pid_item:
            return
        try:
            pid = int(pid_item.text())
        except ValueError:
            return
        self.show_person_detail_dialog(pid)

    def on_fief_table_clicked(self, row, column):
        name_item = self.fief_table.item(row, 0)
        if not name_item:
            return
        fief_name = name_item.data(Qt.UserRole) or name_item.text()
        self._selected_fief_name = fief_name
        self.show_fief_lineage(fief_name)

    def show_fief_lineage(self, fief_name):
        if not hasattr(self, "fief_lineage_tree"):
            return
        fiefs = {f["name"]: f for f in self.collect_fiefs()}
        fief = fiefs.get(fief_name)
        self.fief_lineage_tree.clear()
        if not fief:
            self.fief_detail_label.setText("封国不存在")
            return

        rank_label = self.get_rank_label(fief["rank"])
        full_title = (
            self.format_enfeoffed_title(fief_name, fief["rank"])
            if fief["rank"] else fief_name
        )
        current = fief["current"]
        current_txt = current.name if current else "—"
        status = "绝封" if fief["extinct"] else "存续"
        self.fief_detail_label.setText(
            f"{full_title}（{rank_label}）　·　国主 {current_txt}　·　"
            f"在世 {fief['alive_count']}/{fief['total_count']}　·　{status}"
        )

        # 世系：以最早受封者为根，展示其男系后裔；同封国者加标记
        root = self.find_fief_lineage_root(fief_name)
        if not root:
            return

        # 重建到内嵌树
        self.fief_lineage_tree.setUpdatesEnabled(False)
        self.fief_lineage_tree.clear()

        holders_ids = {h.id for h in fief["holders"]}

        def node_label(p):
            title_str = f" {p.title}" if p.title else ""
            mark = ""
            if p.is_alive and p.has_title and p.title_name == fief_name:
                mark = "◆ "
            elif p.id in holders_ids:
                mark = "· "
            return mark + p.name + title_str

        def status_of(p):
            s = "存活" if p.is_alive else "已故"
            if p.extinct:
                s += "·绝嗣"
            if p.is_heir:
                s += "·世子"
            if p.title_name == fief_name and p.has_title and p.is_alive:
                s += "·国主"
            return s

        def shimiao_of(p):
            if p.miaohao:
                return f"庙号 {p.miaohao}"
            return p.shihao or ""

        def add_node(parent_item, person, depth=0):
            # 只展示：本封国持有者，或其后裔中有本封国者（保持世系连通）
            item = QTreeWidgetItem(parent_item if parent_item is not None else self.fief_lineage_tree, [
                node_label(person),
                status_of(person),
                shimiao_of(person),
                str(person.generation),
            ])
            item.setData(0, Qt.UserRole, person.id)
            item.setExpanded(True)
            sons = []
            for cid in person.children:
                child = self.get_person_by_id(cid)
                if child and child.gender == "M":
                    sons.append(child)
            sons.sort(key=lambda c: (c.birth_year, c.id))
            for son in sons:
                add_node(item, son, depth + 1)

        add_node(None, root)
        self.fief_lineage_tree.setUpdatesEnabled(True)

    def show_person_detail_dialog(self, pid):
        person = self.get_person_by_id(pid)
        if not person:
            return

        dialog = QDialog(self)
        dialog.setWindowTitle(f"人物 · {person.name}")
        dialog.resize(720, 700)
        layout = QVBoxLayout()

        # —— 基本信息 ——
        info_section = QLabel("— 人 物 详 情 —")
        info_section.setObjectName("section_label")
        layout.addWidget(info_section)

        form = QFormLayout()
        form.addRow("姓名:", QLabel(person.name))
        form.addRow("年龄:", QLabel(str(person.age)))
        form.addRow("生卒:", QLabel(self.format_person_year(person)))
        form.addRow("状态:", QLabel("存活" if person.is_alive else "已故"))
        form.addRow("代数:", QLabel(str(person.generation)))
        form.addRow("字辈:", QLabel(self.get_zibei_char(person.generation) if self.zibei_poem else "—"))
        form.addRow("称号:", QLabel(person.title or "—"))
        form.addRow("国别:", QLabel(self.get_guobie(person)))
        form.addRow("封号:", QLabel(person.title_name or "—"))
        form.addRow("爵位:", QLabel(self.get_rank_label(person.title_rank) if person.title_rank else "—"))
        form.addRow("世子:", QLabel("是" if person.is_heir else "否"))
        form.addRow("在封:", QLabel("是" if person.has_title else "否"))
        form.addRow("能力:", QLabel(str(person.ability)))
        form.addRow("父亲:", QLabel(self.get_father_name(person)))
        form.addRow("子嗣:", QLabel(self.get_children_summary(person)))
        if person.miaohao:
            form.addRow("庙号:", QLabel(person.miaohao))
        if person.shihao:
            form.addRow("谥号:", QLabel(person.shihao))
        if person.zunhao:
            form.addRow("尊号:", QLabel(person.zunhao))
        if person.extinct:
            form.addRow("绝嗣:", QLabel("是"))
        if person.adopted_from is not None:
            adp = self.get_person_by_id(person.adopted_from)
            form.addRow("过继自:", QLabel(adp.name if adp else str(person.adopted_from)))
        layout.addLayout(form)

        # —— 家族树（图示：中心 ±2 代，可展开 / 全屏）——
        tree_section = QLabel("— 家 族 树（男系）—")
        tree_section.setObjectName("section_label")
        layout.addWidget(tree_section)

        chart_panel = LineageChartPanel(
            get_person_by_id=self.get_person_by_id,
            center_person=person,
            focus_id=person.id,
            current_emperor_pid=self.current_emperor_pid,
            compact=True,
        )
        chart_panel.personActivated.connect(self.show_person_detail_dialog)
        layout.addWidget(chart_panel, 1)

        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        dialog.setLayout(layout)
        dialog.exec()

    def show_family_tree_dialog(self, row, column):
        """兼容旧双击入口 → 人物详情。"""
        self.on_family_table_clicked(row, column)

    def show_end_game_dialog(self):

        self.dialog_emperor_list_table.setRowCount(0)
        for i, emp in enumerate(self.listjson):
            self.dialog_emperor_list_table.insertRow(i)
            self.dialog_emperor_list_table.setItem(i, 0, QTableWidgetItem(str(emp["id"])))
            self.dialog_emperor_list_table.setItem(i, 1, QTableWidgetItem(emp["miaohao"]))
            self.dialog_emperor_list_table.setItem(i, 2, QTableWidgetItem(emp["shihao"]))
            self.dialog_emperor_list_table.setItem(i, 3, QTableWidgetItem(emp["name"]))
            self.dialog_emperor_list_table.setItem(i, 4, QTableWidgetItem(str(emp["age"])))
            self.dialog_emperor_list_table.setItem(i, 5, QTableWidgetItem(emp["nianhao"]))
            self.dialog_emperor_list_table.setItem(i, 6, QTableWidgetItem(str(emp["jinian"])))
            self.dialog_emperor_list_table.setItem(i, 7, QTableWidgetItem(str(emp["ab"])))
            self.dialog_emperor_list_table.setItem(i, 8, QTableWidgetItem(emp["verdict"]))

        self.dialog_event_table.setRowCount(0)
        for i, ev in enumerate(self.event_happened[1:]):
            self.dialog_event_table.insertRow(i)
            self.dialog_event_table.setItem(i, 0, QTableWidgetItem(ev.get("time", "")))
            self.dialog_event_table.setItem(i, 1, QTableWidgetItem(ev.get("emperor", "")))
            self.dialog_event_table.setItem(i, 2, QTableWidgetItem(ev.get("event", "")))

        if self.auto_run:
            self.toggle_auto_run()

        self.end_game_dialog.exec()

    def setup_main_game_screen(self):
        layout = QVBoxLayout()




        self.tabs = QTabWidget()

        # Tab 1: 主界面 (Main Interface)
        self.tab1 = QWidget()
        tab1_layout = QVBoxLayout()
        tab1_layout.setContentsMargins(16, 12, 16, 12)

        # 朝代年号匾额
        self.reign_banner = QLabel("　　")
        self.reign_banner.setObjectName("reign_banner")
        tab1_layout.addWidget(self.reign_banner)

        self.basic_info_form = QFormLayout()
        self.dynasty_label = QLabel()
        self.emperor_label = QLabel()
        self.year_number_label = QLabel()
        self.jinian_label = QLabel()
        self.dynasty_st_label = QLabel()
        self.emperor_hp_label = QLabel()

        self.basic_info_form.addRow("朝代:", self.dynasty_label)
        self.basic_info_form.addRow("皇帝:", self.emperor_label)
        self.basic_info_form.addRow("年号:", self.year_number_label)
        self.basic_info_form.addRow("纪年:", self.jinian_label)
        self.basic_info_form.addRow("国势:", self.dynasty_st_label)
        self.basic_info_form.addRow("天寿:", self.emperor_hp_label)

        tab1_layout.addLayout(self.basic_info_form)

        # Event Table
        event_section = QLabel("— 天 下 纪 事 —")
        event_section.setObjectName("section_label")
        tab1_layout.addWidget(event_section)
        self.event_table = QTableWidget()
        self.event_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.event_table.setColumnCount(3)
        self.event_table.setHorizontalHeaderLabels(["时间", "皇帝", "事件"])
        self.event_table.verticalHeader().setVisible(False)
        self.event_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        tab1_layout.addWidget(self.event_table)

        # Sliders
        sliders_layout = QFormLayout()
        self.hardworking_slider = QSlider(Qt.Horizontal)
        self.hardworking_slider.setRange(0, 100)
        self.hardworking_slider.setValue(50)
        sliders_layout.addRow("勤政爱民:", self.hardworking_slider)

        self.amuse_slider = QSlider(Qt.Horizontal)
        self.amuse_slider.setRange(0, 100)
        self.amuse_slider.setValue(50)
        sliders_layout.addRow("声色犬马:", self.amuse_slider)

        tab1_layout.addLayout(sliders_layout)

        btn_layout = QHBoxLayout()
        self.auto_run_btn = QPushButton("自动运行")
        btn_layout.addWidget(self.auto_run_btn)
        self.export_prompt_btn = QPushButton("一键导出国史提示词")
        btn_layout.addWidget(self.export_prompt_btn)
        # 翻阅国史模式下替换上面两个按钮，平时隐藏
        self.restart_btn = QPushButton("重新开始")
        self.restart_btn.hide()
        btn_layout.addWidget(self.restart_btn)
        tab1_layout.addLayout(btn_layout)

        # Connect Signals for Tab 1
        self.hardworking_slider.valueChanged.connect(self.bchange)
        self.amuse_slider.valueChanged.connect(self.achange)
        self.auto_run_btn.clicked.connect(self.toggle_auto_run)
        self.export_prompt_btn.clicked.connect(self.show_history_prompt_dialog)
        self.restart_btn.clicked.connect(self.dio2)
        self.tab1.setLayout(tab1_layout)

        # Tab 2: 皇帝信息 (Emperor Info)
        self.tab2 = QWidget()
        tab2_layout = QVBoxLayout()

        self.emp_info_form = QFormLayout()
        self.emp_name_label = QLabel()
        self.emp_age_label = QLabel()
        self.emp_hp_label = QLabel()
        self.emp_ab_label = QLabel()
        self.emp_zunhao_label = QLabel()

        self.emp_info_form.addRow("姓名:", self.emp_name_label)
        self.emp_info_form.addRow("尊号:", self.emp_zunhao_label)
        self.emp_info_form.addRow("年龄:", self.emp_age_label)
        self.emp_info_form.addRow("天寿:", self.emp_hp_label)
        self.emp_info_form.addRow("治国手腕:", self.emp_ab_label)

        tab2_layout.addLayout(self.emp_info_form)
        self.tab2.setLayout(tab2_layout)

        # Tab 3: 王朝信息 (Dynasty Info)
        self.tab3 = QWidget()
        tab3_layout = QVBoxLayout()
        tab3_layout.setContentsMargins(16, 12, 16, 12)

        self.dyn_info_form = QFormLayout()
        self.dyn_name_label = QLabel()
        self.dyn_age_label = QLabel()
        self.dyn_st_label = QLabel()

        self.dyn_info_form.addRow("朝代:", self.dyn_name_label)
        self.dyn_info_form.addRow("王朝国祚:", self.dyn_age_label)
        self.dyn_info_form.addRow("天下大势:", self.dyn_st_label)

        tab3_layout.addLayout(self.dyn_info_form)

        self.fortune_chart_btn = QPushButton("查看国运图")
        self.fortune_chart_btn.clicked.connect(self.show_fortune_chart_dialog)
        fortune_btn_row = QHBoxLayout()
        fortune_btn_row.addWidget(self.fortune_chart_btn)
        fortune_btn_row.addStretch(1)
        tab3_layout.addLayout(fortune_btn_row)

        self.emperor_list_table = QTableWidget()
        self.emperor_list_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.emperor_list_table.setColumnCount(9)
        self.emperor_list_table.setHorizontalHeaderLabels(["序号", "庙号", "谥号", "姓名", "年龄", "年号", "纪年", "治国手腕", "史书评价"])
        self.emperor_list_table.verticalHeader().setVisible(False)
        emp_section = QLabel("— 历 代 帝 王 —")
        emp_section.setObjectName("section_label")
        tab3_layout.addWidget(emp_section)
        tab3_layout.addWidget(self.emperor_list_table)

        self.tab3.setLayout(tab3_layout)

        # Tab 4: 皇室宗亲 (Royal Family Info)
        self.tab4 = QWidget()
        tab4_layout = QVBoxLayout()
        tab4_layout.setContentsMargins(16, 12, 16, 12)

        # 显眼的皇室宗亲树状图（按国别分组）
        tree_section = QLabel("— 皇 室 宗 亲 世 系 —（单击人名查看详情）")
        tree_section.setObjectName("section_label")
        tab4_layout.addWidget(tree_section)
        self.family_tree_widget = QTreeWidget()
        self.family_tree_widget.setColumnCount(5)
        self.family_tree_widget.setHeaderLabels(["宗亲", "国别", "状态", "谥号 / 庙号", "代数"])
        self.family_tree_widget.setColumnWidth(0, 200)
        self.family_tree_widget.setColumnWidth(1, 80)
        self.family_tree_widget.setColumnWidth(2, 90)
        self.family_tree_widget.setColumnWidth(3, 180)
        self.family_tree_widget.setColumnWidth(4, 50)
        self.family_tree_widget.setAlternatingRowColors(True)
        tab4_layout.addWidget(self.family_tree_widget, 3)

        table_section = QLabel("— 宗 亲 录 —（单击姓名查看详情与家族树）")
        table_section.setObjectName("section_label")
        tab4_layout.addWidget(table_section)
        self.family_table = QTableWidget()
        self.family_table.setColumnCount(9)
        self.family_table.setHorizontalHeaderLabels(["ID", "姓名", "年龄", "称号", "国别", "状态", "谥号", "代数", "绝嗣"])
        self.family_table.verticalHeader().setVisible(False)
        self.family_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.family_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        tab4_layout.addWidget(self.family_table, 2)
        self.tab4.setLayout(tab4_layout)

        self.family_table.cellClicked.connect(self.on_family_table_clicked)
        self.family_table.cellDoubleClicked.connect(self.show_family_tree_dialog)
        self.family_tree_widget.itemClicked.connect(self.on_family_tree_item_clicked)

        # Tab 5: 宗藩（左侧精简列表 + 右侧世系主区）
        self.tab5 = QWidget()
        tab5_layout = QVBoxLayout()
        tab5_layout.setContentsMargins(10, 8, 10, 8)
        tab5_layout.setSpacing(6)

        fief_header = QHBoxLayout()
        fief_header.setContentsMargins(0, 0, 0, 0)
        fief_title = QLabel("宗藩")
        fief_title.setObjectName("fief_title")
        self.fief_count_label = QLabel("")
        self.fief_count_label.setObjectName("fief_count_label")
        fief_header.addWidget(fief_title)
        fief_header.addStretch(1)
        fief_header.addWidget(self.fief_count_label)
        tab5_layout.addLayout(fief_header)

        fief_splitter = QSplitter(Qt.Horizontal)
        fief_splitter.setObjectName("fief_splitter")
        fief_splitter.setChildrenCollapsible(False)
        fief_splitter.setHandleWidth(4)

        left_fief = QWidget()
        left_fief.setObjectName("fief_list_panel")
        left_fief.setMaximumWidth(300)
        left_fief.setMinimumWidth(200)
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(4)
        left_hint = QLabel("封国一览")
        left_hint.setObjectName("fief_panel_caption")
        left_layout.addWidget(left_hint)
        self.fief_table = QTableWidget()
        self.fief_table.setObjectName("fief_table")
        self.fief_table.setColumnCount(4)
        self.fief_table.setHorizontalHeaderLabels(["封国", "爵", "国主", "态"])
        self.fief_table.verticalHeader().setVisible(False)
        self.fief_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.fief_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.fief_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.fief_table.setShowGrid(False)
        self.fief_table.setAlternatingRowColors(True)
        self.fief_table.setWordWrap(False)
        self.fief_table.horizontalHeader().setStretchLastSection(False)
        self.fief_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.fief_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.fief_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.fief_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.fief_table.verticalHeader().setDefaultSectionSize(26)
        left_layout.addWidget(self.fief_table)
        left_fief.setLayout(left_layout)

        right_fief = QWidget()
        right_fief.setObjectName("fief_lineage_panel")
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(4)

        self.fief_detail_label = QLabel("点选左侧封国，查看该支世系")
        self.fief_detail_label.setObjectName("fief_detail_banner")
        self.fief_detail_label.setWordWrap(True)
        right_layout.addWidget(self.fief_detail_label)

        lineage_hint = QLabel("◆ 现任国主　　· 本封成员　　双击人名查看详情")
        lineage_hint.setObjectName("fief_lineage_hint")
        right_layout.addWidget(lineage_hint)

        self.fief_lineage_tree = QTreeWidget()
        self.fief_lineage_tree.setObjectName("fief_lineage_tree")
        self.fief_lineage_tree.setColumnCount(4)
        self.fief_lineage_tree.setHeaderLabels(["姓名 / 称号", "状态", "谥号", "代数"])
        self.fief_lineage_tree.setColumnWidth(0, 240)
        self.fief_lineage_tree.setColumnWidth(1, 88)
        self.fief_lineage_tree.setColumnWidth(2, 130)
        self.fief_lineage_tree.setColumnWidth(3, 48)
        self.fief_lineage_tree.setAlternatingRowColors(True)
        self.fief_lineage_tree.setUniformRowHeights(True)
        self.fief_lineage_tree.itemDoubleClicked.connect(self.on_lineage_tree_person_clicked)
        right_layout.addWidget(self.fief_lineage_tree, 1)
        right_fief.setLayout(right_layout)

        fief_splitter.addWidget(left_fief)
        fief_splitter.addWidget(right_fief)
        fief_splitter.setStretchFactor(0, 0)
        fief_splitter.setStretchFactor(1, 1)
        fief_splitter.setSizes([240, 720])
        tab5_layout.addWidget(fief_splitter, 1)
        self.tab5.setLayout(tab5_layout)
        self._selected_fief_name = None
        self.fief_table.cellClicked.connect(self.on_fief_table_clicked)

        # Add tabs
        self.tabs.addTab(self.tab1, "主界面")
        self.tabs.addTab(self.tab2, "皇帝信息")
        self.tabs.addTab(self.tab3, "王朝信息")
        self.tabs.addTab(self.tab4, "皇室宗亲")
        self.tabs.addTab(self.tab5, "宗藩")
        self.tabs.currentChanged.connect(self.on_main_tab_changed)

        layout.addWidget(self.tabs)
        self.main_game_screen.setLayout(layout)

    def show_fortune_chart_dialog(self):
        """弹出王朝国运折线图（标注在位皇帝与年号）。"""
        history = getattr(self, "dynasty_hp_history", None) or []
        dialog = FortuneChartDialog(history, self.dynasty, self)
        dialog.exec()

    def show_history_prompt_dialog(self):
        """据本局模拟结果生成国史写作提示词，供预览与一键复制到剪贴板。"""
        prompt_text = self.build_history_prompt()

        dialog = QDialog(self)
        dialog.setWindowTitle("国史提示词 · 可复制到 AI")
        dialog.resize(720, 640)
        layout = QVBoxLayout()

        hint = QLabel("将下面的提示词复制到任意 AI 对话（如 ChatGPT、Claude、豆包等），即可生成一部完整国史。")
        hint.setObjectName("section_label")
        hint.setWordWrap(True)
        layout.addWidget(hint)

        text_edit = QPlainTextEdit()
        text_edit.setPlainText(prompt_text)
        text_edit.setReadOnly(True)
        layout.addWidget(text_edit, 1)

        btn_row = QHBoxLayout()
        copy_btn = QPushButton("复制到剪贴板")
        close_btn = QPushButton("关闭")
        btn_row.addWidget(copy_btn)
        btn_row.addStretch(1)
        btn_row.addWidget(close_btn)
        layout.addLayout(btn_row)

        def do_copy():
            clipboard = QApplication.clipboard()
            clipboard.setText(prompt_text)
            copy_btn.setText("已复制 ✓")
            QTimer.singleShot(1500, lambda: copy_btn.setText("复制到剪贴板"))

        copy_btn.clicked.connect(do_copy)
        close_btn.clicked.connect(dialog.accept)

        dialog.setLayout(layout)
        dialog.exec()

    def on_main_tab_changed(self, index):
        """切到宗亲/宗藩时立即刷新，避免因节流看到过期数据。"""
        if index in (3, 4) and self.ongame and self.people:
            self.update_ui()

    def toggle_auto_run(self):
        self.auto_run = not self.auto_run
        if self.auto_run:
            self.auto_run_btn.setText("停止运行")
            # 人物多时拉长步进间隔，减轻卡顿
            interval = 800 if len(self.people) > 120 else 500
            self.timer.start(interval)
        else:
            self.auto_run_btn.setText("自动运行")
            self.timer.stop()

    def auto_run_step(self):
        if self.ongame:
            self.gamemin()
            if self.auto_run:
                n = len(self.people)
                self.timer.setInterval(900 if n > 150 else (700 if n > 100 else 500))
