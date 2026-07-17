# styles.py — 古风主题样式

**路径：** `dynasty/styles.py`  
**类：** `StylesMixin`  
**职责：** 向全局 `QApplication` 注入一套「宣纸明堂 · 朱漆金边」QSS。

---

## 1. `apply_stylesheet()`

在 `DynastyApp.__init__` 末尾调用。

### 视觉基调

- 背景：米宣纸色 `#f5efe3` 渐变  
- 文字：深褐 `#2c1810`  
- 字体优先：楷体 / 仿宋 / 宋体  
- 强调色：朱漆红 `#c4453c`、金边 `#c9a24b` / `#b5893f`

### 使用了 `objectName` 的控件

| objectName | 用途 |
|------------|------|
| `title_label` | 开始界面大标题「王 朝」 |
| `subtitle_label` | 副标题、提示小字 |
| `reign_banner` | 主界面「朝代 · 年号」匾额 |
| `section_label` | 各区段标题（天下纪事、历代帝王…） |

在 `app.py` 里创建 `QLabel` 后调用 `setObjectName(...)` 才会吃到对应样式。

### 覆盖的 Qt 控件类型

`QWidget`、`QMainWindow`、`QDialog`、`QLineEdit`、`QPushButton`、`QTabWidget`/`QTabBar`、`QTableWidget`/`QTreeWidget`、`QHeaderView`、`QSlider`、`QScrollBar`、`QLabel`。

---

## 2. 修改建议

- 只改颜色/字号：编辑本文件中的 QSS 字符串即可。  
- 新控件样式：优先复用已有 objectName，或追加选择器。  
- 不要在业务 mixin 里散落 `setStyleSheet`，保持主题单一入口。
