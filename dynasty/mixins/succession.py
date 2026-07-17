# -*- coding: utf-8 -*-
"""嫡长继承、代位、储君、兄终弟及与皇位继承人查找。"""


class SuccessionMixin:
    """嫡长继承、代位、储君、兄终弟及与皇位继承人查找。"""

    def get_sons_by_birth(self, person, alive_only=True):
        """嫡长序：按出生年、再按 id（同年出生先生成者为长）。"""
        sons = []
        for child_id in person.children:
            child = self.get_person_by_id(child_id)
            if child and child.gender == "M":
                if alive_only and not child.is_alive:
                    continue
                sons.append(child)
        sons.sort(key=lambda c: (c.birth_year, c.id))
        return sons

    def get_eldest_living_son(self, person):
        sons = self.get_sons_by_birth(person, alive_only=True)
        return sons[0] if sons else None

    def find_heir_of_line(self, person):
        """
        嫡长子继承（含代位继承）：
        诸子按出生序；长子在则长子继；长子已故则长子之长子（孙）代位，以此类推。
        """
        for son in self.get_sons_by_birth(person, alive_only=False):
            if son.is_alive:
                return son
            heir = self.find_heir_of_line(son)
            if heir:
                return heir
        return None

    def update_heirs(self):
        # 每位有爵/皇帝：嫡长（含代位）为世子——长子在则长子，长子已故则长子一系代位
        for p in self.people:
            is_current_emperor = (p.id == self.current_emperor_pid)
            if p.gender == "M" and ((p.is_alive and p.has_title) or is_current_emperor):
                rightful = self.find_heir_of_line(p)
                # 先清空本支直接诸子的世子标记，再标正统（可能是孙）
                for child_id in p.children:
                    child = self.get_person_by_id(child_id)
                    if child and child.gender == "M":
                        child.is_heir = False
                if rightful and rightful.is_alive:
                    rightful.is_heir = True

    def update_crown_prince(self):
        self.update_heirs()
        self.next_emperor_pid = None

        emp = self.get_person_by_id(self.current_emperor_pid) if self.current_emperor_pid else None
        if not emp:
            return

        # 储君 = 皇帝嫡长子（在世诸子中出生最早者）；若长子已故则由长子一系代位
        rightful = self.find_heir_of_line(emp)

        # 撤去非正统的「太子」头衔
        for p in self.people:
            if p.is_alive and p.title == "太子":
                if not rightful or p.id != rightful.id:
                    p.title = ""
                    p.title = self.format_alive_title(p)

        if not rightful or not rightful.is_alive:
            return

        # 太子收回私封，专任储君
        if rightful.title_name and rightful.has_title:
            self.available_title_pools.setdefault(rightful.title_rank, []).append(rightful.title_name)
            rightful.has_title = False
            rightful.title_name = ""

        rightful.is_heir = True
        rightful.title = "太子"
        self.next_emperor_pid = rightful.id

    def find_collateral_successor(self, deceased):
        """
        无直系男嗣时：兄终弟及，再及侄；再向上寻叔伯一系。
        严格按父系、出生顺序，不按年龄乱序挑人。
        """
        if not deceased:
            return None

        # 1) 已故皇帝的男系后裔（含代位）——调用方通常已查过，此处再兜底
        heir = self.find_heir_of_line(deceased)
        if heir and heir.id != deceased.id:
            return heir.id

        # 2) 自本人向上：先尽诸弟及其后裔，再及更旁的兄弟支
        current = deceased
        visited_fathers = set()
        while current and current.father_id is not None:
            father = self.get_person_by_id(current.father_id)
            if not father or father.id in visited_fathers:
                break
            visited_fathers.add(father.id)

            brothers = self.get_sons_by_birth(father, alive_only=False)
            # 定位 current 在兄弟中的位置，优先「弟」及其后裔（兄终弟及）
            idx = next((i for i, b in enumerate(brothers) if b.id == current.id), None)
            if idx is not None:
                for bro in brothers[idx + 1:]:
                    if bro.is_alive and bro.id != deceased.id:
                        return bro.id
                    line_heir = self.find_heir_of_line(bro)
                    if line_heir and line_heir.id != deceased.id:
                        return line_heir.id

                # 诸弟绝：再看兄长一系（兄已故时其孙可继）
                for bro in brothers[:idx]:
                    if bro.id == deceased.id:
                        continue
                    if bro.is_alive:
                        return bro.id
                    line_heir = self.find_heir_of_line(bro)
                    if line_heir and line_heir.id != deceased.id:
                        return line_heir.id

            current = father

        # 3) 仍无：宗室在世男丁，按代数升序、同代按出生序
        candidates = [
            p for p in self.people
            if p.is_alive and p.gender == "M" and p.id != deceased.id
        ]
        if not candidates:
            return None
        candidates.sort(key=lambda x: (x.generation, x.birth_year, x.id))
        return candidates[0].id

    def find_successor(self):
        self.update_crown_prince()
        if self.next_emperor_pid:
            p = self.get_person_by_id(self.next_emperor_pid)
            if p and p.is_alive:
                return self.next_emperor_pid

        emp = self.get_person_by_id(self.current_emperor_pid) if self.current_emperor_pid else None
        if emp:
            # 直系嫡长（含代位）
            heir = self.find_heir_of_line(emp)
            if heir:
                return heir.id
            return self.find_collateral_successor(emp)
        return self.find_collateral_successor(emp)

