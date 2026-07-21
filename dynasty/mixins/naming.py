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
        """生成姓名。宗室（use_zibei=True 且有代数）按字辈取名。"""
        is_male = gender == "M"
        name_chars = self.zibei_name_chars_male if is_male else self.zibei_name_chars_female
        single_names = self.tang_male_given_single if is_male else self.tang_female_given_single
        double_names = self.tang_male_given_double if is_male else self.tang_female_given_double
        if use_zibei and generation is not None and self.zibei_poem:
            zibei = self.get_zibei_char(generation)
            # 双名为主：字辈 + 名用字；少量单名用字辈本身
            if random.random() < 0.12:
                return zibei
            second = random.choice(name_chars)
            if second == zibei and len(name_chars) > 1:
                second = random.choice([c for c in name_chars if c != zibei])
            return zibei + second

        if random.random() < 0.35:
            return random.choice(single_names)
        return random.choice(double_names)

    # —— 尊号（仿唐宋上尊号礼制）——
    # 登基初上二段（天命 + 功德），在位中群臣屡请加号，累加至多六段
    ZUNHAO_MAX_SEGMENTS = 6
    # 距登基/上次加号至少满此年数，群臣方再议加号
    ZUNHAO_ADD_MIN_YEARS = 8

    def _zunhao_full(self, frags):
        return "".join(frags) + "皇帝"

    def _zunhao_pick_fragment(self, themes, exclude=()):
        """从若干义类池中抽一段未用碎片。"""
        pool = []
        for theme in themes:
            pool.extend(self.zunhao_theme_pools.get(theme, []))
        pool = [f for f in pool if f not in exclude]
        if not pool:
            return ""
        return random.choice(pool)

    def generate_zunhao(self):
        """登基初上尊号：天命一段 + 功德一段，如「应天神武皇帝」。

        局内查重（`used_zunhao`）：编年旧档按尊号归入各帝名下，同朝撞号
        会致事件张冠李戴。在位加号时的新全称同样须查重登记。
        """
        used = getattr(self, "used_zunhao", None)
        if used is None:
            used = self.used_zunhao = []

        candidate_frags = None
        for _ in range(80):
            first = self._zunhao_pick_fragment(("tianming",))
            merit_theme = random.choice(self.zunhao_merit_themes)
            second = self._zunhao_pick_fragment((merit_theme,), exclude=(first,))
            if not first or not second:
                break
            frags = [first, second]
            if self._zunhao_full(frags) not in used:
                candidate_frags = frags
                break

        if candidate_frags is None:
            # 二段组合耗尽（极长局）：加一段功德碎片兜底
            for _ in range(80):
                first = self._zunhao_pick_fragment(("tianming",))
                second = self._zunhao_pick_fragment(self.zunhao_merit_themes, exclude=(first,))
                third = self._zunhao_pick_fragment(
                    self.zunhao_merit_themes, exclude=(first, second)
                )
                if not (first and second and third):
                    break
                frags = [first, second, third]
                if self._zunhao_full(frags) not in used:
                    candidate_frags = frags
                    break

        if candidate_frags is None:
            candidate_frags = ["应天", "光宅"]

        self.emperor_zunhao_frags = candidate_frags
        # 记加号年（绝对纪年；jinian 改元会归一，不可用）
        self.zunhao_last_add_year = getattr(self, "year", 0)
        candidate = self._zunhao_full(candidate_frags)
        used.append(candidate)
        return candidate

    def _zunhao_add_theme(self):
        """按当下情势择加号义类：大捷尚武，治世崇文颂德，圣主归道。"""
        if self.data_dynasty_hp_change >= 5:
            return "wugong"
        if self.dynasty_hp >= 85:
            return random.choice(("wenzhi", "dexing"))
        if self.emperor_ab >= 8:
            return "daoyun"
        return random.choice(self.zunhao_merit_themes)

    def try_offer_zunhao(self):
        """年度加号礼：治世或大捷时群臣上表请加尊号，帝或受或辞。

        返回纪事文本（None 表示今年无此礼）。受号则尊号增一段、
        礼成靡费国祚微损；固辞则天下称颂、国祚微增。
        """
        frags = getattr(self, "emperor_zunhao_frags", None)
        if not frags or len(frags) >= self.ZUNHAO_MAX_SEGMENTS:
            return None
        if self.year - getattr(self, "zunhao_last_add_year", 0) < self.ZUNHAO_ADD_MIN_YEARS:
            return None
        # 触发情势：治世（国运高）或本年大功（如边关大捷）；乱世无人议此
        prosperous = self.dynasty_hp >= 60
        triumph = self.data_dynasty_hp_change >= 5
        if not prosperous and not triumph:
            return None
        chance = 0.05
        if triumph:
            chance += 0.15
        if self.dynasty_hp >= 85:
            chance += 0.05
        if random.random() > chance:
            return None

        self.zunhao_last_add_year = self.year

        # 谦抑之主固辞不受（勤政愈甚，辞让愈坚）
        decline_chance = 0.35 if self.hardworking >= 60 else 0.15
        if random.random() < decline_chance:
            self.dynasty_hp = min(100, self.dynasty_hp + 1)
            return "群臣三上表请加尊号，帝谦抑固辞，天下称颂。"

        theme = self._zunhao_add_theme()
        used = self.used_zunhao
        for _ in range(40):
            frag = self._zunhao_pick_fragment((theme,), exclude=tuple(frags))
            if not frag:
                frag = self._zunhao_pick_fragment(
                    self.zunhao_merit_themes, exclude=tuple(frags)
                )
            if not frag:
                return None
            new_frags = frags + [frag]
            if self._zunhao_full(new_frags) not in used:
                break
        else:
            return None

        self.emperor_zunhao_frags = new_frags
        self.emperor_zunhao = self._zunhao_full(new_frags)
        used.append(self.emperor_zunhao)
        emp_person = self.get_person_by_id(self.current_emperor_pid)
        if emp_person:
            emp_person.zunhao = self.emperor_zunhao
        # 上尊号例行御殿受册、大赦告庙，礼成靡费
        self.dynasty_hp = max(1, self.dynasty_hp - 1)
        return f"群臣以功德上表请加尊号，帝御殿受册，号曰「{self.emperor_zunhao}」，大赦天下。"

    def generate_full_name(self, gender="M", surname=None, generation=None, use_zibei=True):
        family_name = surname if surname else random.choice(self.tang_surnames)
        attempts = 0
        max_attempts = 800
        while attempts < max_attempts:
            given_name = self.generate_given_name(
                gender=gender, generation=generation, use_zibei=use_zibei
            )
            candidate = family_name + given_name
            if not self.is_name_used(candidate):
                return candidate
            attempts += 1

        # 字辈库耗尽时：字辈 + 随机双字，再不行加数字后缀
        zibei = self.get_zibei_char(generation) if (use_zibei and generation is not None) else ""
        for _ in range(400):
            name_chars = self.zibei_name_chars_male if gender == "M" else self.zibei_name_chars_female
            tail = random.choice(name_chars) + random.choice(name_chars)
            candidate = family_name + (zibei + tail if zibei else tail)
            if not self.is_name_used(candidate):
                return candidate

        suffix = 1
        while True:
            given_name = self.generate_given_name(
                gender=gender, generation=generation, use_zibei=use_zibei
            )
            candidate = f"{family_name}{given_name}{suffix}"
            if not self.is_name_used(candidate):
                return candidate
            suffix += 1

    def generate_minister_name(self):
        """朝臣取名：随机异姓（避国姓）+ 不走字辈的常规名，登记查重。"""
        surname = random.choice(self.tang_surnames)
        for _ in range(40):
            if surname != self.emperor_firstname:
                break
            surname = random.choice(self.tang_surnames)
        name = self.generate_full_name(gender="M", surname=surname, use_zibei=False)
        self.register_person_name(name)
        return name

    def get_random_name(self, gender="M", generation=None):
        name = self.generate_full_name(
            gender=gender,
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

    def suggest_accession_nianhao(self):
        """新君登基默认新年号（不继承前帝）。"""
        return self.get_unique_nianhao(reason=nh.REASON_ACCESSION)
