# -*- coding: utf-8 -*-
"""一局游戏的运行时状态初始化（人物列表、国祚、事件、已用名号等）。"""


class GameStateMixin:
    """一局游戏的运行时状态初始化（人物列表、国祚、事件、已用名号等）。"""

    def init_game_state(self):
        self.people = []
        self.people_by_id = {}
        self.next_pid = 1
        self.current_emperor_pid = None
        self.next_emperor_pid = None

        self.ongame = True
        self.emperor_die = False
        self.dynasty_die = False
        self.emperor_id = 1
        self.emperor_age = 0
        self.emperor_hp = 0
        self.emperor_ab = 0
        self.dynasty_age = 0
        self.dynasty_st = ""
        self.dynasty_hp = 0
        self.jinian = 1
        self.dynasty = ""
        self.emperor = ""
        self.yearNumber = ""
        self.emperor_zunhao = ""
        # 开局快照（换代后 self.emperor 会变，国史提示词仍用开国信息）
        self.founder_name = ""
        self.founder_nianhao = ""
        self.amuse = 50
        self.hardworking = 50
        self.year = 0
        self.listjson = []
        self.current_emperor_nianhao_history = []
        # 逐年国运轨迹：[{year, hp, emperor, emperor_id, nianhao, jinian}]，供王朝国运图
        self.dynasty_hp_history = []

        # Name and title lists
        self.dynasty_name = ["夏","商","周","秦","汉","晋","隋","唐","宋","元","明","清"]
        self.init_tang_resources()
        self.emperor_firstname = ""
        self.emperor_lastname = ""
        self.zibei_poem = ""
        from dynasty.nianhao_data import NIANHAO_NAMES
        self.yearNumber_list = list(NIANHAO_NAMES)
        self.shihao = ""
        self.miaohao = ""
        self.verdict = ""
        self.used_shihao = []
        self.used_miaohao = []
        self.used_emperor_names = []
        self.used_person_names = set()
        self.used_nianhao = []
        self.used_zunhao = []
        self.initial_dynasty_hp = 100
        # 本帝在位国运轨迹（登基快照 + 峰值/谷值），供谥庙功绩评定
        self.reign_peak_dynasty_hp = 100
        self.reign_trough_dynasty_hp = 100

        # Event System
        self.event_id = 0
        self.event_happened = [{"time": "", "event": ""}]
        self.event_list = [
            {"time": "", "event": "今年无事发生。", "emperor_hp_change": 0, "dynasty_hp_change": 0},
            {"time": "", "event": "今年无事发生。", "emperor_hp_change": 0, "dynasty_hp_change": 0},
            {"time": "", "event": "今年无事发生。", "emperor_hp_change": 0, "dynasty_hp_change": 0},
            {"time": "", "event": "今年无事发生。", "emperor_hp_change": 0, "dynasty_hp_change": 0},
            {"time": "", "event": "今年无事发生。", "emperor_hp_change": 0, "dynasty_hp_change": 0},
            {"time": "", "event": "风调雨顺，五谷丰登。", "emperor_hp_change": 1, "dynasty_hp_change": 3},
            {"time": "", "event": "天降祥瑞，国泰民安。", "emperor_hp_change": 1, "dynasty_hp_change": 4},
            {"time": "", "event": "科举开科，广揽天下贤才。", "emperor_hp_change": 0, "dynasty_hp_change": 3},
            {"time": "", "event": "边关大捷，扬威海外。", "emperor_hp_change": 1, "dynasty_hp_change": 5},
            {"time": "", "event": "大兴土木，修建宫殿，劳民伤财。", "emperor_hp_change": -1, "dynasty_hp_change": -4},
            {"time": "", "event": "黄河决堤，流民遍野，民不聊生。", "emperor_hp_change": -1, "dynasty_hp_change": -6},
            {"time": "", "event": "地方叛乱，朝野震动。", "emperor_hp_change": -1, "dynasty_hp_change": -5},
            {"time": "", "event": "后宫干政，朝政混乱。", "emperor_hp_change": -2, "dynasty_hp_change": -3},
            {"time": "", "event": "宦官专权，陷害忠良。", "emperor_hp_change": -1, "dynasty_hp_change": -4},
            {"time": "", "event": "外敌入侵，边患严重。", "emperor_hp_change": -1, "dynasty_hp_change": -7},
            {"time": "", "event": "减免赋税，与民休息。", "emperor_hp_change": 0, "dynasty_hp_change": 4},
            {"time": "", "event": "瘟疫横行，十室九空。", "emperor_hp_change": -2, "dynasty_hp_change": -6},
            {"time": "", "event": "藩镇割据，听调不听宣。", "emperor_hp_change": -1, "dynasty_hp_change": -5},
            {"time": "", "event": "皇帝沉迷声色，不理朝政。", "emperor_hp_change": -2, "dynasty_hp_change": -4},
            {"time": "", "event": "修建水利，造福百姓。", "emperor_hp_change": 0, "dynasty_hp_change": 3},
            {"time": "", "event": "开通商路，国库充盈。", "emperor_hp_change": 0, "dynasty_hp_change": 4},
            {"time": "", "event": "发现金矿，国库大增。", "emperor_hp_change": 0, "dynasty_hp_change": 3},
            {"time": "", "event": "编纂大典，文化繁荣。", "emperor_hp_change": 0, "dynasty_hp_change": 4},
            {"time": "", "event": "诸王争储，朝堂党争不断。", "emperor_hp_change": -2, "dynasty_hp_change": -4},
            {"time": "", "event": "连年干旱，颗粒无收。", "emperor_hp_change": -1, "dynasty_hp_change": -5},
        ]
        self.data_emperor_hp_change = 0
        self.data_dynasty_hp_change = 0
        self.d_time = ""
        self.d_event = ""
        self.d_emperor = ""
        self.d_event_id = 0

