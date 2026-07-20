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


def post_display(post):
    """界面/纪事用职名：群辅一/二/三统称「群辅」。"""
    return "群辅" if post in QUNFU_POSTS else post


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

    def recruit_minister(self, post, min_age=35, max_age=49):
        """招募一名新朝臣就任 post。"""
        age = min_age + math.floor(random.random() * (max_age - min_age + 1))
        m = Minister(
            self.next_minister_id,
            self.generate_minister_name(),
            self.year - age,
            self.year,
            post,
        )
        m.age = age
        self.next_minister_id += 1
        self.ministers.append(m)
        self.court_posts[post] = m.id
        return m

    def init_court(self):
        """开国组建朝廷：11 职各授一人，首辅偏年长。"""
        for post in ALL_POSTS:
            if post == POST_SHOUFU:
                self.recruit_minister(post, min_age=45, max_age=55)
            else:
                self.recruit_minister(post, min_age=35, max_age=49)
        shoufu = self.get_shoufu()
        self.shoufu_history.append({
            "name": shoufu.name,
            "ability": shoufu.ability,
            "start_year": self.year,
            "end_year": None,
            "exit": "",
        })
        self._append_court_event(f"拜{shoufu.name}为内阁首辅，总揽机务。")

    # —— 年度演化 ——

    def gamemin_court(self):
        """每年：老与卒/致仕 → 自上而下递补 → 首辅级纪事。"""
        if not self.court_posts:
            return
        self._court_aging_and_exit()
        self._court_fill_vacancies()

    def _court_aging_and_exit(self):
        for post in ALL_POSTS:
            m = self.get_post_holder(post)
            if m is None:
                continue
            m.age = self.year - m.birth_year
            if m.age >= m.death_age:
                m.is_alive = False
                m.death_year = self.year
                self.court_posts[post] = None
                if post == POST_SHOUFU:
                    self._close_shoufu_term(m, "卒")
                    self._append_court_event(f"内阁首辅{m.name}卒于任上，帝辍朝三日。")
                continue
            if m.age >= RETIRE_AGE:
                chance = 0.10 + 0.05 * (m.age - RETIRE_AGE)
                force_age = RETIRE_FORCE_AGE
                if post == POST_SHOUFU:
                    chance *= 0.5
                    force_age = RETIRE_FORCE_AGE_SHOUFU
                if m.age >= force_age or random.random() < chance:
                    m.retired = True
                    self.court_posts[post] = None
                    if post == POST_SHOUFU:
                        self._close_shoufu_term(m, "致仕")
                        self._append_court_event(f"首辅{m.name}乞骸骨，累疏获准，赐驰驿归里。")

    def _court_fill_vacancies(self):
        """递补链：次辅升首辅 → 群辅升次辅 → 尚书入阁 → 招新人补尚书。

        多职同年出缺时需级联多轮（如首辅、次辅同年卒），故循环至无缺可补。
        """
        for _ in range(len(ALL_POSTS)):
            moved = False

            if self.court_posts.get(POST_SHOUFU) is None:
                cifu = self.get_post_holder(POST_CIFU)
                if cifu is not None:
                    self._move_minister(cifu, POST_CIFU, POST_SHOUFU)
                    self.shoufu_history.append({
                        "name": cifu.name,
                        "ability": cifu.ability,
                        "start_year": self.year,
                        "end_year": None,
                        "exit": "",
                    })
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
                    self.recruit_minister(post)
                    moved = True

            if not moved:
                break

        # 极端情形（内阁连年凋零）：仍空的阁职直接招新人，保证 11 职常满
        for post in [POST_SHOUFU, POST_CIFU] + QUNFU_POSTS:
            if self.court_posts.get(post) is None:
                m = self.recruit_minister(post, min_age=45, max_age=55)
                if post == POST_SHOUFU:
                    self.shoufu_history.append({
                        "name": m.name,
                        "ability": m.ability,
                        "start_year": self.year,
                        "end_year": None,
                        "exit": "",
                    })
                    self._append_court_event(f"擢{m.name}入阁为首辅，以补台阁之虚。")

    def _best_holder_of(self, posts):
        """诸职在任者中能力最高者，返回 (minister, post)；全虚位返回 None。"""
        best = None
        for post in posts:
            m = self.get_post_holder(post)
            if m is not None and (best is None or m.ability > best[0].ability):
                best = (m, post)
        return best

    def _move_minister(self, m, from_post, to_post):
        self.court_posts[from_post] = None
        self.court_posts[to_post] = m.id
        m.post = to_post
        m.post_since_year = self.year

    def _close_shoufu_term(self, m, exit_reason):
        for rec in reversed(self.shoufu_history):
            if rec["name"] == m.name and rec["end_year"] is None:
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
