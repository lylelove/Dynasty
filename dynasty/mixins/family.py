# -*- coding: utf-8 -*-
"""宗室人物查询、衰老死亡、婚育、过继、封国汇总。"""
import random
from dynasty.models import Person


class FamilyMixin:
    """宗室人物查询、衰老死亡、婚育、过继、封国汇总。"""

    # 人物过多时裁剪；仅亲王/郡王（rank≤2）可繁衍；在世过多时进一步收紧
    PRUNE_THRESHOLD = 100
    BREED_RANK_MAX = 2
    MAX_LIVING_SONS = 5
    SOFT_ALIVE_CAP = 55
    HARD_ALIVE_CAP = 90

    def get_person_by_id(self, pid):
        if pid is None:
            return None
        by_id = getattr(self, "people_by_id", None)
        if by_id is not None:
            return by_id.get(pid)
        for p in self.people:
            if p.id == pid:
                return p
        return None

    def _register_person(self, person):
        self.people.append(person)
        if not hasattr(self, "people_by_id") or self.people_by_id is None:
            self.people_by_id = {}
        self.people_by_id[person.id] = person

    def rebuild_people_index(self):
        self.people_by_id = {p.id: p for p in self.people}

    def gamemin_family_aging_death(self):
        for p in self.people:
            if p.is_alive and p.id != self.current_emperor_pid:
                p.age += 1
                p.hp -= 1
                if p.hp <= 0:
                    p.is_alive = False
                    p.death_year = self.year

    def get_descendants(self, pid):
        descendants = []
        p = self.get_person_by_id(pid)
        if p:
            for child_id in p.children:
                descendants.append(child_id)
                descendants.extend(self.get_descendants(child_id))
        return descendants

    def check_extinct(self, pid):
        p = self.get_person_by_id(pid)
        if not p or p.gender != "M":
            return False

        # Check if any male descendants are alive
        descendant_ids = self.get_descendants(pid)
        has_alive_male_heir = False
        for d_id in descendant_ids:
            d = self.get_person_by_id(d_id)
            if d and d.gender == "M" and d.is_alive:
                has_alive_male_heir = True
                break

        return not has_alive_male_heir

    def find_adoptee(self, person):
        """过继：择兄弟之子（侄）中尚存者承嗣，优先未受封、年长者，以减少绝嗣。"""
        father_id = person.father_id
        if father_id is None:
            return None

        candidates = []
        for sib in self.people:
            if sib.id == person.id or sib.father_id != father_id or sib.gender != "M":
                continue
            for child_id in sib.children:
                child = self.get_person_by_id(child_id)
                if child and child.gender == "M" and child.is_alive:
                    # 已过继给他人者不可再过继
                    if child.father_id != sib.id:
                        continue
                    candidates.append(child)

        if not candidates:
            return None

        # 优先未受封者（可继承本支封国），其次年长者
        candidates.sort(key=lambda c: (0 if not c.has_title else 1, -c.age))
        return candidates[0]

    def apply_adoption(self, adoptive_father, adoptee):
        """
        过继入嗣（宗法）：
        - adopted_from 记本生父；
        - father_id 改嗣父，并迁入嗣父 children；
        - 代数随嗣父，并下推其已有后裔，便于世系与字辈一致。
        """
        if not adoptive_father or not adoptee:
            return
        if adoptee.id == adoptive_father.id:
            return

        bio_father_id = adoptee.father_id
        if adoptee.adopted_from is None:
            adoptee.adopted_from = bio_father_id

        bio_father = self.get_person_by_id(bio_father_id) if bio_father_id is not None else None
        if bio_father and adoptee.id in bio_father.children:
            bio_father.children = [c for c in bio_father.children if c != adoptee.id]

        adoptee.father_id = adoptive_father.id
        if adoptee.id not in adoptive_father.children:
            adoptive_father.children.append(adoptee.id)

        new_gen = adoptive_father.generation + 1
        delta = new_gen - adoptee.generation
        adoptee.generation = new_gen
        if delta:
            for d_id in self.get_descendants(adoptee.id):
                d = self.get_person_by_id(d_id)
                if d:
                    d.generation += delta

    def format_person_year(self, person):
        if person.death_year >= 0:
            return f"{person.birth_year}—{person.death_year}"
        return f"{person.birth_year}—"

    def get_father_name(self, person):
        if person.father_id is None:
            return "—"
        father = self.get_person_by_id(person.father_id)
        return father.name if father else "—"

    def get_children_summary(self, person):
        names = []
        for cid in person.children:
            child = self.get_person_by_id(cid)
            if child and child.gender == "M":
                names.append(child.name)
        return "、".join(names) if names else "无"

    def is_important_person(self, person):
        """展示/保留：在世者、现任帝储、曾为帝（庙号）、现任有爵者。
        已故无后支系不靠此标记保留，由 prune 时从在世者向上补祖先。"""
        if person.is_alive:
            return True
        if person.id in (self.current_emperor_pid, self.next_emperor_pid):
            return True
        if person.miaohao:
            return True
        if person.title in ("皇帝", "太子"):
            return True
        return False

    def prune_unimportant_people(self):
        """裁剪无在世后裔的已故旁支；保留全部在世者及其父系祖先、历任皇帝。"""
        if len(self.people) < self.PRUNE_THRESHOLD:
            return

        keep = set()
        for p in self.people:
            if p.is_alive or p.miaohao or p.id in (self.current_emperor_pid, self.next_emperor_pid):
                keep.add(p.id)
            elif p.title in ("皇帝", "太子"):
                keep.add(p.id)

        # 现任封国主（在世 has_title）已在 is_alive 中；补在世有爵者的封号链祖先即可

        for pid in list(keep):
            p = self.get_person_by_id(pid)
            while p and p.father_id is not None:
                if p.father_id in keep:
                    break
                keep.add(p.father_id)
                p = self.get_person_by_id(p.father_id)

        if len(keep) >= len(self.people):
            return

        self.people = [p for p in self.people if p.id in keep]
        for p in self.people:
            p.children = [c for c in p.children if c in keep]
        self.rebuild_people_index()

    def collect_fiefs(self):
        """汇总现存/历史封国：有 title_name 的男系宗室按封国名聚合。"""
        fiefs = {}
        for p in self.people:
            if p.gender != "M" or not p.title_name:
                continue
            key = p.title_name
            entry = fiefs.setdefault(key, {
                "name": key,
                "rank": p.title_rank,
                "holders": [],
                "current": None,
            })
            entry["holders"].append(p)
            if p.title_rank and (entry["rank"] == 0 or p.title_rank < entry["rank"]):
                entry["rank"] = p.title_rank
            if p.is_alive and p.has_title:
                if entry["current"] is None or p.age > entry["current"].age:
                    entry["current"] = p
        # 当前持有者优先用 has_title 者；否则取该国在世最长者
        for entry in fiefs.values():
            if entry["current"] is None:
                living = [h for h in entry["holders"] if h.is_alive]
                if living:
                    living.sort(key=lambda x: (-x.has_title, x.birth_year, x.id))
                    entry["current"] = living[0]
            entry["holders"].sort(key=lambda x: (x.birth_year, x.id))
            entry["alive_count"] = sum(1 for h in entry["holders"] if h.is_alive)
            entry["total_count"] = len(entry["holders"])
            entry["extinct"] = entry["alive_count"] == 0
        result = list(fiefs.values())
        result.sort(key=lambda e: (
            0 if not e["extinct"] else 1,
            e["rank"] or 9,
            e["name"],
        ))
        return result

    def find_fief_lineage_root(self, fief_name):
        """封国世系根：该封号最早受封者（出生最早且曾持有该封号）。"""
        holders = [p for p in self.people if p.gender == "M" and p.title_name == fief_name]
        if not holders:
            return None
        holders.sort(key=lambda p: (p.birth_year, p.id))
        return holders[0]

    def try_spawn_child(self, father, child_rank):
        # 仅男系：唐制九等 1 亲王 … 9 县男；超出不再授爵
        if child_rank > 9:
            return

        child_gen = father.generation + 1
        child_name = self.get_random_name("M", generation=child_gen)
        child = Person(self.next_pid, child_name, "M", self.year, father.id, None, child_gen)
        child.title_rank = max(0, min(int(child_rank), 9))

        self._register_person(child)
        father.children.append(child.id)
        self.next_pid += 1

    def gamemin_family_marriage_birth(self):
        """男系繁衍：不生成女性与配偶，仅按年龄生育皇子/宗子。"""
        alive_count = sum(1 for p in self.people if p.is_alive)
        # 在世过多：只许皇帝生育，避免指数膨胀
        only_emperor = alive_count >= self.HARD_ALIVE_CAP
        dampen = alive_count >= self.SOFT_ALIVE_CAP

        for p in self.people:
            if not p.is_alive or p.gender != "M":
                continue

            is_emperor = (p.id == self.current_emperor_pid)
            if only_emperor and not is_emperor:
                continue

            # 仅亲王/郡王（及皇帝）繁衍；未实封的低爵不育
            if not is_emperor:
                if p.title_rank <= 0 or p.title_rank > self.BREED_RANK_MAX:
                    continue
                if not p.has_title and not p.is_heir:
                    continue

            max_age = 50 if is_emperor else 45
            if p.age < 16 or p.age > max_age:
                continue

            existing_sons = [self.get_person_by_id(cid) for cid in p.children]
            existing_sons = [s for s in existing_sons if s and s.gender == "M"]
            living_sons = [s for s in existing_sons if s.is_alive]
            son_cap = self.MAX_LIVING_SONS if is_emperor else 3
            if len(living_sons) >= son_cap:
                continue
            if not is_emperor and len(existing_sons) >= 3:
                continue

            if is_emperor:
                chance = 0.3
            elif p.title_rank == 1:
                chance = 0.07
            else:
                chance = 0.04

            if dampen:
                chance *= 0.5

            if random.random() < chance:
                # 唐制：皇子皆封亲王；宗室余子降一等
                if is_emperor:
                    child_rank = 1
                elif len(existing_sons) == 0:
                    child_rank = p.title_rank
                else:
                    child_rank = min(p.title_rank + 1, 9)

                self.try_spawn_child(p, child_rank)

                if is_emperor and len(existing_sons) == 0 and random.random() < 0.12:
                    self.try_spawn_child(p, 1)

