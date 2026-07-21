# -*- coding: utf-8 -*-
"""朝廷：内阁与六部的自动演化（老病致仕、卒于任、递补拜相）。"""
import math
import random

from dynasty.models import Minister

# 官职（明制）：内阁三级 + 六部尚书，共 11 职
POST_SHOUFU = "首辅"
POST_CIFU = "次辅"
QUNFU_POSTS = ["群辅一", "群辅二", "群辅三"]   # 内阁大学士（不分先后，界面统称群辅）
SIX_MINISTRIES = ["吏部尚书", "户部尚书", "礼部尚书", "兵部尚书", "刑部尚书", "工部尚书"]
ALL_POSTS = [POST_SHOUFU, POST_CIFU] + QUNFU_POSTS + SIX_MINISTRIES

# 致仕：65 起逐年概率上升，75 强制（首辅恋栈：概率减半，78 强制）
RETIRE_AGE = 65
RETIRE_FORCE_AGE = 75
RETIRE_FORCE_AGE_SHOUFU = 78

# 朝臣谥号（文臣以「文」字为首；文正为极品，历代不轻授）
MINISTER_SHIHAO_TOP = ["文正", "文贞", "文成", "文忠"]
MINISTER_SHIHAO_COMMON = [
    "文端", "文定", "文简", "文懿", "文肃", "文毅", "文宪", "文庄",
    "文敬", "文裕", "文节", "文靖", "文穆", "文昭", "文恪", "文恭",
    "文襄", "文清", "文安", "文和", "文敏", "文通", "文达", "文直",
    "文惠", "文良", "文静", "文慎", "文介", "文修", "文洁", "文确",
]
# 材具平庸者亦有身后之谥（略次一等，仍以文臣常谥）
MINISTER_SHIHAO_MODEST = [
    "文勤", "文恪", "文敏", "文直", "文惠", "文良", "文通", "文达",
    "文静", "文慎", "文介", "文确", "文端", "文定", "文简", "文懿",
    "文肃", "文毅", "文宪", "文庄", "文敬", "文裕", "文节", "文靖",
    "文穆", "文昭", "文恭", "文襄", "文清", "文安", "文和", "文修",
]

# 权臣：主弱（帝能力≤3）而相强（首辅能力≥8）且秉政有年
QUANCHEN_EMPEROR_AB_MAX = 3
QUANCHEN_SHOUFU_AB_MIN = 8
QUANCHEN_MIN_TENURE = 5

# 去向文案（历任表 / 弹窗 / 国史）——仿史实：不止致仕与升迁
# 码值短而稳；展示文案可随朝代语感微调
EXIT_LABELS = {
    "卒": "卒于任",
    "暴卒": "暴卒于任",
    "致仕": "致仕",
    "病免": "以疾致仕",
    "终养": "乞终养",
    "丁忧": "丁忧去位",
    "罢": "罢黜",
    "劾罢": "为言官所劾罢",
    "削职": "削职闲住",
    "外放": "外放边郡",
    "谪贬": "谪贬",
    "赐死": "赐死",
    "伏诛": "伏诛",
    "升迁": "升迁",
    "": "在任",
}

# 去职大类
EXIT_DEATH_LIKE = frozenset({"卒", "暴卒", "赐死", "伏诛"})
EXIT_NO_SHIHAO = frozenset({"伏诛", "赐死"})  # 罪死多不获美谥


def post_display(post):
    """界面/纪事用职名：群辅一/二/三统称「群辅」。"""
    return "群辅" if post in QUNFU_POSTS else post


def empty_post_history():
    """各官职历任账空表。"""
    return {p: [] for p in ALL_POSTS}


