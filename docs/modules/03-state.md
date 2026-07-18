# state.py — 一局游戏状态

**路径：** `dynasty/state.py`  
**类：** `GameStateMixin`  
**职责：** `init_game_state()` 初始化（或重置前的默认）全部运行时变量。

---

## 1. 人物与皇位指针

| 变量 | 含义 |
|------|------|
| `people` | `Person` 列表 |
| `next_pid` | 下一个可用人物 ID |
| `current_emperor_pid` | 今上 ID |
| `next_emperor_pid` | 预定储君/继位者 ID |

---

## 2. 游戏开关与皇帝/国祚数值

| 变量 | 含义 |
|------|------|
| `ongame` | 是否允许继续推进一年（换代/亡国时暂 False） |
| `emperor_die` / `dynasty_die` | 驾崩/亡国标志 |
| `emperor_id` | 第几位皇帝（从 1 起） |
| `emperor_age` / `emperor_hp` / `emperor_ab` | 年龄、天寿、治国手腕 |
| `dynasty_age` / `dynasty_hp` / `dynasty_st` | 国祚年数、国运值、天下大势文案 |
| `jinian` | 当前年号下第几年（元年 = 1） |
| `dynasty` / `emperor` / `yearNumber` | 朝名、帝名、年号字符串 |
| `emperor_zunhao` | 当前尊号 |
| `amuse` / `hardworking` | 声色 / 勤政（滑块，和为 100） |
| `year` | 全局游戏年计数 |
| `listjson` | 已故/卸任皇帝史书记录列表 |
| `current_emperor_nianhao_history` | 本帝各年号段及年数 |
| `dynasty_hp_history` | 逐年国运轨迹（年份/国运/在位皇帝/年号），供王朝国运图 |
| `initial_dynasty_hp` | 本帝登基时国祚快照 |
| `reign_peak_dynasty_hp` | 本帝在位期间国运峰值 |
| `reign_trough_dynasty_hp` | 本帝在位期间国运谷值 |

---

## 3. 去重与词库引用

| 变量 | 含义 |
|------|------|
| `dynasty_name` | 可选朝代名 |
| `yearNumber_list` | 历史年号名列表（来自 `nianhao_data.NIANHAO_NAMES`） |
| `used_shihao` / `used_miaohao` | 已用谥号、庙号 |
| `used_emperor_names` / `used_person_names` | 已用帝名、人名 |
| `used_nianhao` | 已用年号（仅确认登基/改元时登记） |

并调用 `init_tang_resources()` 加载资源。年号结构化数据见 `dynasty/nianhao_data.py`。

---

## 4. 事件系统初值

| 变量 | 含义 |
|------|------|
| `event_id` | 当前抽中的事件下标 |
| `event_happened` | 纪事列表（首项占位空事件） |
| `event_list` | 事件模板：文案 + 对皇帝 hp / 国祚的增减 |
| `data_emperor_hp_change` / `data_dynasty_hp_change` | 本年度事件结算值 |
| `d_time` / `d_event` / `d_event_id` | 展示用当前事件快照 |

---

## 5. 注意

- **重开一局**主要在 `gamemin_dynasty_new`（`dynasty_logic`）里清空，并不整段重跑 `init_game_state`；两者字段应保持语义一致。  
- 改事件平衡：优先编辑本文件中的 `event_list` 条目数值。  
- 状态与 UI 控件是分离的：状态在 mixins 改，显示靠 `update_ui` 读这些字段。
