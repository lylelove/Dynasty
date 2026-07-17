# succession.py — 继承法与储君

**路径：** `dynasty/mixins/succession.py`  
**类：** `SuccessionMixin`  
**职责：** 嫡长子继承（含代位）、世子标记、太子册立、无直系时兄终弟及与旁系寻嗣。

---

## 1. 嫡长序基础

| 方法 | 作用 |
|------|------|
| `get_sons_by_birth(person, alive_only)` | 诸子按 `(birth_year, id)` 排序 |
| `get_eldest_living_son` | 在世长子 |
| `find_heir_of_line(person)` | **代位继承**：长子在则长子；长子已故则递归长子一系 |

这是全游戏继承的核心算法，封爵继承与皇位继承都依赖它。

---

## 2. 世子：`update_heirs`

对每位在世在封的男性（及今上）：

- 用 `find_heir_of_line` 定正统（**含代位**：长子已故则长孙等）  
- 该继承人 `is_heir=True`，本支其余直接诸子清为 `False`  

注意：此处世子是「父爵继承人」，与「太子」相关但不完全等同。

---

## 3. 储君：`update_crown_prince`

1. 先 `update_heirs`  
2. 对今上做 `find_heir_of_line` 得储君  
3. 清除错误的「太子」称号  
4. 储君若有私封：封号退回池，专任储君  
5. 设 `title="太子"`，`next_emperor_pid=储君.id`  

每年在婚育之后调用，保证新生皇子能参与排序。

---

## 4. 旁系：`find_collateral_successor`

无直系男嗣时：

1. 再兜底 `find_heir_of_line`  
2. 自死者向上：优先**弟**及其后裔（兄终弟及），再兄长一系  
3. 仍无：全体在世男丁按 `(generation, birth_year, id)` 取最早一支  

返回 **pid** 或 `None`。

---

## 5. 皇位：`find_successor`

1. 若已有存活的 `next_emperor_pid`（太子）→ 用之  
2. 否则今上直系代位  
3. 否则旁系  

皇帝驾崩时由 `gamemin_emperor` 调用；无继承人 → 亡国。

---

## 6. 规则小结（实现意图）

```text
皇位：嫡长 → 代位 → 兄终弟及 → 叔伯支 → 最近旁支男丁
封爵：嫡长/代位 → 过继侄（titles+family）→ 绝封还池
```

修改继承法时务必同时检查 `titles.gamemin_family_shihao_titles` 与 `emperor.gamemin_emperor`。
