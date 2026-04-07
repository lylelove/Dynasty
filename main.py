import sys
import math
import random
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QStackedWidget, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QLineEdit, QPushButton, QFormLayout, QDialog,
    QDialogButtonBox, QHeaderView, QTabWidget, QTableWidget, QSlider, QTableWidgetItem
)
from PySide6.QtCore import Qt

import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QStackedWidget, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QLineEdit, QPushButton, QFormLayout, QDialog,
    QDialogButtonBox, QHeaderView, QTabWidget, QTableWidget, QSlider, QTableWidgetItem
)



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

    def init_game_state(self):
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
        self.dynasty_name = ["宋","周","齐","梁","魏","夏","陈","唐","晋","秦","汉","楚"]
        self.emperor_firstname_list = "王李张刘陈杨黄吴赵周徐孙马朱胡林郭何高罗郑梁谢宋唐许邓冯韩曹曾彭肖蔡潘田董袁于余蒋叶杜苏魏程吕丁沈任姚卢钟姜崔谭廖范汪陆金石戴贾韦夏邱方侯邹熊孟秦白毛江闫薛尹付段雷黎史龙钱贺陶顾龚郝邵万严洪赖武傅莫孔"
        self.emperor_lastname_list = "乙一力了人入又卜刀刁丁二土丸兀夕下水小丫幺也已弋于丈才叉川寸大凡干工弓及己巾久口廿女千三山上勺士巳子木内牛匹片亓欠切犬仁壬仍日冗卅少升什氏手巴比卞不尺仇丹仃斗反方分夫父戈公勾互户化幻火介今斤井亢孔毛殳水四太天屯王文毋午心牙爻尹引尤友予元曰月匀允仄仉之支止中皮平仟巧且丘囚去冉仨申生史矢世仕市示石失司他它田仝瓦外未五戊仙兄玄央以永用由右白半包北本必丙布册出代旦氐冬弗付甘功古瓜禾弘乎卉加甲巨句卡刊可立尥令另矛卯民末母目尼奴丕幼玉札占仗召正只主仔左艮亘共光圭亥好合回吉岌匠交决伉考匡老耒吏安百冰并臣丞吃弛充此次存打地多朵而耳帆仿妃份伏旮各列六米名牟囡年妗究君均局克况冷李利良吕芈妙男妞判七岐杞羌求劬汝杉劭佘汜宋町廷彤佗妥完位吾汐希岘孝辛形杏秀序巡汛延言冶甬攸酉佑余妤皂贝兵伯孛步材岑车辰成呈池赤伺村但低弟佃豆杜兑囤坊孚甫告更攻囯含罕何亨宏弧汲即忌见江角戒志助壮灼孜佐作坐屺曲全任戎如式收守寺似汀同伍西先向行休旭旬伢羊伊衣夷亦屹因印有宇羽聿再在兆至仲州舟朱竹自金卺京净纠赳玖咎卷居具抗岢刻肯空快狂坤昆来两林仑侣盲枚妹没门孟氓汨宓岷旻明命沫沐牧奈妮念帕杷抛沛佩帔朋批坡沏妻其歧奇戕沁青穹屈取券乳枘叁沙姗尚舍社沈使始事艾哎岸昂枊坳垇八爸佰攽板版杯表秉幷帛昌长抄弨沉承冲初炊垂耷岱宕狄底玓典店耵定东咚侗抖妒沌儿泛房昉放非氛汾奉扶府阜冈杲庚供姑孤汩固刮卦官炅果杭沆昊和虎佶技季佳肩佼姐届侍受抒叔刷祀松所弢宛汪旺委味汶武昔析弦冼协忻昕欣姓幸岫亚炎兖奄佯肴杳夜依沂宜抑佾易咏於盂雨沅昀争枝知直忠周宙侏竺杼状隹卓宗冒玫眉美沔勉泯某姥娜耐南泮盼盆毗品屏祈芑芊前俏秋俅酋泉染柔是首姝帅思泗亭凃沱娃纨芄威韦畏侠咸相香巷信星庥胥叙宣泫炫泶沿匽彦泱垚姚要页怡舣奕弈羿音垠胤盈映泳保抱祊砭扁便柄炳波泊勃查昶怊重抽穿舡春匆待帝峒垌度段盾法飞风封负赴泔革宫故冠癸河红泓虹侯后厚狐砉皇纪既枷架柬建牮姜姣皆界劲矜俓炯九玦军俊炬看柯科奎厘俚亮泠柃柳律抹芒昴勇幽羑禹芋昱俞垣爰约玥哉昝则昭沼者柘贞政治峙致胄注柱炷咨姿盎敖笆柏班般豹趵倍眧城乘翀刍俶纯祠耽岛玷洞娥恩洱珐芳纺舫芬峰芙服刚罡高哥格根耕耿肱恭贡倌桂衮函航恒洪候祜花洹桓恢洄活姬笈疾记家兼津晋径娟隽珏峻桔珂恪括朗凉烈玲瓴凌留伦洛马勐珉纳能倪娘畔配娉珀圃芪起祗洽虔倩芩芹秦邛容洳桑珊射珅神师十时拾书纾殊恕栓朔凇素孙笋娑索泰唐洮桃特甜庭桐娓纹翁乌务奚息席洗峡夏宵效校笑芯修脩徐栩轩烜眩洵训讯迅衍晏芫洋益殷邕佑育彧峪原袁员纭芸耘奘旃展站钊针珍真洲祝酌笫祖祚邦浜苞毕彪邠彬斌彩曹涔参产常晨趁偁琤晟敕崇处船钏从崔带埭聃得笛钓动梵访烽苻浮匐符副岗舸苟规硅崞国海酣焊毫浩珩胡扈凰悔彗基偈寄坚健将皎教婕堇婧竟涓浚康悝馗浪勒梨笠梁聊苓羚翎流娄鹿略珞麻麦曼茅茂梅密苗敏茉旎涅您培旆佩浦戚崎启弃乾卿朐渠区若啬商绍苕涉笙孰术庶爽堂悌屠望唯伟尉问悟晞浠悉习祥邢袖虚许勖旋雪珣焉闫研野移异翊翌寅英迎庸涌庾苑悦张章浙振峥执珠专茁着梓紫族报堡备弼皕赑博采策曾单场焯超朝程盛淳词兹淙淡登迪第棣奠栋敦发番邡斐费冯涪袱复傅富淦皋贯贵涵寒皓贺闳画淮荒黄惠嵇极集几间绛焦蛟杰荆晶景钧珺竣开凯轲焜岚琅劳犁理荔量淩荦络买嵋媚猛淼闵甯排彭评普期欺祁淇棋茜强乔钦琴清晴邱荃筌然韧茹阮闰森善邵深淑疏舒述顺舜丝斯耜淞邰棠淘添婷茼童统为惟雯淅晰稀喜厦闲现羡翔项象雄须婿絮绚寻荀循雅娅砚雁焱尧壹诒迤贻胰轶茵淯寓渊媛粤越云哲蛰蛰轸植轵智众尊爱奥辟禀渤粲琛絺驰楚传琮当荻钿殿鼎督渡顿沨枫港琯荷湖郇涣焕煌晖汇会浑楫贾笕郊捷解禁靳经敬靖筠琚楷蒯琨廓雷莉里廉炼粱琳零旒辂琭禄路湄渼盟湣莫睦乃楠农暖湃逄聘莆颀琦琪祺佥铅勤诠辁群裟莎诜莘圣嵊诗轼蜀竖嗣肆嵩颂肃睢绥汤塘陀琬微湋炜渭温渥熙苋湘详想新歆惺绣诩煦暄煊铉渲勋询琰扬旸杨业义诣意雍犹游渝愉愚榆虞郁钰预御裕愈煜园圆恽载詹湛照罩蜇浈桢渚庄琢赀资榜碧宾逋菜沧臧察菖嫦畅裳尘诚铖称绰慈翠滇端尔菲逢凤福辅盖纲郜阁构嘏管菡豪郝赫瑚华诲珲嘉菁菊聚逵魁郎连寥廖绫菱领雒瑁萌蜜绵铭溟宁滂裴萍溥齐萁旗綦绮侨溱轻蜻箐铨荣溶榕熔瑞睿箬飒搡瑟僧韶慎寿绶菽塾署墅硕菘诵速愫溯台叹溏滔滕逖通铜图途团绾网维玮萎闻舞误郗溪僖铣郤瑕衔线限像逍箫榭荥需熏鞅祎铱旖银夤瑛荧萤郢墉踊瑜与语鸢源瑗愿造帻翟崭彰嶂幛赵肇祯甄榛筝种僮准菑缁滋综"
        self.emperor_firstname = ""
        self.emperor_lastname = ""
        self.yearNumber_list = "建元承大宝太上始真王武定开乾统文明应国光弘仁洪至治崇德本淳阳天地初熙泰神人正普康晏安同庆久延寿保隆长宁靖成更化中和启顺章清平河汉景孝义雀龙祥嘉会兴贞永丰豋广显昌凤麟重赤白玉露绍青黄通道咸宣意端居拱圣皇"
        self.shihao_list_first = "神圣贤文武成康献懿元章世"
        self.shihao_list_common = "景宣明昭正敬恭庄肃穆翼襄烈桓威勇毅克庄御安定简贞匡质靖真顺思皓显和元高光英睿博宪坚孝忠惠德仁智慎礼义周敏信达理清直钦益良度基慈齐深温让密厚纯勤谦友祁广淑俭灵荣厉絜舒贲逸偲逑懋宜哲察通仪经庇协端休悦绰容确恒熙洽绍"
        self.shihao = ""

        # Event System
        self.event_id = 0
        self.time_year = ""
        self.event_happened = [{"time": "", "event": ""}]
        self.event_list = [
            {
                "time": "",
                "event": "今年无事发生。",
                "emperor_hp_change": 0,
                "dynasty_hp_change": 0,
            },
            {
                "time": "",
                "event": "天降祥瑞，国泰民安。",
                "emperor_hp_change": 1,
                "dynasty_hp_change": 5,
            },
            {
                "time": "",
                "event": "地方叛乱，劳民伤财。",
                "emperor_hp_change": -2,
                "dynasty_hp_change": -10,
            }
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

        end_game_layout.addWidget(QLabel("皇帝列表"))

        self.dialog_emperor_list_table = QTableWidget()
        self.dialog_emperor_list_table.setColumnCount(7)
        self.dialog_emperor_list_table.setHorizontalHeaderLabels(["序号", "谥号", "姓名", "年龄", "年号", "纪年", "能力"])
        self.dialog_emperor_list_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        end_game_layout.addWidget(self.dialog_emperor_list_table)

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
        self.emperor_hp = 20 + math.floor(random.random() * 20) - math.floor(random.random() * 20)
        self.emperor_ab = 10
        self.dynasty_hp = 100
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
        self.gamemin_emperor()
        self.gamemin_dynasty()
        self.dynasty_function_st()
        self.update_ui()

    def gamemin_dynasty(self):
        if self.emperor_hp > 0:
            if self.dynasty_hp > 0:
                self.dynasty_hp = self.dynasty_hp - (self.amuse / 40 * 5 / self.emperor_ab) + (self.hardworking / 40 * self.emperor_ab / 10)
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
            if self.emperor_hp <= 0:
                if self.ongame:
                    self.gamemin_shihao()
                    self.emperor_die = True
                    self.gamemin_emperor_change()
                    self.emperor_hp = 0
                    self.ongame = False
                    self.show_new_emp_dialog()
                else:
                    self.emperor_hp = 0
                    self.emperor_die = True

    def gamemin_shihao(self):
        if self.emperor_id == 1:
            idx = math.floor(random.random() * len(self.shihao_list_first))
            self.shihao = self.dynasty + self.shihao_list_first[idx] + "祖"
        else:
            idx = math.floor(random.random() * len(self.shihao_list_common))
            self.shihao = self.dynasty + self.shihao_list_common[idx] + "宗"

    def gamemin_emperor_change(self):
        self.listjson.append({
            "id": self.emperor_id,
            "name": self.emperor,
            "nianhao": self.yearNumber,
            "age": self.emperor_age,
            "jinian": self.jinian,
            "shihao": self.shihao,
            "ab": self.emperor_ab
        })

    def gamemin_emperor_new(self):
        self.dynasty_hp -= 10
        if self.dynasty_hp <= 0:
            self.dynasty_hp = 1
        self.jinian = 1
        self.emperor_new_age()
        self.emperor_ab = 5 + math.floor(random.random() * 5) - math.floor(random.random() * 5)
        self.emperor_new_hp()
        self.total_amuse = 1
        self.total_hardworking = 1

    def gamemin_dynasty_change(self):
        self.listjson.append({
            "id": self.emperor_id,
            "name": self.emperor,
            "nianhao": self.yearNumber,
            "age": self.emperor_age,
            "jinian": self.jinian,
            "shihao": self.shihao,
            "ab": self.emperor_ab
        })

    def gamemin_dynasty_new(self):
        self.dynasty_age = 0
        self.jinian = 0
        self.listjson = []
        self.year = 0
        self.emperor_id = 0
        self.yearlist = []
        self.opinionData = []

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
        idx1 = math.floor(random.random() * len(self.emperor_firstname_list))
        self.emperor_firstname = self.emperor_firstname_list[idx1]
        idx2 = math.floor(random.random() * len(self.emperor_lastname_list))
        idx3 = math.floor(random.random() * len(self.emperor_lastname_list))
        self.emperor_lastname = self.emperor_lastname_list[idx2] + self.emperor_lastname_list[idx3]
        self.emperor = self.emperor_firstname + self.emperor_lastname
        self.emperor_input.setText(self.emperor)

    def emperor_new_hp(self):
        self.randomdata = math.floor(random.random() * 3)
        if self.emperor_age <= 35:
            if self.randomdata == 0:
                self.emperor_hp = 20 + math.floor(random.random() * 20)
            else:
                self.emperor_hp = 20 - math.floor(random.random() * 20)
        if self.emperor_age > 35:
            self.emperor_hp = 20 - math.floor(random.random() * 20) + math.floor(random.random() * 10)

    def emperor_new_age(self):
        self.randomdata = self.emperor_age
        self.emperor_age = self.randomdata - 16 - math.floor(random.random() * 25)
        while self.emperor_age <= 0:
            self.emperor_age = math.floor(random.random() * 50)

    def yearNumber_change_name(self):
        idx1 = math.floor(random.random() * len(self.yearNumber_list))
        idx2 = math.floor(random.random() * len(self.yearNumber_list))
        self.yearNumber = self.yearNumber_list[idx1] + self.yearNumber_list[idx2]
        self.year_number_input.setText(self.yearNumber)

    def dialog_yearNumber_change_name(self):
        idx1 = math.floor(random.random() * len(self.yearNumber_list))
        idx2 = math.floor(random.random() * len(self.yearNumber_list))
        self.yearNumber = self.yearNumber_list[idx1] + self.yearNumber_list[idx2]
        self.dialog_year_input.setText(self.yearNumber)

    def emperor_change_name_after(self):
        idx2 = math.floor(random.random() * len(self.emperor_lastname_list))
        idx3 = math.floor(random.random() * len(self.emperor_lastname_list))
        self.emperor_lastname = self.emperor_lastname_list[idx2] + self.emperor_lastname_list[idx3]
        self.emperor = self.emperor_firstname + self.emperor_lastname
        self.dialog_emp_input.setText(self.emperor)

    def dynasty_function_st(self):
        if self.dynasty_hp >= 90:
            self.dynasty_st = "国泰民安"
        elif self.dynasty_hp >= 80:
            self.dynasty_st = "风调雨顺"
        elif self.dynasty_hp >= 70:
            self.dynasty_st = "差强人意"
        elif self.dynasty_hp >= 60:
            self.dynasty_st = "山雨欲来"
        elif self.dynasty_hp >= 50:
            self.dynasty_st = "旦夕之间"
        elif self.dynasty_hp >= 30:
            self.dynasty_st = "风雨飘摇"
        elif self.dynasty_hp >= 20:
            self.dynasty_st = "国势倾颓"
        elif self.dynasty_hp >= 10:
            self.dynasty_st = "不绝如缕"
        else:
            self.dynasty_st = "亡国之兆"

    def event_happen(self):
        self.event_id_chose()
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
            self.emperor_list_table.setItem(i, 1, QTableWidgetItem(emp["shihao"]))
            self.emperor_list_table.setItem(i, 2, QTableWidgetItem(emp["name"]))
            self.emperor_list_table.setItem(i, 3, QTableWidgetItem(str(emp["age"])))
            self.emperor_list_table.setItem(i, 4, QTableWidgetItem(emp["nianhao"]))
            self.emperor_list_table.setItem(i, 5, QTableWidgetItem(str(emp["jinian"])))
            self.emperor_list_table.setItem(i, 6, QTableWidgetItem(str(emp["ab"])))

    def show_new_emp_dialog(self):
        self.dialog_emp_input.setText(self.emperor)
        self.dialog_year_input.setText(self.yearNumber)
        self.new_emp_dialog.exec()

    def show_end_game_dialog(self):

        self.dialog_emperor_list_table.setRowCount(0)
        for i, emp in enumerate(self.listjson):
            self.dialog_emperor_list_table.insertRow(i)
            self.dialog_emperor_list_table.setItem(i, 0, QTableWidgetItem(str(emp["id"])))
            self.dialog_emperor_list_table.setItem(i, 1, QTableWidgetItem(emp["shihao"]))
            self.dialog_emperor_list_table.setItem(i, 2, QTableWidgetItem(emp["name"]))
            self.dialog_emperor_list_table.setItem(i, 3, QTableWidgetItem(str(emp["age"])))
            self.dialog_emperor_list_table.setItem(i, 4, QTableWidgetItem(emp["nianhao"]))
            self.dialog_emperor_list_table.setItem(i, 5, QTableWidgetItem(str(emp["jinian"])))
            self.dialog_emperor_list_table.setItem(i, 6, QTableWidgetItem(str(emp["ab"])))
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
        self.basic_info_form.addRow("寿限:", self.emperor_hp_label)

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

        self.continue_btn = QPushButton("继续")
        tab1_layout.addWidget(self.continue_btn)

        # Connect Signals for Tab 1
        self.hardworking_slider.valueChanged.connect(self.bchange)
        self.amuse_slider.valueChanged.connect(self.achange)
        self.continue_btn.clicked.connect(self.gamemin)
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
        self.emp_info_form.addRow("寿限:", self.emp_hp_label)
        self.emp_info_form.addRow("能力:", self.emp_ab_label)

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
        self.dyn_info_form.addRow("国祚:", self.dyn_age_label)
        self.dyn_info_form.addRow("状态:", self.dyn_st_label)

        tab3_layout.addLayout(self.dyn_info_form)

        self.emperor_list_table = QTableWidget()
        self.emperor_list_table.setColumnCount(7)
        self.emperor_list_table.setHorizontalHeaderLabels(["序号", "谥号", "姓名", "年龄", "年号", "纪年", "能力"])
        tab3_layout.addWidget(self.emperor_list_table)

        self.tab3.setLayout(tab3_layout)

        # Add tabs
        self.tabs.addTab(self.tab1, "主界面")
        self.tabs.addTab(self.tab2, "皇帝信息")
        self.tabs.addTab(self.tab3, "王朝信息")

        layout.addWidget(self.tabs)
        self.main_game_screen.setLayout(layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DynastyApp()
    window.show()
    sys.exit(app.exec())
