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
            # 朝政与制度：以具体政务体现治国取舍
            {"time": "", "event": "宰相裁并冗员，三省奏议渐趋精简。", "emperor_hp_change": 0, "dynasty_hp_change": 3},
            {"time": "", "event": "御史台纠弹权贵，数名勋戚罢官归第。", "emperor_hp_change": -1, "dynasty_hp_change": 2},
            {"time": "", "event": "新法骤行，朝臣分为两党，诏令数度反复。", "emperor_hp_change": -2, "dynasty_hp_change": -4},
            {"time": "", "event": "内帑赈济京畿，百官称颂天子恤民。", "emperor_hp_change": 1, "dynasty_hp_change": 3},
            {"time": "", "event": "盐铁专卖弊案发，地方豪商与官吏相互遮掩。", "emperor_hp_change": -1, "dynasty_hp_change": -3},
            # 民生与经济：丰歉、漕运和市舶带来的连锁影响
            {"time": "", "event": "漕渠淤塞，江南粮船滞留数月，京师米价腾贵。", "emperor_hp_change": -1, "dynasty_hp_change": -4},
            {"time": "", "event": "常平仓开仓平粜，灾区饥民得以度过春荒。", "emperor_hp_change": 0, "dynasty_hp_change": 4},
            {"time": "", "event": "市舶司迎来海舶，香药珠玉入市，关税大增。", "emperor_hp_change": 0, "dynasty_hp_change": 4},
            {"time": "", "event": "关中蝗灾蔽日，百姓驱蝗入河，仍损秋收。", "emperor_hp_change": -1, "dynasty_hp_change": -5},
            {"time": "", "event": "郡县丈量田亩，隐户隐田渐次登记入籍。", "emperor_hp_change": -1, "dynasty_hp_change": 3},
            {"time": "", "event": "京畿大雪压塌民舍，朝廷发粟并免除当年租调。", "emperor_hp_change": -1, "dynasty_hp_change": -3},
            # 边疆与外交：军镇、互市及使节往来
            {"time": "", "event": "朔方互市重开，边民以绢帛换取良马，烽烟稍息。", "emperor_hp_change": 1, "dynasty_hp_change": 3},
            {"time": "", "event": "节度使私募牙兵，拒绝交还兵符，朝廷遣使劝谕。", "emperor_hp_change": -1, "dynasty_hp_change": -5},
            {"time": "", "event": "西域诸国遣使入朝，献胡旋舞与汗血宝马。", "emperor_hp_change": 1, "dynasty_hp_change": 3},
            {"time": "", "event": "岭南瘴疠阻断驿路，征南军粮转运几近断绝。", "emperor_hp_change": -1, "dynasty_hp_change": -4},
            {"time": "", "event": "边将轻骑深入敌境，虽获首级甚众，亦折损精锐。", "emperor_hp_change": -1, "dynasty_hp_change": -2},
            # 宗室、礼制与文化：为纪事和国史提示词提供人物化钩子
            {"time": "", "event": "太子释奠国学，亲临讲席，士林以为储君知礼。", "emperor_hp_change": 1, "dynasty_hp_change": 3},
            {"time": "", "event": "宗室蕃衍，岁禄浩繁，有司请裁将军中尉禄米。", "emperor_hp_change": -1, "dynasty_hp_change": 2},
            {"time": "", "event": "礼官议定郊祀新仪，旧贵族与新进士人争论不休。", "emperor_hp_change": 0, "dynasty_hp_change": 1},
            {"time": "", "event": "翰林院编成实录，前朝旧闻与宫门秘档得以保存。", "emperor_hp_change": 0, "dynasty_hp_change": 3},
            {"time": "", "event": "佛寺广置庄田，御史上疏请核免税田亩，僧俗相持。", "emperor_hp_change": -1, "dynasty_hp_change": -2},
            {"time": "", "event": "宫中乐工新制霓裳曲，宴饮连旬，百官忧其奢靡。", "emperor_hp_change": -2, "dynasty_hp_change": -3},
            # 灾异与社会：保留可被改元机制捕捉的重大冲击
            {"time": "", "event": "京师地动，城垣多处倾圮，百姓夜宿空地。", "emperor_hp_change": -1, "dynasty_hp_change": -6},
            {"time": "", "event": "宫城失火，延烧左藏库，典籍与帑银俱有损失。", "emperor_hp_change": -2, "dynasty_hp_change": -5},
            {"time": "", "event": "民间结社聚众抗税，郡守开仓安抚后事态稍平。", "emperor_hp_change": -1, "dynasty_hp_change": -4},
            {"time": "", "event": "名医献治疫方，太医院编成《时气要略》颁行诸道。", "emperor_hp_change": 1, "dynasty_hp_change": 4},
            {"time": "", "event": "祥鸟集于端门，群臣请加尊号，帝以天戒自持而止。", "emperor_hp_change": 1, "dynasty_hp_change": 2},
            {"time": "", "event": "流寇余部转掠江淮，州县闭城自守，商旅断绝。", "emperor_hp_change": -1, "dynasty_hp_change": -6},
        ]
        self.data_emperor_hp_change = 0
        self.data_dynasty_hp_change = 0
        self.d_time = ""
        self.d_event = ""
        self.d_emperor = ""
        self.d_event_id = 0
