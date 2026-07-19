# models.py — 核心数据模型

**路径：** `dynasty/models.py`  
**职责：** 定义游戏中唯一的人物实体 `Person`，以及皇帝/宗室能力随机函数 `roll_ability`。

---

## 1. `roll_ability()`

```text
能力 = max(1, 5 + floor(U[0,1)*5) - floor(U[0,1)*5))
```

- 结果落在 **[1, 9]**（实际因 floor 差多为 0～4，再加 5，再 clamp 到 ≥1）。
- 呈近似三角分布：中间值（约 5）更常见，极端 1 或 9 较少。
- 用于：新建 `Person` 时默认能力；无继承人时随机新君能力。

---

## 2. 类 `Person`

一局游戏中所有已模拟的男系皇室成员都是 `Person` 实例，集中在 `DynastyApp.people` 列表。

### 2.1 构造参数

| 参数 | 含义 |
|------|------|
| `pid` | 全局唯一 ID（由 `next_pid` 递增分配） |
| `name` | 全名（姓+名） |
| `gender` | `"M"` 男 / `"F"` 女 |
| `birth_year` | 出生游戏年（相对 `year`） |
| `father_id` / `mother_id` | 父母 ID；当前男系模拟仅写入 `father_id` |
| `generation` | 相对开国皇帝的代数（开国帝 = 1） |

### 2.2 身份与爵位字段

| 字段 | 含义 |
|------|------|
| `title` | **展示用**完整称号（如「晋亲王」「太子」「皇帝」） |
| `title_name` | 封国/封号名（如「晋」「彭城」） |
| `title_rank` | 爵等：0 帝室相关；1 亲王 … 9 县男 |
| `is_heir` | 是否为父爵之世子（嫡长） |
| `has_title` | 是否**现任**持有该封爵（父死承袭或独立受封后为 True） |

### 2.3 生命与家族

| 字段 | 含义 |
|------|------|
| `hp` | 剩余寿限（每年 -1，≤0 死亡） |
| `age` | 当前年龄 |
| `is_alive` | 存活 |
| `children` | 子嗣 ID 列表（仅男） |
| `extinct` | 是否绝嗣（无男系后裔） |
| `adopted_from` | 过继来源（嗣父 ID） |

### 2.4 谥号 / 庙号 / 尊号

| 字段 | 适用 |
|------|------|
| `shihao` | 死后谥号全文 |
| `miaohao` | 皇帝庙号（如「太宗」） |
| `zunhao` | 在位尊号（如「圣神文武皇帝」） |
| `ability` | 治国手腕 1～9 |

### 2.5 设计注意

- `Person` **不含业务方法**，只存数据；规则在 mixins 中。
- 皇帝同时有「全局状态」（`emperor_hp` 等）与对应 `Person` 对象，`gamemin_emperor` 会同步年龄/hp。
- 仅男系人物；无配偶实体。

---

## 3. 与其他模块关系

```
Person  ←  family 创建/查询/婚育
        ←  titles     写 title / shihao / has_title
        ←  succession 写 is_heir / 太子
        ←  emperor    写皇帝 miaohao/shihao/zunhao
        ←  app        展示
```
