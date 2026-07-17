# naming.py — 姓名、字辈、年号、尊号

**路径：** `dynasty/mixins/naming.py`  
**类：** `NamingMixin`  
**职责：** 生成不重复的人名与年号；处理字辈；开局/登基界面的「刷新」按钮逻辑。

---

## 1. 去重

| 方法 | 作用 |
|------|------|
| `is_name_used(name)` | 是否已在 `used_person_names` 或 `used_emperor_names` |
| `register_person_name(name)` | 登记已用名 |

---

## 2. 姓与字辈

| 方法 | 作用 |
|------|------|
| `choose_dynasty_surname()` | 随机国姓，写入 `emperor_firstname` |
| `infer_surname_from_name(full_name)` | 从全名反推姓（长姓优先匹配） |
| `get_zibei_char(generation)` | 第 n 代取字辈诗第 n 字（超出循环） |

字辈诗来源：开局 `zibei_poem`（下拉/手改），默认 `zibei_options[0]`。

---

## 3. 名与全名

### `generate_given_name(gender, generation, use_zibei)`

- **宗室**（`use_zibei=True` 且有代数）：  
  - 约 12% 单名 = 字辈本身  
  - 否则 字辈 + 名用字（男/女字库不同）  
- **外戚/配偶**（`use_zibei=False`）：从唐宋风格单字/双字库随机。

### `generate_full_name(...)`

姓 + 名，最多尝试数百次避免重名；仍冲突则加长尾字或数字后缀。

### `get_random_name(gender, generation)`

国姓 + 字辈取名并登记，用于皇子皇女出生。

### `generate_zunhao()`

从 `emperor_zunhao_pool` 抽两段拼接 +「皇帝」。

---

## 4. UI 刷新与年号

| 方法 | 绑定场景 |
|------|----------|
| `dynasty_change_name` | 开始界面「朝代」刷新 |
| `zibei_change_poem` | 字辈刷新 |
| `emperor_change_name` | 开始界面皇帝名（第 1 代字辈） |
| `get_unique_nianhao` | 语义主题链选号（见 `dynasty/nianhao.py`） |
| `commit_nianhao` | **确认**采用时才记入 `used_nianhao` |
| `suggest_accession_nianhao` | 新君自动登基时取新年号（不继承前帝） |
| `yearNumber_change_name` | 开始界面年号（仅预览） |

年号候选库：`dynasty/nianhao_data.py`（约 400+ 历史年号，带 `themes` / `tone` / `weight`）。  
选号与改元策略：`dynasty/nianhao.py`。

---

## 5. 依赖

- 读：`resources` 词库、`zibei_poem`、`used_*`、`nianhao` 模块  
- 被：`family.try_spawn_child`、`dynasty_logic.gamestart`、`emperor` 登基流程、开始界面按钮  

---

## 6. 调参提示

- 单名概率：`generate_given_name` 中 `0.12`  
- 无字辈时单/双名：`0.35` 单名比例  
- 改元概率/段长：`dynasty/nianhao.py` 中 `GAIYUAN_*` 常量  
- 扩充年号：编辑 `tools/build_nianhao_data.py` 的 `RAW` 后重跑生成

