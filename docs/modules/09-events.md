# events.py — 年度随机事件

**路径：** `dynasty/mixins/events.py`  
**类：** `EventsMixin`  
**职责：** 每年抽取一条事件，写入纪事，修正皇帝天寿与国祚，极端情况下改元。

---

## 1. 流程：`event_happen`

1. `event_id_chose`：`random.randrange(len(event_list))`  
2. 生成时间串：`{年号}元年` 或 `{年号}{jinian}年`  
3. 取事件文案，并记在位皇帝**尊号**（`emperor_zunhao`，无则姓名）到 `emperor` 字段，append 到 `event_happened`  
4. `record_current_year_for_nianhao`（皇帝模块）累计本段年号年数  
5. `event_change` 读取该事件的数值变化  
6. 应用到 `emperor_hp`、`dynasty_hp`  
7. **改元判定**（混合制，见 `dynasty/nianhao.should_gaiyuan`）：  
   - `|dynasty_hp_change| ≥ 5`，且本段年号已满 ≥2 年，且本帝段数 < 5  
   - 首次改元约 18%（大冲击 +8%），再次改元约 8%  
   - 新年号走**语义主题链**（与本帝已用号共享主题字；灾异偏弭灾向，祥瑞/武功偏吉祥向）  
    - `commit_nianhao` + `begin_next_nianhao_segment`  
    - **改元当年 = 新年号元年**：`jinian = 1`，本年事件改记新年号；再 `record_current_year_for_nianhao`（不重复记入旧号）  
    - 随后 `gamemin_emperor` 中 `jinian += 1`，故**次年事件为二年**（避免连续两个「元年」）  
    - 纪事文案区分灾异改元 / 祥瑞改元  


---

## 2. 事件数据来源

模板在 `state.init_game_state` 的 `event_list`：

```python
# 模板（state.event_list）
{
  "time": "",
  "event": "……",
  "emperor_hp_change": int,
  "dynasty_hp_change": int,
}
# 落库（event_happened 每条）
{
  "time": "贞观元年",
  "emperor": "圣神文武皇帝",  # 在位尊号
  "emperor_id": 3,           # 第几帝（国史提示词按此归档编年）
  "event": "……",
}
```

前若干条为「今年无事发生」（0 变化），用于稀释坏/好事件频率。

事件文案按朝政制度、民生经济、边疆外交、宗室礼制、文化与灾异等题材配置。
新增文案应尽量提供可进入国史的具体叙事钩子（机构、地域、政务或社会反应），
同时避免绑定某一真实朝代、真实帝王或确定年份，以适配随机生成的王朝。

---

## 3. 与其他系统

- 国祚最终是否归零：看 `dynasty_logic.gamemin_dynasty`（本事件只做加减）  
- 史书评价：皇帝驾崩时用整段国祚变化，不只看单次事件  
- UI：主界面「天下纪事」仅显示最新 50 条（`event_happened[1:][-50:]`）；完整历史仍保留在 `event_happened`，结束界面「王朝纪事」展示全部  

---

## 4. 扩展

- 加事件：往 `event_list` 追加字典即可，无需改本模块逻辑。  
- 数值范围：现有事件的皇帝天寿影响为 `-2～+1`，国运影响为 `-7～+5`；新增事件宜维持同一量级。
- 加权抽取：改 `event_id_chose`（当前均匀随机）。  
- 禁用改元：注释/调整 `event_happen` 末尾条件。
