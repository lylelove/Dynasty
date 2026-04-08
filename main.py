import sys
import math
import random
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QStackedWidget, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QLineEdit, QPushButton, QFormLayout, QDialog,
    QDialogButtonBox, QHeaderView, QTabWidget, QTableWidget, QSlider, QTableWidgetItem
)
from PySide6.QtCore import Qt, QTimer

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

        # Auto-run timer
        self.auto_run = False
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.auto_run_step)

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
        self.dynasty_name = ["夏","商","周","秦","汉","晋","隋","唐","宋","元","明","清"]
        self.emperor_firstname_list = "赵钱孙李周吴郑王冯陈褚卫蒋沈韩杨朱秦尤许何吕施张孔曹严华金魏陶姜戚谢邹喻柏水窦章云苏潘葛奚范彭郎鲁韦昌马苗凤花方俞任袁柳酆鲍史唐费廉岑薛雷贺倪汤滕殷罗毕郝邬安常乐于时傅皮卞齐康伍余元卜顾孟平黄和穆萧尹姚邵湛汪祁毛禹狄米贝明臧计伏成戴谈宋茅庞熊纪舒屈项祝董梁杜阮蓝闵席季麻强贾路娄危江童颜郭梅盛林刁钟徐邱骆高夏蔡田樊胡凌霍虞万支柯昝管卢莫经房裘缪干解应宗丁宣贲邓郁单杭洪包诸左石崔吉钮龚程嵇邢滑裴陆荣翁荀羊於惠甄曲家封芮羿储靳汲邴糜松井段富巫乌焦巴弓牧隗山谷车侯宓蓬全郗班仰秋仲伊宫宁仇栾暴甘钭厉戎祖武符刘景詹束龙叶幸司韶郜黎蓟薄印宿白怀蒲邰从鄂索咸籍赖卓蔺屠蒙池乔阴鬱胥能苍双闻莘党翟谭贡劳逄姬申扶堵冉宰郦雍卻璩桑桂濮牛寿通边扈燕冀郏浦尚农温别庄晏柴瞿阎充慕连茹习宦艾鱼容向古易慎戈廖庾终暨居衡步都耿满弘匡国文寇广禄阙东欧殳沃利蔚越夔隆师巩厍聂晁勾敖融冷訾辛阚那简饶空曾毋沙乜养鞠须丰巢关蒯相查后荆红游竺权逯盖益桓公"
        self.emperor_lastname_list = "安百冰并臣丞吃弛充此次存打地多朵而耳帆仿妃份伏旮各列六米名牟囡年妗究君均局克况冷李利良吕芈妙男妞判七岐杞羌求劬汝杉劭佘汜宋町廷彤佗妥完位吾汐希岘孝辛形杏秀序巡汛延言冶甬攸酉佑余妤皂贝兵伯孛步材岑车辰成呈池赤伺村但低弟佃豆杜兑囤坊孚甫告更攻囯含罕何亨宏弧汲即忌见江角戒志助壮灼孜佐作坐屺曲全任戎如式收守寺似汀同伍西先向行休旭旬伢羊伊衣夷亦屹因印有宇羽聿再在兆至仲州舟朱竹自金卺京净纠赳玖咎卷居具抗岢刻肯空快狂坤昆来两林仑侣盲枚妹没门孟氓汨宓岷旻明命沫沐牧奈妮念帕杷抛沛佩帔朋批坡沏妻其歧奇戕沁青穹屈取券乳枘叁沙姗尚舍社沈使始事艾哎岸昂枊坳垇八爸佰攽板版杯表秉幷帛昌长抄弨沉承冲初炊垂耷岱宕狄底玓典店耵定东咚侗抖妒沌儿泛房昉放非氛汾奉扶府阜冈杲庚供姑孤汩固刮卦官炅果杭沆昊和虎佶技季佳肩佼姐届侍受抒叔刷祀松所弢宛汪旺委味汶武昔析弦冼协忻昕欣姓幸岫亚炎兖奄佯肴杳夜依沂宜抑佾易咏於盂雨沅昀争枝知直忠周宙侏竺杼状隹卓宗冒玫眉美沔勉泯某姥娜耐南泮盼盆毗品屏祈芑芊前俏秋俅酋泉染柔是首姝帅思泗亭凃沱娃纨芄威韦畏侠咸相香巷信星庥胥叙宣泫炫泶沿匽彦泱垚姚要页怡舣奕弈羿音垠胤盈映泳保抱祊砭扁便柄炳波泊勃查昶怊重抽穿舡春匆待帝峒垌度段盾法飞风封负赴泔革宫故冠癸河红泓虹侯后厚狐砉皇纪既枷架柬建牮姜姣皆界劲矜俓炯九玦军俊炬看柯科奎厘俚亮泠柃柳律抹芒昴勇幽羑禹芋昱俞垣爰约玥哉昝则昭沼者柘贞政治峙致胄注柱炷咨姿盎敖笆柏班般豹趵倍眧城乘翀刍俶纯祠耽岛玷洞娥恩洱珐芳纺舫芬峰芙服刚罡高哥格根耕耿肱恭贡倌桂衮函航恒洪候祜花洹桓恢洄活姬笈疾记家兼津晋径娟隽珏峻桔珂恪括朗凉烈玲瓴凌留伦洛马勐珉纳能倪娘畔配娉珀圃芪起祗洽虔倩芩芹秦邛容洳桑珊射珅神师十时拾书纾殊恕栓朔凇素孙笋娑索泰唐洮桃特甜庭桐娓纹翁乌务奚息席洗峡夏宵效校笑芯修脩徐栩轩烜眩洵训讯迅衍晏芫洋益殷邕佑育彧峪原袁员纭芸耘奘旃展站钊针珍真洲祝酌笫祖祚邦浜苞毕彪邠彬斌彩曹涔参产常晨趁偁琤晟敕崇处船钏从崔带埭聃得笛钓动梵访烽苻浮匐符副岗舸苟规硅崞国海酣焊毫浩珩胡扈凰悔彗基偈寄坚健将皎教婕堇婧竟涓浚康悝馗浪勒梨笠梁聊苓羚翎流娄鹿略珞麻麦曼茅茂梅密苗敏茉旎涅您培旆佩浦戚崎启弃乾卿朐渠区若啬商绍苕涉笙孰术庶爽堂悌屠望唯伟尉问悟晞浠悉习祥邢袖虚许勖旋雪珣焉闫研野移异翊翌寅英迎庸涌庾苑悦张章浙振峥执珠专茁着梓紫族报堡备弼皕赑博采策曾单场焯超朝程盛淳词兹淙淡登迪第棣奠栋敦发番邡斐费冯涪袱复傅富淦皋贯贵涵寒皓贺闳画淮荒黄惠嵇极集几间绛焦蛟杰荆晶景钧珺竣开凯轲焜岚琅劳犁理荔量淩荦络买嵋媚猛淼闵甯排彭评普期欺祁淇棋茜强乔钦琴清晴邱荃筌然韧茹阮闰森善邵深淑疏舒述顺舜丝斯耜淞邰棠淘添婷茼童统为惟雯淅晰稀喜厦闲现羡翔项象雄须婿絮绚寻荀循雅娅砚雁焱尧壹诒迤贻胰轶茵淯寓渊媛粤越云哲蛰蛰轸植轵智众尊爱奥辟禀渤粲琛絺驰楚传琮当荻钿殿鼎督渡顿沨枫港琯荷湖郇涣焕煌晖汇会浑楫贾笕郊捷解禁靳经敬靖筠琚楷蒯琨廓雷莉里廉炼粱琳零旒辂琭禄路湄渼盟湣莫睦乃楠农暖湃逄聘莆颀琦琪祺佥铅勤诠辁群裟莎诜莘圣嵊诗轼蜀竖嗣肆嵩颂肃睢绥汤塘陀琬微湋炜渭温渥熙苋湘详想新歆惺绣诩煦暄煊铉渲勋询琰扬旸杨业义诣意雍犹游渝愉愚榆虞郁钰预御裕愈煜园圆恽载詹湛照罩蜇浈桢渚庄琢赀资榜碧宾逋菜沧臧察菖嫦畅裳尘诚铖称绰慈翠滇端尔菲逢凤福辅盖纲郜阁构嘏管菡豪郝赫瑚华诲珲嘉菁菊聚逵魁郎连寥廖绫菱领雒瑁萌蜜绵铭溟宁滂裴萍溥齐萁旗綦绮侨溱轻蜻箐铨荣溶榕熔瑞睿箬飒搡瑟僧韶慎寿绶菽塾署墅硕菘诵速愫溯台叹溏滔滕逖通铜图途团绾网维玮萎闻舞误郗溪僖铣郤瑕衔线限像逍箫榭荥需熏鞅祎铱旖银夤瑛荧萤郢墉踊瑜与语鸢源瑗愿造帻翟崭彰嶂幛赵肇祯甄榛筝种僮准菑缁滋综"
        self.emperor_firstname = ""
        self.emperor_lastname = ""
        self.yearNumber_list = ["建元", "元光", "元朔", "元狩", "元鼎", "元封", "太初", "天汉", "太始", "征和", "后元", "始元", "元凤", "平瑞", "本始", "地节", "元康", "神爵", "五凤", "甘露", "黄龙", "初元", "永光", "建昭", "竟宁", "建始", "河平", "阳朔", "鸿嘉", "永始", "元延", "绥和", "建平", "太初元将", "元寿", "元始", "居摄", "初始", "建国", "天凤", "地皇", "更始", "建武", "建武中元", "永平", "建初", "元和", "章和", "永元", "元兴", "延平", "永初", "元初", "永宁", "建光", "延光", "永建", "阳嘉", "永和", "汉安", "建康", "永嘉", "本初", "建和", "和平", "元嘉", "永兴", "永寿", "延熹", "永康", "建宁", "熹平", "光和", "中平", "光熹", "昭宁", "微平", "初平", "兴平", "建安", "延康", "黄初", "太和", "青龙", "景初", "正始", "嘉平", "正元", "甘露", "景元", "咸熙", "泰始", "咸宁", "太康", "太熙", "永熙", "永平", "元康", "永康", "永宁", "太安", "永安", "建武", "永安", "建兴", "永嘉", "建兴", "建武", "太兴", "永昌", "太宁", "咸和", "咸康", "建元", "永和", "升平", "隆和", "兴宁", "太和", "咸安", "宁康", "太元", "隆安", "元兴", "义熙", "元熙", "开皇", "仁寿", "大业", "义宁", "武德", "贞观", "永徽", "显庆", "龙朔", "麟德", "乾封", "总章", "咸亨", "上元", "仪凤", "调露", "永隆", "开耀", "永淳", "弘道", "嗣圣", "文明", "光宅", "垂拱", "永昌", "载初", "天授", "如意", "长寿", "延载", "证圣", "天册万岁", "万岁登封", "万岁通天", "神功", "圣历", "久视", "大足", "长安", "神龙", "景龙", "唐隆", "景云", "太极", "延和", "先天", "开元", "天宝", "至德", "乾元", "上元", "宝应", "广德", "永泰", "大历", "建中", "兴元", "贞元", "永贞", "元和", "长庆", "宝历", "大和", "开成", "会昌", "大中", "咸通", "乾符", "广明", "中和", "光启", "文德", "龙纪", "大顺", "景福", "乾宁", "光化", "天复", "天祐", "建隆", "乾德", "开宝", "太平兴国", "雍熙", "端拱", "淳化", "至道", "咸平", "景德", "大中祥符", "天禧", "乾兴", "天圣", "明道", "景祐", "宝元", "康定", "庆历", "皇祐", "至和", "嘉祐", "治平", "熙宁", "元丰", "元祐", "绍圣", "元符", "建中靖国", "崇宁", "大观", "政和", "重和", "宣和", "靖康", "建炎", "绍兴", "隆兴", "乾道", "纯熙", "淳熙", "绍熙", "庆元", "嘉泰", "开禧", "开禧", "嘉定", "宝庆", "绍定", "端平", "嘉熙", "淳祐", "宝祐", "开庆", "景定", "咸淳", "德祐", "景炎", "祥兴", "中统", "至元", "元贞", "大德", "至大", "皇庆", "延祐", "至治", "泰定", "致和", "天历", "至顺", "元统", "至元", "至正", "洪武", "建文", "永乐", "洪熙", "宣德", "正统", "景泰", "天顺", "成化", "弘治", "正德", "嘉靖", "隆庆", "万历", "泰昌", "天启", "崇祯", "顺治", "康熙", "雍正", "乾隆", "嘉庆", "道光", "咸丰", "同治", "光绪", "宣统"]
        self.shihao_list_first = ["太祖", "高祖", "世祖"]
        self.shihao_list_common = ["太宗", "高宗", "世宗", "中宗", "仁宗", "孝宗", "宣宗", "神宗", "哲宗", "理宗", "光宗", "宁宗", "英宗", "穆宗", "景宗", "圣宗", "兴宗", "道宗", "明宗", "庄宗", "哀宗", "愍宗", "钦宗", "徽宗", "高宗", "中宗", "玄宗", "代宗", "德宗", "顺宗", "宪宗", "穆宗", "敬宗", "文宗", "武宗", "宣宗", "懿宗", "僖宗", "昭宗", "哀帝"]
        self.shihao = ""

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
            {"time": "", "event": "风调雨顺，五谷丰登。", "emperor_hp_change": 1, "dynasty_hp_change": 5},
            {"time": "", "event": "天降祥瑞，国泰民安。", "emperor_hp_change": 1, "dynasty_hp_change": 8},
            {"time": "", "event": "科举开科，广揽天下贤才。", "emperor_hp_change": 0, "dynasty_hp_change": 6},
            {"time": "", "event": "边关大捷，扬威海外。", "emperor_hp_change": 1, "dynasty_hp_change": 10},
            {"time": "", "event": "大兴土木，修建宫殿，劳民伤财。", "emperor_hp_change": -1, "dynasty_hp_change": -8},
            {"time": "", "event": "黄河决堤，流民遍野，民不聊生。", "emperor_hp_change": -2, "dynasty_hp_change": -12},
            {"time": "", "event": "地方叛乱，朝野震动。", "emperor_hp_change": -2, "dynasty_hp_change": -10},
            {"time": "", "event": "后宫干政，朝政混乱。", "emperor_hp_change": -3, "dynasty_hp_change": -7},
            {"time": "", "event": "宦官专权，陷害忠良。", "emperor_hp_change": -2, "dynasty_hp_change": -9},
            {"time": "", "event": "外敌入侵，边患严重。", "emperor_hp_change": -2, "dynasty_hp_change": -15},
            {"time": "", "event": "减免赋税，与民休息。", "emperor_hp_change": 0, "dynasty_hp_change": 8},
            {"time": "", "event": "瘟疫横行，十室九空。", "emperor_hp_change": -3, "dynasty_hp_change": -12},
            {"time": "", "event": "藩镇割据，听调不听宣。", "emperor_hp_change": -1, "dynasty_hp_change": -10},
            {"time": "", "event": "皇帝沉迷声色，不理朝政。", "emperor_hp_change": -3, "dynasty_hp_change": -8},
            {"time": "", "event": "修建水利，造福百姓。", "emperor_hp_change": -1, "dynasty_hp_change": 6},
            {"time": "", "event": "开通商路，国库充盈。", "emperor_hp_change": 0, "dynasty_hp_change": 7},
            {"time": "", "event": "发现金矿，国库大增。", "emperor_hp_change": 0, "dynasty_hp_change": 5},
            {"time": "", "event": "编纂大典，文化繁荣。", "emperor_hp_change": -1, "dynasty_hp_change": 8},
            {"time": "", "event": "诸王争储，朝堂党争不断。", "emperor_hp_change": -3, "dynasty_hp_change": -8},
            {"time": "", "event": "连年干旱，颗粒无收。", "emperor_hp_change": -1, "dynasty_hp_change": -10},
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
            self.shihao = self.dynasty + random.choice(self.shihao_list_first)
        else:
            self.shihao = self.dynasty + random.choice(self.shihao_list_common)

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
        self.yearNumber = random.choice(self.yearNumber_list)
        self.year_number_input.setText(self.yearNumber)

    def dialog_yearNumber_change_name(self):
        self.yearNumber = random.choice(self.yearNumber_list)
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
        if self.auto_run:
            self.emperor_change_name_after()
            self.dialog_yearNumber_change_name()
            self.new_emp_confirm()
        else:
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
