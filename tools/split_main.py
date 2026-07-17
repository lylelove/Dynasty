# -*- coding: utf-8 -*-
"""One-shot splitter: extract DynastyApp methods from main.py into package modules."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = (ROOT / "main.py").read_text(encoding="utf-8")
LINES = SRC.splitlines(keepends=True)


def slice_lines(start: int, end: int) -> str:
    """1-based inclusive line slice, re-indent class methods to module-level class body."""
    chunk = LINES[start - 1 : end]
    return "".join(chunk)


def dedent_methods(text: str, spaces: int = 4) -> str:
    out = []
    prefix = " " * spaces
    for line in text.splitlines(keepends=True):
        if line.startswith(prefix):
            out.append(line[spaces:])
        else:
            out.append(line)
    return "".join(out)


def method_block(name: str, start: int, end: int) -> str:
    # Keep original 4-space class-method indent so bodies sit under the new class.
    return slice_lines(start, end)


# method_name -> (start, end) from AST dump
METHODS = {
    "__init__": (47, 81),
    "init_game_state": (83, 160),
    "init_tang_resources": (162, 344),
    "reset_tang_pools": (346, 352),
    "setup_dialogs": (354, 429),
    "new_emp_confirm": (431, 434),
    "apply_stylesheet": (436, 630),
    "setup_start_screen": (632, 693),
    "start_game_from_ui": (695, 700),
    "achange": (702, 705),
    "bchange": (707, 710),
    "gamestart": (712, 742),
    "start_new_emperor_nianhao_history": (744, 748),
    "record_current_year_for_nianhao": (750, 762),
    "begin_next_nianhao_segment": (764, 770),
    "build_nianhao_summary": (772, 782),
    "gamemin": (784, 794),
    "get_person_by_id": (796, 800),
    "gamemin_family_aging_death": (802, 809),
    "get_descendants": (811, 818),
    "check_extinct": (820, 834),
    "find_adoptee": (836, 856),
    "get_rank_suffix": (858, 859),
    "get_guobie": (861, 868),
    "get_rank_label": (870, 873),
    "format_person_year": (875, 878),
    "get_father_name": (880, 884),
    "get_spouse_name": (886, 891),
    "get_children_summary": (893, 900),
    "collect_fiefs": (902, 938),
    "find_fief_lineage_root": (940, 946),
    "is_name_used": (948, 949),
    "register_person_name": (951, 953),
    "choose_dynasty_surname": (955, 957),
    "infer_surname_from_name": (959, 963),
    "get_zibei_char": (965, 971),
    "generate_given_name": (973, 1001),
    "generate_zunhao": (1003, 1009),
    "generate_full_name": (1011, 1039),
    "draw_title_name": (1041, 1049),
    "draw_female_title_name": (1051, 1059),
    "get_princess_tier": (1061, 1070),
    "ensure_female_title_name": (1072, 1075),
    "format_alive_title": (1077, 1093),
    "get_heir_posthumous_suffix": (1095, 1108),
    "choose_family_posthumous_word": (1110, 1155),
    "build_family_posthumous_title": (1157, 1177),
    "gamemin_family_shihao_titles": (1179, 1234),
    "get_random_name": (1236, 1244),
    "try_spawn_child": (1246, 1273),
    "gamemin_family_marriage_birth": (1275, 1324),
    "get_sons_by_birth": (1326, 1336),
    "get_eldest_living_son": (1338, 1340),
    "find_heir_of_line": (1342, 1353),
    "update_heirs": (1355, 1364),
    "update_crown_prince": (1366, 1395),
    "find_collateral_successor": (1397, 1450),
    "find_successor": (1452, 1466),
    "gamemin_dynasty": (1468, 1489),
    "gamemin_emperor": (1491, 1543),
    "gamemin_shihao": (1545, 1646),
    "_record_emperor": (1648, 1662),
    "gamemin_emperor_change": (1664, 1665),
    "gamemin_emperor_new": (1667, 1700),
    "gamemin_dynasty_change": (1702, 1703),
    "gamemin_dynasty_new": (1705, 1724),
    "dio": (1726, 1733),
    "dio2": (1735, 1749),
    "dynasty_change_name": (1751, 1753),
    "zibei_change_poem": (1755, 1762),
    "emperor_change_name": (1764, 1775),
    "emperor_new_hp": (1777, 1784),
    "emperor_new_age": (1786, 1788),
    "get_unique_nianhao": (1790, 1800),
    "yearNumber_change_name": (1802, 1804),
    "dialog_yearNumber_change_name": (1806, 1809),
    "emperor_change_name_after": (1811, 1826),
    "dynasty_function_st": (1828, 1859),
    "event_happen": (1861, 1889),
    "event_id_chose": (1891, 1892),
    "event_change": (1894, 1904),
    "update_ui": (1906, 1984),
    "update_family_tree": (1986, 2054),
    "update_fief_list": (2056, 2090),
    "build_lineage_tree_widget": (2092, 2162),
    "on_lineage_tree_person_clicked": (2164, 2168),
    "on_family_tree_item_clicked": (2170, 2174),
    "on_family_table_clicked": (2176, 2184),
    "on_fief_table_clicked": (2186, 2192),
    "show_fief_lineage": (2194, 2268),
    "show_person_detail_dialog": (2270, 2336),
    "show_new_emp_dialog": (2338, 2359),
    "show_family_tree_dialog": (2361, 2363),
    "show_end_game_dialog": (2365, 2389),
    "setup_main_game_screen": (2391, 2611),
    "toggle_auto_run": (2613, 2620),
    "auto_run_step": (2622, 2624),
}

GROUPS = {
    "resources": {
        "file": "dynasty/resources.py",
        "class": "ResourcesMixin",
        "doc": "姓氏、字辈、名库、爵位/封号池、庙号谥号池等静态资源初始化。",
        "methods": ["init_tang_resources", "reset_tang_pools"],
        "imports": "import random\n",
    },
    "state": {
        "file": "dynasty/state.py",
        "class": "GameStateMixin",
        "doc": "一局游戏的运行时状态初始化（人物列表、国祚、事件、已用名号等）。",
        "methods": ["init_game_state"],
        "imports": "",
    },
    "styles": {
        "file": "dynasty/styles.py",
        "class": "StylesMixin",
        "doc": "古风主题 QSS 样式（宣纸底、朱漆金边）。",
        "methods": ["apply_stylesheet"],
        "imports": "from PySide6.QtWidgets import QApplication\n",
    },
    "naming": {
        "file": "dynasty/mixins/naming.py",
        "class": "NamingMixin",
        "doc": "姓名/字辈/年号/尊号生成与去重；开局与登基时的随机取名。",
        "methods": [
            "is_name_used", "register_person_name", "choose_dynasty_surname",
            "infer_surname_from_name", "get_zibei_char", "generate_given_name",
            "generate_zunhao", "generate_full_name", "get_random_name",
            "dynasty_change_name", "zibei_change_poem", "emperor_change_name",
            "get_unique_nianhao", "yearNumber_change_name",
            "dialog_yearNumber_change_name", "emperor_change_name_after",
        ],
        "imports": "import random\n",
    },
    "titles": {
        "file": "dynasty/mixins/titles.py",
        "class": "TitlesMixin",
        "doc": "爵位/封号抽取、在世称号格式化、宗室谥号与封爵继承。",
        "methods": [
            "get_rank_suffix", "get_guobie", "get_rank_label",
            "draw_title_name", "draw_female_title_name", "get_princess_tier",
            "ensure_female_title_name", "format_alive_title",
            "get_heir_posthumous_suffix", "choose_family_posthumous_word",
            "build_family_posthumous_title", "gamemin_family_shihao_titles",
        ],
        "imports": "import random\n",
    },
    "family": {
        "file": "dynasty/mixins/family.py",
        "class": "FamilyMixin",
        "doc": "宗室人物查询、衰老死亡、婚育、过继、封国汇总。",
        "methods": [
            "get_person_by_id", "gamemin_family_aging_death", "get_descendants",
            "check_extinct", "find_adoptee", "format_person_year",
            "get_father_name", "get_spouse_name", "get_children_summary",
            "collect_fiefs", "find_fief_lineage_root",
            "try_spawn_child", "gamemin_family_marriage_birth",
        ],
        "imports": "import random\nfrom dynasty.models import Person\n",
    },
    "succession": {
        "file": "dynasty/mixins/succession.py",
        "class": "SuccessionMixin",
        "doc": "嫡长继承、代位、储君、兄终弟及与皇位继承人查找。",
        "methods": [
            "get_sons_by_birth", "get_eldest_living_son", "find_heir_of_line",
            "update_heirs", "update_crown_prince", "find_collateral_successor",
            "find_successor",
        ],
        "imports": "",
    },
    "events": {
        "file": "dynasty/mixins/events.py",
        "class": "EventsMixin",
        "doc": "年度随机事件抽取、国祚/天寿影响与改元。",
        "methods": ["event_happen", "event_id_chose", "event_change"],
        "imports": "import random\n",
    },
    "emperor": {
        "file": "dynasty/mixins/emperor.py",
        "class": "EmperorMixin",
        "doc": "皇帝年岁与驾崩、庙号谥号史评、年号纪年、新君登基。",
        "methods": [
            "start_new_emperor_nianhao_history", "record_current_year_for_nianhao",
            "begin_next_nianhao_segment", "build_nianhao_summary",
            "gamemin_emperor", "gamemin_shihao", "_record_emperor",
            "gamemin_emperor_change", "gamemin_emperor_new",
            "emperor_new_hp", "emperor_new_age", "dio",
        ],
        "imports": "import math\nimport random\nfrom dynasty.models import roll_ability\n",
    },
    "dynasty_logic": {
        "file": "dynasty/mixins/dynasty_logic.py",
        "class": "DynastyLogicMixin",
        "doc": "国祚结算、天下大势文案、开局与王朝覆灭重置。",
        "methods": [
            "gamestart", "gamemin_dynasty", "gamemin_dynasty_change",
            "gamemin_dynasty_new", "dynasty_function_st", "dio2",
        ],
        "imports": "import math\nimport random\nfrom dynasty.models import Person\n",
    },
    "ui": {
        "file": "dynasty/app.py",
        "class": "DynastyApp",
        "doc": "主窗口、各界面 Tab、对话框与 UI 刷新；编排年度循环。",
        "methods": [
            "__init__", "setup_dialogs", "new_emp_confirm",
            "setup_start_screen", "start_game_from_ui", "achange", "bchange",
            "gamemin", "update_ui", "update_family_tree", "update_fief_list",
            "build_lineage_tree_widget", "on_lineage_tree_person_clicked",
            "on_family_tree_item_clicked", "on_family_table_clicked",
            "on_fief_table_clicked", "show_fief_lineage",
            "show_person_detail_dialog", "show_new_emp_dialog",
            "show_family_tree_dialog", "show_end_game_dialog",
            "setup_main_game_screen", "toggle_auto_run", "auto_run_step",
        ],
        "imports": None,  # special
    },
}


def write_mixin(group_key: str, meta: dict) -> None:
    body_parts = []
    for m in meta["methods"]:
        s, e = METHODS[m]
        body_parts.append(method_block(m, s, e).rstrip() + "\n\n")
    body = "".join(body_parts).rstrip() + "\n"

    path = ROOT / meta["file"]
    path.parent.mkdir(parents=True, exist_ok=True)

    if group_key == "ui":
        content = f'''# -*- coding: utf-8 -*-
"""{meta["doc"]}"""
from PySide6.QtWidgets import (
    QMainWindow, QStackedWidget, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QLineEdit, QPushButton, QFormLayout, QDialog,
    QHeaderView, QTabWidget, QTableWidget, QSlider, QTableWidgetItem,
    QTreeWidget, QTreeWidgetItem, QComboBox, QSplitter, QAbstractItemView
)
from PySide6.QtCore import Qt, QTimer

from dynasty.mixins.dynasty_logic import DynastyLogicMixin
from dynasty.mixins.emperor import EmperorMixin
from dynasty.mixins.events import EventsMixin
from dynasty.mixins.family import FamilyMixin
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
    QMainWindow,
):
    """王朝模拟主窗口：组合各功能 Mixin，负责界面与年度主循环编排。"""

{body}
'''
    else:
        content = f'''# -*- coding: utf-8 -*-
"""{meta["doc"]}"""
{meta["imports"]}

class {meta["class"]}:
    """{meta["doc"]}"""

{body}
'''
    path.write_text(content, encoding="utf-8")
    print(f"wrote {path.relative_to(ROOT)} ({len(meta['methods'])} methods)")


def write_models() -> None:
    person = dedent_methods(slice_lines(18, 43))  # class Person
    # Person is already a class at indent 0... wait it's at indent 0 in file
    person = slice_lines(18, 43)
    roll = slice_lines(13, 15)
    content = f'''# -*- coding: utf-8 -*-
"""核心数据模型：人物 Person 与能力掷骰。"""
import math
import random


{roll}

{person}
'''
    path = ROOT / "dynasty" / "models.py"
    path.write_text(content, encoding="utf-8")
    print("wrote dynasty/models.py")


def write_package_inits() -> None:
    (ROOT / "dynasty" / "__init__.py").write_text(
        '''# -*- coding: utf-8 -*-
"""王朝（Dynasty）游戏包：按功能拆分的 PySide6 桌面模拟。"""
from dynasty.app import DynastyApp
from dynasty.models import Person, roll_ability

__all__ = ["DynastyApp", "Person", "roll_ability"]
''',
        encoding="utf-8",
    )
    (ROOT / "dynasty" / "mixins" / "__init__.py").write_text(
        '''# -*- coding: utf-8 -*-
"""游戏逻辑 Mixin 集合（命名、爵位、宗室、继承、事件、皇帝、国祚）。"""
''',
        encoding="utf-8",
    )
    print("wrote package __init__ files")


def write_main() -> None:
    content = '''# -*- coding: utf-8 -*-
"""王朝 V0.18 入口：启动 PySide6 主窗口。

详细模块说明见 docs/modules/。
"""
import sys

from PySide6.QtWidgets import QApplication

from dynasty import DynastyApp


def main():
    app = QApplication(sys.argv)
    window = DynastyApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
'''
    (ROOT / "main.py").write_text(content, encoding="utf-8")
    print("wrote main.py entry")


def main() -> None:
    write_models()
    for key, meta in GROUPS.items():
        write_mixin(key, meta)
    write_package_inits()
    write_main()
    print("done")


if __name__ == "__main__":
    main()
