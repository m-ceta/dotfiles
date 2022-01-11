import sys
import os
import os.path
import re
import time
import math
import lhafile
import traceback
import datetime
import pathlib
import codecs
import csv
import urllib.request
import pandas as pd
import numpy as np
import sklearn.datasets
from sklearn.preprocessing import minmax_scale
from sklearn.model_selection import train_test_split
from bs4 import BeautifulSoup

burl = "https://www.boatrace.jp/owpc/pc/race/beforeinfo?rno={0}&jcd={1}&hd={2}"
wreg1 = re.compile(r".*is-wind([0-9]+)")
wreg2 = re.compile(r"([0-9]+).*")

ktxtfile = "K{0}{1:02}{2:02}.TXT"
ksavfile = "k{0}{1:02}{2:02}.lzh"
kurlbase = "http://www1.mbrace.or.jp/od2/K/{0}{1:02}/"

btxtfile = "B{0}{1:02}{2:02}.TXT"
bsavfile = "b{0}{1:02}{2:02}.lzh"
burlbase = "http://www1.mbrace.or.jp/od2/B/{0}{1:02}/"

kssign = "STARTK"
kesign = "FINALK"
kreg1 = re.compile(r"^([0-9]+)KBGN$")
kreg2 = re.compile(r"^([0-9]+)KEND$")
kreg3 = re.compile(r"^[ ]*([0-9]+)R[ ]+([^ ]+)[ ]+H([0-9]+)m[ ]+([^ ]+)[ ]+風[ ]+([^ 0-9]+)[ ]*([-.0-9]+)m[ ]+波[^ 0-9]*[ ]*([-.0-9]+)cm$")
kreg4_2 = re.compile(r"^[ ]*([A-Z0-9]+)[ ]+([1-6])[ ]+([0-9]+)[ ]+([^ ]+)[ ]+([0-9]+)[ ]+([0-9]+)")
kreg4 = re.compile(r"^[ ]*([A-Z0-9]+)[ ]+([1-6])[ ]+([0-9]+)[ ]+([^ ]+)[ ]+([0-9]+)[ ]+([0-9]+)[ ]+([.0-9]+)[ ]+([1-9]+)[ ]+([.0-9]+)")
# kreg4 = re.compile(r"^[ ]*([A-Z0-9]+)[ ]+([1-6])[ ]+([0-9]+)[ ]+([^ ]+)[ ]+([0-9]+)[ ]+([0-9]+)[ ]+([.0-9]+)[ ]+([0-9]+)[ ]+([F.0-9]+)[ ]+([.0-9 ]+)$")
# kreg5 = re.compile(r"^[ ]+([^-. 0-9]+)[ ]+([-0-9]+)[ ]+([0-9]+)[ ]*$")
# kreg6 = re.compile(r"^[ ]+([^-. 0-9]+)[ ]+([-0-9]+)[ ]+([0-9]+)[ ]+([-0-9]+)[ ]+([0-9]+)[ ]*$")
# kreg7 = re.compile(r"^[ ]+([^-. 0-9]+)[ ]+([-0-9]+)[ ]+([0-9]+)[ ]+([^-. 0-9]+)[ ]+([0-9]+)[ ]*$")
# kreg8 = re.compile(r"^[ ]+([-0-9]+)[ ]+([0-9]+)[ ]+([^ ]+)[ ]+([0-9]+)[ ]*$")

bssign = "STARTB"
besign = "FINALB"
breg1 = re.compile(r"^([0-9]+)BBGN$")
breg2 = re.compile(r"^([0-9]+)BEND$")
breg3 = re.compile(r"^[ ]*([0-9]+)R[ ]+(.+)[ ]+H([0-9]+)m.*$")
breg4 = re.compile(r"^[ ]*([1-6])[ ]+([0-9]{4})([^-. 0-9]{4})([0-9]{2})([^-. 0-9]{2})([0-9]{2})([A-Z0-9]{2})([. 0-9]{5})([. 0-9]{6})([. 0-9]{5})([. 0-9]{6})([ 0-9]{3})([. 0-9]{6})([ 0-9]{3})([. 0-9]{6})(.*)$")

csvhead = ["rank", "id", "place", "race_number", "race_type", "weather", "wind_direction", "wind", "wave", "curse_number", "mortor", "boat", "start_time", "exhibition_time", "racer_id", "racer_age", "racer_weight", "racer_base", "racer_grade", "racer_rate1", "racer_rate2", "racer_rate3", "racer_rate4", "recent_battle_record1", "recent_battle_record2", "recent_battle_record3", "recent_battle_record4", "recent_battle_record5", "recent_battle_record6", "recent_battle_record7", "recent_battle_record8", "recent_battle_record9", "recent_battle_record10", "recent_battle_record11", "recent_battle_record12", "racer_other_participation"]

