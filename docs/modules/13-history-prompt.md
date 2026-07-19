# history_prompt.py — AI 国史提示词生成

**路径：** `dynasty/mixins/history_prompt.py`
**类：** `HistoryPromptMixin`
**职责：** 把本局模拟结果（帝系、编年、国运、宗藩）拼装成一段结构化中文提示词，供玩家复制给 AI 大模型生成纪传体国史。入口按钮见 `app.show_history_prompt_dialog`。

---

## 1. 提示词结构（`build_history_prompt`）

```
角色设定 + 架空声明
【写作约束】     1-6 条（+第 7 条，仅局中导出时出现）
【一、王朝概况】 朝代 / 开国帝 / 字辈（附用途说明）/ 帝数 / 国祚 / 盛衰阶段 / 大势
【二、帝系本纪表】逐帝：庙谥、与前代关系、年号、在位、享年、材具、国运、子嗣、史评
【三、编年要事】 逐帝分段的压缩编年（即位/崩/亡国穿插其中）
【四、宗藩世家】 王/郡王/国公级封国承袭脉络（选用素材，无封国时整节省略）
【输出要求】     直接开写、自拟书名、序 → 诸帝本纪 → 史臣曰
```

## 2. 数据来源

| 数据 | 来源 |
|------|------|
| 已盖棺帝王 | `state.listjson`（`emperor._record_emperor` 驾崩/亡国时写入） |
| 当今在位皇帝 | `emperor` / `emperor_zunhao` / `current_emperor_nianhao_history` / 在位国运快照等散字段 |
| 编年事件 | `state.event_happened`（含 `emperor_id`，按帝精确归档） |
| 亲属关系 | `family.describe_kinship`（父系称谓推导） |
| 封国脉络 | `family.collect_fiefs`（仅取 rank 1–3） |

## 3. 局中导出（王朝未亡时）

`listjson` 只在盖棺时写入，故局中导出需单独拼当今皇帝：

- `_has_reigning_emperor`：`not dynasty_die and ongame and 有今上` 时为真。
- `_current_emperor_as_emp`：把散字段拼成与 `listjson` 条目同构的 dict，复用各格式化函数。
- 帝系表末尾附「当今在位」段（`_append_reigning_emperor_entry`），编年末尾附今上已发生纪事。
- 约束区追加第 7 条：今上本纪写至当下即止，不得虚构结局与庙谥。

## 4. 事件归档与压缩

- `_events_for_emperor`：优先按事件的 `emperor_id` 精确匹配；无该字段的旧记录退回尊号/姓名匹配（尊号已查重，见 `naming.generate_zunhao`）。
- `_compress_reign_events`：
  - 改元事件全文保留（缘由文案是叙事钩子，约束 3 要求正文呼应）；
  - 同文案合并为「……（凡 N 见）」；
  - 每帝至多 `_PROMPT_EVENTS_PER_REIGN`（8）条；帝数超过 `_PROMPT_FULL_DETAIL_EMP_MAX`（15）时，中段诸帝压至 3 条；
  - 截断时补一行「其余同类事约 N 类从略」。

## 5. 提示词工程要点

- **硬/软事实分离**：帝系、名号、结局不可改；性格、朝臣、情节允许演绎但须与史评方向一致。
- **防泄漏**：正文禁国运数值、公元纪年、系统词（「国运/数据/模拟/史评」）与现代口语；国运数字仅在帝系表出现一次，行内不再重复注释。
- **防跑偏**：输出要求里明确「直接开写、勿复述提示词、勿提问」；超长朝代允许「（未完，俟续）」分段收束。
- **体例示范**：「与前代」一栏用 `庙号·姓名` 称先帝；嗣位子嗣写作「嗣位，是为某宗」（内部不带括号，因外层已包一层），与正史行文一致。

## 6. 调参入口

| 想改什么 | 改哪里 |
|----------|--------|
| 每帝事件条数上限 | `_PROMPT_EVENTS_PER_REIGN` |
| 长朝代压缩阈值 | `_PROMPT_FULL_DETAIL_EMP_MAX` |
| 宗藩小节规模 | `_PROMPT_FIEFS_MAX` / `_PROMPT_FIEF_HOLDERS_MAX` |
| 篇幅分档文案 | `_build_constraints` 第 6 条 |
