# dynasty_logic.py — 国祚、开局、覆灭

**路径：** `dynasty/mixins/dynasty_logic.py`  
**类：** `DynastyLogicMixin`  
**职责：** 开局创建开国皇帝、国祚逐年结算、天下大势文案、亡国重置。

---

## 1. `gamestart`

开始界面确认后：

1. 校验帝名非空；从姓名推断国姓  
2. 开国帝年龄 26，天寿 20～44，能力固定 10  
3. 创建 `Person`（代数 1，title 皇帝，已婚，尊号）  
4. 国祚 100；登记已用名/年号；初始化年号史  
5. 刷新大势文案与 UI，切到主游戏页  

---

## 2. `gamemin_dynasty` — 国祚公式

每年（国祚仍 >0）：

```text
dynasty_hp +=
  - (amuse / 60 * 2.5 / max(1, emperor_ab))
  + (hardworking / 60 * emperor_ab / 15)
dynasty_age += 1
```

- 上限 clamp 到 100  
- 若 `0 < dynasty_hp ≤ 15` 且 `emperor_ab ≥ 8`：地板 15（能臣可暂缓崩溃）  
- `dynasty_hp ≤ 0`：亡国 → 给末帝上谥、记入史书、结束对话框  

**设计目标：** 合理存续约 150～300 年（配合滑块与事件）。

---

## 3. `dynasty_function_st`

按 `dynasty_hp` 与 `emperor_ab` 组合输出天下大势短句，如：

- 高国运 + 高能力 →「开元盛世，万国来朝」  
- 低国运 →「亡国之兆，日暮途穷」  

仅影响展示，不改数值。

---

## 4. 亡国与重开

| 方法 | 作用 |
|------|------|
| `gamemin_dynasty_change` | 亡国时 `_record_emperor` |
| `gamemin_dynasty_new` | 清空人物、ID、池子、史书、已用名号、字辈等 |
| `dio2` | 结束对话框确定 → 重置 + 回开始界面并清空输入 |

---

## 5. 与皇帝模块的分工

| 场景 | 主导模块 |
|------|----------|
| 国运逐年变化 | dynasty_logic |
| 皇帝寿终换代 | emperor |
| 无继承人亡国 | emperor 触发 + dynasty 收尾 |
| 国运归零亡国 | dynasty_logic |

---

## 6. 调参

- 国祚公式系数：`gamemin_dynasty` 内 `/60`、`2.5`、`/15`  
- 能臣地板：`15` 与 `emperor_ab >= 8`  
- 换代国祚损耗：`gamemin_emperor_new` 中 `-2`
