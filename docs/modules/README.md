# 模块说明总览

本文档说明如何将原先单体 `main.py`（约 2600 行）按功能拆分为 `dynasty` 包。  
**行为与 V0.18 逻辑保持一致**，仅做结构重组，便于阅读与维护。

## 目录结构

```
Dynasty/
├── main.py                 # 程序入口（极薄）
├── test_run.py             # 无界面冒烟测试
├── dynasty/                # 游戏主包
│   ├── __init__.py         # 对外导出 DynastyApp / Person
│   ├── models.py           # 数据模型 Person、roll_ability
│   ├── resources.py        # 姓名/爵位/庙谥等静态资源
│   ├── state.py            # 一局游戏运行时状态
│   ├── styles.py           # 古风 QSS 主题
│   ├── app.py              # 主窗口 UI + 年度循环编排
│   └── mixins/             # 按领域拆分的逻辑 Mixin
│       ├── naming.py       # 姓名、字辈、年号、尊号
│       ├── titles.py       # 爵位、封号、宗室谥号
│       ├── family.py       # 宗室、婚育、过继、封国
│       ├── succession.py   # 嫡长继承、储君、皇位继承
│       ├── events.py       # 年度随机事件
│       ├── emperor.py      # 皇帝寿命、庙谥、登基
│       └── dynasty_logic.py# 国祚、开局、覆灭重置
└── docs/modules/           # 本说明目录（各文件详见下文）
```

## 设计原则

1. **按职责拆分，不按“文件大小”硬切**  
   例如“取名”与“继承法”分开，避免改名时误伤继承逻辑。

2. **Mixin 组合，主类只做编排**  
   `DynastyApp` 多重继承各 Mixin + `QMainWindow`，自身负责：
   - 界面搭建与信号连接  
   - `gamemin()` 年度主循环顺序  
   - 表格/树刷新与对话框展示  

3. **数据与逻辑分离**  
   - `Person`：纯数据对象  
   - `resources`：词库与池子  
   - `state`：本局变量  
   - mixins：规则与演算  

4. **依赖方向（推荐心智模型）**

```
main.py
   └── app.DynastyApp
          ├── UI 控件 / update_ui
          ├── mixins.* （规则）
          ├── state / resources / styles
          └── models.Person
```

## 年度主循环（`gamemin`）

每点一次「继续」（或自动运行一步）依次执行：

| 顺序 | 调用 | 所在模块 | 作用 |
|------|------|----------|------|
| 1 | `year += 1` | app | 推进游戏年 |
| 2 | `event_happen` | events | 随机事件（记尊号），改国祚/天寿，可能改元 |
| 3 | `gamemin_family_aging_death` | family | 宗室（非今上）衰老、死亡 |
| 4 | `gamemin_emperor` | emperor | 皇帝年龄/天寿；驾崩则庙谥与**自动登基** |
| 5 | `gamemin_dynasty` | dynasty_logic | 国祚结算；归零则亡国 |
| 6 | `gamemin_family_marriage_birth` | family | 婚配与生育 |
| 7 | `update_crown_prince` | succession | 嫡长/代位 → 太子与世子 |
| 8 | `gamemin_family_shihao_titles` | titles | 成年授爵、谥号、封爵继承/过继 |
| 9 | `dynasty_function_st` | dynasty_logic | 天下大势文案 |
| 10 | `update_ui` | app | 刷新全部界面 |

主界面仅「自动运行」推进年份（无「继续」按钮）；换代无弹窗。

## 各模块文档索引

| 文档 | 对应源码 | 一句话 |
|------|----------|--------|
| [01-models.md](./01-models.md) | `dynasty/models.py` | 人物实体与能力掷骰 |
| [02-resources.md](./02-resources.md) | `dynasty/resources.py` | 词库与封号/庙谥资源池 |
| [03-state.md](./03-state.md) | `dynasty/state.py` | 本局状态变量 |
| [04-styles.md](./04-styles.md) | `dynasty/styles.py` | 古风主题样式 |
| [05-naming.md](./05-naming.md) | `mixins/naming.py` | 姓名字辈年号尊号 |
| [06-titles.md](./06-titles.md) | `mixins/titles.py` | 爵位封号宗室谥号 |
| [07-family.md](./07-family.md) | `mixins/family.py` | 宗室婚育过继封国 |
| [08-succession.md](./08-succession.md) | `mixins/succession.py` | 继承法与储君 |
| [09-events.md](./09-events.md) | `mixins/events.py` | 随机事件与改元 |
| [10-emperor.md](./10-emperor.md) | `mixins/emperor.py` | 皇帝与登基 |
| [11-dynasty-logic.md](./11-dynasty-logic.md) | `mixins/dynasty_logic.py` | 国祚与开局/重开 |
| [12-app.md](./12-app.md) | `dynasty/app.py` | 主窗口与 UI |
| [13-history-prompt.md](./13-history-prompt.md) | `mixins/history_prompt.py` | AI 国史提示词生成 |

## 入口与兼容

- 运行游戏：`python main.py`（与原先相同）  
- 包导入：`from dynasty import DynastyApp`  
- 兼容：`from main import DynastyApp` 仍可用（入口文件 re-export）  

## 修改指南（常见需求）

| 想改什么 | 去哪里 |
|----------|--------|
| 生育率 / 成婚率 | `mixins/family.py` → `gamemin_family_marriage_birth` |
| 国祚衰减公式 | `mixins/dynasty_logic.py` → `gamemin_dynasty` |
| 事件文案与数值 | `state.py` 中 `event_list` |
| 姓名字库 / 字辈诗 | `resources.py` → `init_tang_resources` |
| 爵位等级与封号名 | `resources.py` 明制八等 + `mixins/titles.py` 命名 |
| 庙号谥号规则 | `mixins/emperor.py` → `gamemin_shihao` |
| 界面布局 / 新 Tab | `app.py` → `setup_main_game_screen` |
| 主题颜色 | `styles.py` → `apply_stylesheet` |
