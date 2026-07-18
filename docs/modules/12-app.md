# app.py — 主窗口与界面

**路径：** `dynasty/app.py`  
**类：** `DynastyApp`  
**职责：** PySide6 主窗口；组合全部 Mixin；搭建界面；编排 `gamemin`；刷新表格/树与对话框。

---

## 1. 类继承顺序

```text
DynastyApp(
  ResourcesMixin, GameStateMixin, StylesMixin,
  NamingMixin, TitlesMixin, FamilyMixin, SuccessionMixin,
  EventsMixin, EmperorMixin, DynastyLogicMixin,
  QMainWindow,
)
```

MRO 保证：业务方法来自各 Mixin；窗口基类为 `QMainWindow`。  
`super().__init__()` 初始化 Qt 窗口。

---

## 2. `__init__` 启动顺序

1. `init_game_state`（含资源）  
2. `QStackedWidget`：开始页 / 主游戏页  
3. `setup_start_screen` / `setup_main_game_screen`  
4. `setup_dialogs`（新皇、结束）  
5. `apply_stylesheet`  
6. `QTimer` 绑定 `auto_run_step`  

---

## 3. 界面结构

### 开始页

- 朝代 / 皇帝 / 年号 / 字辈（可刷新）  
- 「开始游戏」→ `start_game_from_ui` → `gamestart`  

### 主界面 Tab

| Tab | 内容 |
|-----|------|
| 主界面 | 匾额、基本信息、天下纪事表、勤政/声色滑块、继续、自动运行 |
| 皇帝信息 | 姓名、尊号、年龄、天寿、治国手腕 |
| 王朝信息 | 国祚、大势、「查看国运图」按钮（弹出逐年国运折线图，标注在位皇帝与年号）、历代帝王表 |
| 皇室宗亲 | 父系世系树 + 宗亲表（点击详情） |
| 宗藩 | 封国表 + 选中封国世系树 |

### 对话框

- **新皇登基**：姓名/年号（有储君则姓名只读）  
- **结束**：历代皇帝 + 王朝纪事，确认后重开  
- **人物详情**：字段表 + 男系世系图（卡片节点 / 父子连线）  
- **国运图**：`FortuneChartDialog`（`fortune_chart.py`）——逐年国运折线，顶部标在位皇帝分段、底部标年号更迭（▲），悬浮查看单年数值；数据来自 `dynasty_hp_history`（`dynasty_logic.record_dynasty_hp_history`）  

自动运行时：新皇对话框自动刷新并确认；结束时会停自动运行。

---

## 4. 年度编排：`gamemin`

见 [总览 README](./README.md#年度主循环gamemin)。  
**只在本类定义顺序**；具体规则在对应 mixin。

---

## 5. UI 刷新要点

| 方法 | 作用 |
|------|------|
| `update_ui` | 刷新 Tab1～3 标签与表；调树与宗藩 |
| `update_family_tree` | 男系完整父系树（开国为根）；人物行背景浅色（见 styles） |
| `update_fief_list` / `show_fief_lineage` | 宗藩列表与右侧世系（人物行浅色底） |
| `build_lineage_tree_widget` | QTreeWidget 世系树（宗藩等仍用） |
| `LineageChartPanel` | 人物详情世系图：中心±2代、⊕展开、全屏；卡片底均为浅色（`lineage_chart.py`） |
| `show_person_detail_dialog` | 人物弹窗 |
| `toggle_auto_run` / `auto_run_step` | 500ms 一步，仅 `ongame` 时推进 |

滑块：`achange` / `bchange` 使勤政与声色互补为 100。

---

## 6. 入口

```text
main.py → DynastyApp → show → app.exec()
```

测试：`test_run.py` stub 掉阻塞对话框后循环 `gamemin`。

---

## 7. 加功能时放哪里

| 需求 | 位置 |
|------|------|
| 新按钮/新 Tab | 本文件 `setup_*` |
| 新规则数值 | 对应 mixin，不要塞进 `update_ui` |
| 新全局变量 | `state.init_game_state`（及重开清理） |
| 新词库 | `resources` |
