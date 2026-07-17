# resources.py — 静态资源与词库

**路径：** `dynasty/resources.py`  
**类：** `ResourcesMixin`  
**职责：** 初始化一整局可用的姓名、字辈、爵位封号、女封、庙号/谥号/尊号等「资源池」。

---

## 1. `init_tang_resources()`

在 `init_game_state()` 中调用，挂载到 `self` 上的主要属性：

### 1.1 姓名相关

| 属性 | 内容 |
|------|------|
| `tang_surnames` | 姓氏列表（去重保序） |
| `zibei_options` | 字辈诗备选（每字一代） |
| `tang_male_given_single` / `double` | 男名单字/双字库 |
| `tang_female_given_single` / `double` | 女名库 |
| `zibei_name_chars_male` / `female` | 字辈后第二字用字 |
| `emperor_firstname_list` | 姓氏拼接串（兼容旧逻辑） |

### 1.2 爵位与封号（唐制九等）

| 属性 | 内容 |
|------|------|
| `rank_suffix_map` | 1→王，2→郡王，3→国公 … 9→县男（亲王展示用「王」） |
| `rank_full_label_map` | 1→亲王，4→开国郡公 …（界面全称） |
| `rank_name_pools` | 各爵等封号名（秦、彭城、英、长乐…） |
| `female_title_pools` | 公主/郡主/县主/县君/乡君 |

### 1.3 庙号、谥法、尊号

| 属性 | 用途 |
|------|------|
| `emperor_miaohao_founders` | 开国（高祖、太祖…） |
| `emperor_miaohao_prosperous` / `stable` / `decline` | 盛世/守成/末代庙号池 |
| `emperor_shifa_core_*` / `assist_*` | 谥号核心字与辅助字（好/中/恶） |
| `empress_*` / `taizi_*` / `prince_*` / `princess_*` | 后妃、太子、亲王、公主谥号 |
| `emperor_zunhao_pool` | 尊号两段碎片（圣神、文武…） |

末尾调用 `reset_tang_pools()`。

---

## 2. `reset_tang_pools()`

把「可抽取」池重置为词库的拷贝：

- `available_title_pools[rank]` ← `rank_name_pools[rank]`
- `available_female_title_pools[tier]` ← `female_title_pools[tier]`

**何时调用：**

- 资源初始化后  
- 王朝覆灭重开（`gamemin_dynasty_new`）时，避免上一局封号耗尽  

**消耗方式：** `draw_title_name` / `draw_female_title_name` 优先 `pop(0)`；池空则从原词库 `random.choice`。

---

## 3. 设计意图

- 词库集中一处，改「风味」只动本文件。  
- 「静态全量词库」与「本局可用池」分离，实现封号不轻易重复。  
- 不依赖 Qt，可单独被逻辑层使用。

---

## 4. 扩展建议

- 新增爵等：同步改 `rank_suffix_map`、`rank_name_pools` 与 `titles` 中的继承规则。  
- 新增字辈诗：只往 `zibei_options` 追加即可；开局界面 `QComboBox` 会加载该列表。
