# Dynasty —— 王朝模拟游戏

这是一个使用纯 Python + PySide6 框架编写的单机桌面历史模拟小游戏（原基于 Vue + ElementWeb 版本重构而成）。

玩家可以通过设定初始朝代、皇帝与年号，开始一局波澜壮阔的王朝史诗模拟。在不断的年度步进中，游戏将模拟皇帝的执政生涯、后宫繁衍、爵位承袭、天灾人祸以及大势演变，直至国祚终结。

---

## 运行游戏

请确保已安装 Python 3.8+ 环境，并在项目根目录下执行以下命令安装依赖并运行：

```bash
pip install -r requirements.txt
python main.py
```

---

## 代码结构

项目整体结构采用模块化的 Mixin 混入设计，将主窗口界面绘制与不同的业务逻辑合理拆分：

| 路径 | 职责与核心类/混入 |
|------|------------------|
| [main.py](file:///D:/github/Dynasty/main.py) | 启动入口 |
| [dynasty/app.py](file:///D:/github/Dynasty/dynasty/app.py) | 主窗口 UI 框架与界面刷新控制类 [DynastyApp](file:///D:/github/Dynasty/dynasty/app.py) |
| [dynasty/models.py](file:///D:/github/Dynasty/dynasty/models.py) | 人物数据模型 [Person](file:///D:/github/Dynasty/dynasty/models.py)（管理寿命、爵位、状态与繁衍） |
| [dynasty/state.py](file:///D:/github/Dynasty/dynasty/state.py) | 局内全局状态管理器 [GameStateMixin](file:///D:/github/Dynasty/dynasty/state.py) |
| [dynasty/resources.py](file:///D:/github/Dynasty/dynasty/resources.py) | 汉字姓名、庙号、谥号、爵位等词库 [ResourcesMixin](file:///D:/github/Dynasty/dynasty/resources.py) |
| [dynasty/styles.py](file:///D:/github/Dynasty/dynasty/styles.py) | QSS 古风墨底金边主题样式类 [StylesMixin](file:///D:/github/Dynasty/dynasty/styles.py) |
| [dynasty/fortune_chart.py](file:///D:/github/Dynasty/dynasty/fortune_chart.py) | 国运曲线图绘制组件与弹窗 [FortuneChartDialog](file:///D:/github/Dynasty/dynasty/fortune_chart.py) |
| [dynasty/lineage_chart.py](file:///D:/github/Dynasty/dynasty/lineage_chart.py) | 人物详情中的男系世系关系拓扑图 [LineageChartPanel](file:///D:/github/Dynasty/dynasty/lineage_chart.py) |
| [dynasty/mixins/naming.py](file:///D:/github/Dynasty/dynasty/mixins/naming.py) | 姓名随机生成、年号改元、去重追踪逻辑 [NamingMixin](file:///D:/github/Dynasty/dynasty/mixins/naming.py) |
| [dynasty/mixins/titles.py](file:///D:/github/Dynasty/dynasty/mixins/titles.py) | 宗室爵位分封、降等袭爵与绝嗣管理 [TitlesMixin](file:///D:/github/Dynasty/dynasty/mixins/titles.py) |
| [dynasty/mixins/family.py](file:///D:/github/Dynasty/dynasty/mixins/family.py) | 宗室繁衍、生老病死、孤儿过继机制 [FamilyMixin](file:///D:/github/Dynasty/dynasty/mixins/family.py) |
| [dynasty/mixins/succession.py](file:///D:/github/Dynasty/dynasty/mixins/succession.py) | 皇位嫡长子继承、代位继承、兄终弟及、旁支过继算法 [SuccessionMixin](file:///D:/github/Dynasty/dynasty/mixins/succession.py) |
| [dynasty/mixins/events.py](file:///D:/github/Dynasty/dynasty/mixins/events.py) | 历史大事件生成与动态反馈逻辑 [EventsMixin](file:///D:/github/Dynasty/dynasty/mixins/events.py) |
| [dynasty/mixins/emperor.py](file:///D:/github/Dynasty/dynasty/mixins/emperor.py) | 皇帝在位生命周期、余寿计算、庙谥评定与尊号生成 [EmperorMixin](file:///D:/github/Dynasty/dynasty/mixins/emperor.py) |
| [dynasty/mixins/dynasty_logic.py](file:///D:/github/Dynasty/dynasty/mixins/dynasty_logic.py) | 王朝建立、大势计算、国运起伏与崩盘判定 [DynastyLogicMixin](file:///D:/github/Dynasty/dynasty/mixins/dynasty_logic.py) |
| [dynasty/mixins/history_prompt.py](file:///D:/github/Dynasty/dynasty/mixins/history_prompt.py) | 本局王朝大事记 AI 史书写作提示词生成器 [HistoryPromptMixin](file:///D:/github/Dynasty/dynasty/mixins/history_prompt.py) |

**详细说明文档请参阅：** [docs/modules/README.md](docs/modules/README.md)

---

## 核心系统特色

1. **唐制九等爵系统**
   - 包含亲王（如「晋王」）、郡王、国公、县侯等九等爵，采取嫡长子承袭，其余子嗣降等袭爵的规则。
   - 封国成员无后时，触发绝嗣判定，支持收继侄嗣以延续香火。

2. **完整皇位继承机制**
   - 严格遵循古典继承顺序：嫡长子继承 -> 嫡长孙代位 -> 诸子兄终弟及 -> 旁支宗室过继。
   - 拥有完善的储君/世子代位继承和多代宗亲过继逻辑。

3. **庙号与谥号系统**
   - 模拟历史评议机制，根据皇帝在位期间的**整个国运轨迹**（登基点、峰值点、谷值点、终局点）、在位年数和治国手腕进行功过综合评分。
   - 盛世中兴得褒谥（如太宗、成祖），守成得中谥，昏庸亡国则获恶谥（如哀宗、炀帝），并匹配唐代风味的复杂谥号。

4. **可视化国运图表与世系拓扑**
   - 支持逐年记录国运值并渲染折线图，直观标记历代帝王在位区间与改元时刻。
   - 提供节点树状图以交互方式展示复杂宗亲家族树，双击人物即可追溯其三代世系。

5. **AI 国史提示词一键导出**
   - 记录王朝重大历史纪年，自动生成结构化的 Prompt，方便玩家复制给 ChatGPT / Claude 等 AI 模型生成一部栩栩如生的长篇国史。

---

## ToDo / 未来规划

- **朝廷系统**：引入朝臣、官职、三省六部、内阁与朋党党争等机制，深化君臣互动与政治博弈。

---

## 版本演进历史

### V0.10 ~ V0.17 (Web 单体奠基版)
- **V0.10**：创建项目，使用前端技术栈搭建初步模型。
- **V0.11**：修复基础 Bug，在界面增加前任皇帝列表展示。
- **V0.12**：增加朝代、皇帝姓名、年号的随机抽取系统，并在游戏结束时完整展示皇帝列表。
- **V0.13**：初步实装谥号机制，对逝世皇帝进行简单的功过认定。
- **V0.14**：重构单体结构，优化代码逻辑。
- **V0.15**：优化图表展示，引入可视化折线图。
- **V0.16**：删除占用较多资源的动态 HP 逻辑，重新设计数值曲线。
- **V0.17**：添加事件系统框架并调整了皇帝寿命参数。

---

### V0.20 (纯 Python / PySide6 重写版)
- 放弃了原有的 Vue + Element 架构，将项目使用 **Python** 与 **PySide6** 桌面 GUI 框架进行纯原生重写。
- 逻辑行为与前期积累的 V0.18 保持一致，保证性能和稳定性，并按功能细化分拆为模块包。

---

### V0.30 (游戏深度优化与机制升级)
- **新增**：添加**自动运行模式**（通过定时器 QTimer 步进运行），用户可一键开启或停止挂机。
- **新增**：游戏结束弹窗中增加“王朝纪事”选项卡，完整展示本朝大事件历程。
- **优化**：重构百家姓与名讳词库，支持生成单字名与双字名，使其更加贴合古代历史背景。
- **优化**：全面汉化与雅化 UI 文案，如“寿命”改为“天寿”，“能力”改为“治国手腕”等。
- **优化**：**重构庙谥系统**。根据皇帝一生治国评分动态分发谥法与庙号，杜绝不合理的恶谥发生。
- **优化**：**实装防重复机制**。通过局内历史跟踪，保证同朝之内的皇帝名、年号、庙谥绝对不会出现重复。
- **优化**：大幅扩充大事件库，加入黄河决堤、藩镇割据、科举开科等极具代入感的历史事件。

---

### V0.40 (宗室系统与继承法变革)
- **新增**：引入 `Person` 人物实体，开始全面模拟庞大的皇室宗亲子嗣。
- **新增**：实现包含嫡长子继承、代位继承、兄终弟及、旁系过继在内的完整皇位继承算法。
- **新增**：主界面加入「皇室宗亲」Tab 页，展示父系完整的层级世系。
- **新增**：双击宗亲列表可弹出可视化世系树（QTreeWidget 嵌套节点），直观掌握皇族繁衍。

---

### V0.50 (唐制九等爵与宗藩封国)
- **新增**：实装唐代九等爵承袭规则（如亲王称「某王」，嫡长子袭爵，其余降等分封）。
- **新增**：新增「宗藩」UI 选项卡，展示本局游戏内的所有受封封国、各封国国主承袭脉络。
- **优化**：提升了非皇帝宗室成员的生育繁衍能力，加入了因绝嗣导致的降等袭爵与过继算法。

---

### V0.60 (后宫称号与模块化重构)
- **优化**：重构后宫命名和称号分配算法，增强历史厚重感。
- **优化**：将原单体 `main.py` 的臃肿代码正式剥离拆入 `dynasty/` 目录下，并建立 `mixins/` 逻辑混入层。

---

### V0.70 (国运折线图与世系拓扑交互)
- **新增**：重做图表系统，引入 `FortuneChartDialog`（国运折线图），在“王朝信息”页中支持点击“查看国运图”展示历代皇帝在位折线，并标注重要改元节点（▲）。
- **新增**：在人物详情中添加 `LineageChartPanel` 组件，利用 QPainter 动态绘制选中人物中心五代的男系亲属拓扑树（支持双击卡片连环跳转）。
- **优化**：优化 QSS 皮肤，统一采用沉稳的墨底金边视觉风格，提高文字对比度。

---

### V0.80 (AI 史书导出与历史余寿重塑)
- **新增**：**一键导出国史提示词**。点击主界面按钮即可将结构化的国史大事记复制到剪贴板，玩家可一键输入至 AI 大模型生成定制纪传体史书。
- **新增**：在国史提示词中加入**前任皇帝亲属关系描述**（例如：自动推导新君为先皇之“侄”、“叔”、“曾孙”等关系描述）。
- **优化**：采用真实的古代皇帝寿命概率分布模型，重塑寿命与继位余寿的掷取逻辑，解决幼帝高天寿或老帝瞬崩等不真实数值。

---

### V0.90 (UI 防误触与安全性加固 - 本次更新)
- **优化**：**全局锁定数据展示文本与表格**。
- **优化**：开始游戏界面中的“朝代”、“皇帝”、“年号”文本框设为**只读**，字辈选择下拉框改为**不可编辑**，只能通过专属“刷新”按钮随机摇取，防止游戏开始前的数据手误篡改。
- **优化**：将主界面的历代帝王表、天下纪事表，以及游戏结束弹出对话框中的所有数据表格，均设置为**禁用编辑触发器（`NoEditTriggers`）**，彻底杜绝了用户双击单元格后文字被手误修改的问题。