def format_term_years(start_year, end_year, current_year):
    """历任表任期文案：不用绝对年号（开局 year=0 回溯会成负数）。"""
    end = end_year if end_year is not None else current_year
    years = max(0, end - start_year)
    if end_year is None:
        if start_year < 0:
            return f"在任 {years} 年（开国前已任）"
        return f"在任 {years} 年"
    if years <= 0:
        return "未满一年"
    if start_year < 0:
        return f"任 {years} 年（开国前起）"
    return f"任 {years} 年"


class CourtMixin:
    """朝廷（内阁 + 六部）的组建、年度演化与国运影响。"""

    # —— 查询 ——

    def get_minister_by_id(self, mid):
        if mid is None:
            return None
        for m in self.ministers:
            if m.id == mid:
                return m
        return None

    def get_post_holder(self, post):
        return self.get_minister_by_id(self.court_posts.get(post))

    def get_shoufu(self):
        return self.get_post_holder(POST_SHOUFU)

    def get_post_history(self, post):
        """某职历任记录列表（可变引用）。"""
        hist = getattr(self, "post_history", None)
        if not hist:
            return []
        return hist.get(post, [])

    def get_minister_career(self, mid):
        """某朝臣各职履历，按就任年排序。每项含 post 字段。"""
        if mid is None:
            return []
        terms = []
        hist_all = getattr(self, "post_history", None) or {}
        for post in ALL_POSTS:
            for rec in hist_all.get(post) or []:
                if rec.get("mid") == mid:
                    terms.append({**rec, "post": post})
        terms.sort(key=lambda r: (r.get("start_year", 0), ALL_POSTS.index(r["post"]) if r.get("post") in ALL_POSTS else 99))
        return terms

    def _court_avg_ability(self):
        """在职朝臣均能力（1–9）；朝廷未组建时返回中平 5.0。"""
        posts = getattr(self, "court_posts", None) or {}
        abilities = []
        for mid in posts.values():
            m = self.get_minister_by_id(mid)
            if m is not None and m.is_alive and not m.retired:
                abilities.append(m.ability)
        if not abilities:
            return 5.0
        return sum(abilities) / len(abilities)

    # —— 组建与补员 ——

    def _min_career_before_post(self, post):
        """就任该职前至少须有的仕途年数（自初仕起算）。"""
        if post == POST_SHOUFU or post == POST_CIFU or post in QUNFU_POSTS:
            return 20
        return 15

    def _min_ability_for_post(self, post):
        """该职最低材具门槛（高位不宜庸才久居）。"""
        if post == POST_SHOUFU:
            return 6
        if post == POST_CIFU or post in QUNFU_POSTS:
            return 5
        return 3

    def _roll_entry_year(self, age, post, prior_tenure=0):
        """据现年、官职与已任年数，回溯初仕年。

        尚书/阁臣皆由科第历练而来，不可「刚释褐即拜尚书」。
        初仕约 22–30 岁；至尚书至少约 15 年仕途、直接入阁至少约 20 年。
        若现职已回溯 prior_tenure 年，则初仕须更早，保证「授职时」已满资历。
        """
        min_before_post = self._min_career_before_post(post)
        tenure = max(0, int(prior_tenure))
        min_total_career = min_before_post + tenure
        latest_entry_age = max(22, age - min_total_career)
        earliest_entry_age = 22
        if latest_entry_age < earliest_entry_age:
            entry_age = max(18, age - min_total_career)
        else:
            span = latest_entry_age - earliest_entry_age
            entry_age = earliest_entry_age + (
                math.floor(random.random() * (span + 1)) if span > 0 else 0
            )
        return self.year - (age - entry_age)

    def _apply_post_ability_floor(self, m, post):
        """高位能力保底：首辅/阁臣不得过庸。"""
        floor = self._min_ability_for_post(post)
        if m.ability < floor:
            m.ability = floor + math.floor(random.random() * max(1, 9 - floor + 1))
            m.ability = min(9, max(floor, m.ability))

    def recruit_minister(self, post, min_age=42, max_age=55, prior_tenure=0):
        """招募一名新朝臣就任 post（默认按尚书资历：年长且已有仕途）。

        prior_tenure: 开国时可回溯现职已任年数（中途补缺则为 0）。
        """
        age = min_age + math.floor(random.random() * (max_age - min_age + 1))
        tenure = max(0, int(prior_tenure))
        # 年龄须撑得住：初仕下限 18 + 授职前资历 + 已任年数
        min_age_needed = 18 + self._min_career_before_post(post) + tenure
        if age < min_age_needed:
            age = min_age_needed
        birth_year = self.year - age
        entry_year = self._roll_entry_year(age, post, prior_tenure=tenure)
        m = Minister(
            self.next_minister_id,
            self.generate_minister_name(),
            birth_year,
            entry_year,
            post,
        )
        self._apply_post_ability_floor(m, post)
        # 现职就任年：补缺自本年；开国可回溯已任若干年（不得早于初仕+最低资历）
        post_since = self.year - tenure
        min_before = self._min_career_before_post(post)
        earliest_post = entry_year + min_before
        if post_since < earliest_post:
            post_since = earliest_post
        if post_since > self.year:
            post_since = self.year
        m.post_since_year = post_since
        m.age = age
        # 终年须晚于「现职起算之年」时的年龄，避免开局回溯后立刻卒于任
        age_at_post = post_since - birth_year
        min_death = max(age, age_at_post) + 2
        if m.death_age < min_death:
            m.death_age = min_death + math.floor(random.random() * 8)
        self.next_minister_id += 1
        self.ministers.append(m)
        self.court_posts[post] = m.id
        self._open_post_term(m, post, start_year=post_since)
        return m

    def init_court(self):
        """开国组建朝廷：11 职各授一人；尚书已有资历，首辅偏年长。"""
        self.court_last_emperor_id = self.emperor_id
        if not getattr(self, "post_history", None):
            self.post_history = empty_post_history()
            self.shoufu_history = self.post_history[POST_SHOUFU]
        for post in ALL_POSTS:
            # 开国班底：现职已任 1–8 年，非「本年方授」
            prior = 1 + math.floor(random.random() * 8)
            if post == POST_SHOUFU:
                self.recruit_minister(post, min_age=50, max_age=62, prior_tenure=prior)
            elif post == POST_CIFU or post in QUNFU_POSTS:
                self.recruit_minister(post, min_age=48, max_age=58, prior_tenure=prior)
            else:
                self.recruit_minister(post, min_age=42, max_age=55, prior_tenure=prior)
        shoufu = self.get_shoufu()
        self._append_court_event(f"拜{shoufu.name}为内阁首辅，总揽机务。")

    # —— 年度演化 ——

    def gamemin_court(self):
        """每年：新君察相 → 老/病/政争去职 → 林下终老 → 递补 → 权臣察验。"""
        if not self.court_posts:
            return
        self._court_new_emperor_check()
        self._court_aging_and_exit()
        self._court_offstage_deaths()
        self._court_fill_vacancies()
        self._court_quanchen_check()

    def _remove_from_post(self, m, post, exit_reason, event_text=None):
        """统一卸任：闭合任期、清空席位、按去向处理生死/致仕，可选纪事。"""
        self.court_posts[post] = None
        self._close_post_term(m, post, exit_reason)
        if exit_reason in EXIT_DEATH_LIKE:
            m.is_alive = False
            m.death_year = self.year
            m.retired = True
            if exit_reason not in EXIT_NO_SHIHAO:
                self._grant_minister_shihao(m)
        else:
            m.retired = True
        if event_text:
            self._append_court_event(event_text)

    def _pick_age_exit_reason(self, m, post):
        """高年去位：致仕为主，间以病免、终养（史实常见）。"""
        r = random.random()
        if m.age < 70 and r < 0.35:
            return "病免"
        if r < 0.12:
            return "终养"
        if r < 0.22:
            return "病免"
        return "致仕"

    def _pick_midcareer_exit(self, m, post):
        """中途去职（非高年强制）：按材具/权臣/职位略加权，仿史实分布。

        返回 (exit_reason, event_text|None)；不触发则 (None, None)。
        全院每年约 8–15% 有人因政争、丁忧、外放等去位，避免几乎全是致仕/升迁。
        """
        tenure = max(0, self.year - m.post_since_year)
        # 新任未满二年少动（站稳脚跟）
        if tenure < 2:
            return None, None
        # 基率：尚书略高、首辅略低（首辅去位更敏感，另有新君察相）
        if post == POST_SHOUFU:
            base = 0.04
        elif post == POST_CIFU or post in QUNFU_POSTS:
            base = 0.055
        else:
            base = 0.07
        # 材庸易劾；权臣易见忌；帝暗弱时政争略多
        if m.ability <= 3:
            base += 0.03
        elif m.ability >= 8:
            base -= 0.015
        if m.quanchen:
            base += 0.05
        if getattr(self, "emperor_ab", 5) <= 3:
            base += 0.02
        if random.random() >= base:
            return None, None

        # 加权抽取去向（升迁不在此列，由递补链产生）
        # 权臣：更多罢/削/死；能臣：更多外放/丁忧/病免
        weights = {
            "丁忧": 18,
            "病免": 16,
            "劾罢": 14,
            "外放": 12,
            "罢": 10,
            "削职": 8,
            "谪贬": 7,
            "终养": 6,
            "致仕": 5,   # 中年亦有急流勇退
            "赐死": 2,
            "伏诛": 1,
        }
        if m.quanchen:
            weights["罢"] += 12
            weights["削职"] += 8
            weights["赐死"] += 6
            weights["伏诛"] += 4
            weights["外放"] += 4
        if m.ability <= 3:
            weights["劾罢"] += 10
            weights["削职"] += 6
            weights["谪贬"] += 4
        if m.ability >= 7:
            weights["外放"] += 6
            weights["丁忧"] += 4
            weights["伏诛"] = max(0, weights["伏诛"] - 1)
            weights["赐死"] = max(0, weights["赐死"] - 1)
        if m.age < 50:
            weights["致仕"] = 0
            weights["终养"] = max(2, weights["终养"] // 2)
        if post == POST_SHOUFU:
            weights["外放"] = max(0, weights["外放"] // 2)  # 首辅少外放
            weights["罢"] += 4

        reason = self._weighted_choice(weights)
        title = post_display(post)
        events = {
            "丁忧": f"{title}{m.name}以亲丧丁忧，解职归里。",
            "病免": f"{title}{m.name}以疾疏请，准其回籍调理。",
            "劾罢": f"言官交章劾{title}{m.name}，诏罢其职。",
            "外放": f"{title}{m.name}出为边方巡抚，不复预中枢。",
            "罢": f"诏罢{title}{m.name}，放归田里。",
            "削职": f"{title}{m.name}坐事削职闲住。",
            "谪贬": f"{title}{m.name}谪贬外郡，以示薄惩。",
            "终养": f"{title}{m.name}疏乞终养，得请归侍。",
            "致仕": f"{title}{m.name}急流勇退，准予致仕。",
            "赐死": f"{title}{m.name}获罪，诏赐自尽。",
            "伏诛": f"{title}{m.name}以大逆伏诛，中外震悚。",
        }
        # 非首辅级且非死罪：多数不入总纪事（避免刷屏），仅首辅/死罪/名臣记一笔
        text = events.get(reason)
        notable = (
            post == POST_SHOUFU
            or reason in EXIT_DEATH_LIKE
            or (m.ability >= 8 and reason in ("劾罢", "削职", "谪贬", "外放"))
        )
        return reason, (text if notable else None)

    def _weighted_choice(self, weights):
        """weights: {key: non-negative weight} → 按权随机一键。"""
        items = [(k, w) for k, w in weights.items() if w > 0]
        if not items:
            return "罢"
        total = sum(w for _, w in items)
        r = random.random() * total
        acc = 0.0
        for k, w in items:
            acc += w
            if r <= acc:
                return k
        return items[-1][0]

    def _court_new_emperor_check(self):
        """新君临朝，或罢前朝首辅（权臣尤易见忌）；去向不必尽是「罢」。"""
        if self.court_last_emperor_id is None:
            self.court_last_emperor_id = self.emperor_id
            return
        if self.emperor_id == self.court_last_emperor_id:
            return
        self.court_last_emperor_id = self.emperor_id
        shoufu = self.get_shoufu()
        if shoufu is None:
            return
        chance = 0.5 if shoufu.quanchen else 0.18
        if random.random() >= chance:
            return
        # 新君处置前朝首辅：罢 / 削职 / 外放 / 闲住 / 偶赐死
        if shoufu.quanchen:
            reason = self._weighted_choice({
                "罢": 30, "削职": 25, "外放": 15, "谪贬": 10, "赐死": 12, "伏诛": 8,
            })
        else:
            reason = self._weighted_choice({
                "罢": 40, "外放": 25, "削职": 15, "病免": 12, "致仕": 8,
            })
        texts = {
            "罢": f"新君临朝，罢首辅{shoufu.name}政，放归田里。",
            "削职": f"新君既立，削首辅{shoufu.name}职，令其闲住。",
            "外放": f"新君调首辅{shoufu.name}出镇边方，不复入阁。",
            "谪贬": f"新君谪贬前朝首辅{shoufu.name}，以肃朝纲。",
            "赐死": f"新君忌前朝首辅{shoufu.name}威权，诏赐自尽。",
            "伏诛": f"新君以大逆罪诛前朝首辅{shoufu.name}。",
            "病免": f"新君优礼前朝首辅{shoufu.name}，准其以疾致仕。",
            "致仕": f"新君允首辅{shoufu.name}乞骸骨，赐驰驿归里。",
        }
        self._remove_from_post(shoufu, POST_SHOUFU, reason, texts.get(reason))

    def _court_aging_and_exit(self):
        for post in ALL_POSTS:
            m = self.get_post_holder(post)
            if m is None:
                continue
            m.age = self.year - m.birth_year
            if m.age >= m.death_age:
                # 任上病故为主，偶有暴卒
                reason = "暴卒" if random.random() < 0.08 else "卒"
                self._remove_from_post(m, post, reason)
                if post == POST_SHOUFU:
                    shi = f"，追谥{m.shihao}" if m.shihao else ""
                    if reason == "暴卒":
                        self._append_court_event(
                            f"内阁首辅{m.name}暴卒于任上，朝野骇愕{shi}。"
                        )
                    else:
                        self._append_court_event(
                            f"内阁首辅{m.name}卒于任上，帝辍朝三日{shi}。"
                        )
                continue
            # 高年致仕 / 病免 / 终养
            if m.age >= RETIRE_AGE:
                chance = 0.10 + 0.05 * (m.age - RETIRE_AGE)
                force_age = RETIRE_FORCE_AGE
                if post == POST_SHOUFU:
                    chance *= 0.5
                    force_age = RETIRE_FORCE_AGE_SHOUFU
                if m.age >= force_age or random.random() < chance:
                    reason = self._pick_age_exit_reason(m, post)
                    event = None
                    if post == POST_SHOUFU:
                        event = {
                            "致仕": f"首辅{m.name}乞骸骨，累疏获准，赐驰驿归里。",
                            "病免": f"首辅{m.name}以疾恳辞，准予回籍调理。",
                            "终养": f"首辅{m.name}疏乞终养，帝勉从之。",
                        }.get(reason, f"首辅{m.name}去位归里。")
                    self._remove_from_post(m, post, reason, event)
                    continue
            # 中途：丁忧、劾罢、外放、政争等
            reason, event = self._pick_midcareer_exit(m, post)
            if reason:
                self._remove_from_post(m, post, reason, event)

    def _court_offstage_deaths(self):
        """去职仍在世者林下终老：继续计龄，至天年而卒（曾任首辅者记一笔）。"""
        for m in self.ministers:
            if not m.is_alive or not m.retired:
                continue
            m.age = self.year - m.birth_year
            if m.age >= m.death_age:
                m.is_alive = False
                m.death_year = self.year
                self._grant_minister_shihao(m)
                if m.shihao and any(
                    rec.get("mid") == m.id for rec in self.shoufu_history
                ):
                    self._append_court_event(f"前首辅{m.name}薨于里第，诏赠太傅，谥{m.shihao}。")

    def _grant_minister_shihao(self, m):
        """身后追谥：寻常卒后多得谥；材具高者更易得美谥之极（文正等）。"""
        if m.shihao:
            return
        if m.ability >= 8 and random.random() < 0.4:
            pool = MINISTER_SHIHAO_TOP
        elif m.ability >= 6:
            pool = MINISTER_SHIHAO_COMMON
        else:
            pool = MINISTER_SHIHAO_MODEST
        used = self.used_minister_shihao
        candidates = [s for s in pool if s not in used]
        if not candidates:
            all_pool = (
                MINISTER_SHIHAO_TOP
                + MINISTER_SHIHAO_COMMON
                + MINISTER_SHIHAO_MODEST
            )
            seen = set()
            uniq = []
            for s in all_pool:
                if s not in seen:
                    seen.add(s)
                    uniq.append(s)
            candidates = [s for s in uniq if s not in used]
        if not candidates:
            # 一朝谥号用尽：允许重用非常谥/常谥（极品仍尽量不重）
            candidates = list(dict.fromkeys(
                MINISTER_SHIHAO_COMMON + MINISTER_SHIHAO_MODEST
            ))
        m.shihao = random.choice(candidates)
        used.add(m.shihao)

    def _court_quanchen_check(self):
        """权臣秉政：主上暗弱而首辅雄才、久居揆席，则威权震主（每任首辅至多记一次）。"""
        shoufu = self.get_shoufu()
        if shoufu is None or shoufu.quanchen:
            return
        tenure = self.year - shoufu.post_since_year
        if (
            self.emperor_ab <= QUANCHEN_EMPEROR_AB_MAX
            and shoufu.ability >= QUANCHEN_SHOUFU_AB_MIN
            and tenure >= QUANCHEN_MIN_TENURE
            and random.random() < 0.25
        ):
            shoufu.quanchen = True
            self._append_court_event(
                f"首辅{shoufu.name}秉政日久，中外奏章皆决于私第，帝拱手而已。"
            )
            # 权柄下移：政务犹能运转（首辅之才补国运），然纲纪隳颓（略损）；
            # 国祚生死只在 gamemin_dynasty() 结算，此处不直接压到 0 以下
            self.dynasty_hp = max(1.0, self.dynasty_hp - 1.5)

    def _court_fill_vacancies(self):
        """递补链：次辅升首辅 → 群辅升次辅 → 尚书入阁 → 招新人补尚书。

        多职同年出缺时需级联多轮（如首辅、次辅同年卒），故循环至无缺可补。
        同年连升时中间职的 0 年记录由 `_close_post_term` 折叠删除。
        """
        for _ in range(len(ALL_POSTS)):
            moved = False

            if self.court_posts.get(POST_SHOUFU) is None:
                cifu = self.get_post_holder(POST_CIFU)
                if cifu is not None:
                    self._move_minister(cifu, POST_CIFU, POST_SHOUFU)
                    self._append_court_event(f"拜{cifu.name}为内阁首辅，朝野属望。")
                    moved = True

            if self.court_posts.get(POST_CIFU) is None:
                best = self._best_holder_of(QUNFU_POSTS)
                if best is not None:
                    self._move_minister(best[0], best[1], POST_CIFU)
                    moved = True

            for post in QUNFU_POSTS:
                if self.court_posts.get(post) is None:
                    best = self._best_holder_of(SIX_MINISTRIES)
                    if best is not None:
                        self._move_minister(best[0], best[1], post)
                        moved = True
                        if best[0].ability >= 8:
                            self._append_court_event(
                                f"{best[0].name}以才望入阁预机务，时论许为名臣。"
                            )

            for post in SIX_MINISTRIES:
                if self.court_posts.get(post) is None:
                    # 新拜尚书：已有多年仕途的中年郎署之选
                    self.recruit_minister(post, min_age=42, max_age=55)
                    moved = True

            if not moved:
                break

        # 极端情形（内阁连年凋零）：仍空的阁职直接招资深者，保证 11 职常满
        for post in [POST_SHOUFU, POST_CIFU] + QUNFU_POSTS:
            if self.court_posts.get(post) is None:
                m = self.recruit_minister(post, min_age=48, max_age=60)
                if post == POST_SHOUFU:
                    self._append_court_event(f"擢{m.name}入阁为首辅，以补台阁之虚。")

    def _best_holder_of(self, posts):
        """诸职在任者中能力最高者；同能力取本任更久者。返回 (minister, post)。"""
        best = None
        for post in posts:
            m = self.get_post_holder(post)
            if m is None:
                continue
            tenure = self.year - m.post_since_year
            if best is None:
                best = (m, post, tenure)
                continue
            if m.ability > best[0].ability or (
                m.ability == best[0].ability and tenure > best[2]
            ):
                best = (m, post, tenure)
        if best is None:
            return None
        return (best[0], best[1])

    def _move_minister(self, m, from_post, to_post):
        self._close_post_term(m, from_post, "升迁")
        self.court_posts[from_post] = None
        self.court_posts[to_post] = m.id
        m.post = to_post
        m.post_since_year = self.year
        # 升入更高职时抬升能力门槛（不降）
        self._apply_post_ability_floor(m, to_post)
        self._open_post_term(m, to_post)

    def _new_post_record(self, m):
        return {
            "mid": m.id,
            "name": m.name,
            "ability": m.ability,
            "start_year": self.year,
            "end_year": None,
            "exit": "",
        }

    def _open_post_term(self, m, post, start_year=None):
        """就任某职：写入该职历任账（首辅账与 shoufu_history 为同一列表）。"""
        hist = self.post_history.setdefault(post, [])
        rec = self._new_post_record(m)
        if start_year is not None:
            rec["start_year"] = start_year
        # 升迁后能力可能被抬升，记录抬升后的材具
        rec["ability"] = m.ability
        hist.append(rec)

    def _close_post_term(self, m, post, exit_reason):
        """卸任某职：按 mid 闭合该职最近一任。

        同年级联升迁产生的 0 年中间职（start==end==本年 且 exit=升迁）直接删除，
        避免历任表出现「未任即迁」的噪声记录。
        """
        hist = self.post_history.get(post) or []
        for i in range(len(hist) - 1, -1, -1):
            rec = hist[i]
            if rec.get("mid") == m.id and rec["end_year"] is None:
                if (
                    exit_reason == "升迁"
                    and rec["start_year"] == self.year
                ):
                    hist.pop(i)
                else:
                    rec["end_year"] = self.year
                    rec["exit"] = exit_reason
                break

    def _append_court_event(self, text):
        """朝廷纪事：结构与 event_happen() 一致，自动流入纪事表与国史提示词。"""
        time_str = self.d_time or (
            self.yearNumber + ("元年" if self.jinian == 1 else f"{self.jinian}年")
        )
        self.event_happened.append({
            "time": time_str,
            "emperor": self.emperor_zunhao or self.emperor or "",
            "emperor_id": self.emperor_id,
            "event": text,
        })
