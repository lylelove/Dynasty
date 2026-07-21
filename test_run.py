import sys
from PySide6.QtWidgets import QApplication
from main import DynastyApp

app = QApplication(sys.argv)
window = DynastyApp()

# Stub out the blocking end-game dialog so this can run headless.
window.show_end_game_dialog = lambda: None

window.dynasty_input.setText("唐")
window.emperor_input.setText("李世民")
window.year_number_input.setText("贞观")
window.start_game_from_ui()

# Run until the dynasty ends, or a safety limit is reached.
for _ in range(5000):
    if not window.ongame:
        break
    window.gamemin()

# Spot-check: chronicle rows carry emperor honorific when present
events = [e for e in window.event_happened[1:] if e.get("event")]
assert events, "expected chronicle events"
assert any(e.get("emperor") for e in events), "chronicle should record emperor (尊号)"

# 朝廷：11 职常满、首辅有更替记录、纪事含拜相
from dynasty.mixins.court import ALL_POSTS, POST_SHOUFU, POST_CIFU, QUNFU_POSTS, SIX_MINISTRIES
assert window.court_posts, "court should be initialized"
holders = [window.get_post_holder(p) for p in ALL_POSTS]
assert all(m is not None for m in holders), "all 11 court posts should be filled"
assert all(m.is_alive and not m.retired for m in holders), "post holders should be active"
assert window.shoufu_history, "shoufu history should be recorded"
assert any("首辅" in e.get("event", "") for e in events), "chronicle should record 首辅 events"
assert all(m.name[0] != window.emperor_firstname for m in window.ministers), \
    "ministers should not share the imperial surname"

# 仕途资历：尚书/阁臣不得「刚入仕」；初仕早于（或等于）现职，仕途年数达标
for m in window.ministers:
    assert m.entry_year <= m.post_since_year, "初仕不得晚于现职就任"
    # 就任尚书/阁职时，初仕至少已满 15 年（post_since - entry）
    assert (m.post_since_year - m.entry_year) >= 15, \
        f"{m.name} 初仕至现职仅 {m.post_since_year - m.entry_year} 年"
    entry_age = m.entry_year - m.birth_year
    assert 18 <= entry_age <= 42, f"{m.name} 初仕年龄异常: {entry_age}"
# 现任者仕途年数（自初仕）至少 15 年——绝无「本任尚书、入仕 0 年」
for post in ALL_POSTS:
    m = window.get_post_holder(post)
    assert (window.year - m.entry_year) >= 15, \
        f"{post} holder career years = {window.year - m.entry_year}"
# 高位能力门槛
shoufu = window.get_post_holder(POST_SHOUFU)
assert shoufu.ability >= 6, f"首辅 ability {shoufu.ability} < 6"
for post in [POST_CIFU] + QUNFU_POSTS:
    m = window.get_post_holder(post)
    assert m.ability >= 5, f"{post} ability {m.ability} < 5"
# 同年级联升迁的 0 年中间职不应残留
for p in ALL_POSTS:
    for rec in window.post_history[p]:
        if rec["exit"] == "升迁" and rec["end_year"] is not None:
            assert rec["end_year"] > rec["start_year"], \
                f"zero-year 升迁 residual in {p}: {rec}"

# 朝臣寿数与致仕：终年必须晚于就任之年；致仕者也会终老（不能长生不死）
assert all(m.death_age > (m.entry_year - m.birth_year) for m in window.ministers), \
    "minister death_age should exceed entry age"
retired_alive_over = [
    m for m in window.ministers
    if m.retired and m.is_alive and (window.year - m.birth_year) >= m.death_age
]
assert not retired_alive_over, "retired ministers past their death_age should be dead"

# 死后多有谥号（伏诛/赐死可不谥）
from dynasty.mixins.court import EXIT_LABELS, EXIT_NO_SHIHAO
dead = [m for m in window.ministers if not m.is_alive]
assert dead, "expected some deceased ministers after a full run"
for m in dead:
    career_exits = {
        r.get("exit")
        for r in window.get_minister_career(m.id)
        if r.get("exit")
    }
    if career_exits & EXIT_NO_SHIHAO:
        continue
    assert m.shihao, f"{m.name} deceased without 谥号 (exits={career_exits})"
alive_with_shihao = [m for m in window.ministers if m.is_alive and m.shihao]
assert not alive_with_shihao, "living ministers should not yet have 谥号"

# 去职原因应多样：不能几乎全是升迁/致仕
all_exits = []
for p in ALL_POSTS:
    for rec in window.post_history[p]:
        if rec.get("exit"):
            all_exits.append(rec["exit"])
assert all_exits, "expected some closed terms with exit reasons"
exit_set = set(all_exits)
# 至少出现若干种非升迁去向
non_promo = [e for e in all_exits if e != "升迁"]
assert non_promo, "expected non-promotion exits"
assert len(set(non_promo)) >= 3, \
    f"exit reasons too homogeneous: {sorted(exit_set)}"
# 升迁+致仕不应垄断全部非空去向
promo_retire = sum(1 for e in all_exits if e in ("升迁", "致仕"))
assert promo_retire < len(all_exits) * 0.85, \
    f"升迁/致仕占比过高: {promo_retire}/{len(all_exits)} ({sorted(exit_set)})"
# 码值均在已知表内
unknown = exit_set - set(EXIT_LABELS.keys())
assert not unknown, f"unknown exit codes: {unknown}"

# 各职历任账：11 职皆有记录；shoufu_history 与 post_history["首辅"] 同一列表
assert hasattr(window, "post_history") and window.post_history, "post_history required"
assert all(p in window.post_history for p in ALL_POSTS), "every post should have a history list"
assert all(len(window.post_history[p]) >= 1 for p in ALL_POSTS), \
    "every post should have at least one term recorded"
assert window.shoufu_history is window.post_history["首辅"], \
    "shoufu_history should alias post_history['首辅']"

# 首辅任期记录闭合：除最后在任者外，均应有 end_year
open_terms = [rec for rec in window.shoufu_history if rec["end_year"] is None]
assert len(open_terms) <= 1, "at most one shoufu term should be open"
assert all(rec.get("mid") for rec in window.shoufu_history), \
    "shoufu records should carry minister id"
# 非首辅职亦应正确闭合（在职者至多一任未闭）
for p in ALL_POSTS:
    open_p = [r for r in window.post_history[p] if r["end_year"] is None]
    assert len(open_p) <= 1, f"at most one open term for {p}"

# 国史提示词含宰辅节
prompt = window.build_history_prompt()
assert "【五、宰辅（选用素材" in prompt, "history prompt should include 宰辅 section"
assert any(rec["name"] in prompt for rec in window.shoufu_history), \
    "宰辅 section should list 首辅 names"

print(f"Passed: ran to year {window.year}, dynasty "
      f"{'ended' if window.dynasty_die else 'still standing'}, "
      f"{len(window.listjson)} emperors recorded, "
      f"{len(events)} chronicle rows, "
      f"{len(window.ministers)} ministers, {len(window.shoufu_history)} 首辅")

# 重开路径：朝廷清空
window.gamemin_dynasty_new()
assert window.ministers == [] and window.court_posts == {} and window.shoufu_history == [], \
    "restart should reset the court"
assert all(window.post_history.get(p) == [] for p in ALL_POSTS), \
    "restart should clear all post histories"
assert window.shoufu_history is window.post_history["首辅"], \
    "restart should re-alias shoufu_history"
assert window.used_minister_shihao == set() and window.court_last_emperor_id is None, \
    "restart should reset court bookkeeping"
assert window.d_time == "", "restart should clear the yearly event snapshot"
sys.exit(0)
