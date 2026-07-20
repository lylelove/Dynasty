# -*- coding: utf-8 -*-
"""爵位/封号抽取、在世称号格式化、宗室谥号与封爵继承（明制宗藩）。"""
import random


class TitlesMixin:
    """爵位/封号抽取、在世称号格式化、宗室谥号与封爵继承。

    明制宗藩爵等（title_rank）：
      1 亲王（称「某王」，世袭罔替）  2 郡王（双字封号，世袭罔替）
      3 镇国将军  4 辅国将军  5 奉国将军
      6 镇国中尉  7 辅国中尉  8 奉国中尉（世代皆奉国中尉，不再降）
    亲王/郡王嫡长袭爵不降等，余子降一等；将军中尉诸子皆降一等，无封号不承袭。
    """

    # 明制八等；仅亲王/郡王有封号并可承袭
    RANK_MAX = 8
    FIEF_RANKS = (1, 2)
    # 有「世子/长子」正式称谓的爵等（亲王世子、郡王长子）
    HEIR_TITLE_RANKS = (1, 2)

    def get_rank_suffix(self, rank):
        """封号后缀：亲王/郡王皆称「王」，将军中尉即职名。"""
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
            1: "亲王", 2: "郡王", 3: "镇国将军", 4: "辅国将军",
            5: "奉国将军", 6: "镇国中尉", 7: "辅国中尉", 8: "奉国中尉",
        }
        return short.get(rank, "—")

    def format_enfeoffed_title(self, title_name, rank, shihao=""):
        """
        拼在世/谥号称号（明制）。
        亲王：秦王 / 秦愍王
        郡王：永兴王 / 永兴恭定王
        将军中尉：无封号，直接返回职名（不加谥）。
        """
        if rank in self.FIEF_RANKS:
            if not title_name:
                return ""
            suffix = self.get_rank_suffix(rank)
            return f"{title_name}{shihao}{suffix}" if shihao else f"{title_name}{suffix}"
        if 3 <= rank <= self.RANK_MAX:
            return self.get_rank_label(rank)
        return ""

    def get_guobie(self, person):
        """皇亲国戚的国别。皇帝归皇室；王爵归其封国；将军中尉归所属王府支系。"""
        if (person.id == self.current_emperor_pid or person.title == "皇帝"
                or person.title == "太子" or person.miaohao):
            return "皇室"
        if person.title_name:
            return person.title_name
        branch = self.get_clan_branch(person)
        if branch:
            return branch
        return "未封"

    def draw_title_name(self, rank):
        if rank not in self.FIEF_RANKS:
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
        # 将军中尉无封号，授爵后直接以职名相称
        if person.has_title and 3 <= person.title_rank <= self.RANK_MAX:
            return self.get_rank_label(person.title_rank)
        if person.is_heir:
            father = self.get_person_by_id(person.father_id)
            if father and father.title_name and father.title_rank in self.HEIR_TITLE_RANKS:
                return f"{father.title_name}{self.get_heir_posthumous_suffix(father)}"
            if father and father.id == self.current_emperor_pid:
                return "皇太子"
        return ""

    def get_heir_posthumous_suffix(self, father):
        """明制：皇子为皇太子；亲王嫡长称「某王世子」；郡王嫡长称「某王长子」。"""
        if father:
            if father.id == self.current_emperor_pid:
                return "皇太子"
            if father.title_rank == 1:
                return "王世子"
            if father.title_rank == 2:
                return "王长子"
        return "世子"

    def _family_posthumous_age_ok(self, token, age):
        """宗室谥字是否与享年相称：殇仅幼殇，冲仅幼冲，悼不宜高寿。"""
        if not token:
            return True
        age = age or 0
        if "殇" in token:
            return age < 20
        if "少" in token:
            return age < 25
        if "沖" in token or "冲" in token:
            return age < 18
        if "悼" in token:
            return age < 45
        return True

    def _pick_family_posthumous(self, pool, age, fallback="恭"):
        eligible = [w for w in pool if self._family_posthumous_age_ok(w, age)]
        if not eligible:
            eligible = [w for w in pool if "殇" not in w and "少" not in w and "冲" not in w and "沖" not in w]
        if not eligible:
            return fallback
        return random.choice(eligible)

    def choose_family_posthumous_word(self, person):
        context_score = person.ability
        age = person.age or 0
        if age >= 60:
            context_score += 2
        elif age < 20:
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

        # 幼殇专用：未成童而夭
        if age < 8:
            return random.choice(["殇", "悼"])
        if person.title == "太子":
            pool = self.taizi_shihao_good if context_score >= 8 else self.taizi_shihao_neutral
            if context_score <= 3:
                pool = self.taizi_shihao_bad
            return self._pick_family_posthumous(pool, age, fallback="悼" if age < 45 else "愍")

        if context_score >= 8:
            pool = self.prince_shihao_good
        elif context_score >= 4:
            pool = self.prince_shihao_neutral
        else:
            pool = self.prince_shihao_bad

        core = self._pick_family_posthumous(pool, age, fallback="恭")

        # 明制：亲王一字谥（秦愍王）；郡王例用双字谥（永兴恭定王）
        if person.title_rank == 2:
            assist_pool = [
                a for a in self.prince_shihao_assist
                if a != core and self._family_posthumous_age_ok(a, age)
            ]
            if assist_pool:
                return f"{core}{random.choice(assist_pool)}"
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

    def _grant_initial_titles(self):
        """成年授爵（明制年十岁受封，游戏取 10 岁）。

        - 亲王/郡王：非世子者抽封号开府；世子不另封，待承袭
        - 将军中尉：无封号，直接授职
        """
        for p in self.people:
            if (
                not p.is_alive
                or p.gender != "M"
                or p.age < 10
                or p.has_title
                or p.id == self.current_emperor_pid
                or not (1 <= p.title_rank <= self.RANK_MAX)
            ):
                continue

            if p.title_rank in self.FIEF_RANKS:
                # 王世子/王长子不另封，等袭父爵
                if p.is_heir:
                    continue
                if not p.title_name:
                    p.title_name = self.draw_title_name(p.title_rank)
                if p.title_name:
                    p.has_title = True
            else:
                # 将军中尉：即授职名
                p.has_title = True

    def _inherit_fief(self, deceased):
        """王府承袭（仅亲王/郡王）：嫡长（含代位）袭同封同爵（世袭罔替）；
        无后则过继侄嗣承封；再无则除国、封号还池。"""
        # 现任皇帝/储君不得承袭藩爵（其支系跳过）
        exclude = {
            pid for pid in (self.current_emperor_pid, self.next_emperor_pid)
            if pid is not None
        }
        heir = self.find_heir_of_line(deceased, exclude_ids=exclude)
        if heir and heir.id == deceased.id:
            heir = None

        if heir:
            self._transfer_fief(deceased, heir)
            return

        adoptee = self.find_adoptee(deceased)
        if adoptee:
            # 过继入嗣：改父系与子女链，使代位/绝嗣/世系树一致
            self.apply_adoption(deceased, adoptee)
            deceased.extinct = False
            if deceased.title_name:
                self._transfer_fief(deceased, adoptee)
            return

        deceased.extinct = self.check_extinct(deceased.id)
        if deceased.title_name:
            self.available_title_pools.setdefault(
                deceased.title_rank, []
            ).append(deceased.title_name)
            deceased.has_title = False

    def _transfer_fief(self, deceased, heir):
        """将王府封号移交承袭人；承袭人原有王府封号退还池。"""
        if heir.has_title and heir.title_name and heir.title_name != deceased.title_name:
            self.available_title_pools.setdefault(
                heir.title_rank, []
            ).append(heir.title_name)
        heir.title_name = deceased.title_name
        heir.title_rank = deceased.title_rank
        heir.has_title = True
        heir.is_heir = False  # 已袭爵为国主，不再是世子
        deceased.has_title = False

    def gamemin_family_shihao_titles(self):
        self._grant_initial_titles()

        for p in self.people:
            if p.is_alive:
                p.title = self.format_alive_title(p)

            if not p.is_alive and p.death_year == self.year:
                # 谥号：太子、亲王、郡王及王世子/王长子；将军中尉无谥
                if not p.shihao and (
                    p.title == "太子"
                    or (p.has_title and p.title_rank in self.FIEF_RANKS)
                    or (p.is_heir and self._heir_of_fief(p))
                ):
                    p.shihao = self.build_family_posthumous_title(p)

                # 封爵承袭：仅亲王/郡王世袭罔替；将军中尉身故无承袭
                if p.gender == "M" and p.has_title and p.title_rank in self.FIEF_RANKS:
                    self._inherit_fief(p)

    def _heir_of_fief(self, person):
        """是否为亲王/郡王（或皇帝）之储贰，身后可得世子/长子谥。"""
        father = self.get_person_by_id(person.father_id)
        if not father:
            return False
        if father.id == self.current_emperor_pid:
            return True
        return father.title_rank in self.HEIR_TITLE_RANKS and bool(father.title_name)
