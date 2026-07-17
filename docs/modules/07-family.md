# family.py — 宗室、婚育、过继、封国

**路径：** `dynasty/mixins/family.py`  
**类：** `FamilyMixin`  
**职责：** 人物查询、非皇帝的衰老死亡、婚姻生育、绝嗣判定、过继、封国汇总。

---

## 1. 查询与谱系工具

| 方法 | 作用 |
|------|------|
| `get_person_by_id` | O(n) 按 ID 查人 |
| `get_descendants` | 递归全部后裔 ID |
| `check_extinct` | 男系是否无在世男后裔 |
| `find_adoptee` | 兄弟之子中选嗣（优先未受封、年长；已过继者排除） |
| `apply_adoption` | 过继入嗣：记本生父于 `adopted_from`，改 `father_id`/子女链/代数 || `format_person_year` / `get_father_name` / `get_children_summary` | 人物详情展示用 |

---

## 2. 衰老：`gamemin_family_aging_death`

对**在世且非今上**的人：`age+1`，`hp-1`；`hp≤0` 则死亡并记 `death_year`。  
（皇帝寿限由 `emperor` 模块单独处理。）

---

## 3. 繁衍：`gamemin_family_marriage_birth`

**仅男系**：皇帝与已实封亲王/郡王（`title_rank ≤ BREED_RANK_MAX`，默认 2）可生子；国公以下不模拟繁衍。

| 角色 | 基础生育率（约） |
|------|------------------|
| 皇帝 | 0.30 |
| 亲王 | 0.07 |
| 郡王 | 0.04 |

在世宗室 ≥ `SOFT_ALIVE_CAP` 时生育减半；≥ `HARD_ALIVE_CAP` 时仅皇帝可育。

### `try_spawn_child(father, child_rank)`

- 仅生男：国姓 + 字辈取名，设 `title_rank`  
- 皇子皆亲王；宗室嫡长同父爵，余子 `min(父+1, 9)`  
- 经 `_register_person` 写入 `people` 与 `people_by_id`

---

## 4. 性能：索引与裁剪

| 方法 | 作用 |
|------|------|
| `people_by_id` / `get_person_by_id` | O(1) 查人 |
| `is_important_person` | 在世、帝系、有爵/谥庙号等 |
| `prune_unimportant_people` | 人数 ≥ `PRUNE_THRESHOLD`(180) 时删无关已故支系，保留祖先链 |

---

## 5. 封国：`collect_fiefs` / `find_fief_lineage_root`

- 按 `title_name` 聚合男系持有者  
- 统计在世/历任、现任国主、是否绝封  
- 世系根 = 该封号最早出生的持有者  

供「宗藩」Tab 与封国世系树使用。

---

## 6. 调参

- `BREED_RANK_MAX` / `MAX_LIVING_SONS` / `PRUNE_THRESHOLD`  
- 生育 `chance` 与无子额外概率  

提高生育或阈值 → 宗室膨胀快、绝嗣少、性能与 UI 更重。
