# family.py — 宗室、婚育、过继、封国

**路径：** `dynasty/mixins/family.py`  
**类：** `FamilyMixin`  
**职责：** 人物查询、非皇帝的衰老死亡、婚姻生育、绝嗣判定、过继、封国汇总。

---

## 1. 查询与谱系工具

| 方法 | 作用 |
|------|------|
| `get_person_by_id` | O(1) 按 ID 查人 |
| `get_descendants` | 递归全部后裔 ID |
| `check_extinct` | 男系是否无在世男后裔 |
| `find_adoptee` | 兄弟之子中选嗣（优先未受封、年长；已过继者排除） |
| `apply_adoption` | 过继入嗣：记本生父于 `adopted_from`，改 `father_id`/子女链/代数 |
| `get_clan_branch` | 沿父系上溯至最近的亲王/郡王封号（将军中尉归所属王府） |
| `format_person_year` / `get_father_name` / `get_children_summary` | 人物详情展示用 |

---

## 2. 衰老：`gamemin_family_aging_death`

对**在世且非今上**的人：`age+1`，`hp-1`；`hp≤0` 则死亡并记 `death_year`。  
（皇帝寿限由 `emperor` 模块单独处理。）

---

## 3. 繁衍：`gamemin_family_marriage_birth`（明制）

**仅男系**：全体已受封（或待袭）成年宗室皆可生子，生育率按爵位递减。

| 角色 | 基础生育率（约） | 存活子上限 |
|------|------------------|-----------|
| 皇帝 | 0.30 | 5 |
| 亲王 | 0.12 | 4 |
| 郡王 | 0.08 | 4 |
| 镇/辅/奉国将军 | 0.05 | 3 |
| 镇/辅/奉国中尉 | 0.03 | 3 |

在世宗室 ≥ `SOFT_ALIVE_CAP`(80) 时生育减半；≥ `HARD_ALIVE_CAP`(140) 时仅皇帝与亲王/郡王可育。

### `child_rank_for(father, existing_son_count)` — 明制子嗣爵位

- 皇子皆亲王
- 亲王/郡王：长子袭本爵（预定世子/长子），余子降一等
- 将军中尉：诸子皆降一等，至奉国中尉（rank 8）后世代不再降

### `try_spawn_child(father, child_rank)`

- 仅生男：国姓 + 字辈取名，设 `title_rank`
- 经 `_register_person` 写入 `people` 与 `people_by_id`

---

## 4. 性能：索引与裁剪

| 方法 | 作用 |
|------|------|
| `people_by_id` / `get_person_by_id` | O(1) 查人 |
| `is_important_person` | 在世、帝系、谥庙号等展示所需人物 |
| `prune_unimportant_people` | 人数 ≥ `PRUNE_THRESHOLD`(160) 时删无关已故支系，保留祖先链及历代封国持有者 |

---

## 5. 封国：`collect_fiefs` / `find_fief_lineage_root`

- 按 `title_name` 聚合男系持有者（天然只含亲王/郡王封国——将军中尉无封号）
- 统计在世/历任、现任国主、是否除国
- 世系根 = 该封号最早出生的持有者

供「宗藩」Tab 与封国世系树使用。

---

## 6. 调参

- `MAX_LIVING_SONS` / `SOFT_ALIVE_CAP` / `HARD_ALIVE_CAP` / `PRUNE_THRESHOLD`
- `rank_chance`（各爵生育率）

提高生育或阈值 → 宗室膨胀快、绝嗣少、性能与 UI 更重。