ZEN = "".join(chr(0xff01 + i) for i in range(94)) + "　"
HAN = "".join(chr(0x21 + i) for i in range(94)) + " "
ZEN2HAN = str.maketrans(ZEN, HAN)
RANKLABEL = [v for v in range(5, -1, -1)]
WINDLABEL = ["北","北北東","北東","東北東","東","東南東","南東","南南東","南","南南西","南西","西南西","西","西北西","北西","北北西","無風"]
AGELABEL = [(v, v + 5) for v in range(15, 80, 5)]
WEATHERLABEL = [["晴", "はれ"], ["雨", "あめ"], ["雪", "ゆき"], ["曇", "くもり"], ["霧", "きり"], ["他", "ほか", "た"]]
KINDLABEL = ["予選", "準優", "優勝", "順位決定", "選抜", "一般"]
PLACLABEL = [v for v in range(1, 25)]
RCNMLABEL = [v for v in range(1, 13)]
CSNMLABEL = [v for v in range(1, 7)]
RCRWLABEL = [v for v in range(35, 65)]
RCRBLABEL = ["東京", "香川", "佐賀", "熊本", "広島", "大阪", "愛知", "徳島", "福岡", "静岡", "山口", "岡山", "埼玉", "長崎", "兵庫", "島根", "栃木", "高知", "三重", "千葉", "神奈", "群馬", "和歌", "石川", "滋賀", "京都", "愛媛", "福井", "山梨", "富山", "鹿児", "茨城", "宮崎", "宮城", "大分", "奈良", "岐阜", "沖縄", "北海", "秋田", "青森", "福島", "長野", "新潟", "鳥取"]
RCRGLABEL = ["A1", "A2", "B1", "B2"]
#RACERLABEL = [str(v).zfill(4) for v in range(1, 10000)]

class Race:

    def __init__(self, ids, place, kinds, number, around):
        self.ids = ids 
        self.place = place
        self.kinds = kinds
        self.number = number
        self.around = around
        self.weather = 0
        self.wind_direction = 0
        self.wind = 0
        self.wave = 0
        self.curses = [] 

    def set_weather(self, weather, wind_direction, wind, wave):
        self.weather = weather
        self.wind_direction = wind_direction
        self.wind = wind
        self.wave = wave

    def append_curse(self, curse):
        self.curses.append(curse)

    def to_list(self, predict = False):
        lst = []
        for curse in self.curses:
            if not predict and curse.ranking < 1:
                continue
            row = [ curse.ranking, self.ids, self.place, self.number, self.kinds, \
                    self.weather, self.wind_direction, self.wind, self.wave, curse.number, \
                    curse.mortor, curse.boat, curse.stime, curse.extime, curse.racer.ids, curse.racer.age, \
                    curse.racer.weight, curse.racer.base, curse.racer.group, curse.racer.rate1, \
                    curse.racer.rate2, curse.racer.rate3, curse.racer.rate4, curse.racer.report, \
                    curse.racer.other ]
            lst.append(row)
        return lst

class Curse:

    def __init__(self, number, mortor, boat, racer):
        self.number = number
        self.mortor = mortor
        self.boat = boat
        self.racer = racer
        self.stime = -1
        self.extime = -1
        self.ranking = -1

    def set_ranking(self, ranking):
        self.ranking = ranking

    def set_number(self, number):
        self.number = number

    def set_time(self, stime, extime):
        self.stime = stime
        self.extime = extime

class Racer:

    def __init__(self, ids, name, age, weight, base, group, rate1, rate2, rate3, rate4, report, other):
        self.ids = ids
        self.name = name
        self.age  = age
        self.weight = weight
        self.base = base
        self.group = group
        self.rate1 = rate1
        self.rate2 = rate2
        self.rate3 = rate3
        self.rate4 = rate4
        self.report = report
        self.other = other

def download_all(ddir):
    if not os.path.exists(ddir):
        os.mkdir(ddir)
    for y in range(1997, 2022):
        sty = str(y)
        for m in range(1, 13):
            for d in range(1, 32):
                ktxt = ktxtfile.format(sty[2:], m, d)
                ktxtpath = os.path.join(ddir, ktxt)
                if os.path.isfile(ktxtpath):
                    print("url: {0}, sav: {1} --> EXISTS".format(kurl, ksav))
                    continue
                ksav = ksavfile.format(sty[2:], m, d)
                kurl = kurlbase.format(sty, m) + ksav
                time.sleep(1)
                if download(kurl, ksav, ddir):
                    print("url: {0}, sav: {1} --> OK".format(kurl, ksav))
                    bsav = bsavfile.format(sty[2:], m, d)
                    burl = burlbase.format(sty, m) + bsav
                    time.sleep(1)
                    if download(burl, bsav, ddir):
                        print("url: {0}, sav: {1} --> OK".format(burl, bsav))
                    else:
                        print("url: {0}, sav: {1} --> NG".format(burl, bsav))
                else:
                    print("url: {0}, sav: {1} --> NG".format(kurl, ksav))

def download(url, sav, ddir):
    try:
        filepath = os.path.join(ddir, sav)
        with urllib.request.urlopen(url) as response:
            data = response.read()
            with open(filepath, mode="wb") as f:
                f.write(data)
        if os.path.isfile(filepath):
            lzhf = lhafile.Lhafile(filepath)
            info = lzhf.infolist()
            name = info[0].filename
            txtf = os.path.join(ddir, name)
            with open(txtf, "wb") as f2:
                f2.write(lzhf.read(name))
            lzhf.fp.close()
            os.remove(filepath)
            return True
    except Exception as e:
        print("Download failed: {0}".format(traceback.format_exception_only(type(e), e)[0].rstrip()))
    return False

