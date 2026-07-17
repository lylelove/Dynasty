# -*- coding: utf-8 -*-
"""核心数据模型：人物 Person 与能力掷骰。"""
import math
import random


def roll_ability():
    """Random ruler ability score in [1, 9] with a triangular distribution."""
    return max(1, 5 + math.floor(random.random() * 5) - math.floor(random.random() * 5))


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
        # 天寿：目标终年约 45–70（均值约 55），贴合古代上层男子
        self.hp = 45 + math.floor(random.random() * 25)
        self.age = 0
        self.is_alive = True
        self.generation = generation # Generation distance from first emperor
        self.extinct = False # 绝嗣
        self.adopted_from = None # 过继来源（嗣父 ID）
        self.miaohao = "" # 庙号
        self.zunhao = "" # 尊号（风味化称谓）

