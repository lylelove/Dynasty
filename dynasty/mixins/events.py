# -*- coding: utf-8 -*-
"""年度随机事件抽取、国祚/天寿影响与改元。"""
import random

from dynasty import nianhao as nh


class EventsMixin:
    """年度随机事件抽取、国祚/天寿影响与改元。"""

    def event_happen(self):
        self.event_id_chose()

        # Determine current year string before possible change
        if self.jinian == 1:
            self.d_time = self.yearNumber + "元年"
        else:
            self.d_time = self.yearNumber + str(self.jinian) + "年"

        self.d_event = self.event_list[self.event_id]["event"]
        self.d_event_id = self.event_id
        self.d_emperor = self.emperor_zunhao or self.emperor or ""

        event_dict = {
            "time": self.d_time,
            "emperor": self.d_emperor,
            "event": self.d_event,
        }
        self.event_happened.append(event_dict)

        self.event_change()
        self.emperor_hp += self.data_emperor_hp_change
        self.dynasty_hp += self.data_dynasty_hp_change
        self.track_reign_dynasty_fortune()

        # 混合制改元：极端国运冲击 + 本段已满数年 + 概率；同帝新年号走主题链
        # 改元当年即为新年号元年（不重复记入旧号），次年应为二年——故先改号再记年
        segment_years = 0
        segment_count = len(self.current_emperor_nianhao_history or [])
        if self.current_emperor_nianhao_history:
            segment_years = self.current_emperor_nianhao_history[-1].get("years", 0)

        if nh.should_gaiyuan(self.data_dynasty_hp_change, segment_years, segment_count):
            old_name = self.yearNumber
            reason = nh.gaiyuan_reason_from_impact(self.data_dynasty_hp_change)
            self.yearNumber = self.get_unique_nianhao(
                reason=reason,
                previous_name=old_name,
                linked=True,
            )
            self.commit_nianhao(self.yearNumber)
            self.begin_next_nianhao_segment()
            # 当年即新年号元年；随后 gamemin_emperor 会 jinian+=1 → 次年=二年
            self.jinian = 1
            self.d_time = self.yearNumber + "元年"
            event_dict["time"] = self.d_time
            change_event = {
                "time": self.d_time,
                "emperor": self.d_emperor,
                "event": nh.gaiyuan_event_text(old_name, self.yearNumber, self.data_dynasty_hp_change),
            }
            self.event_happened.append(change_event)

        self.record_current_year_for_nianhao()

    def event_id_chose(self):
        self.event_id = random.randrange(len(self.event_list))

    def event_change(self):
        evt = self.event_list[self.d_event_id]
        if "emperor_hp_change" in evt and evt["emperor_hp_change"] is not None:
            self.data_emperor_hp_change = evt["emperor_hp_change"]
        else:
            self.data_emperor_hp_change = 0

        if "dynasty_hp_change" in evt and evt["dynasty_hp_change"] is not None:
            self.data_dynasty_hp_change = evt["dynasty_hp_change"]
        else:
            self.data_dynasty_hp_change = 0