def install_url_opener():
    proxy1 = os.environ.get("HTTP_PROXY")
    proxy2 = os.environ.get("HTTPS_PROXY")
    if proxy1 or proxy2:
        proxies = {}
        if proxy1:
            proxies["http"] = proxy1
        if proxy2:
            proxies["https"] = proxy2
        proxy_handler = urllib.request.ProxyHandler(proxies)
        opener = urllib.request.build_opener(proxy_handler)
    else:
        opener = urllib.request.build_opener()
    opener.addheaders = [('User-Agent','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36')]
    urllib.request.install_opener(opener)
    return opener

def parse_all(ddir):
    races_all = []
    datalist = os.listdir(ddir)
    for filename in datalist:
        try:
            if filename.startswith("B") and filename.lower().endswith("txt"):
                bfilepath = os.path.join(ddir, "B" + filename[1:])
                kfilepath = os.path.join(ddir, "K" + filename[1:])
                print("file: {0}, {1}".format(bfilepath, kfilepath))
                races = parse_bfile(bfilepath)
                if races:
                    parse_kfile(kfilepath, races)
                    races_all.extend(races)
                    print("  --> Done".format(bfilepath, kfilepath))
        except Exception as e:
            print("Parse failed: {0}".format(traceback.format_exception_only(type(e), e)[0].rstrip()))

    return races_all

def parse_bfile(filepath):
    filename = os.path.basename(filepath)
    filepref = os.path.splitext(filename)[0]
    races = []
    start = False
    plcode = -1 
    race = None
    with codecs.open(filepath, "r", "cp932", "ignore") as f:
        for line in iter(f.readline, ""):
            line = line.rstrip("\r\n")
            hline = line.translate(ZEN2HAN)
            if hline.find(bssign) >= 0:
                start = True
            elif hline.find(besign) >= 0:
                start = False
            elif start:
                matched = breg1.match(hline)
                if matched:
                    plcode = to_number(matched.group(1), True)
                    continue
                matched = breg2.match(hline)
                if matched:
                    plcode = -1
                    continue
                if plcode > 0:
                    matched = breg3.match(hline)
                    if matched:
                        rnum = to_number(matched.group(1), True)
                        rids = filepref[1:] + str(plcode).zfill(3) + str(rnum).zfill(3)
                        kinds = matched.group(2)
                        around = matched.group(3)
                        race = Race(rids, plcode, kinds, rnum, around)
                        races.append(race)
                        continue
                    if race:
                        matched = breg4.match(line)
                        if matched:
                            number = matched.group(1)
                            ids = matched.group(2)
                            name = matched.group(3)
                            age = to_number(matched.group(4), True)
                            base = matched.group(5)
                            weight = to_number(matched.group(6))
                            group = matched.group(7)
                            rate1 = to_number(matched.group(8))
                            rate2 = to_number(matched.group(9))
                            rate3 = to_number(matched.group(10))
                            rate4 = to_number(matched.group(11))
                            mortor = to_number(matched.group(13))
                            boat = to_number(matched.group(15))
                            lest = matched.group(16)
                            other = ""
                            if len(lest) > 12:
                                other = lest[12:].strip()
                            if not other:
                                other = "-"
                            report = [0 for _ in range(12)]
                            i = 0
                            for ch in lest:
                                if i >= 12:
                                    break
                                n = to_number(ch, True)
                                if n > 0:
                                    report[i] = n
                                i += 1
                            racer = Racer(ids, name, age, weight, base, group, rate1, rate2, rate3, rate4, report, other)
                            curse = Curse(number, mortor, boat, racer)
                            race.append_curse(curse)
                        else:
                            if race.ids == "200115023010":
                                #print(line)
                                pass
    return races

