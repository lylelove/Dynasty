# -*- coding: utf-8 -*-
"""核心数据模型：人物 Person 与能力掷骰。"""
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
        # 爵等（唐制九等）：0=帝室/无爵
        # 1亲王 2郡王 3国公 4开国郡公 5开国县公 6开国县侯 7开国县伯 8开国县子 9开国县男
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

