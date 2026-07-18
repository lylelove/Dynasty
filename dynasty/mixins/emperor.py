# -*- coding: utf-8 -*-
"""皇帝年岁与驾崩、庙号谥号史评、年号纪年、新君登基。"""
import math
import random
from dynasty.models import Person, roll_ability


class EmperorMixin:
    """皇帝年岁与驾崩、庙号谥号史评、年号纪年、新君登基。"""

    def start_new_emperor_nianhao_history(self):
        self.current_emperor_nianhao_history = [{
            "nianhao": self.yearNumber,
            "years": 0
        }]

    def record_current_year_for_nianhao(self):
        if not self.current_emperor_nianhao_history:
            self.start_new_emperor_nianhao_history()

        current = self.current_emperor_nianhao_history[-1]
        if current["nianhao"] != self.yearNumber:
            self.current_emperor_nianhao_history.append({
                "nianhao": self.yearNumber,
                "years": 0
            })
            current = self.current_emperor_nianhao_history[-1]

        current["years"] += 1

    def begin_next_nianhao_segment(self):
        if self.current_emperor_nianhao_history and self.current_emperor_nianhao_history[-1]["nianhao"] == self.yearNumber:
            return
        self.current_emperor_nianhao_history.append({
            "nianhao": self.yearNumber,
            "years": 0
        })

    def build_nianhao_summary(self, nianhao_history):
        if not nianhao_history:
            return ""
        parts = []
        for item in nianhao_history:
            years = item.get("years", 0)
            label = item.get("nianhao", "")
            if years <= 0:
                continue
            parts.append(f"{label}{years}年")
        return "、".join(parts)

    def gamemin_emperor(self):
        if self.dynasty_hp > 0:
            if self.emperor_hp > 0:
                self.emperor_age += 1
                self.jinian += 1
                self.emperor_hp -= 1

                # Sync emperor's age with Person object
                emp_person = self.get_person_by_id(self.current_emperor_pid)
                if emp_person:
                    emp_person.age = self.emperor_age
                    emp_person.hp = self.emperor_hp

            if self.emperor_hp <= 0:
                # Mark person as dead
                emp_person = self.get_person_by_id(self.current_emperor_pid)
                if emp_person:
                    emp_person.hp = 0
                    emp_person.is_alive = False
                    emp_person.death_year = self.year

                if self.ongame:
                    self.gamemin_shihao()
                    if emp_person:
                        emp_person.shihao = self.shihao
                        emp_person.miaohao = self.miaohao

                    self.emperor_die = True
                    self.gamemin_emperor_change()
                    self.emperor_hp = 0

                    # Find successor
                    succ_id = self.find_successor()
                    if succ_id is None:
                        # No successor found, dynasty ends
                        # 上方 gamemin_emperor_change() 已记录末帝，此处不可再记，否则重复
                        self.ongame = False
                        self.dynasty_die = True
                        self.dynasty_hp = 0
                        self.show_end_game_dialog()
                    else:
                        # If the successor had a title, reclaim it so it can be used again
                        succ = self.get_person_by_id(succ_id)
                        if succ and succ.has_title and succ.title_name:
                            self.available_title_pools.setdefault(succ.title_rank, []).append(succ.title_name)
                            succ.has_title = False

                        self.next_emperor_pid = succ_id
                        self.ongame = False
                        self.auto_accession()
                else:
                    self.emperor_hp = 0
                    self.emperor_die = True

    def track_reign_dynasty_fortune(self):
        """逐年记录本帝在位期间国运峰值与谷值。"""
        hp = self.dynasty_hp
        if not hasattr(self, "reign_peak_dynasty_hp"):
            self.reign_peak_dynasty_hp = hp
            self.reign_trough_dynasty_hp = hp
            return
        if hp > self.reign_peak_dynasty_hp:
            self.reign_peak_dynasty_hp = hp
        if hp < self.reign_trough_dynasty_hp:
            self.reign_trough_dynasty_hp = hp

    def reset_reign_fortune_tracking(self, dynasty_hp=None):
        """新君登基时重置在位国运轨迹。"""
        hp = self.dynasty_hp if dynasty_hp is None else dynasty_hp
        self.initial_dynasty_hp = hp
        self.reign_peak_dynasty_hp = hp
        self.reign_trough_dynasty_hp = hp

    def _reign_years(self):
        history = self.current_emperor_nianhao_history or []
        return sum(item.get("years", 0) for item in history)

    def evaluate_reign_merit(self):
        """
        按整个在位期间的功绩评定：国运轨迹 + 在位年数 + 治国手腕。
        返回 merit 分（越高越贤明）与标签集合。
        """
        start = getattr(self, "initial_dynasty_hp", self.dynasty_hp)
        end = self.dynasty_hp
        peak = getattr(self, "reign_peak_dynasty_hp", max(start, end))
        trough = getattr(self, "reign_trough_dynasty_hp", min(start, end))
        net = end - start
        swing_up = peak - start
        swing_down = start - trough
        reign_years = self._reign_years()
        ab = self.emperor_ab
        dynasty_fallen = end <= 0 or self.dynasty_die

        # —— 国运净变（在位终局）——
        merit = net / 4.0

        # —— 轨迹：中兴（低开高走/曾大幅回升）与崩坏（高开低走/深谷）——
        if net >= 12 or (start <= 45 and end >= start + 15):
            merit += 4.0
        elif net >= 6:
            merit += 2.0
        if swing_up >= 20 and net > 0:
            merit += 2.5
        if swing_down >= 25 and net < 0:
            merit -= 3.0
        if swing_down >= 40:
            merit -= 2.0

        # 长期维持高国运（守成盛世）
        if peak >= 85 and trough >= 55 and net >= -5:
            merit += 3.0
        elif peak >= 75 and trough >= 40 and net >= -8:
            merit += 1.5

        # 末年崩坏或亡国
        if dynasty_fallen:
            merit -= 8.0
        elif end < 20 and net < -15:
            merit -= 4.0
        elif end < 30 and net < -10:
            merit -= 2.0

        # —— 在位年数：久理朝政方见功过，短祚权重略减、久任放大轨迹——
        if reign_years >= 40:
            merit += 3.0
        elif reign_years >= 25:
            merit += 2.0
        elif reign_years >= 15:
            merit += 1.0
        elif reign_years >= 8:
            merit += 0.3
        elif reign_years <= 2:
            merit -= 1.5
        elif reign_years <= 5:
            merit -= 0.5

        # 久任而国运大坏，罪更重；久任而中兴，功更著
        if reign_years >= 15:
            merit += net / 10.0

        # —— 治国手腕：能力是基础，但不压过全程国运功绩——
        merit += (ab - 5) * 0.85
        if ab >= 9 and net >= 0:
            merit += 1.5
        if ab <= 3 and net <= 0:
            merit -= 1.5

        # 标签（用于史评措辞）
        tags = set()
        if self.emperor_id == 1:
            tags.add("founder")
        if dynasty_fallen:
            tags.add("fallen")
        if net >= 15 or (start <= 40 and end >= start + 20):
            tags.add("zhongxing")
        if peak >= 90 and trough >= 60 and net >= -3 and reign_years >= 12:
            tags.add("shengshi")
        if net >= 6 and "zhongxing" not in tags and "shengshi" not in tags:
            tags.add("youwei")
        if abs(net) <= 8 and trough >= 35 and not dynasty_fallen and reign_years >= 8:
            tags.add("shoucheng")
        if net <= -12 or (swing_down >= 30 and net < 0):
            tags.add("shuai")
        if reign_years <= 3:
            tags.add("duanzuo")
        if reign_years >= 30:
            tags.add("jiuren")
        if ab >= 8:
            tags.add("nengchen")
        if ab <= 3:
            tags.add("nengruo")

        return {
            "merit": merit,
            "tags": tags,
            "net": net,
            "start": start,
            "end": end,
            "peak": peak,
            "trough": trough,
            "reign_years": reign_years,
            "ability": ab,
            "dynasty_fallen": dynasty_fallen,
        }

    def _pick_unique_miaohao(self, pool, fallback=None):
        available = list(set(pool) - set(self.used_miaohao))
        if available:
            return random.choice(available)
        return fallback

    def _assign_miaohao_from_merit(self, eval_result):
        merit = eval_result["merit"]
        tags = eval_result["tags"]
        fallen = eval_result["dynasty_fallen"]

        if self.emperor_id == 1:
            self.miaohao = self._pick_unique_miaohao(self.emperor_miaohao_founders, "高祖")
        else:
            # 庙号依全程功绩分档，亡国/大衰优先末代池
            if fallen or merit < -8:
                target_pool = self.emperor_miaohao_decline
            elif merit >= 8 or "shengshi" in tags or "zhongxing" in tags:
                target_pool = self.emperor_miaohao_prosperous
            elif merit >= -3:
                target_pool = self.emperor_miaohao_stable
            else:
                target_pool = self.emperor_miaohao_decline

            self.miaohao = self._pick_unique_miaohao(target_pool)
            if not self.miaohao:
                for fallback_pool in [
                    self.emperor_miaohao_prosperous,
                    self.emperor_miaohao_stable,
                    self.emperor_miaohao_decline,
                ]:
                    self.miaohao = self._pick_unique_miaohao(fallback_pool)
                    if self.miaohao:
                        break
            if not self.miaohao:
                self.miaohao = "元宗"

        self.used_miaohao.append(self.miaohao)

    def _assign_shihao_from_merit(self, eval_result):
        merit = eval_result["merit"]
        tags = eval_result["tags"]
        fallen = eval_result["dynasty_fallen"]

        # 开国例用褒谥；其余依全程功绩；恶谥仅明显败坏或亡国
        if self.emperor_id == 1:
            core_pool = self.emperor_shifa_core_good
            assist_pool = self.emperor_shifa_assist_good
            grade = "good"
        elif fallen or merit < -6:
            core_pool = self.emperor_shifa_core_bad
            assist_pool = self.emperor_shifa_assist_bad
            grade = "bad"
        elif merit >= 10 or "shengshi" in tags or ("zhongxing" in tags and merit >= 6):
            core_pool = self.emperor_shifa_core_good
            assist_pool = self.emperor_shifa_assist_good
            grade = "good"
        elif merit >= -2:
            core_pool = self.emperor_shifa_core_mid
            assist_pool = self.emperor_shifa_assist_mid
            grade = "mid"
        else:
            # 偏衰但不至于恶谥：仍用中谥，避免轻用恶谥
            core_pool = self.emperor_shifa_core_mid
            assist_pool = self.emperor_shifa_assist_mid
            grade = "mid"
            if merit < -4:
                core_pool = self.emperor_shifa_core_bad
                assist_pool = self.emperor_shifa_assist_bad
                grade = "bad"

        candidate_pool = []
        for _ in range(80):
            core = random.choice(core_pool)
            use_assist = random.random() < 0.45
            if use_assist:
                assist = random.choice(assist_pool)
                if assist != core:
                    candidate_pool.append(f"{core}{assist}皇帝")
            candidate_pool.append(f"{core}皇帝")

        # 极盛之治可上美谥长号
        if grade == "good" and merit >= 14 and eval_result["reign_years"] >= 15:
            candidate_pool.extend([
                "文武圣德皇帝",
                "睿文广孝皇帝",
                "英武景成皇帝",
                "钦文睿武皇帝",
                "文明武德皇帝",
            ])

        unique_candidate = None
        for candidate in candidate_pool:
            if candidate not in self.used_shihao:
                unique_candidate = candidate
                break

        if not unique_candidate:
            if grade == "good":
                fallback_core = "文"
            elif grade == "bad":
                fallback_core = "哀"
            else:
                fallback_core = "恭"
            unique_candidate = f"{fallback_core}皇帝"
            while unique_candidate in self.used_shihao:
                unique_candidate = f"{fallback_core}{random.choice(['安', '简', '昭', '悼'])}皇帝"

        self.used_shihao.append(unique_candidate)
        self.shihao = unique_candidate

    def _assign_verdict_from_merit(self, eval_result):
        merit = eval_result["merit"]
        tags = eval_result["tags"]
        years = eval_result["reign_years"]
        net = eval_result["net"]

        if "founder" in tags:
            self.verdict = "开国之君，肇基宏业"
            return

        if "fallen" in tags:
            if years <= 3:
                self.verdict = random.choice([
                    "短祚亡国，宗社倾覆",
                    "在位日浅，国祚遽绝",
                    "末帝仓皇，宗庙毁绝",
                ])
            elif merit < -12:
                self.verdict = random.choice([
                    "亡国之君，宗庙毁绝",
                    "暴虐无道，天下大乱",
                    "失德失政，社稷丘墟",
                ])
            else:
                self.verdict = random.choice([
                    "国运已尽，回天乏术",
                    "末世嗣君，难支大厦",
                    "时势倾颓，终致亡国",
                ])
            return

        if "shengshi" in tags or merit >= 14:
            self.verdict = random.choice([
                "千古一帝，开创盛世",
                "文治武功，威震海内",
                "一代明君，泽被苍生",
                "在位日久，海内乂安",
            ])
        elif "zhongxing" in tags or merit >= 8:
            picks = [
                "中兴之主，力挽狂澜",
                "知人善任，励精图治",
                "再造乾坤，国势复振",
            ]
            if years >= 20:
                picks.append("久理朝政，终成中兴")
            self.verdict = random.choice(picks)
        elif "youwei" in tags or merit >= 4:
            self.verdict = random.choice([
                "守成有余，天下太平",
                "勤政有为，国运渐隆",
                "治绩可观，朝野称颂",
            ])
        elif "shoucheng" in tags or merit >= 0:
            self.verdict = random.choice([
                "平庸无为，守成之君",
                "功过参半，治政平平",
                "因循守旧，乏善可陈",
            ])
            if "duanzuo" in tags:
                self.verdict = random.choice([
                    "在位日浅，未展宏图",
                    "短祚嗣君，史载寥寥",
                ])
        elif merit >= -6:
            picks = [
                "宠信奸佞，朝政日非",
                "好大喜功，劳民伤财",
                "昏庸无道，纲纪败坏",
            ]
            if net <= -15 and years >= 15:
                picks.append("在位虽久，国势日颓")
            self.verdict = random.choice(picks)
        else:
            self.verdict = random.choice([
                "失德败政，国势倾颓",
                "暴虐无道，天下离心",
                "沉迷酒色，丧权辱国",
            ])

    def gamemin_shihao(self):
        """驾崩/亡国时，据整个在位期间的功绩认定庙号、谥号与史评。"""
        self.track_reign_dynasty_fortune()
        eval_result = self.evaluate_reign_merit()
        self._last_reign_merit = eval_result

        self._assign_miaohao_from_merit(eval_result)
        self._assign_shihao_from_merit(eval_result)
        self._assign_verdict_from_merit(eval_result)

    def _record_emperor(self):
        nianhao_history = [dict(item) for item in self.current_emperor_nianhao_history if item.get("years", 0) > 0]
        total_reign_years = sum(item["years"] for item in nianhao_history)
        merit_info = getattr(self, "_last_reign_merit", None) or {}
        self.listjson.append({
            "id": self.emperor_id,
            "name": self.emperor,
            "nianhao_history": nianhao_history,
            "nianhao": self.build_nianhao_summary(nianhao_history),
            "age": self.emperor_age,
            "jinian": total_reign_years,
            "miaohao": self.miaohao,
            "shihao": self.shihao,
            "ab": self.emperor_ab,
            "verdict": self.verdict,
            "merit": round(merit_info.get("merit", 0), 2),
            "dynasty_hp_start": merit_info.get("start"),
            "dynasty_hp_end": merit_info.get("end"),
            "dynasty_hp_peak": merit_info.get("peak"),
            "dynasty_hp_trough": merit_info.get("trough"),
        })

    def gamemin_emperor_change(self):
        self._record_emperor()

    def gamemin_emperor_new(self):
        self.dynasty_hp -= 2
        if self.dynasty_hp <= 0:
            self.dynasty_hp = 1
        self.jinian = 1

        # Inherit from the chosen successor, or generate a new ruler if none exists
        if self.next_emperor_pid:
            succ = self.get_person_by_id(self.next_emperor_pid)
        else:
            succ = None

        if succ:
            # 新君对话框可能已改名：以 self.emperor 为准并回写人物，避免被旧名覆盖
            if self.emperor and self.emperor != succ.name:
                succ.name = self.emperor
            else:
                self.emperor = succ.name
            self.emperor_age = succ.age
            self.emperor_ab = succ.ability
            # 登基时按年龄重算余寿，避免幼年低天寿继承导致壮年即崩
            self.emperor_new_hp()
            succ.hp = self.emperor_hp
            succ.title = "皇帝"
            succ.is_heir = False
            succ.has_title = False
            succ.title_name = ""
            succ.title_rank = 0  # 即帝位，爵位品级归零，不再保留旧封号
            self.current_emperor_pid = succ.id
            self.next_emperor_pid = None
        else:
            # 兜底：继位人物对象缺失（如已被裁剪）时生成新君并入宗谱，
            # 避免 current_emperor_pid 仍指向已故皇帝导致其数据被逐年改写
            old_emp = self.get_person_by_id(self.current_emperor_pid)
            gen = (old_emp.generation + 1) if old_emp else 1
            self.emperor_new_age()
            self.emperor_ab = roll_ability()
            self.emperor_new_hp()
            self.emperor = self.get_random_name("M", generation=gen)
            self.used_emperor_names.append(self.emperor)
            new_emp = Person(
                self.next_pid, self.emperor, "M",
                self.year - self.emperor_age, None, None, gen,
            )
            new_emp.age = self.emperor_age
            new_emp.hp = self.emperor_hp
            new_emp.ability = self.emperor_ab
            new_emp.title = "皇帝"
            self._register_person(new_emp)
            self.current_emperor_pid = new_emp.id
            self.next_pid += 1
            succ = new_emp

        self.emperor_zunhao = self.generate_zunhao()
        if succ:
            succ.zunhao = self.emperor_zunhao

        self.reset_reign_fortune_tracking()

    def emperor_new_hp(self):
        # 大一统皇帝终年大致 48–72（均值约 58），与宗室天寿同一量级
        target_lifespan = 48 + math.floor(random.random() * 25)
        self.emperor_hp = target_lifespan - self.emperor_age

        # 至少在位数年；高龄继位者仍给 3–10 年
        if self.emperor_hp <= 0:
            self.emperor_hp = 3 + math.floor(random.random() * 8)

    def emperor_new_age(self):
        # A realistic succession age: an adult heir is usually 15-40 years old
        self.emperor_age = 15 + math.floor(random.random() * 25)

    def auto_accession(self):
        """新君自动登基：沿用储君姓名，自动取新年号，不弹窗。"""
        if self.next_emperor_pid is not None:
            succ = self.get_person_by_id(self.next_emperor_pid)
            if succ:
                self.emperor = succ.name
        self.yearNumber = self.suggest_accession_nianhao()
        self.commit_nianhao(self.yearNumber)
        self.dio()

    def dio(self):
        self.emperor_die = False
        self.gamemin_emperor_new()
        self.start_new_emperor_nianhao_history()
        self.emperor_id += 1
        self.ongame = True
        self.update_ui()

