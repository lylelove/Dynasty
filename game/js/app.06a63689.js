(function(e){function t(t){for(var s,n,o=t[0],h=t[1],l=t[2],_=0,p=[];_<o.length;_++)n=o[_],Object.prototype.hasOwnProperty.call(i,n)&&i[n]&&p.push(i[n][0]),i[n]=0;for(s in h)Object.prototype.hasOwnProperty.call(h,s)&&(e[s]=h[s]);m&&m(t);while(p.length)p.shift()();return r.push.apply(r,l||[]),a()}function a(){for(var e,t=0;t<r.length;t++){for(var a=r[t],s=!0,o=1;o<a.length;o++){var h=a[o];0!==i[h]&&(s=!1)}s&&(r.splice(t--,1),e=n(n.s=a[0]))}return e}var s={},i={app:0},r=[];function n(t){if(s[t])return s[t].exports;var a=s[t]={i:t,l:!1,exports:{}};return e[t].call(a.exports,a,a.exports,n),a.l=!0,a.exports}n.m=e,n.c=s,n.d=function(e,t,a){n.o(e,t)||Object.defineProperty(e,t,{enumerable:!0,get:a})},n.r=function(e){"undefined"!==typeof Symbol&&Symbol.toStringTag&&Object.defineProperty(e,Symbol.toStringTag,{value:"Module"}),Object.defineProperty(e,"__esModule",{value:!0})},n.t=function(e,t){if(1&t&&(e=n(e)),8&t)return e;if(4&t&&"object"===typeof e&&e&&e.__esModule)return e;var a=Object.create(null);if(n.r(a),Object.defineProperty(a,"default",{enumerable:!0,value:e}),2&t&&"string"!=typeof e)for(var s in e)n.d(a,s,function(t){return e[t]}.bind(null,s));return a},n.n=function(e){var t=e&&e.__esModule?function(){return e["default"]}:function(){return e};return n.d(t,"a",t),t},n.o=function(e,t){return Object.prototype.hasOwnProperty.call(e,t)},n.p="/";var o=window["webpackJsonp"]=window["webpackJsonp"]||[],h=o.push.bind(o);o.push=t,o=o.slice();for(var l=0;l<o.length;l++)t(o[l]);var m=h;r.push([0,"chunk-vendors"]),a()})({0:function(e,t,a){e.exports=a("56d7")},"034f":function(e,t,a){"use strict";a("85ec")},"56d7":function(e,t,a){"use strict";a.r(t);a("e260"),a("e6cf"),a("cca6"),a("a79d");var s=a("2b0e"),i=a("5c96"),r=a.n(i),n=(a("0fae"),function(){var e=this,t=e.$createElement,a=e._self._c||t;return a("div",{attrs:{id:"app"}},[a("el-tag",{attrs:{type:"success"}},[e._v("王朝V0.17")]),a("el-dialog",{class:1==e.emperor_die?"":"none",attrs:{title:"新皇登基",visible:e.emperor_die},on:{"update:visible":function(t){e.emperor_die=t}}},[a("el-form",[a("el-form-item",{attrs:{label:"姓名"}},[a("el-button",{staticStyle:{margin:"10px"},attrs:{type:"primary",icon:"el-icon-refresh",circle:""},on:{click:e.emperor_change_name_after}}),a("el-input",{attrs:{autocomplete:"off"},model:{value:e.emperor,callback:function(t){e.emperor=t},expression:"emperor"}})],1),a("el-form-item",{attrs:{label:"年号"}},[a("el-button",{staticStyle:{margin:"10px"},attrs:{type:"primary",icon:"el-icon-refresh",circle:""},on:{click:e.yearNumber_change_name}}),a("el-input",{attrs:{autocomplete:"off"},model:{value:e.yearNumber,callback:function(t){e.yearNumber=t},expression:"yearNumber"}})],1)],1),a("div",{staticClass:"dialog-footer",attrs:{slot:"footer"},slot:"footer"},[a("el-button",{attrs:{type:"primary"},on:{click:e.dio}},[e._v("确 定")])],1)],1),a("el-dialog",{class:1==e.dynasty_die?"":"none",attrs:{title:"结束",visible:e.dynasty_die},on:{"update:visible":function(t){e.dynasty_die=t}}},[a("div",[e._v("皇帝列表")]),a("el-table",{attrs:{data:e.listjson}},[a("el-table-column",{attrs:{prop:"id",label:"序号"}}),a("el-table-column",{attrs:{prop:"shihao",label:"谥号"}}),a("el-table-column",{attrs:{prop:"name",label:"姓名"}}),a("el-table-column",{attrs:{prop:"age",label:"年龄"}}),a("el-table-column",{attrs:{prop:"nianhao",label:"年号"}}),a("el-table-column",{attrs:{prop:"jinian",label:"纪年"}}),a("el-table-column",{attrs:{prop:"ab",label:"能力"}})],1),a("div",[e._v("重新开始游戏？")]),a("div",{staticClass:"dialog-footer",attrs:{slot:"footer"},slot:"footer"},[a("el-button",{attrs:{type:"primary"},on:{click:e.dio2}},[e._v("确 定")])],1)],1),a("el-form",{staticClass:"demo-form-inline",class:1==e.firstgame?"":"none",attrs:{inline:!0}},[a("el-form-item",{attrs:{label:"朝代"}},[a("el-input",{attrs:{placeholder:"朝代"},model:{value:e.dynasty,callback:function(t){e.dynasty=t},expression:"dynasty"}}),a("el-button",{staticStyle:{margin:"10px"},attrs:{type:"primary",icon:"el-icon-refresh",circle:""},on:{click:e.dynasty_change_name}})],1),a("el-form-item",{attrs:{label:"皇帝"}},[a("el-input",{attrs:{placeholder:"姓名"},model:{value:e.emperor,callback:function(t){e.emperor=t},expression:"emperor"}}),a("el-button",{staticStyle:{margin:"10px"},attrs:{type:"primary",icon:"el-icon-refresh",circle:""},on:{click:e.emperor_change_name}})],1),a("el-form-item",{attrs:{label:"年号"}},[a("el-input",{attrs:{placeholder:"年号"},model:{value:e.yearNumber,callback:function(t){e.yearNumber=t},expression:"yearNumber"}}),a("el-button",{staticStyle:{margin:"10px"},attrs:{type:"primary",icon:"el-icon-refresh",circle:""},on:{click:e.yearNumber_change_name}})],1),a("el-form-item",[a("el-button",{attrs:{type:"primary"},on:{click:e.gamestart}},[e._v("开始游戏")])],1)],1),a("el-tabs",{class:0==e.firstgame?"":"none",attrs:{type:"border-card","tab-position":"left"},model:{value:e.activeName,callback:function(t){e.activeName=t},expression:"activeName"}},[a("el-tab-pane",{attrs:{label:"主界面",name:"first"}},[a("el-descriptions",{attrs:{title:"基本信息",direction:"vertical",column:2,border:""}},[a("el-descriptions-item",{attrs:{label:"朝代"}},[e._v(e._s(e.dynasty))]),a("el-descriptions-item",{attrs:{label:"皇帝"}},[e._v(e._s(e.emperor))]),a("el-descriptions-item",{attrs:{label:"年号"}},[e._v(e._s(e.yearNumber))]),a("el-descriptions-item",{attrs:{label:"纪年"}},[e._v(e._s(1==e.jinian?"元":e.jinian)+"年")]),a("el-descriptions-item",{attrs:{label:"国势"}},[e._v(e._s(e.dynasty_st))]),a("el-descriptions-item",{attrs:{label:"寿限"}},[e._v(e._s(e.emperor_hp))])],1),a("Event",{ref:"event",staticClass:"none"}),a("el-divider",{attrs:{"content-position":"center"}},[e._v("设置策略")]),a("div",{staticClass:"block"},[a("span",{staticClass:"demonstration"},[e._v("勤政爱民")]),a("el-slider",{attrs:{"show-tooltip":!1},on:{change:e.bchange},model:{value:e.hardworking,callback:function(t){e.hardworking=t},expression:"hardworking"}})],1),a("div",{staticClass:"block"},[a("span",{staticClass:"demonstration"},[e._v("声色犬马")]),a("el-slider",{attrs:{"show-tooltip":!1},on:{change:e.achange},model:{value:e.amuse,callback:function(t){e.amuse=t},expression:"amuse"}})],1),a("el-button",{attrs:{type:"primary",round:""},on:{click:e.gamemin}},[e._v("继续")])],1),a("el-tab-pane",{attrs:{label:"皇帝信息",name:"second"}},[a("el-descriptions",{attrs:{title:"基本信息",direction:"vertical",column:4,border:""}},[a("el-descriptions-item",{attrs:{label:"姓名"}},[e._v(e._s(e.emperor))]),a("el-descriptions-item",{attrs:{label:"年龄"}},[e._v(e._s(e.emperor_age))]),a("el-descriptions-item",{attrs:{label:"寿限"}},[e._v(e._s(e.emperor_hp))]),a("el-descriptions-item",{attrs:{label:"能力"}},[e._v(e._s(e.emperor_ab))])],1)],1),a("el-tab-pane",{attrs:{label:"王朝信息",name:"third"}},[a("el-descriptions",{attrs:{title:"基本信息",direction:"vertical",column:3,border:""}},[a("el-descriptions-item",{attrs:{label:"朝代"}},[e._v(e._s(e.dynasty))]),a("el-descriptions-item",{attrs:{label:"国祚"}},[e._v(e._s(e.dynasty_age))]),a("el-descriptions-item",{attrs:{label:"状态"}},[e._v(e._s(e.dynasty_st))])],1),a("el-table",{attrs:{data:e.listjson}},[a("el-table-column",{attrs:{prop:"id",label:"序号"}}),a("el-table-column",{attrs:{prop:"shihao",label:"谥号"}}),a("el-table-column",{attrs:{prop:"name",label:"姓名"}}),a("el-table-column",{attrs:{prop:"age",label:"年龄"}}),a("el-table-column",{attrs:{prop:"nianhao",label:"年号"}}),a("el-table-column",{attrs:{prop:"jinian",label:"纪年"}}),a("el-table-column",{attrs:{prop:"ab",label:"能力"}})],1)],1)],1)],1)}),o=[],h=function(){var e=this,t=e.$createElement,a=e._self._c||t;return a("el-table",{attrs:{data:e.event_show}},[a("el-table-column",{attrs:{prop:"time",label:"时间"}}),a("el-table-column",{attrs:{prop:"event",label:"事件"}})],1)},l=[],m={name:"Event",data:function(){return{event_show:[],event_list:[{time:"",event:"今年无事发生。",emperor_hp_change:0,dynasty_hp_change:0},{time:"",event:"事件2",emperor_hp_change:0,dynasty_hp_change:0}],data_emperor_hp_change:0,data_dynasty_hp_change:0,d_time:"",d_event:"",d_event_id:0}},methods:{event_change:function(){null!=this.event_list[this.d_event_id].emperor_hp_change&&(this.data_emperor_hp_change=this.event_list[this.d_event_id].emperor_hp_change),null!=this.event_list[this.d_event_id].dynasty_hp_change&&(this.data_dynasty_hp_change=this.event_list[this.d_event_id].dynasty_hp_change)}}},_=m,p=a("2877"),d=Object(p["a"])(_,h,l,!1,null,null,null),c=d.exports,y={components:{Event:c},name:"App",data:function(){return{charts:"",opinionData:[],yearlist:[],call_event:!1,ongame:!0,emperor_die:!1,dynasty_die:!1,emperor_id:1,firstgame:!0,emperor_age:0,emperor_hp:0,emperor_ab:0,dynasty_age:0,dynasty_st:"",dynasty_hp:0,jinian:1,dynasty:"",emperor:"",yearNumber:"",activeName:"first",amuse:50,hardworking:50,year:0,randomdata:0,total_amuse:1,total_hardworking:1,listjson:[],dynasty_name:["宋","周","齐","梁","魏","夏","陈","唐","晋","秦","汉","楚"],emperor_firstname_list:"王李张刘陈杨黄吴赵周徐孙马朱胡林郭何高罗郑梁谢宋唐许邓冯韩曹曾彭肖蔡潘田董袁于余蒋叶杜苏魏程吕丁沈任姚卢钟姜崔谭廖范汪陆金石戴贾韦夏邱方侯邹熊孟秦白毛江闫薛尹付段雷黎史龙钱贺陶顾龚郝邵万严洪赖武傅莫孔",emperor_lastname_list:"乙一力了人入又卜刀刁丁二土丸兀夕下水小丫幺也已弋于丈才叉川寸大凡干工弓及己巾久口廿女千三山上勺士巳子木内牛匹片亓欠切犬仁壬仍日冗卅少升什氏手巴比卞不尺仇丹仃斗反方分夫父戈公勾互户化幻火介今斤井亢孔毛殳水四太天屯王文毋午心牙爻尹引尤友予元曰月匀允仄仉之支止中皮平仟巧且丘囚去冉仨申生史矢世仕市示石失司他它田仝瓦外未五戊仙兄玄央以永用由右白半包北本必丙布册出代旦氐冬弗付甘功古瓜禾弘乎卉加甲巨句卡刊可立尥令另矛卯民末母目尼奴丕幼玉札占仗召正只主仔左艮亘共光圭亥好合回吉岌匠交决伉考匡老耒吏安百冰并臣丞吃弛充此次存打地多朵而耳帆仿妃份伏旮各列六米名牟囡年妗究君均局克况冷李利良吕芈妙男妞判七岐杞羌求劬汝杉劭佘汜宋町廷彤佗妥完位吾汐希岘孝辛形杏秀序巡汛延言冶甬攸酉佑余妤皂贝兵伯孛步材岑车辰成呈池赤伺村但低弟佃豆杜兑囤坊孚甫告更攻囯含罕何亨宏弧汲即忌见江角戒志助壮灼孜佐作坐屺曲全任戎如式收守寺似汀同伍西先向行休旭旬伢羊伊衣夷亦屹因印有宇羽聿再在兆至仲州舟朱竹自金卺京净纠赳玖咎卷居具抗岢刻肯空快狂坤昆来两林仑侣盲枚妹没门孟氓汨宓岷旻明命沫沐牧奈妮念帕杷抛沛佩帔朋批坡沏妻其歧奇戕沁青穹屈取券乳枘叁沙姗尚舍社沈使始事艾哎岸昂枊坳垇八爸佰攽板版杯表秉幷帛昌长抄弨沉承冲初炊垂耷岱宕狄底玓典店耵定东咚侗抖妒沌儿泛房昉放非氛汾奉扶府阜冈杲庚供姑孤汩固刮卦官炅果杭沆昊和虎佶技季佳肩佼姐届侍受抒叔刷祀松所弢宛汪旺委味汶武昔析弦冼协忻昕欣姓幸岫亚炎兖奄佯肴杳夜依沂宜抑佾易咏於盂雨沅昀争枝知直忠周宙侏竺杼状隹卓宗冒玫眉美沔勉泯某姥娜耐南泮盼盆毗品屏祈芑芊前俏秋俅酋泉染柔是首姝帅思泗亭凃沱娃纨芄威韦畏侠咸相香巷信星庥胥叙宣泫炫泶沿匽彦泱垚姚要页怡舣奕弈羿音垠胤盈映泳保抱祊砭扁便柄炳波泊勃查昶怊重抽穿舡春匆待帝峒垌度段盾法飞风封负赴泔革宫故冠癸河红泓虹侯后厚狐砉皇纪既枷架柬建牮姜姣皆界劲矜俓炯九玦军俊炬看柯科奎厘俚亮泠柃柳律抹芒昴勇幽羑禹芋昱俞垣爰约玥哉昝则昭沼者柘贞政治峙致胄注柱炷咨姿盎敖笆柏班般豹趵倍眧城乘翀刍俶纯祠耽岛玷洞娥恩洱珐芳纺舫芬峰芙服刚罡高哥格根耕耿肱恭贡倌桂衮函航恒洪候祜花洹桓恢洄活姬笈疾记家兼津晋径娟隽珏峻桔珂恪括朗凉烈玲瓴凌留伦洛马勐珉纳能倪娘畔配娉珀圃芪起祗洽虔倩芩芹秦邛容洳桑珊射珅神师十时拾书纾殊恕栓朔凇素孙笋娑索泰唐洮桃特甜庭桐娓纹翁乌务奚息席洗峡夏宵效校笑芯修脩徐栩轩烜眩洵训讯迅衍晏芫洋益殷邕佑育彧峪原袁员纭芸耘奘旃展站钊针珍真洲祝酌笫祖祚邦浜苞毕彪邠彬斌彩曹涔参产常晨趁偁琤晟敕崇处船钏从崔带埭聃得笛钓动梵访烽苻浮匐符副岗舸苟规硅崞国海酣焊毫浩珩胡扈凰悔彗基偈寄坚健将皎教婕堇婧竟涓浚康悝馗浪勒梨笠梁聊苓羚翎流娄鹿略珞麻麦曼茅茂梅密苗敏茉旎涅您培旆佩浦戚崎启弃乾卿朐渠区若啬商绍苕涉笙孰术庶爽堂悌屠望唯伟尉问悟晞浠悉习祥邢袖虚许勖旋雪珣焉闫研野移异翊翌寅英迎庸涌庾苑悦张章浙振峥执珠专茁着梓紫族报堡备弼皕赑博采策曾单场焯超朝程盛淳词兹淙淡登迪第棣奠栋敦发番邡斐费冯涪袱复傅富淦皋贯贵涵寒皓贺闳画淮荒黄惠嵇极集几间绛焦蛟杰荆晶景钧珺竣开凯轲焜岚琅劳犁理荔量淩荦络买嵋媚猛淼闵甯排彭评普期欺祁淇棋茜强乔钦琴清晴邱荃筌然韧茹阮闰森善邵深淑疏舒述顺舜丝斯耜淞邰棠淘添婷茼童统为惟雯淅晰稀喜厦闲现羡翔项象雄须婿絮绚寻荀循雅娅砚雁焱尧壹诒迤贻胰轶茵淯寓渊媛粤越云哲蛰轸植轵智众尊爱奥辟禀渤粲琛絺驰楚传琮当荻钿殿鼎督渡顿沨枫港琯荷湖郇涣焕煌晖汇会浑楫贾笕郊捷解禁靳经敬靖筠琚楷蒯琨廓雷莉里廉炼粱琳零旒辂琭禄路湄渼盟湣莫睦乃楠农暖湃逄聘莆颀琦琪祺佥铅勤诠辁群裟莎诜莘圣嵊诗轼蜀竖嗣肆嵩颂肃睢绥汤塘陀琬微湋炜渭温渥熙苋湘详想新歆惺绣诩煦暄煊铉渲勋询琰扬旸杨业义诣意雍犹游渝愉愚榆虞郁钰预御裕愈煜园圆恽载詹湛照罩蜇浈桢渚庄琢赀资榜碧宾逋菜沧臧察菖嫦畅裳尘诚铖称绰慈翠滇端尔菲逢凤福辅盖纲郜阁构嘏管菡豪郝赫瑚华诲珲嘉菁菊聚逵魁郎连寥廖绫菱领雒瑁萌蜜绵铭溟宁滂裴萍溥齐萁旗綦绮侨溱轻蜻箐铨荣溶榕熔瑞睿箬飒搡瑟僧韶慎寿绶菽塾署墅硕菘诵速愫溯台叹溏滔滕逖通铜图途团绾网维玮萎闻舞误郗溪僖铣郤瑕衔线限像逍箫榭荥需熏鞅祎铱旖银夤瑛荧萤郢墉踊瑜与语鸢源瑗愿造帻翟崭彰嶂幛赵肇祯甄榛筝种僮准菑缁滋综",emperor_firstname:"",emperor_lastname:"",yearNumber_list:"建元承大宝太上始真王武定开乾统文明应国光弘仁洪至治崇德本淳阳天地初熙泰神人正普康晏安同庆久延寿保隆长宁靖成更化中和启顺章清平河汉景孝义雀龙祥嘉会兴贞永丰豋广显昌凤麟重赤白玉露绍青黄通道咸宣意端居拱圣皇",shihao_list_first:"神圣贤文武成康献懿元章世",shihao_list_common:"景宣明昭正敬恭庄肃穆翼襄烈桓威勇毅克庄御安定简贞匡质靖真顺思皓显和元高光英睿博宪坚孝忠惠德仁智慎礼义周敏信达理清直钦益良度基慈齐深温让密厚纯勤谦友祁广淑俭灵荣厉絜舒贲逸偲逑懋宜哲察通仪经庇协端休悦绰容确恒熙洽绍",shihao:"",event_id:0,time_year:"",event_happened:[{time:"",event:""}]}},methods:{achange:function(){this.hardworking=100-this.amuse},bchange:function(){this.amuse=100-this.hardworking},gamestart:function(){this.emperor_firstname=this.emperor[0],this.firstgame=!this.firstgame,this.emperor_age=26,this.emperor_hp=20+Math.floor(20*Math.random())-Math.floor(20*Math.random()),this.emperor_ab=10,this.dynasty_hp=100,this.dynasty_function_st(),this.opinionData.push(this.dynasty_hp),this.yearlist.push(this.year)},gamemin:function(){this.year=this.year+1,this.event_happen(),this.opinionData.push(this.dynasty_hp),this.yearlist.push(this.year),this.gamemin_emperor(),this.gamemin_dynasty(),this.dynasty_function_st()},gamemin_dynasty:function(){this.emperor_hp>0&&(this.dynasty_hp>0&&(this.dynasty_hp=this.dynasty_hp-this.amuse/40*5/this.emperor_ab+this.hardworking/40*this.emperor_ab/10,this.dynasty_age=this.dynasty_age+1),this.dynasty_hp>=100&&(this.dynasty_hp=100),this.dynasty_hp<=0&&(1==this.ongame&&(this.gamemin_shihao(),this.gamemin_dynasty_change(),this.dynasty_die=!0,this.dynasty_hp=0,this.ongame=!1),this.dynasty_die=!0,this.dynasty_hp=0),this.dynasty_hp<=15&&this.emperor_ab>=8&&(this.dynasty_hp=15))},gamemin_emperor:function(){this.dynasty_hp>0&&(this.emperor_hp>0&&(this.emperor_age=this.emperor_age+1,this.jinian=this.jinian+1,this.randomdata=Math.random(),this.emperor_hp=this.emperor_hp-1),this.emperor_hp<=0&&(1==this.ongame&&(this.gamemin_shihao(),this.emperor_die=!0,this.gamemin_emperor_change(),this.emperor_hp=0,this.ongame=!1),this.emperor_hp=0,this.emperor_die=!0))},gamemin_shihao:function(){1==this.emperor_id?this.shihao=this.dynasty+this.shihao_list_first[Math.floor(Math.random()*this.shihao_list_first.length)]+"祖":this.shihao=this.dynasty+this.shihao_list_common[Math.floor(Math.random()*this.shihao_list_common.length)]+"宗"},gamemin_emperor_change:function(){this.listjson.push({id:this.emperor_id,name:this.emperor,nianhao:this.yearNumber,age:this.emperor_age,jinian:this.jinian,shihao:this.shihao,ab:this.emperor_ab})},gamemin_emperor_new:function(){this.dynasty_hp=this.dynasty_hp-10,this.dynasty_hp<=0&&(this.dynasty_hp=1),this.jinian=1,this.emperor_new_age(),this.emperor_ab=5+Math.floor(5*Math.random())-Math.floor(5*Math.random()),this.emperor_new_hp(),this.total_amuse=1,this.total_hardworking=1},gamemin_dynasty_change:function(){this.listjson.push({id:this.emperor_id,name:this.emperor,nianhao:this.yearNumber,age:this.emperor_age,jinian:this.jinian,shihao:this.shihao,ab:this.emperor_ab})},gamemin_dynasty_new:function(){this.dynasty_age=0,this.jinian=0,this.listjson=[],this.year=0,this.emperor_id=0,this.yearlist=[],this.opinionData=[]},dio:function(){this.emperor_die=!1,this.dialogFormVisible=!1,this.gamemin_emperor_new(),this.emperor_id=this.emperor_id+1,this.ongame=!0},dio2:function(){this.dynasty_die=!1,this.dialogFormVisible=!1,this.firstgame=!0,this.gamemin_dynasty_new(),this.ongame=!0},dynasty_change_name:function(){this.dynasty=this.dynasty_name[Math.floor(Math.random()*this.dynasty_name.length)]},emperor_change_name:function(){this.emperor_firstname=this.emperor_firstname_list[Math.floor(Math.random()*this.emperor_firstname_list.length)],this.emperor_lastname=this.emperor_lastname_list[Math.floor(Math.random()*this.emperor_lastname_list.length)]+this.emperor_lastname_list[Math.floor(Math.random()*this.emperor_lastname_list.length)],this.emperor=this.emperor_firstname+this.emperor_lastname},emperor_new_hp:function(){this.randomdata=Math.floor(3*Math.random()),this.emperor_age<=35&&(0==this.randomdata?this.emperor_hp=20+Math.floor(20*Math.random()):this.emperor_hp=20-Math.floor(20*Math.random())),this.emperor_age>35&&(this.emperor_hp=20-Math.floor(20*Math.random())+Math.floor(10*Math.random()))},emperor_new_age:function(){this.randomdata=this.emperor_age,this.emperor_age=this.randomdata-16-Math.floor(25*Math.random());while(this.emperor_age<=0)this.emperor_age=Math.floor(50*Math.random())},yearNumber_change_name:function(){this.yearNumber=this.yearNumber_list[Math.floor(Math.random()*this.yearNumber_list.length)]+this.yearNumber_list[Math.floor(Math.random()*this.yearNumber_list.length)]},emperor_change_name_after:function(){this.emperor_lastname=this.emperor_lastname_list[Math.floor(Math.random()*this.emperor_lastname_list.length)]+this.emperor_lastname_list[Math.floor(Math.random()*this.emperor_lastname_list.length)],this.emperor=this.emperor_firstname+this.emperor_lastname},dynasty_function_st:function(){this.dynasty_hp>=90?this.dynasty_st="国泰民安":this.dynasty_hp>=80?this.dynasty_st="风调雨顺":this.dynasty_hp>=70?this.dynasty_st="":this.dynasty_hp>=60?this.dynasty_st="差强人意":this.dynasty_hp>=30?this.dynasty_st="风雨飘摇":this.dynasty_hp>=20?this.dynasty_st="国势倾颓":this.dynasty_hp>=10?this.dynasty_st="不绝如缕":this.dynasty_hp>=50&&(this.dynasty_st="旦夕之间")},event_happen:function(){this.event_id_chose(),1==this.jinian?this.$refs.event.d_time=this.yearNumber+"元年":this.$refs.event.d_time=this.yearNumber+this.jinian+"年",this.$refs.event.d_event=this.$refs.event.event_list[this.event_id].event,this.$refs.event.d_event_id=this.event_id,this.$refs.event.event_show=[{time:this.$refs.event.d_time,event:this.$refs.event.d_event}],this.event_happened.push({time:this.$refs.event.d_time,event:this.$refs.event.d_event}),this.$refs.event.event_change(),this.emperor_hp=this.emperor_hp+this.$refs.event.data_emperor_hp_change,this.dynasty_hp=this.dynasty_hp+this.$refs.event.data_dynasty_hp_change},event_id_chose:function(){0==this.call_event&&(this.event_id=Math.floor(Math.random()*this.$refs.event.event_list.length))}}},u=y,f=(a("034f"),Object(p["a"])(u,n,o,!1,null,null,null)),b=f.exports;s["default"].use(r.a),new s["default"]({render:function(e){return e(b)}}).$mount("#app")},"85ec":function(e,t,a){}});
//# sourceMappingURL=app.06a63689.js.map