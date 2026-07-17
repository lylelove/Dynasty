# titles.py — 爵位、封号、宗室谥号（唐制）

**路径：** `dynasty/mixins/titles.py`  
**类：** `TitlesMixin`  
**职责：** 封号抽取、在世称号展示、宗室死后谥号、成年授爵与封爵继承（含过继交接）。

---

## 1. 唐制九等爵（`title_rank`）

| rank | 爵等 | 展示后缀 | 封号名库 |
|------|------|----------|----------|
| 0 | 帝室 / 无爵 | — | — |
| 1 | **亲王** | **王**（秦王，非「秦亲王」） | 古国、道名（单字） |
| 2 | 郡王 | 郡王 | 郡望（双字，如彭城） |
| 3 | 国公 | 国公 | 国名（英、卫…） |
| 4 | 开国郡公 | 郡公 | 县/郡地名 |
| 5 | 开国县公 | 县公 | 县名 |
| 6 | 开国县侯 | 县侯 | 县名 |
| 7 | 开国县伯 | 县伯 | 县名 |
| 8 | 开国县子 | 县子 | 县名 |
| 9 | 开国县男 | 县男 | 县名 |

词库与全称见 `resources.py`：`rank_suffix_map`、`rank_full_label_map`、`rank_name_pools`。

### 命名示例

| 爵 | 在世 | 谥后 |
|----|------|------|
| 亲王 | 秦王 | 秦恭王 |
| 郡王 | 彭城郡王 | 彭城靖郡王 |
| 国公 | 英国公 | 英忠国公 |
| 县侯 | 长兴县侯 | 长兴思县侯 |

拼装入口：`format_enfeoffed_title(title_name, rank, shihao="")`。

---

## 2. 主要方法

| 方法 | 作用 |
|------|------|
| `get_rank_suffix` / `get_rank_label` / `get_rank_short` | 后缀 / 全称 / 列表缩写 |
| `format_enfeoffed_title` | 唐式封号拼接 |
| `draw_title_name` | 抽封号 |
| `format_alive_title` | 在世展示（皇帝/太子/有爵/世子） |
| `get_heir_posthumous_suffix` | 王世子、郡王世子、国公世子… |
| `build_family_posthumous_title` | 死后谥号全文 |
| `gamemin_family_shihao_titles` | 成年授爵、谥号、承袭/过继/绝封 |

（游戏仅模拟男系宗室，无后妃/公主。）

---

## 4. 世子与承袭

- 亲王～县公：嫡长称「某王世子 / 郡王世子 / …」  
- 皇太子专任储君，不兼私封  
- 死后嫡长（含代位）承袭同封同爵；无则过继侄嗣（`apply_adoption` 改父系）后承封；再无则封号还池  

降爵与生育见 `family.py`：皇子皆亲王；宗室余子 `min(父爵+1, 9)`。
