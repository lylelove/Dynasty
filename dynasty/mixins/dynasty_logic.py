# -*- coding: utf-8 -*-
"""国祚结算、天下大势文案、开局与王朝覆灭重置。"""
import math
import random
from dynasty.models import Person


class DynastyLogicMixin:
    """国祚结算、天下大势文案、开局与王朝覆灭重置。"""

    def gamestart(self):
        if not self.emperor:
            return
        self.emperor_firstname = self.infer_surname_from_name(self.emperor)
        self.emperor_age = 26
        # 开国帝约 26 岁登基，余寿 22–42 年 → 终年约 48–68
        self.emperor_hp = 22 + math.floor(random.random() * 21)
        self.emperor_ab = 10

        # Create first Emperor Person
        emp_person = Person(self.next_pid, self.emperor, "M", self.year - self.emperor_age, None, None, 1)
        emp_person.age = self.emperor_age
        emp_person.hp = self.emperor_hp
        emp_person.ability = self.emperor_ab
        emp_person.title = "皇帝"
        self.emperor_zunhao = self.generate_zunhao()
        emp_person.zunhao = self.emperor_zunhao
        self._register_person(emp_person)
        self.current_emperor_pid = emp_person.id
        self.next_pid += 1

        self.dynasty_hp = 100
        self.initial_dynasty_hp = 100
        self.reign_peak_dynasty_hp = 100
        self.reign_trough_dynasty_hp = 100
        self.used_emperor_names.append(self.emperor)
        self.register_person_name(self.emperor)
        self.commit_nianhao(self.yearNumber)
        self.start_new_emperor_nianhao_history()
        self.dynasty_function_st()
        self.update_ui()
        self.stacked_widget.setCurrentIndex(1)

    def gamemin_dynasty(self):
        if self.dynasty_hp > 0:
            # Balance: Slow down dynasty decay to last ~150-300 years
            self.dynasty_hp = self.dynasty_hp - (self.amuse / 60 * 2.5 / max(1, self.emperor_ab)) + (self.hardworking / 60 * self.emperor_ab / 15)
            self.dynasty_age += 1

        if self.dynasty_hp >= 100:
            self.dynasty_hp = 100

        # A brilliant ruler (ability >= 8) can keep the dynasty from collapsing
        # below a floor of 15, but only while the dynasty still stands.
        if 0 < self.dynasty_hp <= 15 and self.emperor_ab >= 8:
            self.dynasty_hp = 15

        self.track_reign_dynasty_fortune()

        if self.dynasty_hp <= 0:
            self.dynasty_die = True
            self.dynasty_hp = 0
            if self.ongame:
                self.gamemin_shihao()
                self.gamemin_dynasty_change()
                self.ongame = False
                self.show_end_game_dialog()

    def gamemin_dynasty_change(self):
        self._record_emperor()

    def gamemin_dynasty_new(self):
        self.people = []
        self.people_by_id = {}
        self.next_pid = 1
        self.current_emperor_pid = None
        self.next_emperor_pid = None
        self.reset_tang_pools()
        self.dynasty_age = 0
        self.jinian = 1
        self.listjson = []
        self.current_emperor_nianhao_history = []
        self.year = 0
        self.emperor_id = 1
        self.event_happened = [{"time": "", "event": ""}]
        self.used_shihao = []
        self.used_miaohao = []
        self.used_emperor_names = []
        self.used_person_names = set()
        self.used_nianhao = []
        self.zibei_poem = ""
        self.initial_dynasty_hp = 100
        self.reign_peak_dynasty_hp = 100
        self.reign_trough_dynasty_hp = 100

    def dynasty_function_st(self):
        if self.dynasty_hp >= 90:
            if self.emperor_ab >= 8:
                self.dynasty_st = "开元盛世，万国来朝"
            else:
                self.dynasty_st = "国泰民安，海晏河清"
        elif self.dynasty_hp >= 80:
            if self.emperor_ab >= 6:
                self.dynasty_st = "风调雨顺，百业兴旺"
            else:
                self.dynasty_st = "天下承平，守成之局"
        elif self.dynasty_hp >= 60:
            if self.emperor_ab >= 7:
                self.dynasty_st = "中兴在望，奋发图强"
            elif self.emperor_ab <= 4:
                self.dynasty_st = "外强中干，隐患暗生"
            else:
                self.dynasty_st = "差强人意，平平无奇"
        elif self.dynasty_hp >= 40:
            if self.emperor_ab >= 8:
                self.dynasty_st = "励精图治，力挽狂澜"
            else:
                self.dynasty_st = "山雨欲来，动荡不安"
        elif self.dynasty_hp >= 20:
            if self.emperor_ab >= 9:
                self.dynasty_st = "独木难支，夕阳无限"
            else:
                self.dynasty_st = "风雨飘摇，国势倾颓"
        elif self.dynasty_hp >= 10:
            self.dynasty_st = "不绝如缕，大厦将倾"
        else:
            self.dynasty_st = "亡国之兆，日暮途穷"

    def dio2(self):
        self.dynasty_die = False
        self.end_game_dialog.accept()
        self.gamemin_dynasty_new()
        self.ongame = True

        # When restarting, they go to the start screen.
        # But we need to clear inputs just in case, or let them input again.
        self.dynasty_input.setText("")
        self.emperor_input.setText("")
        self.year_number_input.setText("")
        if self.zibei_options:
            self.zibei_combo.setCurrentIndex(0)

        self.stacked_widget.setCurrentIndex(0)

