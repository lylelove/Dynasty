# -*- coding: utf-8 -*-
"""姓名/字辈/年号/尊号生成与去重；开局与登基时的随机取名。"""
import random

from dynasty import nianhao as nh


class NamingMixin:
    """姓名/字辈/年号/尊号生成与去重；开局与登基时的随机取名。"""

    def is_name_used(self, name):
        return name in self.used_person_names or name in self.used_emperor_names

    def register_person_name(self, name):
        if name:
            self.used_person_names.add(name)

    def choose_dynasty_surname(self):
        self.emperor_firstname = random.choice(self.tang_surnames)
        return self.emperor_firstname

    def infer_surname_from_name(self, full_name):
        for surname in sorted(self.tang_surnames, key=len, reverse=True):
            if full_name.startswith(surname):
                return surname
        return full_name[0] if full_name else ""

    def get_zibei_char(self, generation):
        """按代数取字辈：第1代用诗首字，第2代用第2字……超出则循环。"""
        poem = self.zibei_poem or (self.zibei_options[0] if self.zibei_options else "元亨利贞祥")
        if not poem:
            return "元"
        idx = max(0, int(generation) - 1) % len(poem)
        return poem[idx]

    def generate_given_name(self, gender="M", generation=None, use_zibei=True):
        """生成男名。宗室（use_zibei=True 且有代数）按字辈取名。"""
        if use_zibei and generation is not None and self.zibei_poem:
            zibei = self.get_zibei_char(generation)
            # 双名为主：字辈 + 名用字；少量单名用字辈本身
            if random.random() < 0.12:
                return zibei
            second = random.choice(self.zibei_name_chars_male)
            if second == zibei and len(self.zibei_name_chars_male) > 1:
                second = random.choice([c for c in self.zibei_name_chars_male if c != zibei])
            return zibei + second

        if random.random() < 0.35:
            return random.choice(self.tang_male_given_single)
        return random.choice(self.tang_male_given_double)

    def generate_zunhao(self):
        """组合两段尊号碎片，生成如『圣神文武皇帝』的风味化尊号。"""
        pool = list(self.emperor_zunhao_pool)
        if len(pool) < 2:
            return "皇帝"
        frags = random.sample(pool, 2)
        return "".join(frags) + "皇帝"

    def generate_full_name(self, gender="M", surname=None, generation=None, use_zibei=True):
        family_name = surname if surname else random.choice(self.tang_surnames)
        attempts = 0
        max_attempts = 800
        while attempts < max_attempts:
            given_name = self.generate_given_name(generation=generation, use_zibei=use_zibei)
            candidate = family_name + given_name
            if not self.is_name_used(candidate):
                return candidate
            attempts += 1

        # 字辈库耗尽时：字辈 + 随机双字，再不行加数字后缀
        zibei = self.get_zibei_char(generation) if (use_zibei and generation is not None) else ""
        for _ in range(400):
            tail = random.choice(self.zibei_name_chars_male) + random.choice(self.zibei_name_chars_male)
            candidate = family_name + (zibei + tail if zibei else tail)
            if not self.is_name_used(candidate):
                return candidate

        suffix = 1
        while True:
            given_name = self.generate_given_name(generation=generation, use_zibei=use_zibei)
            candidate = f"{family_name}{given_name}{suffix}"
            if not self.is_name_used(candidate):
                return candidate
            suffix += 1

    def get_random_name(self, gender="M", generation=None):
        name = self.generate_full_name(
            surname=self.emperor_firstname,
            generation=generation,
            use_zibei=True,
        )
        self.register_person_name(name)
        return name

    def dynasty_change_name(self):
        self.dynasty = random.choice(self.dynasty_name)
        self.dynasty_input.setText(self.dynasty)

    def zibei_change_poem(self):
        poem = random.choice(self.zibei_options)
        idx = self.zibei_combo.findText(poem)
        if idx >= 0:
            self.zibei_combo.setCurrentIndex(idx)
        else:
            self.zibei_combo.setEditText(poem)
        self.zibei_poem = poem

    def emperor_change_name(self):
        self.choose_dynasty_surname()
        # 开国皇帝用字辈第1代
        poem = self.zibei_combo.currentText().strip() if hasattr(self, "zibei_combo") else ""
        self.zibei_poem = poem or (self.zibei_options[0] if self.zibei_options else "元亨利贞祥")
        while True:
            self.emperor_lastname = self.generate_given_name("M", generation=1, use_zibei=True)
            candidate = self.emperor_firstname + self.emperor_lastname
            if candidate not in self.used_emperor_names and not self.is_name_used(candidate):
                self.emperor = candidate
                break
        self.emperor_input.setText(self.emperor)

    def current_emperor_theme_anchor(self):
        """本帝主题链锚点：优先已用段，其次当前年号。"""
        themes = []
        for item in getattr(self, "current_emperor_nianhao_history", None) or []:
            name = item.get("nianhao") or ""
            for t in nh.themes_of(name):
                if t not in themes:
                    themes.append(t)
        if not themes and getattr(self, "yearNumber", None):
            themes = nh.themes_of(self.yearNumber)
        return themes

    def get_unique_nianhao(self, reason=None, previous_name=None, linked=False):
        """
        选取未用年号。
        linked=True 时沿用本帝主题链（改元）；登基/开局刷新不强制关联前帝。
        """
        reason = reason or nh.REASON_REFRESH
        anchor = self.current_emperor_theme_anchor() if linked else None
        prev = previous_name if linked else None
        if linked and not prev and self.current_emperor_nianhao_history:
            prev = self.current_emperor_nianhao_history[-1].get("nianhao")
        return nh.pick_nianhao(
            used=self.used_nianhao,
            reason=reason,
            previous_name=prev,
            anchor_themes=anchor,
        )

    def commit_nianhao(self, name):
        """确认采用年号时才登记已用（刷新预览不占用）。"""
        if name:
            self.used_nianhao = nh.register_nianhao(self.used_nianhao, name)

    def yearNumber_change_name(self):
        self.yearNumber = self.get_unique_nianhao(reason=nh.REASON_REFRESH)
        self.year_number_input.setText(self.yearNumber)

    def dialog_yearNumber_change_name(self):
        # 仅预览，确认登基时再 commit
        self.yearNumber = self.get_unique_nianhao(reason=nh.REASON_ACCESSION)
        self.dialog_year_input.setText(self.yearNumber)

    def suggest_accession_nianhao(self):
        """新君登基默认新年号（不继承前帝）。"""
        return self.get_unique_nianhao(reason=nh.REASON_ACCESSION)

    def emperor_change_name_after(self):
        # 新君改名：按继位者代数取字辈（无继位者则按当前代数+1）
        gen = 1
        if self.next_emperor_pid:
            succ = self.get_person_by_id(self.next_emperor_pid)
            if succ:
                gen = succ.generation
        while True:
            self.emperor_lastname = self.generate_given_name("M", generation=gen, use_zibei=True)
            candidate = self.emperor_firstname + self.emperor_lastname
            if candidate not in self.used_emperor_names and not self.is_name_used(candidate):
                self.emperor = candidate
                self.used_emperor_names.append(candidate)
                self.register_person_name(candidate)
                break
        self.dialog_emp_input.setText(self.emperor)