def parse_kfile(filepath, races):

    if not races:
        return

    filename = os.path.basename(filepath)
    filepref = os.path.splitext(filename)[0]
    start = False
    plcode = -1 
    race = None
    with codecs.open(filepath, "r", "cp932", "ignore") as f:
        for line in iter(f.readline, ""):
            line = line.rstrip("\r\n")
            if line.find(kssign) >= 0:
                start = True
            elif line.find(kesign) >= 0:
                start = False
            elif start:
                matched = kreg1.match(line)
                if matched:
                    plcode = to_number(matched.group(1), True)
                    continue
                matched = kreg2.match(line)
                if matched:
                    plcode = -1
                    continue
                if plcode > 0:
                    matched = kreg3.match(line)
                    if matched:
                        rnum = to_number(matched.group(1), True)
                        rids = filepref[1:] + str(plcode).zfill(3) + str(rnum).zfill(3)
                        race = [v for _, v in enumerate(races) if v.ids == rids]
                        if race:
                            weather = matched.group(4)
                            wdir = matched.group(5)
                            wind = to_number(matched.group(6))
                            wave = to_number(matched.group(7))
                            race[0].set_weather(weather, wdir, wind, wave)
                        else:
                            print("===========================")
                            print(rids)
                            print("---")
                            for racetmp in races:
                                print(racetmp.ids)
                            print("===========================")
                        continue
                    if race:
                        matched = kreg4.match(line)
                        matched2 = kreg4_2.match(line)
                        if not matched and matched2:
                            print(line)
                        if matched:
                            rkst = matched.group(1)
                            ids = matched.group(3)
                            ext = to_number(matched.group(7))
                            num = to_number(matched.group(8), True)
                            stt = to_number(matched.group(9))
                            curse = [v for _, v in enumerate(race[0].curses) if v.racer.ids == ids]
                            if curse:
                                curse[0].set_time(stt, ext)
                                if curse[0].number != num:
                                    curse[0].set_number(num)
                                res = to_number(rkst, True)
                                if res <= 6 and res >= 1:
                                    curse[0].set_ranking(res)
                                #elif rkst.startswith("F"):
                                #    curse[0].set_ranking(6)
                        else:
                            if race[0].ids == "200115023010":
                                #print(line)
                                pass

def get_last_info(races, weather, wind_direction, wind, wave, curse_number, start_time, exhibition_time):

    if not races:
        return

    today = datetime.date.today().strftime("%Y%m%d")

    for race in races:

        web_weather = ""
        web_wind = -1
        web_wind_direction = ""
        web_wave = -1

        web_curse_number = [0, 0, 0, 0, 0, 0]
        web_start_time = [-10, -10, -10, -10, -10, -10]
        web_exhibition_time = [-10, -10, -10, -10, -10, -10]

        time.sleep(1)
        url = burl.format(race.number, race.place, today)
        try:
            with urllib.request.urlopen(url) as response:
                response = urllib.request.urlopen(url)
                content = response.read()
                html = content.decode()
                soup = BeautifulSoup(html, "lxml")
                weather_div = soup.find("div", class_="weather1_bodyUnit is-weather")
                if weather_div:
                    label_div = weather_div.find("div", class_="weather1_bodyUnitLabel")
                    if label_div:
                        data_span = label_div.find("span", class_="weather1_bodyUnitLabelTitle")
                        if data_span:
                            web_weather = data_span.text
                winddir_div = soup.find("div", class_="weather1_bodyUnit is-windDirection")
                if winddir_div:
                    image_p = winddir_div.find("p")
                    if image_p and image_p.attrs["class"]:
                        clstxt = image_p.attrs["class"][1]
                        matched = wreg1.match(clstxt)
                        if matched:
                            num = to_number(matched.group(1), True)
                            if num >= 1 and num <= 17:
                                web_wind_direction = WINDLABEL[num - 1]
                wind_div = soup.find("div", class_="weather1_bodyUnit is-wind")
                if wind_div:
                    label_div = wind_div.find("div", class_="weather1_bodyUnitLabel")
                    if label_div:
                        data_span = label_div.find("span", class_="weather1_bodyUnitLabelData")
                        if data_span:
                            matched = wreg2.match(data_span.text)
                            if matched:
                                web_wind = to_number(matched.group(1))
                wave_div = soup.find("div", class_="weather1_bodyUnit is-wave")
                if wave_div:
                    label_div = wave_div.find("div", class_="weather1_bodyUnitLabel")
                    if label_div:
                        data_span = label_div.find("span", class_="weather1_bodyUnitLabelData")
                        if data_span:
                            matched = wreg2.match(data_span.text)
                            if matched:
                                web_wave = to_number(matched.group(1))

                info_table = soup.find("table", class_="is-w748")
                if info_table:
                    info_tbody_all = info_table.findAll("tbody", class_="is-fs12")
                    if info_tbody_all:
                        for info_tbody in info_tbody_all:
                            info_row = info_tbody.find("tr")
                            if info_row:
                                info_td_all = info_row.findAll("td")
                                if info_td_all and len(info_td_all) > 4:
                                    num = to_number(info_td_all[0].text, True)
                                    ext = to_number(info_td_all[4].text)
                                    if num >= 1 and num <= 6 and ext >= 0:
                                        web_exhibition_time[num - 1] = ext

                st_table = soup.find("table", class_="is-w238")
                if st_table:
                    st_tbody = st_table.find("tbody", class_="is-p10-0")
                    if st_tbody:
                        st_tr_all = st_tbody.findAll("tr")
                        if st_tr_all:
                            for i, st_tr in enumerate(st_tr_all):
                                st_div = st_tr.find("div", class_="table1_boatImage1")
                                if st_div:
                                    num_span = st_div.find("span", class_="table1_boatImage1Number is-type")
                                    tme_span = st_div.find("span", class_="table1_boatImage1Time")
                                    if tme_span:
                                        stt = to_number(tme_span.text)
                                        num_span1 = st_div.find("span", class_="table1_boatImage1Number is-type1")
                                        if num_span1:
                                            if stt >= 0:
                                                web_start_time[0] = stt
                                            web_curse_number[0] = i + 1
                                        num_span2 = st_div.find("span", class_="table1_boatImage1Number is-type2")
                                        if num_span2:
                                            if stt >= 0:
                                                web_start_time[1] = stt
                                            web_curse_number[1] = i + 1
                                        num_span3 = st_div.find("span", class_="table1_boatImage1Number is-type3")
                                        if num_span3:
                                            if stt >= 0:
                                                web_start_time[2] = stt
                                            web_curse_number[2] = i + 1
                                        num_span4 = st_div.find("span", class_="table1_boatImage1Number is-type4")
                                        if num_span4:
                                            if stt >= 0:
                                                web_start_time[3] = stt
                                            web_curse_number[3] = i + 1
                                        num_span5 = st_div.find("span", class_="table1_boatImage1Number is-type5")
                                        if num_span5:
                                            if stt >= 0:
                                                web_start_time[4] = stt
                                            web_curse_number[4] = i + 1
                                        num_span6 = st_div.find("span", class_="table1_boatImage1Number is-type6")
                                        if num_span6:
                                            if stt >= 0:
                                                web_start_time[5] = stt
                                            web_curse_number[5] = i + 1

        except Exception as e:
            traceback.print_exc()

        if weather >= 0:
            web_weather = weather
        if wind_direction >= 0:
            web_wind_direction = wind_direction
        if wind >= 0:
            web_wind = wind
        if wave >= 0:
            web_wave = wave

        if web_weather < 0 or web_wind_direction < 0 or web_wind < 0 or web_wave < 0:
            return False

        race.set_weather(web_weather, web_wind_direction, web_wind, web_wave)

        for i in range(len(web_curse_number)):
            if len(curse_number) > i and curse_number[i] > 0:
                web_curse_number[i] = curse_number[i]

        for i in range(len(web_start_time)):
            if len(start_time) > i and start_time[i] > 0:
                web_start_time[i] = start_time[i]

        for i in range(len(web_exhibition_time)):
            if len(exhibition_time) > i and exhibition_time[i] > 0:
                web_exhibition_time[i] = exhibition_time[i]

        invalid = []
        for i, curse in enumerate(race.curses):
            num = to_number(curse.number, True)
            if len(web_curse_number) >= num and web_curse_number[num - 1] > 0:
                curse.set_number(web_curse_number[num - 1])
            elif not i in invalid:
                invalid.append(i)
            if len(web_start_time) >= num and web_start_time[num - 1] > 0 \
                    and len(web_exhibition_time) >= num and web_exhibition_time[num - 1] > 0:
                curse.set_time(web_start_time[num - 1], web_exhibition_time[num - 1])
            elif not i in invalid:
                invalid.append(i)
        invalid.reverse()
        for i in invalid:
            del(race.curses[i])

        if len(race.curses) < 4:
            return False

    return True

