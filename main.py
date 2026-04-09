import sys
import math
import random
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QStackedWidget, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QLineEdit, QPushButton, QFormLayout, QDialog,
    QDialogButtonBox, QHeaderView, QTabWidget, QTableWidget, QSlider, QTableWidgetItem,
    QTreeWidget, QTreeWidgetItem
)
from PySide6.QtCore import Qt, QTimer



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
        self.title = "" # 亲王, 郡王, 国公, 公主, etc
        self.shihao = ""
        self.ability = 5 + math.floor(random.random() * 5) - math.floor(random.random() * 5)
        if self.ability <= 0:
            self.ability = 1
        self.hp = 20 + math.floor(random.random() * 40) # life expectancy
        self.age = 0
        self.is_married = False
        self.is_alive = True
        self.generation = generation # Generation distance from first emperor
        self.extinct = False # 绝嗣


class DynastyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("王朝 V0.17")
        self.resize(800, 600)

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

        # Auto-run timer
        self.auto_run = False
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.auto_run_step)

    def init_game_state(self):
        self.people = []
        self.next_pid = 1
        self.current_emperor_pid = None
        self.next_emperor_pid = None

        self.charts = ''
        self.opinionData = []
        self.yearlist = []
        self.call_event = False
        self.ongame = True
        self.emperor_die = False
        self.dynasty_die = False
        self.emperor_id = 1
        self.firstgame = True
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
        self.amuse = 50
        self.hardworking = 50
        self.year = 0
        self.randomdata = 0
        self.total_amuse = 1
        self.total_hardworking = 1
        self.listjson = []

        # Name and title lists
        self.dynasty_name = ["夏","商","周","秦","汉","晋","隋","唐","宋","元","明","清"]
        self.emperor_firstname_list = "赵钱孙李周吴郑王冯陈褚卫蒋沈韩杨朱秦尤许何吕施张孔曹严华金魏陶姜戚谢邹喻柏水窦章云苏潘葛奚范彭郎鲁韦昌马苗凤花方俞任袁柳史唐薛雷贺倪汤滕殷罗毕郝安常乐于时傅皮卞齐康伍余元卜顾孟平黄和穆萧尹姚邵汪祁毛禹狄米贝明计伏成戴谈宋茅庞熊纪舒屈项祝董梁杜阮蓝闵席季麻强贾路娄危江童颜郭梅盛林刁钟徐邱骆高夏蔡田樊胡凌霍虞万支柯管卢莫经房裘干解应宗丁宣邓郁单杭洪包诸左石崔吉钮龚程嵇邢裴陆荣翁荀羊惠甄曲家封储靳段富巫乌焦巴弓山谷车侯全班仰秋仲伊宫宁仇栾暴甘厉戎祖武符刘景詹束龙叶幸司韶黎薄印宿白怀蒲邰从索咸赖卓蔺屠蒙池乔阴能苍双闻党翟谭贡劳逄姬申扶堵冉宰郦雍桑桂濮牛寿通边扈燕冀浦尚农温别庄晏柴瞿阎充慕连茹习宦艾鱼容向古易慎戈廖庾终暨居衡步都耿满弘匡国文寇广禄阙东欧殳沃利蔚越隆师巩聂晁勾敖融冷訾辛阚那简饶空曾毋沙乜养鞠须丰巢关相查后荆红游竺权盖益桓公"
        self.emperor_lastname_list = "胤祯禛宏隆炎治弘德景泰宪睿宗康乾启承延建嘉靖万历天顺道文武成懿元章世景宣明昭正敬恭庄肃穆翼襄烈桓威勇毅克庄御安定简贞匡质靖真顺思皓显和元高光英睿博宪坚孝忠惠德仁智慎礼义周敏信达理清直钦益良度基慈齐深温让密厚纯勤谦友祁广淑俭灵荣厉舒逸宜哲察通仪经庇协端休悦绰容确恒熙洽绍"
        self.emperor_firstname = ""
        self.emperor_lastname = ""
        self.yearNumber_list = ["建元", "元光", "元朔", "元狩", "元鼎", "元封", "太初", "天汉", "太始", "征和", "后元", "始元", "元凤", "平瑞", "本始", "地节", "元康", "神爵", "五凤", "甘露", "黄龙", "初元", "永光", "建昭", "竟宁", "建始", "河平", "阳朔", "鸿嘉", "永始", "元延", "绥和", "建平", "太初元将", "元寿", "元始", "居摄", "初始", "建国", "天凤", "地皇", "更始", "建武", "建武中元", "永平", "建初", "元和", "章和", "永元", "元兴", "延平", "永初", "元初", "永宁", "建光", "延光", "永建", "阳嘉", "永和", "汉安", "建康", "永嘉", "本初", "建和", "和平", "元嘉", "永兴", "永寿", "延熹", "永康", "建宁", "熹平", "光和", "中平", "光熹", "昭宁", "微平", "初平", "兴平", "建安", "延康", "黄初", "太和", "青龙", "景初", "正始", "嘉平", "正元", "甘露", "景元", "咸熙", "泰始", "咸宁", "太康", "太熙", "永熙", "永平", "元康", "永康", "永宁", "太安", "永安", "建武", "永安", "建兴", "永嘉", "建兴", "建武", "太兴", "永昌", "太宁", "咸和", "咸康", "建元", "永和", "升平", "隆和", "兴宁", "太和", "咸安", "宁康", "太元", "隆安", "元兴", "义熙", "元熙", "开皇", "仁寿", "大业", "义宁", "武德", "贞观", "永徽", "显庆", "龙朔", "麟德", "乾封", "总章", "咸亨", "上元", "仪凤", "调露", "永隆", "开耀", "永淳", "弘道", "嗣圣", "文明", "光宅", "垂拱", "永昌", "载初", "天授", "如意", "长寿", "延载", "证圣", "天册万岁", "万岁登封", "万岁通天", "神功", "圣历", "久视", "大足", "长安", "神龙", "景龙", "唐隆", "景云", "太极", "延和", "先天", "开元", "天宝", "至德", "乾元", "上元", "宝应", "广德", "永泰", "大历", "建中", "兴元", "贞元", "永贞", "元和", "长庆", "宝历", "大和", "开成", "会昌", "大中", "咸通", "乾符", "广明", "中和", "光启", "文德", "龙纪", "大顺", "景福", "乾宁", "光化", "天复", "天祐", "建隆", "乾德", "开宝", "太平兴国", "雍熙", "端拱", "淳化", "至道", "咸平", "景德", "大中祥符", "天禧", "乾兴", "天圣", "明道", "景祐", "宝元", "康定", "庆历", "皇祐", "至和", "嘉祐", "治平", "熙宁", "元丰", "元祐", "绍圣", "元符", "建中靖国", "崇宁", "大观", "政和", "重和", "宣和", "靖康", "建炎", "绍兴", "隆兴", "乾道", "纯熙", "淳熙", "绍熙", "庆元", "嘉泰", "开禧", "开禧", "嘉定", "宝庆", "绍定", "端平", "嘉熙", "淳祐", "宝祐", "开庆", "景定", "咸淳", "德祐", "景炎", "祥兴", "中统", "至元", "元贞", "大德", "至大", "皇庆", "延祐", "至治", "泰定", "致和", "天历", "至顺", "元统", "至元", "至正", "洪武", "建文", "永乐", "洪熙", "宣德", "正统", "景泰", "天顺", "成化", "弘治", "正德", "嘉靖", "隆庆", "万历", "泰昌", "天启", "崇祯", "顺治", "康熙", "雍正", "乾隆", "嘉庆", "道光", "咸丰", "同治", "光绪", "宣统"]
        self.shihao = ""
        self.miaohao = ""
        self.used_shihao = []
        self.used_miaohao = []
        self.used_emperor_names = []
        self.used_nianhao = []
        self.initial_dynasty_hp = 100

        # Event System
        self.event_id = 0
        self.time_year = ""
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
        self.dialog_emperor_list_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        end_game_emp_layout.addWidget(self.dialog_emperor_list_table)
        self.end_game_emp_tab.setLayout(end_game_emp_layout)

        # Events Tab
        self.end_game_event_tab = QWidget()
        end_game_event_layout = QVBoxLayout()
        self.dialog_event_table = QTableWidget()
        self.dialog_event_table.setColumnCount(2)
        self.dialog_event_table.setHorizontalHeaderLabels(["时间", "事件"])
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

    def setup_start_screen(self):
        layout = QVBoxLayout()
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
        self.emperor_firstname = self.emperor[0]
        self.firstgame = not self.firstgame
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
        self.people.append(emp_person)
        self.current_emperor_pid = emp_person.id
        self.next_pid += 1

        self.dynasty_hp = 100
        self.initial_dynasty_hp = 100
        self.used_emperor_names.append(self.emperor)
        self.used_nianhao.append(self.yearNumber)
        self.dynasty_function_st()
        self.opinionData.append(self.dynasty_hp)
        self.yearlist.append(self.year)
        self.update_ui()
        self.stacked_widget.setCurrentIndex(1)

    def gamemin(self):
        self.year += 1
        self.event_happen()
        self.opinionData.append(self.dynasty_hp)
        self.yearlist.append(self.year)
        self.gamemin_family_aging_death()
        self.gamemin_emperor()
        self.gamemin_dynasty()
        self.gamemin_family_marriage_birth()
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

    def gamemin_family_shihao_titles(self):
        for p in self.people:
            # Alive males update titles if they don't have one and reach adulthood (15)
            if p.is_alive and p.gender == "M" and p.age >= 15 and not p.title and p.id != self.current_emperor_pid:
                if p.generation == 2: # Emperor's son
                    p.title = "亲王"
                elif p.generation == 3: # Grandson
                    p.title = "郡王"
                elif p.generation >= 4: # Further descendants
                    p.title = "国公"

            # Alive females
            elif p.is_alive and p.gender == "F" and p.age >= 15 and not p.title:
                if p.generation == 2:
                    p.title = "公主"
                elif p.generation == 3:
                    p.title = "郡主"
                else:
                    p.title = "县主"

            # Dead members logic
            if not p.is_alive and p.death_year == self.year:
                # Assign shihao for males with titles
                if p.gender == "M" and p.title in ["亲王", "郡王", "国公"] and not p.shihao:
                    # Simple shihao generation for nobles
                    shihao_pool = ["忠", "武", "文", "靖", "康", "简", "烈", "庄", "孝", "恭", "悼", "哀", "隐", "敏", "献", "顺"]
                    p.shihao = random.choice(shihao_pool) + p.title[-1] # e.g. 忠王, 简公

                # Check for 绝嗣
                if p.gender == "M" and p.title:
                    p.extinct = self.check_extinct(p.id)

    def get_random_name(self, gender):
        # self.emperor_firstname holds the surname in this game's code logic.
        if gender == "M":
            return self.emperor_firstname + random.choice(list(self.emperor_lastname_list))
        else:
            return self.emperor_firstname + random.choice(list("秀英玉珍慧琼桂兰秋菊红梅雪娇燕婉如意贞淑慈爱和美明媚"))

    def gamemin_family_marriage_birth(self):
        for p in self.people:
            if not p.is_alive:
                continue

            # Marriage logic: Age > 16, 10% chance per year to marry if not married
            if p.age >= 16 and not p.is_married:
                if random.random() < 0.1:
                    p.is_married = True

            # Birth logic: Males have a chance to have a child. Emperor has harem, so no marriage check needed.
            is_emperor = (p.id == self.current_emperor_pid)
            if (p.is_married or is_emperor) and p.gender == "M" and p.age >= 15 and p.age <= 60:
                # Emperor has a very high chance (70% per year) to have a child, others lower
                chance = 0.7 if is_emperor else 0.4
                if random.random() < chance:
                    child_gender = "M" if random.random() < 0.5 else "F"
                    child_name = self.get_random_name(child_gender)
                    child = Person(self.next_pid, child_name, child_gender, self.year, p.id, None, p.generation + 1)
                    self.people.append(child)
                    p.children.append(self.next_pid)
                    self.next_pid += 1

                    # Emperor has a 30% chance for a second child, others 10%
                    second_chance = 0.3 if is_emperor else 0.1
                    if random.random() < second_chance:
                        child_gender = "M" if random.random() < 0.5 else "F"
                        child_name = self.get_random_name(child_gender)
                        child2 = Person(self.next_pid, child_name, child_gender, self.year, p.id, None, p.generation + 1)
                        self.people.append(child2)
                        p.children.append(self.next_pid)
                        self.next_pid += 1

    def update_crown_prince(self):
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
                # Find eldest living male son
                eldest_son = None
                for child_id in emp.children:
                    child = self.get_person_by_id(child_id)
                    if child and child.is_alive and child.gender == "M":
                        if eldest_son is None or child.age > eldest_son.age:
                            eldest_son = child

                if eldest_son:
                    eldest_son.title = "太子"
                    self.next_emperor_pid = eldest_son.id

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
        if self.dynasty_hp <= 0:
            if self.ongame:
                self.gamemin_shihao()
                self.gamemin_dynasty_change()
                self.dynasty_die = True
                self.dynasty_hp = 0
                self.ongame = False
                self.show_end_game_dialog()
            else:
                self.dynasty_die = True
                self.dynasty_hp = 0
        if self.dynasty_hp <= 15:
            if self.emperor_ab >= 8:
                self.dynasty_hp = 15

    def gamemin_emperor(self):
        if self.dynasty_hp > 0:
            if self.emperor_hp > 0:
                self.emperor_age += 1
                self.jinian += 1
                self.randomdata = random.random()
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
                        emp_person.shihao = self.miaohao # Use miaohao for emperors

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
            self.miaohao = get_unique_miaohao(["太祖", "高祖", "世祖"]) or "烈祖"
        else:
            pools = [
                ["太宗", "高宗", "世宗", "中宗", "圣宗", "成宗", "仁宗", "睿宗", "世祖", "显宗", "熙宗"],
                ["宣宗", "景宗", "宪宗", "孝宗", "武宗", "真宗", "理宗", "明宗", "神宗", "纯宗", "文宗"],
                ["穆宗", "光宗", "宁宗", "英宗", "敬宗", "度宗", "德宗", "顺宗", "和宗", "庄宗", "定宗"],
                ["哲宗", "兴宗", "道宗", "钦宗", "徽宗", "玄宗", "代宗", "端宗", "熙宗", "熹宗", "肃宗"],
                ["哀宗", "愍宗", "末帝", "炀帝", "隐帝", "出帝", "废帝", "后主", "殇帝", "少帝", "献帝"]
            ]

            if performance_score >= 10:
                target_pool = pools[0]
            elif performance_score >= 5:
                target_pool = pools[1]
            elif performance_score >= 0:
                target_pool = pools[2]
            elif performance_score >= -5:
                target_pool = pools[3]
            else:
                target_pool = pools[4]

            self.miaohao = get_unique_miaohao(target_pool)
            # Fallback if specific tier is exhausted
            if not self.miaohao:
                for fallback_pool in pools:
                    self.miaohao = get_unique_miaohao(fallback_pool)
                    if self.miaohao:
                        break
            if not self.miaohao:
                self.miaohao = "元宗" # Last resort fallback

        self.used_miaohao.append(self.miaohao)

        # Generate Shihao (Tang style: 4 to 8 characters, ending with "皇帝")
        good_traits = ["神圣", "贤文", "武成", "康献", "懿元", "章世", "景宣", "明昭", "正敬", "恭庄", "肃穆", "翼襄", "烈桓", "威勇", "毅克", "庄御", "安定", "简贞", "匡质", "靖真", "顺思", "皓显", "和元", "高光", "英睿", "博宪", "坚孝", "忠惠", "德仁", "智慎", "礼义", "周敏", "信达", "理清", "直钦", "益良", "度基", "慈齐", "深温", "让密", "厚纯", "勤谦", "友祁", "广淑", "俭灵", "荣厉", "絜舒", "贲逸", "偲逑", "懋宜", "哲察", "通仪", "经庇", "协端", "休悦", "绰容", "确恒", "熙洽", "绍"]
        bad_traits = ["荒", "戾", "炀", "幽", "隐", "哀", "愍", "悼", "厉", "灵", "惑", "废"]

        available_shihao = []
        for _ in range(20): # Generate a pool of candidates
            length = random.choice([4, 5, 6, 7, 8])
            prefix_length = length - 2 # account for "皇帝"
            if performance_score < -2:
                # Poor performance: use fewer good traits, maybe some bad ones, shorter names
                prefix_length = min(prefix_length, random.choice([2, 4]))
                chosen_traits = random.choices(good_traits + bad_traits, k=math.ceil(prefix_length/2))
            elif performance_score >= 8:
                # Great performance: long titles
                prefix_length = max(prefix_length, random.choice([4, 6]))
                chosen_traits = random.choices(good_traits, k=math.ceil(prefix_length/2))
            else:
                chosen_traits = random.choices(good_traits, k=math.ceil(prefix_length/2))

            prefix = "".join(chosen_traits)[:prefix_length]
            candidate = prefix + "皇帝"
            available_shihao.append(candidate)

        # Ensure uniqueness
        unique_candidate = None
        for candidate in available_shihao:
            if candidate not in self.used_shihao:
                unique_candidate = candidate
                break

        if not unique_candidate:
            # Fallback
            unique_candidate = "元孝皇帝"
            while unique_candidate in self.used_shihao:
                unique_candidate = random.choice(good_traits) + "皇帝"

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

    def gamemin_emperor_change(self):
        self.listjson.append({
            "id": self.emperor_id,
            "name": self.emperor,
            "nianhao": self.yearNumber,
            "age": self.emperor_age,
            "jinian": self.jinian,
            "miaohao": self.miaohao,
            "shihao": self.shihao,
            "ab": self.emperor_ab,
            "verdict": self.verdict
        })

    def gamemin_emperor_new(self):
        self.dynasty_hp -= 2
        if self.dynasty_hp <= 0:
            self.dynasty_hp = 1
        self.jinian = 1

        # Inherit from chosen successor if one exists
        if self.next_emperor_pid:
            succ = self.get_person_by_id(self.next_emperor_pid)
            if succ:
                self.emperor = succ.name
                self.emperor_age = succ.age
                self.emperor_ab = succ.ability
                self.emperor_hp = succ.hp
                succ.title = "皇帝"
                self.current_emperor_pid = succ.id
                self.next_emperor_pid = None
            else:
                # Fallback if successor doesn't exist
                self.emperor_new_age()
                self.emperor_ab = 5 + math.floor(random.random() * 5) - math.floor(random.random() * 5)
                if self.emperor_ab <= 0:
                    self.emperor_ab = 1
                self.emperor_new_hp()
        else:
            self.emperor_new_age()
            self.emperor_ab = 5 + math.floor(random.random() * 5) - math.floor(random.random() * 5)
            if self.emperor_ab <= 0:
                self.emperor_ab = 1
            self.emperor_new_hp()

        self.total_amuse = 1
        self.total_hardworking = 1
        self.initial_dynasty_hp = self.dynasty_hp

    def gamemin_dynasty_change(self):
        self.listjson.append({
            "id": self.emperor_id,
            "name": self.emperor,
            "nianhao": self.yearNumber,
            "age": self.emperor_age,
            "jinian": self.jinian,
            "miaohao": self.miaohao,
            "shihao": self.shihao,
            "ab": self.emperor_ab,
            "verdict": self.verdict
        })

    def gamemin_dynasty_new(self):
        self.people = []
        self.next_pid = 1
        self.current_emperor_pid = None
        self.next_emperor_pid = None
        self.dynasty_age = 0
        self.jinian = 1
        self.listjson = []
        self.year = 0
        self.emperor_id = 1
        self.yearlist = []
        self.opinionData = []
        self.event_happened = [{"time": "", "event": ""}]
        self.used_shihao = []
        self.used_miaohao = []
        self.used_emperor_names = []
        self.used_nianhao = []
        self.initial_dynasty_hp = 100

    def dio(self):
        self.emperor_die = False
        self.new_emp_dialog.accept()
        self.gamemin_emperor_new()
        self.emperor_id += 1
        self.ongame = True
        self.update_ui()

    def dio2(self):
        self.dynasty_die = False
        self.end_game_dialog.accept()
        self.firstgame = True
        self.gamemin_dynasty_new()
        self.ongame = True
        self.stacked_widget.setCurrentIndex(0)

    def dynasty_change_name(self):
        idx = math.floor(random.random() * len(self.dynasty_name))
        self.dynasty = self.dynasty_name[idx]
        self.dynasty_input.setText(self.dynasty)

    def emperor_change_name(self):
        self.emperor_firstname = random.choice(list(self.emperor_firstname_list))
        while True:
            # 50% chance for a 1-character given name, 50% for 2-character
            if random.random() < 0.5:
                self.emperor_lastname = random.choice(list(self.emperor_lastname_list))
            else:
                self.emperor_lastname = random.choice(list(self.emperor_lastname_list)) + random.choice(list(self.emperor_lastname_list))
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
            if random.random() < 0.5:
                self.emperor_lastname = random.choice(list(self.emperor_lastname_list))
            else:
                self.emperor_lastname = random.choice(list(self.emperor_lastname_list)) + random.choice(list(self.emperor_lastname_list))
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

        self.event_change()
        self.emperor_hp += self.data_emperor_hp_change
        self.dynasty_hp += self.data_dynasty_hp_change

        # Dynamic Nianhao change: occurs if an extreme event happens (-5 or more impact)
        # and has a 20% chance. We reset jinian to 1 when year number changes.
        if abs(self.data_dynasty_hp_change) >= 5 and random.random() < 0.2:
            self.yearNumber = self.get_unique_nianhao()
            self.used_nianhao.append(self.yearNumber)
            self.jinian = 0  # will be incremented to 1 next tick
            change_event = {"time": self.d_time, "event": f"皇帝为祈福/应天象，改元 {self.yearNumber}。"}
            self.event_happened.append(change_event)

    def event_id_chose(self):
        if not self.call_event:
            self.event_id = math.floor(random.random() * len(self.event_list))

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
            row_idx = 0
            for p in self.people:
                if p.gender == "F":
                    continue
                self.family_table.insertRow(row_idx)
                self.family_table.setItem(row_idx, 0, QTableWidgetItem(str(p.id)))
                self.family_table.setItem(row_idx, 1, QTableWidgetItem(p.name))
                self.family_table.setItem(row_idx, 2, QTableWidgetItem("男" if p.gender == "M" else "女"))
                self.family_table.setItem(row_idx, 3, QTableWidgetItem(str(p.age)))
                self.family_table.setItem(row_idx, 4, QTableWidgetItem(p.title))
                self.family_table.setItem(row_idx, 5, QTableWidgetItem("存活" if p.is_alive else "已故"))
                self.family_table.setItem(row_idx, 6, QTableWidgetItem(p.shihao))
                self.family_table.setItem(row_idx, 7, QTableWidgetItem(str(p.generation)))
                self.family_table.setItem(row_idx, 8, QTableWidgetItem("绝嗣" if p.extinct else ""))
                row_idx += 1

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

            item_text = f"{p.name}{title_str} [{status_str}]"
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
        self.event_table = QTableWidget()
        self.event_table.setColumnCount(2)
        self.event_table.setHorizontalHeaderLabels(["时间", "事件"])
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

        self.emp_info_form.addRow("姓名:", self.emp_name_label)
        self.emp_info_form.addRow("年龄:", self.emp_age_label)
        self.emp_info_form.addRow("天寿:", self.emp_hp_label)
        self.emp_info_form.addRow("治国手腕:", self.emp_ab_label)

        tab2_layout.addLayout(self.emp_info_form)
        self.tab2.setLayout(tab2_layout)

        # Tab 3: 王朝信息 (Dynasty Info)
        self.tab3 = QWidget()
        tab3_layout = QVBoxLayout()

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
        tab3_layout.addWidget(self.emperor_list_table)

        self.tab3.setLayout(tab3_layout)

        # Tab 4: 皇室宗亲 (Royal Family Info)
        self.tab4 = QWidget()
        tab4_layout = QVBoxLayout()
        self.family_table = QTableWidget()
        self.family_table.setColumnCount(9)
        self.family_table.setHorizontalHeaderLabels(["ID", "姓名", "性别", "年龄", "称号", "状态", "谥号", "代数", "绝嗣"])
        tab4_layout.addWidget(self.family_table)
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
