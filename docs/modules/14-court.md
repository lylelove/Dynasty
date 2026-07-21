# 14 朝廷（mixins/court.py）

对应源码：`dynasty/mixins/court.py` · 模型：`models.Minister` · 状态：`state.py` 朝廷段

## 职责

明制内阁 + 六部的纯自动演化：组建、老病致仕、卒于任、递补拜相、权臣事件、
朝臣谥号，以及对国运的「相辅」修正。无玩家交互。

## 官职（11 职）

| 职位 | 员额 | 备注 |
|------|------|------|
| 首辅 | 1 | 致仕概率减半、78 强制（恋栈） |
| 次辅 | 1 | 首辅出缺时第一顺位 |
| 群辅 | 3 | 内部不分先后，界面统称「群辅」（`post_display`） |
| 六部尚书 | 6 | 吏户礼兵刑工 |

## Minister 字段（models.py）

独立于宗室 `Person`：无父系、爵位、子嗣，不进 `self.people`，不参与 prune。
关键字段：`entry_year`（入仕）、`post_since_year`（现职就任）、`death_age`
（50–84，招募时保证大于就任年龄）、`retired`、`shihao`（身后追谥）、
`quanchen`（本任内已记权臣纪事）。

## 年度流程（`gamemin_court`，在 `gamemin_family_shihao_titles` 之后调用）

1. **新君察相**（`_court_new_emperor_check`）：检测 `emperor_id` 变化；新君
   以 15% 概率罢免前朝首辅（权臣 50%），去向记「罢」。
2. **老与卒/致仕**（`_court_aging_and_exit`）：在职者 `age = year - birth_year`；
   `age >= death_age` 卒（能力 ≥6 追谥）；65 起致仕概率
   `0.10 + 0.05*(age-65)`，75 强制（首辅减半 / 78 强制）。
3. **林下终老**（`_court_offstage_deaths`）：致仕者继续计龄至天年；曾任首辅
   且得谥者记「薨于里第」纪事。
4. **递补链**（`_court_fill_vacancies`）：次辅升首辅 → 群辅（能力最高）升次辅 →
   尚书（能力最高）入阁 → 招新补尚书；循环级联至无缺。极端情形下阁职直接
   招新（45–55 岁），保证 11 职常满。
5. **权臣察验**（`_court_quanchen_check`）：帝能力 ≤3、首辅能力 ≥8、在任 ≥5 年
   时每年 25% 触发一次「威权震主」纪事（每任至多一次），国运 -1.5（保底 1，
   生死只在 `gamemin_dynasty` 结算）。

## 谥号（`_grant_minister_shihao`）

能力 ≥6 身后得谥；≥8 有 40% 得极品谥（文正/文贞/文成/文忠），否则常谥
（文端、文定……20 个）。一朝不重谥（`used_minister_shihao`）。

## 国运影响（dynasty_logic.py）

`dynasty_hp += (_court_avg_ability() - 5.0) * 0.06`——在职 11 人均能力对 5 的
偏差，每年约 ±0.24，为主衰减项的 10–20%。空表/未组建返回 5.0（零影响）。

## 首辅任期账（`shoufu_history`）

`[{mid, name, ability, start_year, end_year, exit}]`；`exit ∈ {卒, 致仕, 罢, ""(在任)}`。
开闭一律按 `mid` 匹配（`_close_shoufu_term`），避免同名歧义。
流入：朝廷 Tab 下表、国史提示词【五、宰辅】节。

## 纪事口径

只记首辅级 + 名臣入阁（ability ≥8），约每局 20–40 条。事件 dict 与
`event_happen()` 同构（含 `emperor_id`），自动流入纪事表、结束弹窗与国史提示词。

## 重置

三处必须同步：`state.init_game_state()`、`dynasty_logic.gamemin_dynasty_new()`
（重开）。字段：`ministers`、`next_minister_id`、`court_posts`、`shoufu_history`、
`used_minister_shihao`、`court_last_emperor_id`。重开另清 `d_time/d_event/d_emperor`
快照，防新朝开国纪事带前朝年号。

## V2 扩展点

朋党（`Minister.faction`）、科举出身（`exam_rank`）、权臣篡逆分支。