def to_table(races, predict = False):
    if not races:
        return
    table = []
    for race in races:
        lst = race.to_list(predict)
        if lst:
            table.append(lst)
            if len(lst) < 6:
                print(lst[0][1])
    return table

def normalize(csv_path, sdir):

    if not os.path.isfile(csv_path):
        return
    df = pd.read_csv(csv_path)

    # 0:curse.ranking        :reverse
    df["rank"] = df["rank"].apply(lambda x: RANKLABEL[x - 1] if x >= 1 and x <= 6 else 0)
    # 1:self.ids             :
    # 2:self.place           :one hot
    df["place"] = df["place"].apply(lambda x: get_vector(x, PLACLABEL))
    # 3:self.number          :one hot
    df["race_number"] = df["race_number"].apply(lambda x: get_vector(x, RCNMLABEL))
    # 4:self.kinds           :one hot
    df["race_type"] = df["race_type"].apply(lambda x: get_vector(x, KINDLABEL))
    # 5:self.weather         :one hot
    df["weather"] = df["weather"].apply(lambda x: get_vector(x, WEATHERLABEL))
    # 6:self.wind_direction  :one hot
    df["wind_direction"] = df["wind_direction"].apply(lambda x: get_vector(x, WINDLABEL))
    # 7:self.wind            :scale
    df["wind"] = minmax_scale(df["wind"])
    # 8:self.wave            :scale
    df["wave"] = minmax_scale(df["wave"])
    # 9:curse.number        :one hot
    df["curse_number"] = df["curse_number"].apply(lambda x: get_vector(x, CSNMLABEL))
    # 10:curse.mortor        :scale
    df["mortor"] = minmax_scale(df["mortor"])
    # 11:curse.boat          :scale
    df["boat"] = minmax_scale(df["boat"])
    # 12:curse.stime         :scale
    df["start_time"] = minmax_scale(df["start_time"])
    # 13:curse.extime         :scale
    df["exhibition_time"] = minmax_scale(df["exhibition_time"])
    # 14:curse.racer.ids     :one hot
    # df["racer_id"] = df["racer_id"].apply(lambda x: get_vector(x, RACERLABEL))
    df.drop("racer_id", axis=1)
    # 15:curse.racer.age     :one hot
    df["racer_age"] = df["racer_age"].apply(lambda x: get_vector(x, AGELABEL))
    # 16:curse.racer.weight  :one hot
    df["racer_weight"] = df["racer_weight"].apply(lambda x: get_vector(x, RCRWLABEL))
    # 17:curse.racer.base    :one hot
    df["racer_base"] = df["racer_base"].apply(lambda x: get_vector(x, RCRBLABEL))
    # 18:curse.racer.group   :one hot
    df["racer_grade"] = df["racer_grade"].apply(lambda x: get_vector(x, RCRGLABEL))
    # 19:curse.racer.rate1   :scale
    df["racer_rate1"] = minmax_scale(df["racer_rate1"])
    # 20:curse.racer.rate2   :scale
    df["racer_rate2"] = minmax_scale(df["racer_rate2"])
    # 21:curse.racer.rate3   :scale
    df["racer_rate3"] = minmax_scale(df["racer_rate3"])
    # 22:curse.racer.rate4   :scale
    df["racer_rate4"] = minmax_scale(df["racer_rate4"])
    # 23:curse.racer.report  :each reverse
    btcols = ["recent_battle_record" + str(i + 1) for i in range(12)]
    df[btcols[0]] = minmax_scale(df[btcols].apply(calc_condition, axis = 1))
    df = df.drop(btcols[1:], axis=1)
    # 24:curse.racer.other   :one hot
    df["racer_other_participation"] = df[["racer_other_participation","race_number"]].apply(lambda x: get_vector(calc_status(x), [0, 1, 2]), axis = 1)


    print("--- Normalized DataFrame ---")
    print(df)

    return df

