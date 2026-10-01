#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成扩展走廊数据集（100+ 条）
成本口径：World Bank Remittance Prices Worldwide 的地区平均值 + 国别调整。
标注为「地区基准 + 公开季报均值」，不冒充逐国实测。
"""
import json

# 地区基准（World Bank RPW 全球加权口径下的地区平均）
REGION = {
    "EAP": {"zh": "东亚与太平洋", "trad": 6.5, "dig": 3.0},
    "SAS": {"zh": "南亚",         "trad": 5.7, "dig": 2.6},
    "ECA": {"zh": "欧洲与中亚",   "trad": 6.6, "dig": 3.2},
    "LAC": {"zh": "拉美与加勒比", "trad": 6.0, "dig": 2.8},
    "MENA": {"zh": "中东北非",    "trad": 6.2, "dig": 2.9},
    "SSA": {"zh": "撒哈拉以南非洲", "trad": 8.1, "dig": 3.9},
}

# (ISO2, English, 中文, 地区, 成本调整)  —— adj 为国别相对地区均值的偏移
C = [
 # ── 东亚与太平洋 ──
 ("PH","Philippines","菲律宾","EAP",-0.1),("ID","Indonesia","印度尼西亚","EAP",0.4),
 ("VN","Vietnam","越南","EAP",0.1),("TH","Thailand","泰国","EAP",0.0),
 ("MY","Malaysia","马来西亚","EAP",-0.2),("CN","China","中国","EAP",0.7),
 ("KH","Cambodia","柬埔寨","EAP",0.5),("MM","Myanmar","缅甸","EAP",0.9),
 ("LA","Laos","老挝","EAP",0.6),("MN","Mongolia","蒙古","EAP",0.3),
 ("FJ","Fiji","斐济","EAP",1.1),("PG","Papua New Guinea","巴布亚新几内亚","EAP",1.3),
 ("TL","Timor-Leste","东帝汶","EAP",1.0),("SB","Solomon Islands","所罗门群岛","EAP",1.6),
 ("VU","Vanuatu","瓦努阿图","EAP",1.4),("WS","Samoa","萨摩亚","EAP",1.2),
 ("TO","Tonga","汤加","EAP",1.5),("KI","Kiribati","基里巴斯","EAP",1.7),
 # ── 南亚 ──
 ("IN","India","印度","SAS",-0.3),("PK","Pakistan","巴基斯坦","SAS",0.1),
 ("BD","Bangladesh","孟加拉","SAS",0.2),("NP","Nepal","尼泊尔","SAS",0.5),
 ("LK","Sri Lanka","斯里兰卡","SAS",0.3),("AF","Afghanistan","阿富汗","SAS",1.2),
 ("BT","Bhutan","不丹","SAS",0.7),("MV","Maldives","马尔代夫","SAS",0.6),
 # ── 欧洲与中亚 ──
 ("UA","Ukraine","乌克兰","ECA",0.1),("TR","Turkey","土耳其","ECA",-0.2),
 ("GE","Georgia","格鲁吉亚","ECA",-0.4),("AM","Armenia","亚美尼亚","ECA",-0.3),
 ("AZ","Azerbaijan","阿塞拜疆","ECA",0.0),("MD","Moldova","摩尔多瓦","ECA",0.4),
 ("RS","Serbia","塞尔维亚","ECA",0.2),("BA","Bosnia and Herzegovina","波黑","ECA",0.3),
 ("AL","Albania","阿尔巴尼亚","ECA",0.5),("MK","North Macedonia","北马其顿","ECA",0.3),
 ("XK","Kosovo","科索沃","ECA",0.6),("KG","Kyrgyzstan","吉尔吉斯斯坦","ECA",0.7),
 ("TJ","Tajikistan","塔吉克斯坦","ECA",0.5),("UZ","Uzbekistan","乌兹别克斯坦","ECA",0.3),
 ("KZ","Kazakhstan","哈萨克斯坦","ECA",-0.1),("RO","Romania","罗马尼亚","ECA",0.1),
 ("BG","Bulgaria","保加利亚","ECA",0.2),("HR","Croatia","克罗地亚","ECA",0.1),
 # ── 拉美与加勒比 ──
 ("MX","Mexico","墨西哥","LAC",-0.1),("BR","Brazil","巴西","LAC",0.2),
 ("CO","Colombia","哥伦比亚","LAC",-0.3),("GT","Guatemala","危地马拉","LAC",-0.2),
 ("HN","Honduras","洪都拉斯","LAC",0.1),("SV","El Salvador","萨尔瓦多","LAC",-0.4),
 ("NI","Nicaragua","尼加拉瓜","LAC",0.3),("CR","Costa Rica","哥斯达黎加","LAC",0.1),
 ("PA","Panama","巴拿马","LAC",-0.1),("DO","Dominican Republic","多米尼加","LAC",-0.3),
 ("HT","Haiti","海地","LAC",0.9),("JM","Jamaica","牙买加","LAC",0.2),
 ("TT","Trinidad and Tobago","特立尼达和多巴哥","LAC",0.3),("GY","Guyana","圭亚那","LAC",0.4),
 ("SR","Suriname","苏里南","LAC",0.5),("EC","Ecuador","厄瓜多尔","LAC",0.0),
 ("PE","Peru","秘鲁","LAC",0.1),("BO","Bolivia","玻利维亚","LAC",0.4),
 ("PY","Paraguay","巴拉圭","LAC",0.3),("UY","Uruguay","乌拉圭","LAC",0.2),
 ("AR","Argentina","阿根廷","LAC",0.8),("CL","Chile","智利","LAC",0.1),
 ("CU","Cuba","古巴","LAC",1.4),("BZ","Belize","伯利兹","LAC",0.6),
 # ── 中东北非 ──
 ("EG","Egypt","埃及","MENA",-0.1),("MA","Morocco","摩洛哥","MENA",-0.2),
 ("TN","Tunisia","突尼斯","MENA",0.0),("DZ","Algeria","阿尔及利亚","MENA",0.3),
 ("JO","Jordan","约旦","MENA",-0.3),("LB","Lebanon","黎巴嫩","MENA",0.6),
 ("IQ","Iraq","伊拉克","MENA",0.4),("YE","Yemen","也门","MENA",1.5),
 ("SY","Syria","叙利亚","MENA",1.6),("PS","Palestine","巴勒斯坦","MENA",0.3),
 ("SD","Sudan","苏丹","MENA",1.3),("LY","Libya","利比亚","MENA",0.8),
 # ── 撒哈拉以南非洲 ──
 ("NG","Nigeria","尼日利亚","SSA",-0.2),("KE","Kenya","肯尼亚","SSA",-0.5),
 ("GH","Ghana","加纳","SSA",0.3),("ZA","South Africa","南非","SSA",0.1),
 ("TZ","Tanzania","坦桑尼亚","SSA",0.2),("UG","Uganda","乌干达","SSA",0.4),
 ("RW","Rwanda","卢旺达","SSA",0.3),("ET","Ethiopia","埃塞俄比亚","SSA",0.5),
 ("SN","Senegal","塞内加尔","SSA",-0.1),("CI","Ivory Coast","科特迪瓦","SSA",0.6),
 ("CM","Cameroon","喀麦隆","SSA",0.7),("ZW","Zimbabwe","津巴布韦","SSA",0.9),
 ("ZM","Zambia","赞比亚","SSA",0.5),("MW","Malawi","马拉维","SSA",0.8),
 ("MZ","Mozambique","莫桑比克","SSA",0.6),("MG","Madagascar","马达加斯加","SSA",0.7),
 ("ML","Mali","马里","SSA",0.4),("BF","Burkina Faso","布基纳法索","SSA",0.5),
 ("NE","Niger","尼日尔","SSA",0.8),("TD","Chad","乍得","SSA",1.0),
 ("CD","DR Congo","刚果（金）","SSA",1.1),("CG","Congo","刚果（布）","SSA",0.9),
 ("AO","Angola","安哥拉","SSA",0.9),("SO","Somalia","索马里","SSA",1.5),
 ("SS","South Sudan","南苏丹","SSA",1.6),("LR","Liberia","利比里亚","SSA",1.0),
 ("SL","Sierra Leone","塞拉利昂","SSA",0.9),("GM","Gambia","冈比亚","SSA",0.7),
 ("GN","Guinea","几内亚","SSA",0.8),("TG","Togo","多哥","SSA",0.5),
 ("BJ","Benin","贝宁","SSA",0.5),("MR","Mauritania","毛里塔尼亚","SSA",0.6),
 ("BW","Botswana","博茨瓦纳","SSA",0.2),("NA","Namibia","纳米比亚","SSA",0.3),
 ("LS","Lesotho","莱索托","SSA",0.7),("SZ","Eswatini","斯威士兰","SSA",0.6),
 ("BI","Burundi","布隆迪","SSA",1.0),("ER","Eritrea","厄立特里亚","SSA",1.4),
]

# 币种映射（用于汇率）
CUR = {
 "PH":"PHP","ID":"IDR","VN":"VND","TH":"THB","MY":"MYR","CN":"CNY","KH":"KHR","MM":"MMK",
 "LA":"LAK","MN":"MNT","FJ":"FJD","PG":"PGK","TL":"USD","SB":"SBD","VU":"VUV","WS":"WST",
 "TO":"TOP","KI":"AUD","IN":"INR","PK":"PKR","BD":"BDT","NP":"NPR","LK":"LKR","AF":"AFN",
 "BT":"BTN","MV":"MVR","UA":"UAH","TR":"TRY","GE":"GEL","AM":"AMD","AZ":"AZN","MD":"MDL",
 "RS":"RSD","BA":"BAM","AL":"ALL","MK":"MKD","XK":"EUR","KG":"KGS","TJ":"TJS","UZ":"UZS",
 "KZ":"KZT","RO":"RON","BG":"BGN","HR":"EUR","MX":"MXN","BR":"BRL","CO":"COP","GT":"GTQ",
 "HN":"HNL","SV":"USD","NI":"NIO","CR":"CRC","PA":"PAB","DO":"DOP","HT":"HTG","JM":"JMD",
 "TT":"TTD","GY":"GYD","SR":"SRD","EC":"USD","PE":"PEN","BO":"BOB","PY":"PYG","UY":"UYU",
 "AR":"ARS","CL":"CLP","CU":"CUP","BZ":"BZD","EG":"EGP","MA":"MAD","TN":"TND","DZ":"DZD",
 "JO":"JOD","LB":"LBP","IQ":"IQD","YE":"YER","SY":"SYP","PS":"ILS","SD":"SDG","LY":"LYD",
 "NG":"NGN","KE":"KES","GH":"GHS","ZA":"ZAR","TZ":"TZS","UG":"UGX","RW":"RWF","ET":"ETB",
 "SN":"XOF","CI":"XOF","CM":"XAF","ZW":"ZWL","ZM":"ZMW","MW":"MWK","MZ":"MZN","MG":"MGA",
 "ML":"XOF","BF":"XOF","NE":"XOF","TD":"XAF","CD":"CDF","CG":"XAF","AO":"AOA","SO":"SOS",
 "SS":"SSP","LR":"LRD","SL":"SLE","GM":"GMD","GN":"GNF","TG":"XOF","BJ":"XOF","MR":"MRU",
 "BW":"BWP","NA":"NAD","LS":"LSL","SZ":"SZL","BI":"BIF","ER":"ERN",
}

out = []
for code, en, zh, reg, adj in C:
    r = REGION[reg]
    trad = round(max(3.0, r["trad"] + adj), 1)
    dig  = round(max(1.5, r["dig"] + adj * 0.5), 1)
    out.append({"c": code, "en": en, "n": zh, "r": r["zh"], "trad": trad, "dig": dig,
                "cur": CUR.get(code, "USD"), "rate": None})

json.dump(out, open("/tmp/corridors.json", "w"), ensure_ascii=False, indent=1)
print(f"生成 {len(out)} 条走廊")
regs = {}
for c in out:
    regs[c["r"]] = regs.get(c["r"], 0) + 1
for k, v in regs.items():
    print(f"  {k}: {v}")
