# emperor.py — 皇帝寿命、庙谥、登基

**路径：** `dynasty/mixins/emperor.py`  
**类：** `EmperorMixin`  
**职责：** 年号纪年记录、皇帝每年老化与驾崩、**按在位全程功绩**认定庙号谥号史评、新君数值继承、登基确认。

---

## 1. 年号段历史

| 方法 | 作用 |
|------|------|
| `start_new_emperor_nianhao_history` | 新帝开始时初始化段列表 |
| `record_current_year_for_nianhao` | 每年给当前年号段 `years+1` |
| `begin_next_nianhao_segment` | 改元时开新段 |
| `build_nianhao_summary` | 史书展示如「贞观23年、永徽5年」 |

---

## 2. 年度：`gamemin_emperor`

国祚仍 >0 时：

- 若天寿 >0：年龄+1、纪年+1、天寿-1，同步到今上 `Person`  
- 若天寿 ≤0：  
  1. 标记人物死亡  
  2. `gamemin_shihao` 生成庙号/谥号/史评，写回 Person  
  3. `_record_emperor` 入 `listjson`（经 `gamemin_emperor_change`）  
  4. `find_successor`：  
     - 无 → 亡国 + 结束对话框  
     - 有 → 收回继位者私封，自动登基  

---

## 3. 在位国运轨迹

| 方法 / 状态 | 作用 |
|-------------|------|
| `initial_dynasty_hp` | 登基时国祚快照 |
| `reign_peak_dynasty_hp` | 在位期间国运峰值 |
| `reign_trough_dynasty_hp` | 在位期间国运谷值 |
| `track_reign_dynasty_fortune` | 事件结算后、国祚年度结算后更新峰谷 |
| `reset_reign_fortune_tracking` | 新君登基时重置轨迹 |

轨迹维度：**登基国祚 → 峰值/谷值 → 崩时/亡国时国祚**，再叠加**在位年数**与**治国手腕**。

---

## 4. `evaluate_reign_merit` — 全程功绩分

```text
merit ≈
  国运净变(end-start)/4
  + 中兴/守成盛世加成
  − 深谷/末年崩坏/亡国惩罚
  + 在位年数（久任放大功过）
  + (能力-5)×0.85
```

同时产出标签：`founder` / `shengshi` / `zhongxing` / `shoucheng` / `shuai` / `fallen` / `duanzuo` / `jiuren` 等。

**不再**使用旧公式 `ability + Δ国祚/5` 作为唯一标准。

---

## 5. `gamemin_shihao` — 庙号、谥号、史评

入口：驾崩或亡国时调用 → `evaluate_reign_merit` → 分派庙/谥/评。

### 庙号

- 第 1 帝：开国池（高祖/太祖…）  
- 亡国或 merit < -8：末代池（哀宗、昭宗…）  
- merit ≥ 8 或盛世/中兴标签：盛世池（太宗、玄宗…）  
- merit ≥ -3：守成池（顺宗、代宗…）  
- 否则末代池；再兜底  
- **享年/在位约束**（仿谥法）：`殇宗` 仅享年 <20；`端宗` 宜幼主或短祚；`恭宗` 不宜久任高寿

### 谥号

- 开国固定褒谥  
- 亡国或 merit < -6：恶谥  
- merit ≥ 10 或盛世/强中兴：褒谥；极盛且在位 ≥15 年、享年 ≥30 可出长谥
- merit ≥ -2：中谥  
- 偏衰但未至恶：中谥；merit < -4 可用恶谥  
- **享年约束**：`殇` 仅未成年早夭；`少` 仅少年；`冲/沖` 仅幼冲；`悼` 不宜高寿（<45）

### 史评 `verdict`

按标签与 merit 选措辞（开国 / 盛世 / 中兴 / 守成 / 短祚 / 昏庸 / 亡国等），并体现在位长短。

### 史书记录 `_record_emperor`

除原有字段外写入：`merit`、`dynasty_hp_start/end/peak/trough`。

---

## 6. 新君：`auto_accession` / `dio`

驾崩有嗣时**不弹窗**，直接 `auto_accession`：

1. 姓名取储君 `succ.name`  
2. `suggest_accession_nianhao` + `commit_nianhao`  
3. `dio` → `gamemin_emperor_new`：国祚 -2（保底 1），纪年归 1，继承年龄/能力/hp，title=皇帝，清旧封，生成新尊号，**重置在位国运轨迹**  
4. 记新年号史、`emperor_id+1`、`ongame=True`  

无继承人时的年龄/hp 后备：`emperor_new_age` / `emperor_new_hp`。

---

## 7. 依赖

- 继承：`succession.find_successor`  
- 取名年号：`naming`  
- 结束 UI：`app.show_end_game_dialog`  
- 轨迹更新：`events.event_happen`、`dynasty_logic.gamemin_dynasty`  