def create_train_file(df_all, sdir):
    for i in range(len(df_all)):
        fold_dir = os.path.join(sdir, "Fold" + str(i + 1))
        if not os.path.exists(fold_dir):
            os.mkdir(fold_dir)
        test_df = df_all[i]
        train_df = pd.concat(df_all[:i] + df_all[i + 1:]).reset_index(drop=True)
        save_file(test_df, os.path.join(fold_dir, "test.txt"))
        save_file(train_df, os.path.join(fold_dir, "train.txt"))

def save_file(df, filepath):
    print("Save File: " + filepath)
    print("--- Save Target DataFrame(ALL) ---")
    print(df)
    X = df.iloc[:,2:].apply(lambda x: flatten(x), axis=1).to_numpy().tolist()
    print("--- Save Target DataFrame(X) ---")
    print(X)
    y = df.iloc[:,0].to_numpy()
    print("--- Save Target DataFrame(y) ---")
    print(y)
    qid = df.iloc[:,1].to_numpy()
    print("--- Save Target DataFrame(qid) ---")
    print(qid)
    with open(filepath, "wb") as f:
        sklearn.datasets.dump_svmlight_file(X, y, f, zero_based=False, query_id=qid)

def save_file_as_csv(table, filepath):
    print("Save File: " + filepath)
    print("--- Save Target Csv Data ---")
    print(table)
    with open(filepath, 'wt', newline="") as f:
        writer = csv.writer(f)
        writer.writerow(csvhead)
        for tg in table:
            for row in tg:
                writer.writerow(flatten(row))

def to_number(st, integer = False):
    try:
        if integer:
            return int(st)
        else:
            return float(st)
    except:
        return -1

def get_vector(val, grp):
    sval = str(val).replace(" ", "").replace("　", "")
    idx = len(grp)
    for i, v in enumerate(grp):
        if type(v) == list:
            found = False
            for vv in v:
                if sval.find(str(vv)) >= 0:
                    found = True
                    break
            if found:
                idx = i
                break
        elif type(v) == tuple:
            if v[0] <= val and v[1] > val:
                idx = i
                break
        else:
            if sval.find(str(v)) >= 0:
                idx = i
                break
    return np.array([1 if x == idx else 0 for x in range(len(grp) + 1)])

def save_one_hot_group(groups, filepath):
    with open(filepath, "wt", encoding = "utf_8") as f:
        f.write("\n".join(groups))

def load_one_hot_group(filepath):
    groups = []
    with open(filepath, "rt", encoding = "utf_8") as f:
        for line in f.readlines():
            data = line.strip()
            if data:
                groups.append(data)
    return groups

def calc_condition(rank_list):
    cond = 0
    for i, v in enumerate(rank_list):
        if v >= 1 and v <= 3:
            cond += (RANKLABEL[v - 1] + 0.0) * (i + 0.0)
    return cond

def calc_status(val):
    status = 0
    splited = val[0].strip().split()
    current = np.where(val[1] == 1)[0][0] + 1
    if current > 0:
        for item in splited:
            if status == 2:
                continue
            if len(item) == 1:
                num = to_number(item, integer = True)
                if current < num:
                    status = 2
                elif 0 < num and num < current:
                    status = 1
            elif len(item) == 2:
                num = to_number(item, integer = True)
                if num > 0 and num <= 12:
                    if current < num:
                        status = 2
                    else:
                        status = 1
                else:
                    num1 = to_number(item[0], integer = True)
                    num2 = to_number(item[1], integer = True)
                    num3 = max(num1, num2)
                    if current < num3:
                        status = 2
                    elif 0 < num3 and num3 < current:
                        status = 1
            else:
                num1 = to_number(item[0], integer = True)
                num2 = to_number(item[1:], integer = True)
                num3 = max(num1, num2)
                if current < num3:
                    status = 2
                elif 0 < num3 and num3 < current:
                    status = 1
    return status

