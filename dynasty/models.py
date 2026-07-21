# -*- coding: utf-8 -*-
"""核心数据模型：人物 Person、朝臣 Minister 与能力掷骰。"""
import math
import random


def roll_ability():
    """Random ruler ability score in [1, 9] with a triangular distribution."""
    return max(1, 5 + math.floor(random.random() * 5) - math.floor(random.random() * 5))


def roll_death_age():
    """掷目标终年（史实分布）：多数 40–69，少数英年早逝或高寿逾八旬，均值约 50。"""
    r = random.random()
    if r < 0.10:
        return 16 + math.floor(random.random() * 14)   # 16–29 英年早逝
    if r < 0.25:
        return 30 + math.floor(random.random() * 10)   # 30–39 中道而殂
    if r < 0.60:
        return 40 + math.floor(random.random() * 15)   # 40–54 常见终年
    if r < 0.88:
        return 55 + math.floor(random.random() * 15)   # 55–69 得享中寿
    if r < 0.97:
        return 70 + math.floor(random.random() * 10)   # 70–79 长寿
    return 80 + math.floor(random.random() * 10)       # 80–89 高寿


def roll_lifespan_at_birth():
    """出生时掷天寿：含约 8% 早夭（不满 10 岁），余按史实终年分布。"""
    if random.random() < 0.08:
        return 2 + math.floor(random.random() * 8)     # 2–9 岁早夭
    return roll_death_age()


def roll_minister_death_age():
    """朝臣终年：入仕时已成年，无早夭段；50–84，均值约 67，大臣多享中高寿。"""
    return 50 + math.floor(random.random() * 35)


class Person:
    def __init__(self, pid, name, gender, birth_year, father_id, mother_id, generation):
        self.id = pid
        self.name = name
        self.gender = gender # "M" or "F"
        self.birth_year = birth_year
        self.death_year = -1
        self.father_id = father_id
        self.mother_id = mother_id
        self.children = []
        self.title = "" # Full display title
        self.title_name = "" # e.g. "晋", "齐", "楚"
        # 爵等（明制宗藩八等）：0=帝室/无爵
        # 1亲王 2郡王 3镇国将军 4辅国将军 5奉国将军 6镇国中尉 7辅国中尉 8奉国中尉
        self.title_rank = 0
        self.is_heir = False # Whether this person is the designated heir of their father's rank
        self.has_title = False # Whether they actively hold the rank (true if father is dead or they are independent)
        self.shihao = ""
        self.ability = roll_ability()
        # 天寿：按史实分布掷目标终年，多数 40–69，少数早夭或高寿逾八旬
        self.hp = roll_lifespan_at_birth()
        self.age = 0
        self.is_alive = True
        self.generation = generation # Generation distance from first emperor
        self.extinct = False # 绝嗣
        self.adopted_from = None # 过继来源（嗣父 ID）
        self.miaohao = "" # 庙号
        self.zunhao = "" # 尊号（风味化称谓）


class Minister:
    """朝臣：内阁大学士与六部尚书。独立于宗室 Person，无父系与爵位。"""

    def __init__(self, mid, name, birth_year, entry_year, post):
        self.id = mid
        self.name = name
        self.birth_year = birth_year
        self.death_year = -1
        self.entry_year = entry_year        # 入仕（就任本朝官职）之年
        self.post = post                    # 现任官职（首辅/次辅/群辅/六部尚书）
        self.post_since_year = entry_year   # 现职就任之年
        self.ability = roll_ability()
        self.death_age = roll_minister_death_age()
        self.age = 0
        self.is_alive = True
        self.retired = False                # 致仕（含罢归）
        self.shihao = ""                    # 谥号（名臣身后追谥，如「文正」）
        self.quanchen = False               # 本任内已记过「权臣」纪事（防重复刷屏）
        # 扩展点（V2）：faction 朋党、exam_rank 科举出身
