import sys
import math
import random
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QStackedWidget, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QLineEdit, QPushButton, QFormLayout, QDialog,
    QHeaderView, QTabWidget, QTableWidget, QSlider, QTableWidgetItem,
    QTreeWidget, QTreeWidgetItem
)
from PySide6.QtCore import Qt, QTimer


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
        self.title_rank = 0 # 0=Emperor, 1=亲王, 2=郡王, 3=国公, 4=郡公, 5=县公, 6=县侯, 7=县伯
        self.is_heir = False # Whether this person is the designated heir of their father's rank
        self.has_title = False # Whether they actively hold the rank (true if father is dead or they are independent)
        self.shihao = ""
        self.ability = roll_ability()
        self.hp = 20 + math.floor(random.random() * 40) # life expectancy
        self.age = 0
        self.is_married = False
        self.is_alive = True
        self.generation = generation # Generation distance from first emperor
        self.extinct = False # 绝嗣
        self.adopted_from = None # 过继来源（嗣父 ID）
        self.miaohao = "" # 庙号
        self.zunhao = "" # 尊号（风味化称谓）


class DynastyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("王朝 V0.17")
        self.resize(920, 640)

        # Initialize Game State
        self.init_game_state()

        # Central stacked widget
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # Start Screen
        self.start_screen = QWidget()
        self.setup_start_screen()
        self.stacked_widget.addWidget(self.start_screen)

        # Main Game Screen
        self.main_game_screen = QWidget()
        self.setup_main_game_screen()
        self.stacked_widget.addWidget(self.main_game_screen)

        # Initially show start screen
        self.stacked_widget.setCurrentIndex(0)

        # Dialogs
        self.setup_dialogs()

        # 古风主题样式（墨底金边 · 朱漆宫墙）
        self.apply_stylesheet()

        # Auto-run timer
        self.auto_run = False
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.auto_run_step)

    def init_game_state(self):
        self.people = []
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
        self.amuse = 50
        self.hardworking = 50
        self.year = 0
        self.listjson = []
        self.current_emperor_nianhao_history = []

        # Name and title lists
        self.dynasty_name = ["夏","商","周","秦","汉","晋","隋","唐","宋","元","明","清"]
        self.init_tang_resources()
        self.emperor_firstname = ""
        self.emperor_lastname = ""
        self.yearNumber_list = ["建元", "元光", "元朔", "元狩", "元鼎", "元封", "太初", "天汉", "太始", "征和", "后元", "始元", "元凤", "平瑞", "本始", "地节", "元康", "神爵", "五凤", "甘露", "黄龙", "初元", "永光", "建昭", "竟宁", "建始", "河平", "阳朔", "鸿嘉", "永始", "元延", "绥和", "建平", "太初元将", "元寿", "元始", "居摄", "初始", "建国", "天凤", "地皇", "更始", "建武", "建武中元", "永平", "建初", "元和", "章和", "永元", "元兴", "延平", "永初", "元初", "永宁", "建光", "延光", "永建", "阳嘉", "永和", "汉安", "建康", "永嘉", "本初", "建和", "和平", "元嘉", "永兴", "永寿", "延熹", "永康", "建宁", "熹平", "光和", "中平", "光熹", "昭宁", "微平", "初平", "兴平", "建安", "延康", "黄初", "太和", "青龙", "景初", "正始", "嘉平", "正元", "甘露", "景元", "咸熙", "泰始", "咸宁", "太康", "太熙", "永熙", "永平", "元康", "永康", "永宁", "太安", "永安", "建武", "永安", "建兴", "永嘉", "建兴", "建武", "太兴", "永昌", "太宁", "咸和", "咸康", "建元", "永和", "升平", "隆和", "兴宁", "太和", "咸安", "宁康", "太元", "隆安", "元兴", "义熙", "元熙", "开皇", "仁寿", "大业", "义宁", "武德", "贞观", "永徽", "显庆", "龙朔", "麟德", "乾封", "总章", "咸亨", "上元", "仪凤", "调露", "永隆", "开耀", "永淳", "弘道", "嗣圣", "文明", "光宅", "垂拱", "永昌", "载初", "天授", "如意", "长寿", "延载", "证圣", "天册万岁", "万岁登封", "万岁通天", "神功", "圣历", "久视", "大足", "长安", "神龙", "景龙", "唐隆", "景云", "太极", "延和", "先天", "开元", "天宝", "至德", "乾元", "上元", "宝应", "广德", "永泰", "大历", "建中", "兴元", "贞元", "永贞", "元和", "长庆", "宝历", "大和", "开成", "会昌", "大中", "咸通", "乾符", "广明", "中和", "光启", "文德", "龙纪", "大顺", "景福", "乾宁", "光化", "天复", "天祐", "建隆", "乾德", "开宝", "太平兴国", "雍熙", "端拱", "淳化", "至道", "咸平", "景德", "大中祥符", "天禧", "乾兴", "天圣", "明道", "景祐", "宝元", "康定", "庆历", "皇祐", "至和", "嘉祐", "治平", "熙宁", "元丰", "元祐", "绍圣", "元符", "建中靖国", "崇宁", "大观", "政和", "重和", "宣和", "靖康", "建炎", "绍兴", "隆兴", "乾道", "纯熙", "淳熙", "绍熙", "庆元", "嘉泰", "开禧", "开禧", "嘉定", "宝庆", "绍定", "端平", "嘉熙", "淳祐", "宝祐", "开庆", "景定", "咸淳", "德祐", "景炎", "祥兴", "中统", "至元", "元贞", "大德", "至大", "皇庆", "延祐", "至治", "泰定", "致和", "天历", "至顺", "元统", "至元", "至正", "洪武", "建文", "永乐", "洪熙", "宣德", "正统", "景泰", "天顺", "成化", "弘治", "正德", "嘉靖", "隆庆", "万历", "泰昌", "天启", "崇祯", "顺治", "康熙", "雍正", "乾隆", "嘉庆", "道光", "咸丰", "同治", "光绪", "宣统"]
        self.shihao = ""
        self.miaohao = ""
        self.used_shihao = []
        self.used_miaohao = []
        self.used_emperor_names = []
        self.used_person_names = []
        self.used_nianhao = []
        self.initial_dynasty_hp = 100

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
        self.d_event_id = 0

    def init_tang_resources(self):
        self.tang_surnames = [
            "李", "赵", "王", "郑", "崔", "卢", "韦", "裴", "杜", "苏", "柳", "薛", "韩", "萧", "房", "长孙",
            "高", "杨", "郭", "窦", "徐", "宋", "孔", "颜", "陆", "贺", "沈", "岑", "元", "武", "独孤", "宇文"
        ]
        self.tang_male_given_single = list("承弘元思守崇景玄世重文武德宗道隆光嗣维贞从温俨倓恪璿祐祎怡俶俊俭倚侃恭昭穆桓烈毅肃靖睿哲宣显英伟雄俊豪杰轩昂昂熙茂勋业基祖宪章经纬韬略邦国天泽润溥淳熙泰恒恒嘉祯祥瑞麟凤龙云鹏鹤松柏山川河岳星辰")
        self.tang_male_given_double = [
            "世民", "承乾", "泰和", "弘义", "弘礼", "弘道", "崇义", "崇礼", "景行", "景仁", "玄成", "守礼",
            "元嘉", "元礼", "宗仪", "宗楚", "德明", "德昭", "道玄", "道兴", "维岳", "从善", "承业", "承礼",
            "弘文", "弘武", "思恭", "思敬", "守正", "守谦", "景让", "景初", "玄晖", "重润", "重茂", "光弼",
            "孝瑜", "孝珩", "孝瓘", "孝琬", "孝瓒", "子建", "子敬", "子渊", "叔宝", "叔慎", "仲卿", "少游",
            "怀仁", "怀义", "怀智", "怀玉", "怀瑾", "明远", "明哲", "明允", "明达", "德裕", "德懋", "德音",
            "文谦", "文炳", "文蔚", "武韬", "武略", "承恩", "承泽", "承宣", "显达", "显宗", "昭嗣", "昭烈"
        ]
        self.tang_female_given_single = list("婉令宜安永宁和柔华真玉仙德丽贞淑静惠昭义清嘉盈瑶璧珂珊珠琦琴书画画诗韵兰菊梅莲蓉萱蕊珍瑶环佩莺燕娥娟娥姬嫱")
        self.tang_female_given_double = [
            "太平", "安乐", "长宁", "金仙", "玉真", "万春", "永宁", "宁国", "和政", "寿安", "新都", "广德",
            "临川", "襄城", "豫章", "巴陵", "普安", "清河", "常乐", "永嘉", "义阳", "定安", "乐安", "咸宜",
            "延庆", "永泰", "安兴", "金城", "宜芳", "怀思", "晋安", "临晋", "普康", "乐城", "新平", "寿光",
            "永穆", "永清", "成安", "广宁", "丹阳", "永昌", "升平", "寿昌", "南康", "建宁", "遂安", "始安"
        ]
        self.emperor_firstname_list = "".join(self.tang_surnames)

        self.rank_suffix_map = {
            1: "亲王",
            2: "郡王",
            3: "国公",
            4: "郡公",
            5: "县公",
            6: "县侯",
            7: "县伯",
        }
        self.rank_name_pools = {
            1: ["秦", "晋", "齐", "楚", "燕", "赵", "韩", "魏", "梁", "蜀", "吴", "越", "鲁", "宋", "郑", "陈", "许", "卫", "代", "雍", "岐", "凉", "益", "荆", "并", "幽", "朔", "宁", "夏", "辽", "潞", "郓", "夔", "潭", "鄂", "扬", "徐", "青", "兖", "豫", "冀", "蒲", "绛", "泽", "汾", "隰", "丹", "延", "绥", "银", "岢", "岚", "云", "应", "寰", "蔚", "新", "沔", "褒", "泾", "原", "渭", "甘", "肃", "瓜", "沙", "伊", "庭", "安", "蒙", "昆", "密", "石", "芳", "茂", "翼", "维", "当", "柘", "恭", "奉", "霸", "堂", "蓟", "檀", "妫", "儒", "丰", "顺", "营", "平", "慎", "渊", "徽", "郢", "随", "温", "处", "婺", "台", "明", "衢", "睦", "秀", "杭", "苏", "常", "润", "湖"],
            2: ["陇西", "清河", "太原", "河间", "平原", "赵郡", "中山", "琅琊", "东平", "彭城", "陈留", "汝南", "颍川", "京兆", "弘农", "扶风", "武威", "南阳", "河东", "河内", "安定", "天水", "江夏", "汝阴", "谯", "下邳", "广陵", "临淮", "广阳", "济北", "任城", "东郡", "济南", "北海", "东莱", "城阳", "胶东", "淮阳", "梁", "鲁", "楚", "齐", "燕", "赵", "魏", "韩", "宋", "陈", "庐江", "弋阳", "南康", "庐陵"],
            3: ["蔡", "曹", "霍", "邓", "申", "谯", "谭", "蒋", "鲁", "许", "郧", "郢", "郜", "芮", "郇", "密", "薛", "程", "尉", "长孙", "宇文", "窦", "于", "毕", "耿", "舒", "邺", "介", "郯", "郪", "郐", "鄅", "鄫", "菖", "鄄", "鄢"],
            4: ["彭泽", "安吉", "长乐", "富平", "华阴", "蓝田", "新安", "临晋", "临淄", "曲江", "栎阳", "高陵", "始平", "安邑", "河清", "渭南", "阳翟", "颍阴", "舞阳", "博陆", "富春", "余姚", "吴兴", "长城", "建康", "丹阳", "宣城", "庐江", "晋陵", "义兴", "兰陵", "东武", "营陵", "平寿", "剧", "瑕丘", "乘氏", "廪丘", "须昌", "寿张", "博平", "聊城", "高唐", "安德", "平昌", "朱虚"],
            5: ["高阳", "武安", "临川", "新都", "安康", "永安", "安平", "义宁", "咸宁", "乐成", "会昌", "丰城", "宁远", "广平", "平恩", "修武", "阳信", "猗氏", "闻喜", "解", "蒲子", "大陵", "祁", "平陶", "京陵", "中都", "邬", "阳曲", "广武", "刚", "汾阳", "隰城", "中阳", "离石", "介休", "武乡", "襄陵", "临汾", "铜鞮", "涅", "襄垣", "屯留", "长子", "壶关", "泫氏", "高都"],
            6: ["长兴", "永丰", "安吉", "富春", "临海", "安喜", "武宁", "崇仁", "延福", "清源", "安义", "平乡", "曲周", "南和", "任", "南皮", "东光", "重合", "重平", "阜城", "修市", "乐乡", "高堤", "建成", "临泾", "安陵", "阴槃", "弋居", "大要", "郁郅", "泥阳", "义渠", "雕阴", "漆垣", "定阳", "高奴", "宜都", "夷道"],
            7: ["永寿", "清苑", "安福", "崇义", "宁化", "乐安", "永平", "宜春", "临汝", "修文", "安仁", "常宁", "南乡", "比阳", "平氏", "复阳", "桐柏", "舞阴", "堵阳", "赭阳", "上陌", "西鄂", "雉", "鲁阳", "犨", "叶", "湖阳", "博望", "涅阳", "棘阳", "育阳", "朝阳", "新野", "安众", "冠军"],
        }
        self.female_title_pools = {
            "公主": ["太平", "安乐", "长宁", "宁国", "咸宜", "寿安", "和政", "新昌", "万安", "永嘉", "义阳", "广德", "乐安", "宣城", "临川", "襄城", "升平", "寿昌", "延庆", "永泰", "安兴", "金城", "宜芳", "怀思", "晋安", "临晋", "普康", "乐城", "新平", "寿光", "永穆", "永清", "成安", "广宁", "丹阳", "永昌"],
            "郡主": ["清河", "兰陵", "弘农", "颍川", "安定", "河东", "平原", "东阳", "义兴", "临海", "义宁", "会稽", "万寿", "寿光", "安乐", "永宁", "南康", "永兴", "永康", "永平", "嘉兴", "建宁", "益昌", "遂安", "始安", "永明", "绥安", "安庆", "广宁", "华容", "寻阳", "庐陵", "豫章", "长沙", "桂阳", "衡阳", "零陵", "营阳", "汝南", "南郡", "江夏", "魏兴", "广汉", "新都", "宜都", "建平", "永安", "西平", "武威", "张掖", "酒泉", "敦煌", "西海", "晋昌", "高昌", "交趾", "日南", "九真"],
            "县主": ["新都", "高阳", "安平", "永安", "乐成", "广平", "武安", "平恩", "义宁", "修武", "安康", "宁远", "金城", "华亭", "宏农", "颍阳", "汝阳", "滍阳", "广城", "崆峒", "肃宁", "博野"],
            "乡主": ["安仁", "宁化", "崇义", "乐安", "永平", "清苑", "安福", "临汝", "宜春", "修文", "高唐", "寿张", "平阳", "襄陵", "猗氏", "安邑", "闻喜", "汾阳", "龙门", "稷山", "绛", "曲沃", "翼城", "沁水", "阳城", "陵川", "高平", "泫氏", "端氏", "获泽", "沁源"],
        }

        self.emperor_miaohao_founders = ["高祖", "太祖", "世祖", "圣祖", "烈祖", "肃祖", "显祖", "昭祖"]
        self.emperor_miaohao_prosperous = ["太宗", "玄宗", "宪宗", "宣宗", "肃宗", "德宗", "睿宗", "中宗", "仁宗", "孝宗", "圣宗", "兴宗", "章宗", "成宗", "钦宗", "理宗", "度宗", "徽宗", "英宗", "神宗"]
        self.emperor_miaohao_stable = ["顺宗", "代宗", "敬宗", "文宗", "穆宗", "懿宗", "僖宗", "真宗", "哲宗", "光宗", "宁宗", "端宗", "庆宗", "显宗", "庄宗"]
        self.emperor_miaohao_decline = ["哀宗", "昭宗", "恭宗", "襄宗", "殇宗", "废宗", "携宗", "怀宗", "思宗", "毅宗", "威宗"]
        self.emperor_shifa_core_good = ["文", "武", "成", "宣", "景", "睿", "仁", "明", "昭", "圣", "神", "钦", "纯", "康", "肃", "哲"]
        self.emperor_shifa_core_mid = ["恭", "顺", "穆", "定", "安", "和", "平", "简", "靖", "懿", "襄", "烈", "僖", "隐", "釐", "温"]
        self.emperor_shifa_core_bad = ["悼", "思", "哀", "愍", "厉", "灵", "炀", "幽", "荒", "悖", "殇", "暴", "沖", "少"]
        self.emperor_shifa_assist_good = ["孝", "德", "昭", "肃", "宪", "懿", "钦", "纯", "哲", "温"]
        self.emperor_shifa_assist_mid = ["恭", "顺", "庄", "静", "和", "靖", "穆", "景", "昭", "温"]
        self.emperor_shifa_assist_bad = ["昏", "荒", "厉", "悖", "悼", "暴", "炀", "幽"]
        self.empress_shihao_good = ["文德", "昭德", "懿德", "恭顺", "贞顺", "元贞", "柔明", "贤肃", "庄宪", "敬慎", "昭", "懿", "仁", "和", "安", "顺", "淑", "庄", "钦", "成", "康", "靖", "徽", "宣"]
        self.empress_shihao_neutral = ["和仪", "恭静", "顺成", "端和", "淑慎", "庄静", "肃恭", "惠", "静", "温", "庄", "肃", "穆", "哲", "仪", "容", "裕"]
        self.empress_shihao_bad = ["哀思", "悼恭", "思顺", "愍和", "幽", "炀", "荒", "暴", "厉", "妖", "惑"]
        self.taizi_shihao_good = ["懿德", "章怀", "恭仁", "孝敬", "宣懿", "忠肃", "惠昭", "昭", "懿", "温", "靖", "献", "睿", "钦"]
        self.taizi_shihao_neutral = ["庄", "昭", "敬", "恭", "思", "悼", "怀", "温", "靖", "穆", "和", "静"]
        self.taizi_shihao_bad = ["悼", "愍", "哀", "厉", "殇", "荒", "炀", "幽"]
        self.prince_shihao_good = ["恭", "靖", "康", "宪", "敬", "庄", "孝", "忠", "惠", "安", "温", "穆", "肃", "昭", "懿", "献", "荣"]
        self.prince_shihao_neutral = ["思", "悼", "怀", "顺", "简", "和", "恪", "靖", "懿", "温", "隐", "僖"]
        self.prince_shihao_bad = ["哀", "愍", "厉", "灵", "荒", "炀", "幽", "暴"]
        self.princess_shihao_good = ["贤", "懿", "淑", "庄", "静", "昭", "宁", "柔", "顺", "华", "婉", "令", "仪", "徽", "宣", "荣", "嘉", "端"]
        self.princess_shihao_neutral = ["悼", "思", "怀", "恭", "惠", "安", "昭", "顺", "靖", "和", "穆"]
        self.princess_shihao_bad = ["悼", "哀", "愍", "荒", "炀", "幽"]

        # 皇帝尊号（风味化称谓，登基时随机组合两段）
        self.emperor_zunhao_pool = ["圣神", "文武", "睿圣", "应天", "至道", "玄元", "神功", "开天", "法天", "体元", "继天", "中和", "大圣", "大明", "光天", "崇文", "体道", "宪天", "述道", "体天", "法古", "建中", "宣和", "隆兴", "昭明", "敦孝", "钦明", "景命", "绍天", "凝命", "熙载", "显道", "绥猷", "敦叙", "彰信", "垂统", "启运", "肇纪", "景福", "嘉庆", "永乐", "太和", "咸熙", "弘道", "淳化", "雍熙", "端拱", "至治", "泰定"]

        self.reset_tang_pools()

    def reset_tang_pools(self):
        self.available_title_pools = {
            rank: list(names) for rank, names in self.rank_name_pools.items()
        }
        self.available_female_title_pools = {
            tier: list(names) for tier, names in self.female_title_pools.items()
        }

    def setup_dialogs(self):


        # New Emperor Dialog
        self.new_emp_dialog = QDialog(self)
        self.new_emp_dialog.setWindowTitle("新皇登基")
        new_emp_layout = QVBoxLayout()

        self.new_emp_form = QFormLayout()

        self.dialog_emp_input = QLineEdit()
        self.dialog_emp_btn = QPushButton("刷新")
        emp_hlayout = QHBoxLayout()
        emp_hlayout.addWidget(self.dialog_emp_input)
        emp_hlayout.addWidget(self.dialog_emp_btn)
        self.new_emp_form.addRow("姓名:", emp_hlayout)

        self.dialog_year_input = QLineEdit()
        self.dialog_year_btn = QPushButton("刷新")
        year_hlayout = QHBoxLayout()
        year_hlayout.addWidget(self.dialog_year_input)
        year_hlayout.addWidget(self.dialog_year_btn)
        self.new_emp_form.addRow("年号:", year_hlayout)

        new_emp_layout.addLayout(self.new_emp_form)

        self.new_emp_confirm_btn = QPushButton("确 定")
        new_emp_layout.addWidget(self.new_emp_confirm_btn)
        self.new_emp_dialog.setLayout(new_emp_layout)
        # Connect Signals for New Emp Dialog
        self.dialog_emp_btn.clicked.connect(self.emperor_change_name_after)
        self.dialog_year_btn.clicked.connect(self.dialog_yearNumber_change_name)
        self.new_emp_confirm_btn.clicked.connect(self.new_emp_confirm)

        # End Game Dialog
        self.end_game_dialog = QDialog(self)
        self.end_game_dialog.setWindowTitle("结束")
        self.end_game_dialog.resize(600, 400)
        end_game_layout = QVBoxLayout()

        self.end_game_tabs = QTabWidget()

        # Emperor List Tab
        self.end_game_emp_tab = QWidget()
        end_game_emp_layout = QVBoxLayout()
        self.dialog_emperor_list_table = QTableWidget()
        self.dialog_emperor_list_table.setColumnCount(9)
        self.dialog_emperor_list_table.setHorizontalHeaderLabels(["序号", "庙号", "谥号", "姓名", "年龄", "年号", "纪年", "治国手腕", "史书评价"])
        self.dialog_emperor_list_table.verticalHeader().setVisible(False)
        self.dialog_emperor_list_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        end_game_emp_layout.addWidget(self.dialog_emperor_list_table)
        self.end_game_emp_tab.setLayout(end_game_emp_layout)

        # Events Tab
        self.end_game_event_tab = QWidget()
        end_game_event_layout = QVBoxLayout()
        self.dialog_event_table = QTableWidget()
        self.dialog_event_table.setColumnCount(2)
        self.dialog_event_table.setHorizontalHeaderLabels(["时间", "事件"])
        self.dialog_event_table.verticalHeader().setVisible(False)
        self.dialog_event_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        end_game_event_layout.addWidget(self.dialog_event_table)
        self.end_game_event_tab.setLayout(end_game_event_layout)

        self.end_game_tabs.addTab(self.end_game_emp_tab, "皇帝列表")
        self.end_game_tabs.addTab(self.end_game_event_tab, "王朝纪事")
        end_game_layout.addWidget(self.end_game_tabs)

        end_game_layout.addWidget(QLabel("重新开始游戏？"))

        self.end_game_confirm_btn = QPushButton("确 定")
        end_game_layout.addWidget(self.end_game_confirm_btn)

        self.end_game_dialog.setLayout(end_game_layout)
        # Connect Signals for End Game Dialog
        self.end_game_confirm_btn.clicked.connect(self.dio2)

    def new_emp_confirm(self):
        self.emperor = self.dialog_emp_input.text()
        self.yearNumber = self.dialog_year_input.text()
        self.dio()

    def apply_stylesheet(self):
        app = QApplication.instance()
        qss = """
        /* ===== 全局：宣纸明堂 · 朱漆金边 ===== */
        QWidget {
            background-color: #f5efe3;
            color: #2c1810;
            font-family: "KaiTi", "STKaiti", "楷体", "FangSong", "仿宋", "SimSun", "宋体", serif;
            font-size: 14px;
        }
        QMainWindow, QDialog {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #faf6ec, stop:0.5 #f5efe3, stop:1 #ebe0cc);
        }

        /* 标题 / 匾额 */
        QLabel#title_label {
            font-size: 42px;
            font-weight: bold;
            color: #8b5a12;
            letter-spacing: 14px;
            padding: 14px 0 6px 14px;
            qproperty-alignment: AlignCenter;
        }
        QLabel#subtitle_label {
            color: #6b4e2e;
            font-size: 15px;
            letter-spacing: 4px;
            padding-bottom: 10px;
            qproperty-alignment: AlignCenter;
        }
        QLabel#reign_banner {
            font-size: 26px;
            font-weight: bold;
            color: #fff8e7;
            letter-spacing: 6px;
            padding: 10px 0;
            border: 2px solid #c9a24b;
            border-radius: 6px;
            background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                stop:0 #b83a32, stop:1 #8f2420);
            qproperty-alignment: AlignCenter;
        }
        QLabel#section_label {
            color: #7a4e12;
            font-size: 16px;
            font-weight: bold;
            padding: 6px 0 2px 0;
            border-bottom: 1px solid #c4a574;
            margin-bottom: 6px;
            letter-spacing: 3px;
        }

        /* 输入框 */
        QLineEdit {
            background-color: #fffdf8;
            border: 1px solid #c4a574;
            border-radius: 4px;
            padding: 6px 8px;
            color: #2c1810;
            selection-background-color: #d45a4a;
            selection-color: #fff8e7;
        }
        QLineEdit:focus {
            border: 1px solid #a67c3d;
            background-color: #ffffff;
        }

        /* 按钮 —— 朱漆玉印 */
        QPushButton {
            background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                stop:0 #c4453c, stop:1 #9a2e28);
            border: 1px solid #b5893f;
            border-radius: 5px;
            color: #fff8e7;
            padding: 7px 16px;
            font-size: 15px;
            letter-spacing: 2px;
        }
        QPushButton:hover {
            background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                stop:0 #d9554a, stop:1 #b83a32);
            border: 1px solid #d4af37;
            color: #ffffff;
        }
        QPushButton:pressed {
            background: #8f2420;
        }

        /* 标签页 */
        QTabWidget::pane {
            border: 1px solid #c4a574;
            border-radius: 4px;
            background: #faf6ec;
            top: -1px;
        }
        QTabBar::tab {
            background: #ebe0cc;
            color: #5c4030;
            padding: 8px 18px;
            border: 1px solid #c4a574;
            border-bottom: none;
            border-top-left-radius: 5px;
            border-top-right-radius: 5px;
            letter-spacing: 2px;
        }
        QTabBar::tab:selected {
            background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                stop:0 #c4453c, stop:1 #9a2e28);
            color: #fff8e7;
            border: 1px solid #b5893f;
            border-bottom: 1px solid #9a2e28;
        }
        QTabBar::tab:hover:!selected {
            background: #f0e6d2;
            color: #8b5a12;
        }

        /* 表格 / 树 */
        QTableWidget, QTreeWidget {
            background-color: #fffdf8;
            gridline-color: #d4c4a8;
            border: 1px solid #c4a574;
            border-radius: 4px;
            color: #2c1810;
            selection-background-color: #c4453c;
            selection-color: #fff8e7;
        }
        QHeaderView::section {
            background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                stop:0 #c4453c, stop:1 #9a2e28);
            color: #fff8e7;
            padding: 6px;
            border: 1px solid #a67c3d;
            font-weight: bold;
            letter-spacing: 1px;
        }
        QTableWidget::item, QTreeWidget::item {
            padding: 4px;
        }
        QTableWidget::item:alternate, QTreeWidget::item:alternate {
            background-color: #f3ead8;
        }

        /* 滑块 */
        QSlider::groove:horizontal {
            border: 1px solid #c4a574;
            height: 6px;
            border-radius: 3px;
            background: #ebe0cc;
        }
        QSlider::sub-page:horizontal {
            background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                stop:0 #c4453c, stop:1 #c9a24b);
            border-radius: 3px;
        }
        QSlider::handle:horizontal {
            background: qradialgradient(cx:0.5,cy:0.5,radius:0.5,
                stop:0 #fff8e7, stop:1 #c9a24b);
            border: 1px solid #a67c3d;
            width: 16px;
            height: 16px;
            border-radius: 8px;
            margin: -6px 0;
        }

        /* 滚动条 */
        QScrollBar:vertical {
            background: #ebe0cc;
            width: 12px;
            border-radius: 6px;
        }
        QScrollBar::handle:vertical {
            background: #c4a574;
            border-radius: 6px;
            min-height: 20px;
        }
        QScrollBar::handle:vertical:hover { background: #b5893f; }
        QScrollBar:horizontal {
            background: #ebe0cc;
            height: 12px;
            border-radius: 6px;
        }
        QScrollBar::handle:horizontal {
            background: #c4a574;
            border-radius: 6px;
            min-width: 20px;
        }

        /* 表单标签 */
        QLabel {
            color: #3d2914;
        }
        """
        app.setStyleSheet(qss)

    def setup_start_screen(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 30, 40, 30)

        # 醒目标题，增强代入感
        title = QLabel("王 朝")
        title.setObjectName("title_label")
        subtitle = QLabel("—— 一代天骄，执掌乾坤 ——")
        subtitle.setObjectName("subtitle_label")
        layout.addWidget(title)
        layout.addWidget(subtitle)

        form_layout = QFormLayout()

        # Dynasty input
        self.dynasty_input = QLineEdit()
        self.dynasty_btn = QPushButton("刷新")
        dynasty_layout = QHBoxLayout()
        dynasty_layout.addWidget(self.dynasty_input)
        dynasty_layout.addWidget(self.dynasty_btn)
        form_layout.addRow("朝代:", dynasty_layout)

        # Emperor input
        self.emperor_input = QLineEdit()
        self.emperor_btn = QPushButton("刷新")
        emperor_layout = QHBoxLayout()
        emperor_layout.addWidget(self.emperor_input)
        emperor_layout.addWidget(self.emperor_btn)
        form_layout.addRow("皇帝:", emperor_layout)

        # Year number input
        self.year_number_input = QLineEdit()
        self.year_number_btn = QPushButton("刷新")
        year_number_layout = QHBoxLayout()
        year_number_layout.addWidget(self.year_number_input)
        year_number_layout.addWidget(self.year_number_btn)
        form_layout.addRow("年号:", year_number_layout)

        layout.addLayout(form_layout)

        # Start Button
        self.start_btn = QPushButton("开始游戏")
        layout.addWidget(self.start_btn)

        self.start_screen.setLayout(layout)
        # Connect signals
        self.dynasty_btn.clicked.connect(self.dynasty_change_name)
        self.emperor_btn.clicked.connect(self.emperor_change_name)
        self.year_number_btn.clicked.connect(self.yearNumber_change_name)
        self.start_btn.clicked.connect(self.start_game_from_ui)

    def start_game_from_ui(self):
        self.dynasty = self.dynasty_input.text()
        self.emperor = self.emperor_input.text()
        self.yearNumber = self.year_number_input.text()
        self.gamestart()

    def achange(self, value):
        self.amuse = value
        self.hardworking = 100 - self.amuse
        self.hardworking_slider.setValue(self.hardworking)

    def bchange(self, value):
        self.hardworking = value
        self.amuse = 100 - self.hardworking
        self.amuse_slider.setValue(self.amuse)

    def gamestart(self):
        if not self.emperor:
            return
        self.emperor_firstname = self.infer_surname_from_name(self.emperor)
        self.emperor_age = 26
        # Start emperor with a solid reign: 20 to 45 years left to live.
        self.emperor_hp = 20 + math.floor(random.random() * 25)
        self.emperor_ab = 10

        # Create first Emperor Person
        emp_person = Person(self.next_pid, self.emperor, "M", self.year - self.emperor_age, None, None, 1)
        emp_person.age = self.emperor_age
        emp_person.hp = self.emperor_hp
        emp_person.ability = self.emperor_ab
        emp_person.title = "皇帝"
        emp_person.is_married = True # Assume married
        self.emperor_zunhao = self.generate_zunhao()
        emp_person.zunhao = self.emperor_zunhao
        self.people.append(emp_person)
        self.current_emperor_pid = emp_person.id
        self.next_pid += 1

        self.dynasty_hp = 100
        self.initial_dynasty_hp = 100
        self.used_emperor_names.append(self.emperor)
        self.register_person_name(self.emperor)
        self.used_nianhao.append(self.yearNumber)
        self.start_new_emperor_nianhao_history()
        self.dynasty_function_st()
        self.update_ui()
        self.stacked_widget.setCurrentIndex(1)

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

    def gamemin(self):
        self.year += 1
        self.event_happen()
        self.gamemin_family_aging_death()
        self.gamemin_emperor()
        self.gamemin_dynasty()
        self.gamemin_family_marriage_birth()
        self.update_crown_prince() # Calls update_heirs internally
        self.gamemin_family_shihao_titles()
        self.dynasty_function_st()
        self.update_ui()

    def get_person_by_id(self, pid):
        for p in self.people:
            if p.id == pid:
                return p
        return None

    def gamemin_family_aging_death(self):
        for p in self.people:
            if p.is_alive and p.id != self.current_emperor_pid:
                p.age += 1
                p.hp -= 1
                if p.hp <= 0:
                    p.is_alive = False
                    p.death_year = self.year

    def get_descendants(self, pid):
        descendants = []
        p = self.get_person_by_id(pid)
        if p:
            for child_id in p.children:
                descendants.append(child_id)
                descendants.extend(self.get_descendants(child_id))
        return descendants

    def check_extinct(self, pid):
        p = self.get_person_by_id(pid)
        if not p or p.gender != "M":
            return False

        # Check if any male descendants are alive
        descendant_ids = self.get_descendants(pid)
        has_alive_male_heir = False
        for d_id in descendant_ids:
            d = self.get_person_by_id(d_id)
            if d and d.gender == "M" and d.is_alive:
                has_alive_male_heir = True
                break

        return not has_alive_male_heir

    def find_adoptee(self, person):
        """过继：择兄弟之子（侄）中尚存者承嗣，优先未受封、年长者，以减少绝嗣。"""
        father_id = person.father_id
        if father_id is None:
            return None

        candidates = []
        for sib in self.people:
            if sib.id == person.id or sib.father_id != father_id or sib.gender != "M":
                continue
            for child_id in sib.children:
                child = self.get_person_by_id(child_id)
                if child and child.gender == "M" and child.is_alive:
                    candidates.append(child)

        if not candidates:
            return None

        # 优先未受封者（可继承本支封国），其次年长者
        candidates.sort(key=lambda c: (0 if not c.has_title else 1, -c.age))
        return candidates[0]

    def get_rank_suffix(self, rank):
        return self.rank_suffix_map.get(rank, "爵")

    def get_guobie(self, person):
        """皇亲国戚的国别（封国）。皇帝（含已崩者）归皇室，受封者归其封国，未受封者标未封。"""
        if (person.id == self.current_emperor_pid or person.title == "皇帝"
                or person.title == "太子" or person.miaohao):
            return "皇室"
        if person.title_name:
            return person.title_name
        return "未封"

    def is_name_used(self, name):
        return name in self.used_person_names or name in self.used_emperor_names

    def register_person_name(self, name):
        if name and name not in self.used_person_names:
            self.used_person_names.append(name)

    def choose_dynasty_surname(self):
        self.emperor_firstname = random.choice(self.tang_surnames)
        return self.emperor_firstname

    def infer_surname_from_name(self, full_name):
        for surname in sorted(self.tang_surnames, key=len, reverse=True):
            if full_name.startswith(surname):
                return surname
        return full_name[0] if full_name else ""

    def generate_given_name(self, gender):
        if gender == "M":
            if random.random() < 0.45:
                return random.choice(self.tang_male_given_single)
            return random.choice(self.tang_male_given_double)

        if random.random() < 0.45:
            return random.choice(self.tang_female_given_single)
        return random.choice(self.tang_female_given_double)

    def generate_zunhao(self):
        """组合两段尊号碎片，生成如『圣神文武皇帝』的风味化尊号。"""
        pool = list(self.emperor_zunhao_pool)
        if len(pool) < 2:
            return "皇帝"
        frags = random.sample(pool, 2)
        return "".join(frags) + "皇帝"

    def generate_full_name(self, gender, surname=None):
        family_name = surname if surname else random.choice(self.tang_surnames)
        attempts = 0
        while attempts < 200:
            given_name = self.generate_given_name(gender)
            candidate = family_name + given_name
            if not self.is_name_used(candidate):
                return candidate
            attempts += 1

        suffix = 1
        while True:
            candidate = f"{family_name}{self.generate_given_name(gender)}{suffix}"
            if not self.is_name_used(candidate):
                return candidate
            suffix += 1

    def draw_title_name(self, rank):
        pool = self.available_title_pools.get(rank, [])
        if pool:
            return pool.pop(0)

        fallback_pool = self.rank_name_pools.get(rank, [])
        if fallback_pool:
            return random.choice(fallback_pool)
        return ""

    def draw_female_title_name(self, tier):
        pool = self.available_female_title_pools.get(tier, [])
        if pool:
            return pool.pop(0)

        fallback_pool = self.female_title_pools.get(tier, [])
        if fallback_pool:
            return random.choice(fallback_pool)
        return ""

    def get_princess_tier(self, person):
        if person.title == "公主":
            return "公主"
        if person.title == "郡主":
            return "郡主"
        if person.title == "县主":
            return "县主"
        if person.title == "乡主":
            return "乡主"
        return ""

    def ensure_female_title_name(self, person):
        tier = self.get_princess_tier(person)
        if tier and not person.title_name:
            person.title_name = self.draw_female_title_name(tier)

    def format_alive_title(self, person):
        if person.id == self.current_emperor_pid:
            return "皇帝"
        if person.title == "皇后":
            return "皇后"
        if person.title == "太子":
            return "太子"
        if person.title in ["公主", "郡主", "县主", "乡主"]:
            self.ensure_female_title_name(person)
            return f"{person.title_name}{person.title}" if person.title_name else person.title
        if person.has_title and person.title_name:
            return f"{person.title_name}{self.get_rank_suffix(person.title_rank)}"
        if person.is_heir:
            father = self.get_person_by_id(person.father_id)
            if father and father.title_name and father.title_rank <= 5:
                return f"{father.title_name}{self.get_heir_posthumous_suffix(father)}"
        return ""

    def get_heir_posthumous_suffix(self, father):
        if father:
            suffix_map = {
                1: "王世子",
                2: "郡王世子",
                3: "国公世子",
                4: "郡公世子",
                5: "县公世子",
            }
            if father.id == self.current_emperor_pid:
                return "皇太子"
            if father.title_rank in suffix_map:
                return suffix_map[father.title_rank]
        return "世子"

    def choose_family_posthumous_word(self, person):
        # Family posthumous naming uses more than ability:
        # age, succession status, lineage continuity and reign climate all affect tone.
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
        if person.title_rank in [1, 2]:
            context_score += 1

        if person.death_year == self.year and self.data_dynasty_hp_change <= -5:
            context_score -= 2
        if self.dynasty_hp < 25:
            context_score -= 1

        if person.age < 8:
            return random.choice(["殇", "悼"])
        if person.title == "皇后":
            pool = self.empress_shihao_good if context_score >= 8 else self.empress_shihao_neutral
            if context_score <= 3:
                pool = self.empress_shihao_bad
            return random.choice(pool)
        if person.title == "太子":
            pool = self.taizi_shihao_good if context_score >= 8 else self.taizi_shihao_neutral
            if context_score <= 3:
                pool = self.taizi_shihao_bad
            return random.choice(pool)
        if person.title in ["公主", "郡主", "县主", "乡主"]:
            pool = self.princess_shihao_good if context_score >= 8 else self.princess_shihao_neutral
            if context_score <= 3:
                pool = self.princess_shihao_bad
            return random.choice(pool)

        if context_score >= 8:
            return random.choice(self.prince_shihao_good)
        if context_score >= 4:
            return random.choice(self.prince_shihao_neutral)
        return random.choice(self.prince_shihao_bad)

    def build_family_posthumous_title(self, person):
        chosen_shihao = self.choose_family_posthumous_word(person)

        if person.title == "皇后":
            return f"{chosen_shihao}皇后"
        if person.title == "太子":
            return f"{chosen_shihao}太子"
        if person.title in ["公主", "郡主", "县主", "乡主"]:
            self.ensure_female_title_name(person)
            if person.title_name:
                return f"{person.title_name}{chosen_shihao}{person.title}"
            return f"{chosen_shihao}{person.title}"
        if person.has_title and person.title_name:
            return f"{person.title_name}{chosen_shihao}{self.get_rank_suffix(person.title_rank)}"
        if person.is_heir:
            father = self.get_person_by_id(person.father_id)
            suffix = self.get_heir_posthumous_suffix(father)
            if father and father.title_name:
                return f"{father.title_name}{chosen_shihao}{suffix}"
            return f"{chosen_shihao}{suffix}"
        return ""

    def gamemin_family_shihao_titles(self):
        for p in self.people:
            # Grant initial titles to those who reached adulthood
            if p.is_alive and p.gender == "M" and p.age >= 15 and not p.title_name and p.id != self.current_emperor_pid:
                if not p.is_heir or (p.is_heir and p.has_title):
                    if not p.has_title:
                        p.title_name = self.draw_title_name(p.title_rank)
                        if p.title_name:
                            p.has_title = True

            # Format display titles for alive members
            if p.is_alive:
                p.title = self.format_alive_title(p)

            # Dead members logic
            if not p.is_alive and p.death_year == self.year:
                # Assign shihao
                if not p.shihao and (p.has_title or p.is_heir or p.title in ["太子", "皇后", "公主", "郡主", "县主", "乡主"]):
                    p.shihao = self.build_family_posthumous_title(p)

                # Title Inheritance Logic
                if p.gender == "M" and p.has_title:
                    # Find heir to pass the title to
                    heir = None
                    for child_id in p.children:
                        child = self.get_person_by_id(child_id)
                        if child and child.is_alive and child.is_heir:
                            heir = child
                            break

                    if heir:
                        heir.title_name = p.title_name
                        heir.title_rank = p.title_rank
                        heir.has_title = True
                        p.has_title = False # Handed off
                    else:
                        # 减少绝嗣：无子则尝试过继侄子承嗣
                        adoptee = self.find_adoptee(p)
                        if adoptee:
                            p.extinct = False
                            adoptee.is_heir = True
                            adoptee.adopted_from = p.id
                            if not adoptee.has_title and p.title_name:
                                # 嗣子继承本支封国，国祚得以延续
                                adoptee.title_name = p.title_name
                                adoptee.title_rank = p.title_rank
                                adoptee.has_title = True
                                p.has_title = False
                            elif p.title_name:
                                # 嗣子已有封国，本支封国收回
                                self.available_title_pools.setdefault(p.title_rank, []).append(p.title_name)
                                p.has_title = False
                        else:
                            # Check extinction properly
                            p.extinct = self.check_extinct(p.id)

                            # Line effectively extinct for inheritance purposes if no direct heir found to take the title
                            if p.title_name:
                                self.available_title_pools.setdefault(p.title_rank, []).append(p.title_name)
                                p.has_title = False

    def get_random_name(self, gender):
        name = self.generate_full_name(gender, surname=self.emperor_firstname)
        self.register_person_name(name)
        return name

    def try_spawn_child(self, father, child_rank, force_gender=None):
        if child_rank > 7:
            return

        gender = force_gender if force_gender else random.choice(["M", "F"])
        child_name = self.get_random_name(gender)
        child = Person(self.next_pid, child_name, gender, self.year, father.id, None, father.generation + 1)

        if gender == "M":
            child.title_rank = child_rank
        else:
            if father.id == self.current_emperor_pid:
                child.title = "公主"
                child.title_rank = 0
            elif father.title_rank == 1:
                child.title = "郡主"
                child.title_rank = 0
            elif father.title_rank <= 3:
                child.title = "县主"
                child.title_rank = 0
            else:
                child.title = "乡主"
                child.title_rank = 0

        self.people.append(child)
        father.children.append(self.next_pid)
        self.next_pid += 1

    def gamemin_family_marriage_birth(self):
        for p in self.people:
            if not p.is_alive or p.gender != "M":
                continue

            # Process reproduction for emperor and those with rank <= 5
            if p.title_rank > 5 and p.id != self.current_emperor_pid:
                continue

            is_emperor = (p.id == self.current_emperor_pid)

            # Marriage logic: Age >= 16, higher chance to marry so fewer bachelors
            if p.age >= 16 and not p.is_married:
                if random.random() < 0.2:
                    p.is_married = True
                    spouse_name = self.generate_full_name("F")
                    self.register_person_name(spouse_name)
                    spouse = Person(self.next_pid, spouse_name, "F", self.year - p.age + random.randint(-5, 2), None, None, p.generation)
                    spouse.age = p.age - random.randint(-2, 5)
                    spouse.is_married = True
                    if is_emperor:
                        spouse.title = "皇后"
                    spouse.spouse_id = p.id
                    p.spouse_id = spouse.id
                    self.people.append(spouse)
                    self.next_pid += 1

            # Birth logic: Emperor has harem, so no marriage check needed.
            if (p.is_married or is_emperor) and p.age >= 15 and p.age <= 60:
                # Calculate chance based on rank (提高生育率)
                chance = 0.5 if is_emperor else 0.2

                if random.random() < chance:
                    existing_sons = [self.get_person_by_id(cid) for cid in p.children]
                    existing_sons = [s for s in existing_sons if s and s.gender == "M"]

                    if len(existing_sons) == 0:
                        child_rank = 1 if is_emperor else p.title_rank
                    else:
                        child_rank = 1 if is_emperor else min(p.title_rank + 1, 7)

                    self.try_spawn_child(p, child_rank)

                    # 提高生育率：尚无子嗣者，额外给一次生育机会，减少无后
                    if len(existing_sons) == 0 and random.random() < 0.3:
                        self.try_spawn_child(p, child_rank)

                    if is_emperor and random.random() < 0.2:
                        self.try_spawn_child(p, 1)

    def update_heirs(self):
        # Ensure every noble or emperor designates their eldest living son as heir
        for p in self.people:
            is_current_emperor = (p.id == self.current_emperor_pid)
            if p.gender == "M" and ((p.is_alive and p.has_title) or is_current_emperor):
                # Find current heir
                current_heir = None
                eldest_living_son = None

                for child_id in p.children:
                    child = self.get_person_by_id(child_id)
                    if child and child.gender == "M":
                        if child.is_alive:
                            if eldest_living_son is None or child.age > eldest_living_son.age:
                                eldest_living_son = child
                        if child.is_heir:
                            current_heir = child

                # If current heir is dead or not eldest, reassign
                if eldest_living_son:
                    if current_heir and current_heir.id != eldest_living_son.id:
                        current_heir.is_heir = False
                    eldest_living_son.is_heir = True

    def update_crown_prince(self):
        self.update_heirs()

        # Find if there is already a Crown Prince
        has_taizi = False
        for p in self.people:
            if p.is_alive and p.title == "太子":
                has_taizi = True
                self.next_emperor_pid = p.id
                break

        if not has_taizi and self.current_emperor_pid:
            emp = self.get_person_by_id(self.current_emperor_pid)
            if emp:
                # Find eldest living male son (should be the designated heir)
                for child_id in emp.children:
                    child = self.get_person_by_id(child_id)
                    if child and child.is_alive and child.is_heir:
                        # Reclaim any title the heir had
                        if child.title_name and child.has_title:
                            self.available_title_pools.setdefault(child.title_rank, []).append(child.title_name)
                            child.has_title = False

                        child.title = "太子"
                        self.next_emperor_pid = child.id
                        break

    def find_collateral_successor(self):
        # Look for the closest male relative.
        # Strategy: find all living males, sort by generation ascending, then age descending
        candidates = []
        for p in self.people:
            if p.is_alive and p.gender == "M" and p.id != self.current_emperor_pid:
                candidates.append(p)

        if not candidates:
            return None

        # Sort candidates
        candidates.sort(key=lambda x: (x.generation, -x.age))
        return candidates[0].id

    def find_successor(self):
        self.update_crown_prince()
        if self.next_emperor_pid:
            # Recheck if the prince is alive
            p = self.get_person_by_id(self.next_emperor_pid)
            if p and p.is_alive:
                return self.next_emperor_pid

        # Find collateral
        return self.find_collateral_successor()

    def gamemin_dynasty(self):
        if self.dynasty_hp > 0:
            # Balance: Slow down dynasty decay to last ~150-300 years
            self.dynasty_hp = self.dynasty_hp - (self.amuse / 60 * 2.5 / max(1, self.emperor_ab)) + (self.hardworking / 60 * self.emperor_ab / 15)
            self.dynasty_age += 1

        if self.dynasty_hp >= 100:
            self.dynasty_hp = 100

        # A brilliant ruler (ability >= 8) can keep the dynasty from collapsing
        # below a floor of 15, but only while the dynasty still stands.
        if 0 < self.dynasty_hp <= 15 and self.emperor_ab >= 8:
            self.dynasty_hp = 15

        if self.dynasty_hp <= 0:
            self.dynasty_die = True
            self.dynasty_hp = 0
            if self.ongame:
                self.gamemin_shihao()
                self.gamemin_dynasty_change()
                self.ongame = False
                self.show_end_game_dialog()

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
                        self.ongame = False
                        self.dynasty_die = True
                        self.dynasty_hp = 0
                        self.gamemin_dynasty_change()
                        self.show_end_game_dialog()
                    else:
                        # If the successor had a title, reclaim it so it can be used again
                        succ = self.get_person_by_id(succ_id)
                        if succ and succ.has_title and succ.title_name:
                            self.available_title_pools.setdefault(succ.title_rank, []).append(succ.title_name)
                            succ.has_title = False

                        self.next_emperor_pid = succ_id
                        self.ongame = False
                        self.show_new_emp_dialog()
                else:
                    self.emperor_hp = 0
                    self.emperor_die = True

    def gamemin_shihao(self):
        # Calculate performance
        hp_change = self.dynasty_hp - self.initial_dynasty_hp
        performance_score = self.emperor_ab + (hp_change / 5)

        # Generate Miaohao
        def get_unique_miaohao(pool):
            available = list(set(pool) - set(self.used_miaohao))
            if available:
                return random.choice(available)
            return None

        if self.emperor_id == 1:
            self.miaohao = get_unique_miaohao(self.emperor_miaohao_founders) or "高祖"
        else:
            # 庙号档次与史书评价档次保持一致：
            #   盛世明君 / 中兴守成  ->  prosperous（太宗、玄宗、宪宗、宣宗…）
            #   平庸 / 昏庸          ->  stable  （顺宗、代宗、文宗、穆宗、敬宗…）
            #   亡国末代             ->  decline （哀宗、昭宗、恭宗、襄宗）
            if performance_score >= 6:
                target_pool = self.emperor_miaohao_prosperous
            elif performance_score >= -6:
                target_pool = self.emperor_miaohao_stable
            else:
                target_pool = self.emperor_miaohao_decline

            self.miaohao = get_unique_miaohao(target_pool)
            if not self.miaohao:
                for fallback_pool in [
                    self.emperor_miaohao_prosperous,
                    self.emperor_miaohao_stable,
                    self.emperor_miaohao_decline,
                ]:
                    self.miaohao = get_unique_miaohao(fallback_pool)
                    if self.miaohao:
                        break
            if not self.miaohao:
                self.miaohao = "元宗"

        self.used_miaohao.append(self.miaohao)

        # 谥号档次：开国之君例用褒谥；其余依功过，且仅明显败坏之朝方用恶谥
        if self.emperor_id == 1:
            core_pool = self.emperor_shifa_core_good
            assist_pool = self.emperor_shifa_assist_good
        elif performance_score >= 8:
            core_pool = self.emperor_shifa_core_good
            assist_pool = self.emperor_shifa_assist_good
        elif performance_score >= -4:
            core_pool = self.emperor_shifa_core_mid
            assist_pool = self.emperor_shifa_assist_mid
        else:
            core_pool = self.emperor_shifa_core_bad
            assist_pool = self.emperor_shifa_assist_bad

        candidate_pool = []
        for _ in range(80):
            core = random.choice(core_pool)
            use_assist = random.random() < 0.45
            if use_assist:
                assist = random.choice(assist_pool)
                if assist != core:
                    candidate_pool.append(f"{core}{assist}皇帝")
            candidate_pool.append(f"{core}皇帝")

        # Strong reigns can occasionally receive longer celebratory styles.
        if performance_score >= 15:
            candidate_pool.extend([
                "文武圣德皇帝",
                "睿文广孝皇帝",
                "英武景成皇帝",
            ])

        unique_candidate = None
        for candidate in candidate_pool:
            if candidate not in self.used_shihao:
                unique_candidate = candidate
                break

        if not unique_candidate:
            fallback_core = "恭" if performance_score >= 0 else "哀"
            unique_candidate = f"{fallback_core}皇帝"
            while unique_candidate in self.used_shihao:
                unique_candidate = f"{fallback_core}{random.choice(['安', '简', '昭', '悼'])}皇帝"

        self.used_shihao.append(unique_candidate)
        self.shihao = unique_candidate

        # Generate Historical Verdict (史书评价)
        if self.emperor_id == 1:
            self.verdict = "开国之君，肇基宏业"
        else:
            if performance_score >= 12:
                self.verdict = random.choice(["千古一帝，开创盛世", "文治武功，威震海内", "一代明君，泽被苍生"])
            elif performance_score >= 6:
                self.verdict = random.choice(["中兴之主，力挽狂澜", "守成有余，天下太平", "知人善任，励精图治"])
            elif performance_score >= 0:
                self.verdict = random.choice(["平庸无为，守成之君", "功过参半，治政平平", "因循守旧，乏善可陈"])
            elif performance_score >= -6:
                self.verdict = random.choice(["宠信奸佞，朝政日非", "好大喜功，劳民伤财", "昏庸无道，纲纪败坏"])
            else:
                self.verdict = random.choice(["亡国之君，宗庙毁绝", "暴虐无道，天下大乱", "沉迷酒色，丧权辱国"])

    def _record_emperor(self):
        nianhao_history = [dict(item) for item in self.current_emperor_nianhao_history if item.get("years", 0) > 0]
        total_reign_years = sum(item["years"] for item in nianhao_history)
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
            "verdict": self.verdict
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
            self.emperor = succ.name
            self.emperor_age = succ.age
            self.emperor_ab = succ.ability
            self.emperor_hp = succ.hp
            succ.title = "皇帝"
            succ.is_heir = False
            succ.has_title = False
            succ.title_name = ""
            succ.title_rank = 0  # 即帝位，爵位品级归零，不再保留旧封号
            self.current_emperor_pid = succ.id
            self.next_emperor_pid = None
        else:
            self.emperor_new_age()
            self.emperor_ab = roll_ability()
            self.emperor_new_hp()

        self.emperor_zunhao = self.generate_zunhao()
        if succ:
            succ.zunhao = self.emperor_zunhao

        self.initial_dynasty_hp = self.dynasty_hp

    def gamemin_dynasty_change(self):
        self._record_emperor()

    def gamemin_dynasty_new(self):
        self.people = []
        self.next_pid = 1
        self.current_emperor_pid = None
        self.next_emperor_pid = None
        self.reset_tang_pools()
        self.dynasty_age = 0
        self.jinian = 1
        self.listjson = []
        self.current_emperor_nianhao_history = []
        self.year = 0
        self.emperor_id = 1
        self.event_happened = [{"time": "", "event": ""}]
        self.used_shihao = []
        self.used_miaohao = []
        self.used_emperor_names = []
        self.used_person_names = []
        self.used_nianhao = []
        self.initial_dynasty_hp = 100

    def dio(self):
        self.emperor_die = False
        self.new_emp_dialog.accept()
        self.gamemin_emperor_new()
        self.start_new_emperor_nianhao_history()
        self.emperor_id += 1
        self.ongame = True
        self.update_ui()

    def dio2(self):
        self.dynasty_die = False
        self.end_game_dialog.accept()
        self.gamemin_dynasty_new()
        self.ongame = True

        # When restarting, they go to the start screen.
        # But we need to clear inputs just in case, or let them input again.
        self.dynasty_input.setText("")
        self.emperor_input.setText("")
        self.year_number_input.setText("")

        self.stacked_widget.setCurrentIndex(0)

    def dynasty_change_name(self):
        self.dynasty = random.choice(self.dynasty_name)
        self.dynasty_input.setText(self.dynasty)

    def emperor_change_name(self):
        self.choose_dynasty_surname()
        while True:
            self.emperor_lastname = self.generate_given_name("M")
            candidate = self.emperor_firstname + self.emperor_lastname
            if candidate not in self.used_emperor_names:
                self.emperor = candidate
                break
        self.emperor_input.setText(self.emperor)

    def emperor_new_hp(self):
        # Target a realistic lifespan: ancient emperors usually lived to 45-65.
        target_lifespan = 45 + math.floor(random.random() * 25)
        self.emperor_hp = target_lifespan - self.emperor_age

        # Ensure a minimum reign of 1 year unless they are very old
        if self.emperor_hp <= 0:
            self.emperor_hp = math.floor(random.random() * 5) + 1

    def emperor_new_age(self):
        # A realistic succession age: an adult heir is usually 15-40 years old
        self.emperor_age = 15 + math.floor(random.random() * 25)

    def get_unique_nianhao(self):
        available = list(set(self.yearNumber_list) - set(self.used_nianhao))
        if available:
            return random.choice(available)
        else:
            # Fallback dynamic generation if list is exhausted
            chars = "建元平太开天宝大中盛和治熙庆兴宁隆顺应永"
            while True:
                candidate = random.choice(chars) + random.choice(chars)
                if candidate not in self.used_nianhao:
                    return candidate

    def yearNumber_change_name(self):
        self.yearNumber = self.get_unique_nianhao()
        self.year_number_input.setText(self.yearNumber)

    def dialog_yearNumber_change_name(self):
        self.yearNumber = self.get_unique_nianhao()
        self.used_nianhao.append(self.yearNumber)
        self.dialog_year_input.setText(self.yearNumber)

    def emperor_change_name_after(self):
        while True:
            self.emperor_lastname = self.generate_given_name("M")
            candidate = self.emperor_firstname + self.emperor_lastname
            if candidate not in self.used_emperor_names:
                self.emperor = candidate
                self.used_emperor_names.append(candidate)
                break
        self.dialog_emp_input.setText(self.emperor)

    def dynasty_function_st(self):
        if self.dynasty_hp >= 90:
            if self.emperor_ab >= 8:
                self.dynasty_st = "开元盛世，万国来朝"
            else:
                self.dynasty_st = "国泰民安，海晏河清"
        elif self.dynasty_hp >= 80:
            if self.emperor_ab >= 6:
                self.dynasty_st = "风调雨顺，百业兴旺"
            else:
                self.dynasty_st = "天下承平，守成之局"
        elif self.dynasty_hp >= 60:
            if self.emperor_ab >= 7:
                self.dynasty_st = "中兴在望，奋发图强"
            elif self.emperor_ab <= 4:
                self.dynasty_st = "外强中干，隐患暗生"
            else:
                self.dynasty_st = "差强人意，平平无奇"
        elif self.dynasty_hp >= 40:
            if self.emperor_ab >= 8:
                self.dynasty_st = "励精图治，力挽狂澜"
            else:
                self.dynasty_st = "山雨欲来，动荡不安"
        elif self.dynasty_hp >= 20:
            if self.emperor_ab >= 9:
                self.dynasty_st = "独木难支，夕阳无限"
            else:
                self.dynasty_st = "风雨飘摇，国势倾颓"
        elif self.dynasty_hp >= 10:
            self.dynasty_st = "不绝如缕，大厦将倾"
        else:
            self.dynasty_st = "亡国之兆，日暮途穷"

    def event_happen(self):
        self.event_id_chose()

        # Determine current year string before possible change
        if self.jinian == 1:
            self.d_time = self.yearNumber + "元年"
        else:
            self.d_time = self.yearNumber + str(self.jinian) + "年"

        self.d_event = self.event_list[self.event_id]["event"]
        self.d_event_id = self.event_id

        event_dict = {"time": self.d_time, "event": self.d_event}
        self.event_happened.append(event_dict)
        self.record_current_year_for_nianhao()

        self.event_change()
        self.emperor_hp += self.data_emperor_hp_change
        self.dynasty_hp += self.data_dynasty_hp_change

        # Dynamic Nianhao change: occurs if an extreme event happens (-5 or more impact)
        # and has a 20% chance. We reset jinian to 1 when year number changes.
        if abs(self.data_dynasty_hp_change) >= 5 and random.random() < 0.2:
            self.yearNumber = self.get_unique_nianhao()
            self.used_nianhao.append(self.yearNumber)
            self.begin_next_nianhao_segment()
            self.jinian = 0  # will be incremented to 1 next tick
            change_event = {"time": self.d_time, "event": f"皇帝为祈福/应天象，改元 {self.yearNumber}。"}
            self.event_happened.append(change_event)

    def event_id_chose(self):
        self.event_id = random.randrange(len(self.event_list))

    def event_change(self):
        evt = self.event_list[self.d_event_id]
        if "emperor_hp_change" in evt and evt["emperor_hp_change"] is not None:
            self.data_emperor_hp_change = evt["emperor_hp_change"]
        else:
            self.data_emperor_hp_change = 0

        if "dynasty_hp_change" in evt and evt["dynasty_hp_change"] is not None:
            self.data_dynasty_hp_change = evt["dynasty_hp_change"]
        else:
            self.data_dynasty_hp_change = 0

    def update_ui(self):

        # 朝代年号匾额
        reign_text = f"　{self.dynasty}　·　{self.yearNumber}　"
        self.reign_banner.setText(reign_text)

        # Update Tab 1
        self.dynasty_label.setText(self.dynasty)
        self.emperor_label.setText(self.emperor)
        self.year_number_label.setText(self.yearNumber)
        self.jinian_label.setText("元" if self.jinian == 1 else str(self.jinian))
        self.dynasty_st_label.setText(self.dynasty_st)
        self.emperor_hp_label.setText(str(round(self.emperor_hp)))

        # Event Table
        self.event_table.setRowCount(0)
        # Skip the first empty placeholder
        for i, ev in enumerate(self.event_happened[1:]):
            self.event_table.insertRow(i)
            self.event_table.setItem(i, 0, QTableWidgetItem(ev["time"]))
            self.event_table.setItem(i, 1, QTableWidgetItem(ev["event"]))
        self.event_table.scrollToBottom()

        # Update Tab 2
        self.emp_name_label.setText(self.emperor)
        self.emp_zunhao_label.setText(self.emperor_zunhao)
        self.emp_age_label.setText(str(self.emperor_age))
        self.emp_hp_label.setText(str(round(self.emperor_hp)))
        self.emp_ab_label.setText(str(self.emperor_ab))

        # Update Tab 3
        self.dyn_name_label.setText(self.dynasty)
        self.dyn_age_label.setText(str(self.dynasty_age))
        self.dyn_st_label.setText(self.dynasty_st)

        self.emperor_list_table.setRowCount(0)
        for i, emp in enumerate(self.listjson):
            self.emperor_list_table.insertRow(i)
            self.emperor_list_table.setItem(i, 0, QTableWidgetItem(str(emp["id"])))
            self.emperor_list_table.setItem(i, 1, QTableWidgetItem(emp["miaohao"]))
            self.emperor_list_table.setItem(i, 2, QTableWidgetItem(emp["shihao"]))
            self.emperor_list_table.setItem(i, 3, QTableWidgetItem(emp["name"]))
            self.emperor_list_table.setItem(i, 4, QTableWidgetItem(str(emp["age"])))
            self.emperor_list_table.setItem(i, 5, QTableWidgetItem(emp["nianhao"]))
            self.emperor_list_table.setItem(i, 6, QTableWidgetItem(str(emp["jinian"])))
            self.emperor_list_table.setItem(i, 7, QTableWidgetItem(str(emp["ab"])))
            self.emperor_list_table.setItem(i, 8, QTableWidgetItem(emp["verdict"]))

        # Update Tab 4
        if hasattr(self, 'family_table'):
            self.family_table.setRowCount(0)
            # 收集所有男性宗亲，按国别分类（同国者聚拢），未封者置后
            males = [p for p in self.people if p.gender != "F"]
            males.sort(key=lambda p: (
                0 if self.get_guobie(p) != "未封" else 1,
                self.get_guobie(p),
                p.generation,
                -p.age,
            ))
            row_idx = 0
            for p in males:
                self.family_table.insertRow(row_idx)
                self.family_table.setItem(row_idx, 0, QTableWidgetItem(str(p.id)))
                self.family_table.setItem(row_idx, 1, QTableWidgetItem(p.name))
                self.family_table.setItem(row_idx, 2, QTableWidgetItem("男" if p.gender == "M" else "女"))
                self.family_table.setItem(row_idx, 3, QTableWidgetItem(str(p.age)))
                self.family_table.setItem(row_idx, 4, QTableWidgetItem(p.title))
                self.family_table.setItem(row_idx, 5, QTableWidgetItem(self.get_guobie(p)))
                self.family_table.setItem(row_idx, 6, QTableWidgetItem("存活" if p.is_alive else "已故"))
                self.family_table.setItem(row_idx, 7, QTableWidgetItem(p.shihao))
                self.family_table.setItem(row_idx, 8, QTableWidgetItem(str(p.generation)))
                self.family_table.setItem(row_idx, 9, QTableWidgetItem("绝嗣" if p.extinct else ""))
                row_idx += 1

            # 显眼的树状图：按国别分组展示谱系
            self.update_family_tree()

    def update_family_tree(self):
        tree = self.family_tree_widget
        tree.setUpdatesEnabled(False)
        tree.clear()

        males = [p for p in self.people if p.gender == "M"]
        if not males:
            tree.setUpdatesEnabled(True)
            return

        # 按父系构建完整世系树（开国皇帝为根，诸子按代数向下嵌套）
        id_map = {p.id: p for p in males}
        children_map = {p.id: [] for p in males}
        roots = []
        for p in males:
            fid = p.father_id
            if fid in id_map:
                children_map[fid].append(p)
            else:
                roots.append(p)

        for cid in children_map:
            children_map[cid].sort(key=lambda x: (-x.age, x.id))

        def make_node(parent, person):
            is_now = (person.id == self.current_emperor_pid)
            title_str = f" {person.title}" if person.title else ""
            name_str = ("★ " if is_now else "") + person.name + ("（今上）" if is_now else "") + title_str
            status = "存活" if person.is_alive else "已故"
            if person.extinct:
                status += "·绝嗣"
            shimiao = ""
            if person.miaohao:
                shimiao = f"庙号 {person.miaohao}"
            elif person.shihao:
                shimiao = person.shihao
            if person.zunhao and person.is_alive:
                shimiao = (shimiao + "　" if shimiao else "") + f"尊号 {person.zunhao}"
            node = QTreeWidgetItem(parent, [
                name_str,
                self.get_guobie(person),
                status,
                shimiao,
                str(person.generation),
            ])
            node.setExpanded(True)
            for child in children_map.get(person.id, []):
                make_node(node, child)

        # 开国皇帝（无父者）为根；其余旁支归入“旁系”
        roots.sort(key=lambda x: (0 if x.father_id is None else 1, x.generation, -x.age))
        main_root = None
        side_roots = []
        for r in roots:
            if r.father_id is None and main_root is None:
                main_root = r
            else:
                side_roots.append(r)

        if main_root is not None:
            make_node(tree, main_root)
        if side_roots:
            side_item = QTreeWidgetItem(tree, ["旁系 / 来源不详", "", "", "", ""])
            side_item.setExpanded(True)
            for r in side_roots:
                make_node(side_item, r)

        tree.setUpdatesEnabled(True)

    def show_new_emp_dialog(self):
        self.dialog_year_input.setText(self.yearNumber)

        # If successor was found, populate their name and disable editing
        if self.next_emperor_pid is not None:
            succ = self.get_person_by_id(self.next_emperor_pid)
            if succ:
                self.dialog_emp_input.setText(succ.name)
            self.dialog_emp_input.setReadOnly(True)
            self.dialog_emp_btn.setEnabled(False)
        else:
            self.dialog_emp_input.setText(self.emperor)
            self.dialog_emp_input.setReadOnly(False)
            self.dialog_emp_btn.setEnabled(True)

        if self.auto_run:
            if self.dialog_emp_btn.isEnabled():
                self.emperor_change_name_after()
            self.dialog_yearNumber_change_name()
            self.new_emp_confirm()
        else:
            self.new_emp_dialog.exec()

    def show_family_tree_dialog(self, row, column):
        pid_item = self.family_table.item(row, 0)
        if not pid_item:
            return

        pid = int(pid_item.text())
        person = self.get_person_by_id(pid)
        if not person:
            return

        dialog = QDialog(self)
        dialog.setWindowTitle(f"{person.name} 的家谱")
        dialog.resize(400, 500)

        layout = QVBoxLayout()
        tree = QTreeWidget()
        tree.setHeaderLabel("家族树 (仅显示男嗣)")

        # Build tree recursively
        def add_node(parent_widget, p_id):
            p = self.get_person_by_id(p_id)
            if not p: return

            # Label format: Name (Title) - Status
            title_str = f" ({p.title})" if p.title else ""
            status_str = "存活" if p.is_alive else "已故"
            if p.extinct: status_str += " - 绝嗣"

            guobie_str = self.get_guobie(p)
            guobie_str = f" {guobie_str}" if guobie_str and guobie_str != "未封" else ""

            item_text = f"{p.name}{title_str}{guobie_str} [{status_str}]"
            item = QTreeWidgetItem(parent_widget, [item_text])

            for child_id in p.children:
                child = self.get_person_by_id(child_id)
                # Only show males in tree to keep it simple and focused on lineage
                if child and child.gender == "M":
                    add_node(item, child_id)

            item.setExpanded(True)

        add_node(tree, pid)
        layout.addWidget(tree)

        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)

        dialog.setLayout(layout)
        dialog.exec()

    def show_end_game_dialog(self):

        self.dialog_emperor_list_table.setRowCount(0)
        for i, emp in enumerate(self.listjson):
            self.dialog_emperor_list_table.insertRow(i)
            self.dialog_emperor_list_table.setItem(i, 0, QTableWidgetItem(str(emp["id"])))
            self.dialog_emperor_list_table.setItem(i, 1, QTableWidgetItem(emp["miaohao"]))
            self.dialog_emperor_list_table.setItem(i, 2, QTableWidgetItem(emp["shihao"]))
            self.dialog_emperor_list_table.setItem(i, 3, QTableWidgetItem(emp["name"]))
            self.dialog_emperor_list_table.setItem(i, 4, QTableWidgetItem(str(emp["age"])))
            self.dialog_emperor_list_table.setItem(i, 5, QTableWidgetItem(emp["nianhao"]))
            self.dialog_emperor_list_table.setItem(i, 6, QTableWidgetItem(str(emp["jinian"])))
            self.dialog_emperor_list_table.setItem(i, 7, QTableWidgetItem(str(emp["ab"])))
            self.dialog_emperor_list_table.setItem(i, 8, QTableWidgetItem(emp["verdict"]))

        self.dialog_event_table.setRowCount(0)
        for i, ev in enumerate(self.event_happened[1:]):
            self.dialog_event_table.insertRow(i)
            self.dialog_event_table.setItem(i, 0, QTableWidgetItem(ev["time"]))
            self.dialog_event_table.setItem(i, 1, QTableWidgetItem(ev["event"]))

        if self.auto_run:
            self.toggle_auto_run()

        self.end_game_dialog.exec()

    def setup_main_game_screen(self):
        layout = QVBoxLayout()




        self.tabs = QTabWidget()

        # Tab 1: 主界面 (Main Interface)
        self.tab1 = QWidget()
        tab1_layout = QVBoxLayout()
        tab1_layout.setContentsMargins(16, 12, 16, 12)

        # 朝代年号匾额
        self.reign_banner = QLabel("　　")
        self.reign_banner.setObjectName("reign_banner")
        tab1_layout.addWidget(self.reign_banner)

        self.basic_info_form = QFormLayout()
        self.dynasty_label = QLabel()
        self.emperor_label = QLabel()
        self.year_number_label = QLabel()
        self.jinian_label = QLabel()
        self.dynasty_st_label = QLabel()
        self.emperor_hp_label = QLabel()

        self.basic_info_form.addRow("朝代:", self.dynasty_label)
        self.basic_info_form.addRow("皇帝:", self.emperor_label)
        self.basic_info_form.addRow("年号:", self.year_number_label)
        self.basic_info_form.addRow("纪年:", self.jinian_label)
        self.basic_info_form.addRow("国势:", self.dynasty_st_label)
        self.basic_info_form.addRow("天寿:", self.emperor_hp_label)

        tab1_layout.addLayout(self.basic_info_form)

        # Event Table
        event_section = QLabel("— 天 下 纪 事 —")
        event_section.setObjectName("section_label")
        tab1_layout.addWidget(event_section)
        self.event_table = QTableWidget()
        self.event_table.setColumnCount(2)
        self.event_table.setHorizontalHeaderLabels(["时间", "事件"])
        self.event_table.verticalHeader().setVisible(False)
        tab1_layout.addWidget(self.event_table)

        # Sliders
        sliders_layout = QFormLayout()
        self.hardworking_slider = QSlider(Qt.Horizontal)
        self.hardworking_slider.setRange(0, 100)
        self.hardworking_slider.setValue(50)
        sliders_layout.addRow("勤政爱民:", self.hardworking_slider)

        self.amuse_slider = QSlider(Qt.Horizontal)
        self.amuse_slider.setRange(0, 100)
        self.amuse_slider.setValue(50)
        sliders_layout.addRow("声色犬马:", self.amuse_slider)

        tab1_layout.addLayout(sliders_layout)

        btn_layout = QHBoxLayout()
        self.continue_btn = QPushButton("继续")
        self.auto_run_btn = QPushButton("自动运行")
        btn_layout.addWidget(self.continue_btn)
        btn_layout.addWidget(self.auto_run_btn)
        tab1_layout.addLayout(btn_layout)

        # Connect Signals for Tab 1
        self.hardworking_slider.valueChanged.connect(self.bchange)
        self.amuse_slider.valueChanged.connect(self.achange)
        self.continue_btn.clicked.connect(self.gamemin)
        self.auto_run_btn.clicked.connect(self.toggle_auto_run)
        self.tab1.setLayout(tab1_layout)

        # Tab 2: 皇帝信息 (Emperor Info)
        self.tab2 = QWidget()
        tab2_layout = QVBoxLayout()

        self.emp_info_form = QFormLayout()
        self.emp_name_label = QLabel()
        self.emp_age_label = QLabel()
        self.emp_hp_label = QLabel()
        self.emp_ab_label = QLabel()
        self.emp_zunhao_label = QLabel()

        self.emp_info_form.addRow("姓名:", self.emp_name_label)
        self.emp_info_form.addRow("尊号:", self.emp_zunhao_label)
        self.emp_info_form.addRow("年龄:", self.emp_age_label)
        self.emp_info_form.addRow("天寿:", self.emp_hp_label)
        self.emp_info_form.addRow("治国手腕:", self.emp_ab_label)

        tab2_layout.addLayout(self.emp_info_form)
        self.tab2.setLayout(tab2_layout)

        # Tab 3: 王朝信息 (Dynasty Info)
        self.tab3 = QWidget()
        tab3_layout = QVBoxLayout()
        tab3_layout.setContentsMargins(16, 12, 16, 12)

        self.dyn_info_form = QFormLayout()
        self.dyn_name_label = QLabel()
        self.dyn_age_label = QLabel()
        self.dyn_st_label = QLabel()

        self.dyn_info_form.addRow("朝代:", self.dyn_name_label)
        self.dyn_info_form.addRow("王朝国祚:", self.dyn_age_label)
        self.dyn_info_form.addRow("天下大势:", self.dyn_st_label)

        tab3_layout.addLayout(self.dyn_info_form)

        self.emperor_list_table = QTableWidget()
        self.emperor_list_table.setColumnCount(9)
        self.emperor_list_table.setHorizontalHeaderLabels(["序号", "庙号", "谥号", "姓名", "年龄", "年号", "纪年", "治国手腕", "史书评价"])
        self.emperor_list_table.verticalHeader().setVisible(False)
        emp_section = QLabel("— 历 代 帝 王 —")
        emp_section.setObjectName("section_label")
        tab3_layout.addWidget(emp_section)
        tab3_layout.addWidget(self.emperor_list_table)

        self.tab3.setLayout(tab3_layout)

        # Tab 4: 皇室宗亲 (Royal Family Info)
        self.tab4 = QWidget()
        tab4_layout = QVBoxLayout()
        tab4_layout.setContentsMargins(16, 12, 16, 12)

        # 显眼的皇室宗亲树状图（按国别分组）
        tree_section = QLabel("— 皇 室 宗 亲 世 系 —")
        tree_section.setObjectName("section_label")
        tab4_layout.addWidget(tree_section)
        self.family_tree_widget = QTreeWidget()
        self.family_tree_widget.setColumnCount(5)
        self.family_tree_widget.setHeaderLabels(["宗亲", "国别", "状态", "谥号 / 庙号", "代数"])
        self.family_tree_widget.setColumnWidth(0, 200)
        self.family_tree_widget.setColumnWidth(1, 80)
        self.family_tree_widget.setColumnWidth(2, 90)
        self.family_tree_widget.setColumnWidth(3, 180)
        self.family_tree_widget.setColumnWidth(4, 50)
        self.family_tree_widget.setAlternatingRowColors(True)
        tab4_layout.addWidget(self.family_tree_widget, 3)

        table_section = QLabel("— 宗 亲 录 —")
        table_section.setObjectName("section_label")
        tab4_layout.addWidget(table_section)
        self.family_table = QTableWidget()
        self.family_table.setColumnCount(10)
        self.family_table.setHorizontalHeaderLabels(["ID", "姓名", "性别", "年龄", "称号", "国别", "状态", "谥号", "代数", "绝嗣"])
        self.family_table.verticalHeader().setVisible(False)
        tab4_layout.addWidget(self.family_table, 2)
        self.tab4.setLayout(tab4_layout)

        self.family_table.cellDoubleClicked.connect(self.show_family_tree_dialog)

        # Add tabs
        self.tabs.addTab(self.tab1, "主界面")
        self.tabs.addTab(self.tab2, "皇帝信息")
        self.tabs.addTab(self.tab3, "王朝信息")
        self.tabs.addTab(self.tab4, "皇室宗亲")

        layout.addWidget(self.tabs)
        self.main_game_screen.setLayout(layout)

    def toggle_auto_run(self):
        self.auto_run = not self.auto_run
        if self.auto_run:
            self.auto_run_btn.setText("停止运行")
            self.timer.start(500)
        else:
            self.auto_run_btn.setText("自动运行")
            self.timer.stop()

    def auto_run_step(self):
        if self.ongame:
            self.gamemin()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DynastyApp()
    window.show()
    sys.exit(app.exec())
