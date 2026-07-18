# -*- coding: utf-8 -*-
"""爵位/封号抽取、在世称号格式化、宗室谥号与封爵继承（唐制九等爵）。"""
import random


class TitlesMixin:
    """爵位/封号抽取、在世称号格式化、宗室谥号与封爵继承。

    唐制爵等（title_rank）：
      1 亲王（称「某王」）  2 郡王  3 国公  4 开国郡公
      5 开国县公  6 开国县侯  7 开国县伯  8 开国县子  9 开国县男
    """

    # 可独立授封并承袭的爵等上限（县伯及以上世子称谓；子男亦承袭）
    RANK_MAX = 9
    # 有「世子」正式称谓的爵等（王、公）
    HEIR_TITLE_RANKS = (1, 2, 3, 4, 5)

    def get_rank_suffix(self, rank):
        """封号后缀：亲王用「王」，其余用郡王/国公/县侯等。"""
        return self.rank_suffix_map.get(rank, "爵")

    def get_rank_label(self, rank):
        """界面用爵位全称。"""
        if rank == 0:
            return "帝室"
        return self.rank_full_label_map.get(
            rank, self.rank_suffix_map.get(rank, "爵")
        )

    def get_rank_short(self, rank):
        """宗藩列表等紧凑显示。"""
        short = {
            1: "王", 2: "郡王", 3: "国公", 4: "郡公", 5: "县公",
            6: "侯", 7: "伯", 8: "子", 9: "男",
        }
        return short.get(rank, "—")

    def format_enfeoffed_title(self, title_name, rank, shihao=""):
        """
        拼在世/谥号称号。
        唐制亲王：秦王 / 秦恭王（非「秦亲王」）
        郡王：彭城郡王
        国公以下：英国公、长乐郡公、武安县公…
        """
        if not title_name:
            return ""
        suffix = self.get_rank_suffix(rank)
        if rank == 1:
            # 亲王：国号 + [谥] + 王
            return f"{title_name}{shihao}{suffix}" if shihao else f"{title_name}{suffix}"
        if rank == 3:
            # 国公：国号 + [谥] + 国公（封号本身是国名时不重复「国」）
            if title_name.endswith("国"):
                base = f"{title_name}{shihao}公" if shihao else f"{title_name}公"
            else:
                base = f"{title_name}{shihao}国公" if shihao else f"{title_name}国公"
            return base
        if rank in (4, 5, 6, 7, 8, 9):
            # 郡公/县公侯伯子男：地名 + [谥] + 爵称
            return f"{title_name}{shihao}{suffix}" if shihao else f"{title_name}{suffix}"
        # 郡王等
        return f"{title_name}{shihao}{suffix}" if shihao else f"{title_name}{suffix}"

    def get_guobie(self, person):
        """皇亲国戚的国别（封国）。皇帝（含已崩者）归皇室，受封者归其封国，未受封者标未封。"""
        if (person.id == self.current_emperor_pid or person.title == "皇帝"
                or person.title == "太子" or person.miaohao):
            return "皇室"
        if person.title_name:
            return person.title_name
        return "未封"

    def draw_title_name(self, rank):
        if rank <= 0 or rank > self.RANK_MAX:
            return ""
        pool = self.available_title_pools.get(rank, [])
        if pool:
            return pool.pop(0)

        fallback_pool = self.rank_name_pools.get(rank, [])
        if fallback_pool:
            return random.choice(fallback_pool)
        return ""

    def format_alive_title(self, person):
        if person.id == self.current_emperor_pid:
            return "皇帝"
        if person.title == "太子":
            return "太子"
        if person.has_title and person.title_name:
            return self.format_enfeoffed_title(person.title_name, person.title_rank)
        if person.is_heir:
            father = self.get_person_by_id(person.father_id)
            if father and father.title_name and father.title_rank in self.HEIR_TITLE_RANKS:
                return f"{father.title_name}{self.get_heir_posthumous_suffix(father)}"
            if father and father.id == self.current_emperor_pid:
                return "皇太子"
        return ""

    def get_heir_posthumous_suffix(self, father):
        """唐制：亲王嫡子称「某王世子」，郡王/国公亦称世子；皇子为皇太子。"""
        if father:
            if father.id == self.current_emperor_pid:
                return "皇太子"
            suffix_map = {
                1: "王世子",
                2: "郡王世子",
                3: "国公世子",
                4: "郡公世子",
                5: "县公世子",
            }
            if father.title_rank in suffix_map:
                return suffix_map[father.title_rank]
        return "世子"

    def choose_family_posthumous_word(self, person):
        context_score = person.ability
        if person.age >= 60:
            context_score += 2
        elif person.age < 20:
            context_score -= 2

        if person.has_title:
            context_score += 1
        if person.is_heir:
            context_score += 1
        if person.extinct:
            context_score -= 2
        if person.title_rank in (1, 2):
            context_score += 1

        if person.death_year == self.year and self.data_dynasty_hp_change <= -5:
            context_score -= 2
        if self.dynasty_hp < 25:
            context_score -= 1

        if person.age < 8:
            return random.choice(["殇", "悼"])
        if person.title == "太子":
            pool = self.taizi_shihao_good if context_score >= 8 else self.taizi_shihao_neutral
            if context_score <= 3:
                pool = self.taizi_shihao_bad
            return random.choice(pool)

        if context_score >= 8:
            core = random.choice(self.prince_shihao_good)
        elif context_score >= 4:
            core = random.choice(self.prince_shihao_neutral)
        else:
            core = random.choice(self.prince_shihao_bad)

        # 亲王/郡王且非恶谥：有几率得双字谥（如「恭靖」「庄宪」），仿唐宋宗王
        if person.title_rank in (1, 2) and context_score >= 4 and random.random() < 0.35:
            assist = random.choice(self.prince_shihao_assist)
            if assist != core:
                return f"{core}{assist}"
        return core

    def build_family_posthumous_title(self, person):
        chosen_shihao = self.choose_family_posthumous_word(person)

        if person.title == "太子":
            return f"{chosen_shihao}太子"
        if person.has_title and person.title_name:
            return self.format_enfeoffed_title(
                person.title_name, person.title_rank, shihao=chosen_shihao
            )
        if person.is_heir:
            father = self.get_person_by_id(person.father_id)
            suffix = self.get_heir_posthumous_suffix(father)
            if father and father.title_name:
                return f"{father.title_name}{chosen_shihao}{suffix}"
            return f"{chosen_shihao}{suffix}"
        return ""

    def gamemin_family_shihao_titles(self):
        for p in self.people:
            # 唐制：男子年十五以上可授爵；世子成年前不另封，承袭后 has_title
            if (
                p.is_alive
                and p.gender == "M"
                and p.age >= 15
                and not p.title_name
                and p.id != self.current_emperor_pid
                and 1 <= p.title_rank <= self.RANK_MAX
            ):
                if not p.is_heir or (p.is_heir and p.has_title):
                    if not p.has_title:
                        p.title_name = self.draw_title_name(p.title_rank)
                        if p.title_name:
                            p.has_title = True

            if p.is_alive:
                p.title = self.format_alive_title(p)

            if not p.is_alive and p.death_year == self.year:
                if not p.shihao and (p.has_title or p.is_heir or p.title == "太子"):
                    p.shihao = self.build_family_posthumous_title(p)

                # 封爵承袭（嫡长含代位）；无后过继；再无则绝封还池
                if p.gender == "M" and p.has_title:
                    # 现任皇帝/储君不得承袭藩爵（其支系跳过）
                    exclude = {
                        pid for pid in (self.current_emperor_pid, self.next_emperor_pid)
                        if pid is not None
                    }
                    heir = self.find_heir_of_line(p, exclude_ids=exclude)
                    if heir and heir.id == p.id:
                        heir = None

                    if heir:
                        # 世子若已有私封，先退还池再承袭父爵，避免封号丢失
                        if heir.has_title and heir.title_name and heir.title_name != p.title_name:
                            self.available_title_pools.setdefault(
                                heir.title_rank, []
                            ).append(heir.title_name)
                        heir.title_name = p.title_name
                        heir.title_rank = p.title_rank
                        heir.has_title = True
                        heir.is_heir = False  # 已承袭为国主，不再是世子
                        p.has_title = False
                    else:
                        adoptee = self.find_adoptee(p)
                        if adoptee:
                            # 过继入嗣：改父系与子女链，使代位/绝嗣/世系树一致
                            self.apply_adoption(p, adoptee)
                            p.extinct = False
                            if p.title_name:
                                # 嗣子承封；若本有私封则退还池后再承嗣父之封
                                if adoptee.has_title and adoptee.title_name:
                                    self.available_title_pools.setdefault(
                                        adoptee.title_rank, []
                                    ).append(adoptee.title_name)
                                adoptee.title_name = p.title_name
                                adoptee.title_rank = p.title_rank
                                adoptee.has_title = True
                                p.has_title = False
                        else:
                            p.extinct = self.check_extinct(p.id)
                            if p.title_name:
                                self.available_title_pools.setdefault(
                                    p.title_rank, []
                                ).append(p.title_name)
                                p.has_title = False