flatten = lambda x: [z for y in x for z in (flatten(y) if hasattr(y, '__iter__') and not isinstance(y, str) else (y,))]

def index_of(lst, target):
    if not lst:
        return -1
    tmp = target.strip()
    for i, itm in enumerate(lst):
        if type(itm) == list or type(itm) == tuple:
            for v in itm:
                if tmp == v:
                    return i
        else:
            if tmp == itm:
                return i
    return -1

#==============================================================================

def download_all_test(ddir):
    if not os.path.exists(ddir):
        os.mkdir(ddir)
    for y in (1998, 2010, 2020):
        sty = str(y)
        for m in (1, 6, 12):
            for d in (1, 15):
                ksav = ksavfile.format(sty[2:], m, d)
                kurl = kurlbase.format(sty, m) + ksav
                time.sleep(1)
                print("url: {0}, sav: {1}".format(kurl, ksav))
                if download(kurl, ksav, ddir):
                    bsav = bsavfile.format(sty[2:], m, d)
                    burl = burlbase.format(sty, m) + bsav
                    time.sleep(1)
                    print("url: {0}, sav: {1}".format(burl, bsav))
                    download(burl, bsav, ddir)

def main(downall = False, gentrain = False, normalize_data = False, genpdict = False, \
        idir = "", odir = "", rnum = 0, pnum = 0, \
        weather = -1, wind = -1, wind_direction = -1, wave = -1, \
        curse = [], stime = [], extime = [], split = 5):

    if idir:
        p = pathlib.Path(idir)
        if not p.is_absolute():
            idir = p.resolve()

    if odir:
        p = pathlib.Path(odir)
        if not p.is_absolute():
            odir = p.resolve()

    if not os.path.exists(idir):
        print("Error: No input directory.")
        return False

    if (gentrain or (genpdict and rnum > 0 and pnum) or normalize_data) and not os.path.exists(odir):
        print("Error: invalid parameter.")
        return False

    install_url_opener()

    if downall:
        download_all(idir)

    if gentrain:
        races = parse_all(idir)
        if races:
            count = len(races)
            step = int(math.floor(count / (split + 0.0)))
            for i in range(split):
                si = int(step * i)
                ei = si + step 
                if i == split - 1:
                    ei = count
                table = to_table(races[si:ei])
                allcsv = os.path.join(odir, "all{0}.csv".format(i + 1))
                if os.path.isfile(allcsv):
                    os.remove(allcsv)
                save_file_as_csv(table, allcsv)

    if normalize_data:
        df_all = []
        for i in range(split):
            allcsv = os.path.join(idir, "all{0}.csv".format(i + 1))
            if os.path.isfile(allcsv):
                df = normalize(allcsv, odir)
                df_all.append(df)
        create_train_file(df_all, odir)

    if genpdict and rnum > 0 and pnum:
        today = datetime.date.today() 
        y1 = today.strftime("%Y")
        y2 = today.strftime("%y")
        m = today.month
        d = today.day
        bsav = bsavfile.format(y2, m, d)
        bsavpath = os.path.join(idir, bsav)
        if not os.path.isfile(bsavpath):
            burl = burlbase.format(y1, m) + bsav
            download(burl, bsav, idir)
        btxt = btxtfile.format(y2, m, d)
        btxtpath = os.path.join(idir, btxt)
        if os.path.isfile(btxtpath):
            races = parse_bfile(btxtpath)
            if races:
                race = [v for v in races if v.place == pnum and v.number == rnum]
                if race:
                    if not get_last_info(race, weather, wind_direction, wind, wave, curse, stime, extime):
                        print("Error: Cannot get last info.")
                        return False
                    table = to_table(race, True)
                    svcsvfile = os.path.join(odir, "predict.csv")
                    if os.path.isfile(svcsvfile):
                        os.remove(svcsvfile)
                    save_file_as_csv(table, svcsvfile)
                    df = normalize(svcsvfile, odir)
                    svfile = os.path.join(odir, "predict.txt")
                    if os.path.isfile(svfile):
                        os.remove(svfile)
                    save_file(df, svfile)

    return True

