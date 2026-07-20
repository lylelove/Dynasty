# 朝廷机制（V1）实施计划

> 范围（已确认）：朝臣个体 + 官职，明制内阁+六部，纯自动演化（无玩家交互）。
> 朋党、科举、权臣事件留作 V2 扩展点。

## 总体思路

沿用现有 mixin 模式：新增 `dynasty/mixins/court.py::CourtMixin`。朝臣用独立的轻量
`Minister` 类（**不**复用 `Person`——朝臣无父系/爵位/子嗣，混入 `self.people` 会污染
宗亲树、prune 与继承逻辑）。国运公式加一个小的「相辅」修正项。UI 追加第 6 个
「朝廷」Tab。国史提示词新增【五、宰辅】节。

## Step 1 — Minister 模型（dynasty/models.py）

`Person` 之后新增：

```python
class Minister:
    def __init__(self, mid, name, birth_year, entry_year, post):
        self.id = mid
        self.name = name
        self.birth_year = birth_year
        self.death_year = -1
        self.entry_year = entry_year        # 入仕之年
        self.post = post                    # 官职
        self.post_since_year = entry_year   # 现职就任之年
        self.ability = roll_ability()       # 复用现有函数
        self.death_age = roll_minister_death_age()
        self.is_alive = True
        self.retired = False                # 致仕
        self.age = 0
```

`roll_minister_death_age()`：`50 + floor(random()*35)`（50–84，均值约 67）。
年龄每年按 `year - birth_year` 推算，不逐人 +1。

官职常量放 court.py 顶部：首辅×1、次辅×1、群辅×3、六部尚书（吏户礼兵刑工）×6，共 11 职。

## Step 2 — 朝臣取名（dynasty/mixins/naming.py）

新增 `generate_minister_name()`（约 8 行）：
- 姓：`random.choice(self.tang_surnames)`，**排除国姓** `self.emperor_firstname`（重抽）。
- 名：调现有 `generate_full_name(gender="M", surname=…, use_zibei=False)`（不走字辈，
  自带查重与 fallback），返回后 `register_person_name(name)`。

## Step 3 — 朝廷状态（state.py + dynasty_logic.py）

`init_game_state()` 追加：

```python
# 朝廷（内阁 + 六部）
self.ministers = []          # 所有朝臣（含已故/致仕）
self.next_minister_id = 1
self.court_posts = {}        # 官职名 -> minister id（None=虚位）
self.shoufu_history = []     # [{name, ability, start_year, end_year, exit}]
```

`gamemin_dynasty_new()`（重开重置路径）**同步重置**这四个字段，加注释提醒两处一致。

初始化：`dynasty_logic.py::gamestart()` 中调 `self.init_court()`——11 职各招一人，
入仕年龄 35–49（首辅偏年长 45–55）；首任首辅记入 `shoufu_history` 并追加纪事
「拜○○为内阁首辅，总揽机务」。

## Step 4 — 年度逻辑（新文件 dynasty/mixins/court.py）

`gamemin_court()` 每年流程：

1. **老与卒/致仕**：`age >= death_age` → 卒；否则 `age >= 65` 起每年致仕概率
   `0.10 + 0.05*(age-65)`，75 强制致仕（首辅概率减半、78 强制）。
2. **递补链**（自上而下）：首辅缺 → 次辅升；次辅缺 → 群辅能力最高者升；
   群辅缺 → 六部尚书能力最高者「入阁」；尚书缺 → `recruit_minister()` 招新人。
   升职时更新 `post` 与 `post_since_year`；首辅更替记 `shoufu_history`。
3. **纪事**（控制刷屏，只记首辅级 + 名臣入阁）：
   - 拜相「拜○○为内阁首辅，朝野属望」；卒「内阁首辅○○卒于任上，帝辍朝三日」；
     致仕「首辅○○乞骸骨，累疏获准，赐驰驿归里」；名臣入阁（ability≥8）
     「○○以才望入阁预机务，时论许为名臣」。
   - 事件 dict 照抄 `event_happen()` 结构（含 `emperor_id`）append 到
     `event_happened`——自动流入纪事表、结束弹窗和国史提示词。

**调用位置**：`app.py::gamemin()` 中放在 `gamemin_family_shihao_titles()` 之后、
`prune_unimportant_people()` 之前（在亡国 return 之后、必须在 `event_happen()`
之后以复用当年 `d_time`）。

`app.py` 顶部 import `CourtMixin` 并加入 `DynastyApp` 基类列表。

内存：`ministers` 全量保留（一局 <500 人），无需 prune。

## Step 5 — 国运影响（dynasty_logic.py::gamemin_dynasty）

衰减公式后追加：

```python
# 相辅之力：贤相匡扶、庸臣蠹政（均能力 5 为中平）
court_ab = self._court_avg_ability()   # 空表/未初始化返回 5.0
self.dynasty_hp += (court_ab - 5.0) * 0.06
```

每年约 ±0.24，为主衰减项的 10–20%，不颠覆现有 150–300 年国祚平衡。

V2 扩展点（只留注释）：`emperor_ab<=3 且首辅 ability>=8` 的权臣事件、faction、科举。

## Step 6 — UI「朝廷」Tab（app.py）

- `setup_main_game_screen()` 新建 `tab6`，**追加在末尾（index 5）**，现有索引不动：
  - 上：`— 内 阁 与 六 部 —`（objectName `section_label`）+ `court_table`
    6 列 `职位/姓名/年龄/能力/任职年数/入仕年数`，固定 11 行，写法照抄 `emperor_list_table`。
  - 下：`— 历 任 首 辅 —` + `shoufu_table` 4 列 `姓名/能力/任期/去向`（卒/致仕/在任）。
- `on_main_tab_changed` 判断 `(3, 4)` 改为 `(3, 4, 5)`。
- `update_ui()` 末尾节流刷新：`tab_idx == 5 or year % 5 == 0` 时 `update_court_ui()`。
- QSS 无需新增（通用 QTableWidget 样式已覆盖）。

## Step 7 — 国史提示词（history_prompt.py）

1. 新增 `_build_court_section(lines)`，照抄 `_build_fief_section` 模式（getattr 守护、
   空表 return），在 `_build_fief_section` 之后调用：

   ```
   【五、宰辅（选用素材：可附「宰辅列传」，亦可在各帝本纪中带出）】
   首辅○○○（材具：明察，某年拜相，在任 N 年，卒于任/致仕）
   （当朝首辅○○○，在任 M 年——尚未盖棺，勿写其结局。）
   ```

   复用 `_ability_label()`；超 12 任中段节略（类常量 `_PROMPT_SHOUFU_MAX = 12`）。
2. 更新约束第 2 条（约 429 行）：朝臣以【五、宰辅】所列为准，可另虚构中下层官吏。

## Step 8 — 实施顺序与验证

顺序：models → naming → state/重置/gamestart → court.py+挂载 → 国运项 → UI → 提示词。

验证：
- `QT_QPA_PLATFORM=offscreen python test_run.py` headless 跑到亡国；建议追加断言：
  `court_posts` 非空、`shoufu_history` 非空、纪事含「首辅」、重开后 `ministers == []`。
- 国运项加入后多跑几次确认国祚仍在 150–300 年量级。
- `python main.py` 手动检查朝廷 Tab 渲染与重开清空。
- 注意：`dynasty/resources.py` 有一处未提交改动（删「废宗」），勿覆盖。

关键数字：11 职全满起局；入仕 35–49；终年 50–84；致仕 65 起、75 强制（首辅 78）；
国运修正 `(均能力-5)*0.06`/年；纪事约每局 20–40 条（<15% 总量）。
