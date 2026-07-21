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
from dynasty.mixins.court import ALL_POSTS
assert window.court_posts, "court should be initialized"
holders = [window.get_post_holder(p) for p in ALL_POSTS]
assert all(m is not None for m in holders), "all 11 court posts should be filled"
assert all(m.is_alive and not m.retired for m in holders), "post holders should be active"
assert window.shoufu_history, "shoufu history should be recorded"
assert any("首辅" in e.get("event", "") for e in events), "chronicle should record 首辅 events"
assert all(m.name[0] != window.emperor_firstname for m in window.ministers), \
    "ministers should not share the imperial surname"

# 朝臣寿数与致仕：终年必须晚于就任之年；致仕者也会终老（不能长生不死）
assert all(m.death_age > (m.entry_year - m.birth_year) for m in window.ministers), \
    "minister death_age should exceed entry age"
retired_alive_over = [
    m for m in window.ministers
    if m.retired and m.is_alive and (window.year - m.birth_year) >= m.death_age
]
assert not retired_alive_over, "retired ministers past their death_age should be dead"

# 首辅任期记录闭合：除最后在任者外，均应有 end_year
open_terms = [rec for rec in window.shoufu_history if rec["end_year"] is None]
assert len(open_terms) <= 1, "at most one shoufu term should be open"
assert all(rec.get("mid") for rec in window.shoufu_history), \
    "shoufu records should carry minister id"

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
assert window.used_minister_shihao == set() and window.court_last_emperor_id is None, \
    "restart should reset court bookkeeping"
assert window.d_time == "", "restart should clear the yearly event snapshot"
sys.exit(0)