def run():

    if len(sys.argv) <= 1:
        return

    downall = False
    gentrain = False
    normalize_data = False
    genpdict = False
    idir = ""
    odir = ""
    rnum = 0
    pnum = ""
    weather = -1
    wind = -1
    wind_direction = -1
    wave = -1
    curse = [1, 2, 3, 4, 5, 6]
    stime = [-10, -10, -10, -10, -10, -10]
    extime = [-10, -10, -10, -10, -10, -10]

    i = 1
    while i < len(sys.argv):
        v = sys.argv[i]
        if v == "-d":
            downall = True
        elif v == "-t":
            gentrain = True
        elif v == "-n":
            normalize_data = True
        elif v == "-p":
            genpdict = True
        elif v == "-i":
            if i + 1 == len(sys.argv):
                print("Error: invalid parameter.")
                return
            idir = sys.argv[i + 1]
            i += 1
        elif v == "-o":
            if i + 1 == len(sys.argv):
                print("Error: invalid parameter.")
                return
            odir = sys.argv[i + 1]
            i += 1
        elif v == "-pr":
            if i + 1 == len(sys.argv):
                print("Error: invalid parameter.")
                return
            rnum = to_number(sys.argv[i + 1])
            i += 1
        elif v == "-pp":
            if i + 1 == len(sys.argv):
                print("Error: invalid parameter.")
                return
            pnum = sys.argv[i + 1]
            i += 1
        elif v == "-pwt":
            if i + 1 == len(sys.argv):
                print("Error: invalid parameter.")
                return
            weather = to_number(sys.argv[i + 1], True)
            i += 1
        elif v == "-pwd":
            if i + 1 == len(sys.argv):
                print("Error: invalid parameter.")
                return
            wind = to_number(sys.argv[i + 1])
            i += 1
        elif v == "-pwdd":
            if i + 1 == len(sys.argv):
                print("Error: invalid parameter.")
                return
            wind_direction = to_number(sys.argv[i + 1], True)
            i += 1
        elif v == "-pwv":
            if i + 1 == len(sys.argv):
                print("Error: invalid parameter.")
                return
            wave = to_number(sys.argv[i + 1])
            i += 1
        elif v == "-pc1":
            if i + 1 == len(sys.argv):
                print("Error: invalid parameter.")
                return
            curse[0] = to_number(sys.argv[i + 1], True)
            i += 1
        elif v == "-ps1":
            if i + 1 == len(sys.argv):
                print("Error: invalid parameter.")
                return
            stime[0] = to_number(sys.argv[i + 1])
            i += 1
        elif v == "-pex1":
            if i + 1 == len(sys.argv):
                print("Error: invalid parameter.")
                return
            extime[0] = to_number(sys.argv[i + 1])
            i += 1
        elif v == "-pc2":
            if i + 1 == len(sys.argv):
                print("Error: invalid parameter.")
                return
            curse[1] = to_number(sys.argv[i + 1], True)
            i += 1
        elif v == "-ps2":
            if i + 1 == len(sys.argv):
                print("Error: invalid parameter.")
                return
            stime[1] = to_number(sys.argv[i + 1])
            i += 1
        elif v == "-pex2":
            if i + 1 == len(sys.argv):
                print("Error: invalid parameter.")
                return
            extime[1] = to_number(sys.argv[i + 1])
            i += 1
        elif v == "-pc3":
            if i + 1 == len(sys.argv):
                print("Error: invalid parameter.")
                return
            curse[2] = to_number(sys.argv[i + 1], True)
            i += 1
        elif v == "-ps3":
            if i + 1 == len(sys.argv):
                print("Error: invalid parameter.")
                return
            stime[2] = to_number(sys.argv[i + 1])
            i += 1
        elif v == "-pex3":
            if i + 1 == len(sys.argv):
                print("Error: invalid parameter.")
                return
            extime[2] = to_number(sys.argv[i + 1])
            i += 1
        elif v == "-pc4":
            if i + 1 == len(sys.argv):
                print("Error: invalid parameter.")
                return
            curse[3] = to_number(sys.argv[i + 1], True)
            i += 1
        elif v == "-ps4":
            if i + 1 == len(sys.argv):
                print("Error: invalid parameter.")
                return
            stime[3] = to_number(sys.argv[i + 1])
            i += 1
        elif v == "-pex4":
            if i + 1 == len(sys.argv):
                print("Error: invalid parameter.")
                return
            extime[3] = to_number(sys.argv[i + 1])
            i += 1
        elif v == "-pc5":
            if i + 1 == len(sys.argv):
                print("Error: invalid parameter.")
                return
            curse[4] = to_number(sys.argv[i + 1], True)
            i += 1
        elif v == "-ps5":
            if i + 1 == len(sys.argv):
                print("Error: invalid parameter.")
                return
            stime[4] = to_number(sys.argv[i + 1])
            i += 1
        elif v == "-pex5":
            if i + 1 == len(sys.argv):
                print("Error: invalid parameter.")
                return
            extime[4] = to_number(sys.argv[i + 1])
            i += 1
        elif v == "-pc6":
            if i + 1 == len(sys.argv):
                print("Error: invalid parameter.")
                return
            curse[5] = to_number(sys.argv[i + 1], True)
            i += 1
        elif v == "-ps6":
            if i + 1 == len(sys.argv):
                print("Error: invalid parameter.")
                return
            stime[5] = to_number(sys.argv[i + 1])
            i += 1
        elif v == "-pex6":
            if i + 1 == len(sys.argv):
                print("Error: invalid parameter.")
                return
            extime[5] = to_number(sys.argv[i + 1])
            i += 1
        i += 1

    main(downall, gentrain, normalize_data, genpdict, idir, odir, rnum, pnum, weather, wind, wind_direction, wave, curse, stime, extime)

if __name__ == '__main__':
    run()

