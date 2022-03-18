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
from pickle import dump, load
import sklearn.datasets
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from bs4 import BeautifulSoup

burl = "https://www.boatrace.jp/owpc/pc/race/beforeinfo?rno={0}&jcd={1:02}&hd={2}"
wreg1 = re.compile(r".*is-wind([0-9]+)")
wreg2 = re.compile(r"([0-9]+).*")

rurl = "https://www.boatrace.jp/owpc/pc/data/racersearch/season?toban={0}"
rreg1 = re.compile(r"([0-9]+).*")

ourl = "https://www.boatrace.jp/owpc/pc/race/oddstf?rno={0}&jcd={1:02}&hd={2}"
surl = "https://www.boatrace.jp/owpc/pc/race/raceresult?rno={0}&jcd={1:02}&hd={2}"

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
kreg9 = re.compile(r"^[ ]+３連単[ 　]+[-1-6]+[ 　]+([0-9]+)")

bssign = "STARTB"
besign = "FINALB"
breg1 = re.compile(r"^([0-9]+)BBGN$")
breg2 = re.compile(r"^([0-9]+)BEND$")
breg3 = re.compile(r"^[ ]*([0-9]+)R[ ]+(.+)[ ]+H([0-9]+)m[ ]+[^0-9]+([0-9]+):([0-9]+)[ ]*$")
breg4 = re.compile(r"^[ ]*([1-6])[ ]+([0-9]{4})([^-. 0-9]{4})([0-9]{2})([^-. 0-9]{2})([0-9]{2})([A-Z0-9]{2})([. 0-9]{5})([. 0-9]{6})([. 0-9]{5})([. 0-9]{6})([ 0-9]{3})([. 0-9]{6})([ 0-9]{3})([. 0-9]{6})(.*)$")

csvhead = ["rank", "id", "place", "race_number", "race_type", "weather", "wind_direction", "wind", "wave", "curse_number", "mortor", "boat", "start_time", "exhibition_time", "racer_id", "racer_age", "racer_weight", "racer_base", "racer_grade", "racer_rate1", "racer_rate2", "racer_rate3", "racer_rate4", "recent_battle_record1", "recent_battle_record2", "recent_battle_record3", "recent_battle_record4", "recent_battle_record5", "recent_battle_record6", "recent_battle_record7", "recent_battle_record8", "recent_battle_record9", "recent_battle_record10", "recent_battle_record11", "recent_battle_record12", "racer_other_participation", "dividend"]

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

    def __init__(self, ids, place, kinds, number, around, hour, minute):
        self.ids = ids 
        self.place = place
        self.kinds = kinds
        self.number = number
        self.around = around
        self.hour = hour
        self.minute = minute
        self.weather = 0
        self.wind_direction = 0
        self.wind = 0
        self.wave = 0
        self.curses = [] 
        self.dividend = 0

    def set_weather(self, weather, wind_direction, wind, wave):
        self.weather = weather
        self.wind_direction = wind_direction
        self.wind = wind
        self.wave = wave

    def append_curse(self, curse):
        self.curses.append(curse)

    def set_dividend(self, dividend):
        self.dividend = dividend

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
                    curse.racer.other, self.dividend ]
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
                download_at(y, m, d, ddir)

def download_kfile(y, m, d, ddir):
    if not os.path.exists(ddir):
        # print("dir: {0} --> Not found.".format(ddir))
        return None
    sty = str(y)
    ktxt = ktxtfile.format(sty[2:], m, d)
    ktxtpath = os.path.join(ddir, ktxt)
    ksav = ksavfile.format(sty[2:], m, d)
    kurl = kurlbase.format(sty, m) + ksav
    if os.path.isfile(ktxtpath):
        # print("url: {0}, sav: {1} --> EXISTS".format(kurl, ksav))
        return ktxtpath
    if download(kurl, ksav, ddir):
        # print("url: {0}, sav: {1} --> OK".format(kurl, ksav))
        return ktxtpath
    else:
        # print("url: {0}, sav: {1} --> NG".format(kurl, ksav))
        return None

def download_bfile(y, m, d, ddir):
    if not os.path.exists(ddir):
        # print("dir: {0} --> Not found.".format(ddir))
        return None
    sty = str(y)
    btxt = btxtfile.format(sty[2:], m, d)
    btxtpath = os.path.join(ddir, btxt)
    bsav = bsavfile.format(sty[2:], m, d)
    burl = burlbase.format(sty, m) + bsav
    if os.path.isfile(btxtpath):
        # print("url: {0}, sav: {1} --> EXISTS".format(burl, bsav))
        return btxtpath
    if download(burl, bsav, ddir):
        # print("url: {0}, sav: {1} --> OK".format(burl, bsav))
        return btxtpath
    else:
        # print("url: {0}, sav: {1} --> NG".format(burl, bsav))
        return None

def download_at(y, m, d, ddir):
    if download_kfile(y, m, d, ddir):
        if download_bfile(y, m, d, ddir):
            return True
    return False

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
                # print("file: {0}, {1}".format(bfilepath, kfilepath))
                races = parse_bfile(bfilepath)
                if races:
                    parse_kfile(kfilepath, races)
                    races_all.extend(races)
                    # print("  --> Done".format(bfilepath, kfilepath))
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
                        rids = "1" + filepref[1:] + str(plcode).zfill(3) + str(rnum).zfill(3)
                        kinds = matched.group(2)
                        around = matched.group(3)
                        hour = to_number(matched.group(4), True)
                        minute = to_number(matched.group(5), True)
                        race = Race(rids, plcode, kinds, rnum, around, hour, minute)
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
                        rids = "1" + filepref[1:] + str(plcode).zfill(3) + str(rnum).zfill(3)
                        race = [v for _, v in enumerate(races) if v.ids == rids]
                        if race:
                            weather = matched.group(4)
                            wdir = matched.group(5)
                            wind = to_number(matched.group(6))
                            wave = to_number(matched.group(7))
                            race[0].set_weather(weather, wdir, wind, wave)
                        else:
                            # print("===========================")
                            # print(rids)
                            # print("---")
                            # for racetmp in races:
                                # print(racetmp.ids)
                            # print("===========================")
                            pass
                        continue
                    if race:
                        matched = kreg4.match(line)
                        matched2 = kreg4_2.match(line)
                        matched3 = kreg9.match(line)
                        # if not matched and matched2:
                            # print(line)
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
                        if matched3:
                            dividend = to_number(matched3.group(1), True)
                            if dividend > 0:
                                race[0].set_dividend(dividend)

def get_last_info(races):

    rslt = []

    if not races:
        return rslt

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
                                    num_span = st_div.find("span", class_=lambda value: value and value.startswith("table1_boatImage1Number"))
                                    tme_span = st_div.find("span", class_=lambda value: value and value.startswith("table1_boatImage1Time"))
                                    if tme_span and num_span:
                                        stt = to_number(tme_span.text)
                                        num = to_number(num_span.text, True)
                                        if num >= 1 and num <= 6:
                                            web_start_time[num - 1] = stt
                                            web_curse_number[num - 1] = i + 1

        except Exception:
            import traceback; traceback.print_exc()
            print("Error!: {0}_{1}".format(race.place, race.number))
        
        print("get result {0}_{1}".format(race.place, race.number))
        print("---")
        print("weather={0}, wind_dir={1}, wind={2}, wave={3}".format(web_weather, web_wind_direction, web_wind, web_wave))
        print(web_start_time)
        print(web_exhibition_time)
        print("---")
        
        if not web_weather or not web_wind_direction or web_wind < 0 or web_wave < 0:
            rslt.append(False)
            continue

        race.set_weather(web_weather, web_wind_direction, web_wind, web_wave)
        invalid = []
        for i, curse in enumerate(race.curses):
            num = to_number(curse.number, True)
            if len(web_curse_number) >= num and web_curse_number[num - 1] > 0:
                curse.set_number(web_curse_number[num - 1])
            elif not i in invalid:
                invalid.append(i)
            if len(web_start_time) >= num and len(web_exhibition_time) >= num:
                mean_st_info = get_start_time(curse.racer.ids)
                if mean_st_info and mean_st_info[0] >= 0:
                    mean_st = mean_st_info[0]
                    if web_start_time[num - 1] - mean_st_info[0] > 0.1:
                        mean_st += 0.03
                    elif web_start_time[num - 1] - mean_st_info[0] < -0.1:
                        mean_st -= 0.03
                    if mean_st_info[1] >= 2:
                        mean_st += 0.06
                    elif mean_st_info[1] >= 1:
                        mean_st += 0.03
                    curse.set_time(round(mean_st, 3), web_exhibition_time[num - 1])
                elif web_start_time[num - 1] > 0:
                    curse.set_time(web_start_time[num - 1], web_exhibition_time[num - 1])
                else:
                    curse.set_time(0.3, web_exhibition_time[num - 1])
            elif not i in invalid:
                invalid.append(i)

        if len(invalid) <= 3:
            invalid.reverse()
            for i in invalid:
                del(race.curses[i])
        rslt.append(True)
    return rslt

def get_start_time(racer_number):
    st = -1
    ft = -1
    url = rurl.format(racer_number)
    try:
        with urllib.request.urlopen(url) as response:
            response = urllib.request.urlopen(url)
            content = response.read()
            html = content.decode()
            soup = BeautifulSoup(html, "lxml")
            main_div = soup.find("div", class_="l-mainWrap is-type3")
            if main_div:
                table =  main_div.find("table", class_="is-w832")
                if table:
                    tbody_all = table.findAll("tbody")
                    if tbody_all and len(tbody_all) >= 4:
                        td_all = tbody_all[3].findAll("td")
                        if td_all and len(td_all) >= 2:
                            st = to_number(td_all[0].text)
                            matched = rreg1.match(td_all[1].text)
                            if matched:
                                ft = to_number(matched.group(1), True)
    except Exception:
        print("Error!: cannot get a start time of {0}.".format(racer_number))
        
    return st, ft
    
def to_table(races, predict = False):
    if not races:
        return
    table = []
    for race in races:
        lst = race.to_list(predict)
        if lst:
            table.append(lst)
            # if len(lst) < 6:
                # print(lst[0][1])
    return table

def normalize(df, dir_scale, scale_load = False):

    if not os.path.exists(dir_scale):
        os.mkdir(dir_scale)

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
    df["wind"] = standardization(df[["wind"]], os.path.join(dir_scale, "wind_scale.pkl"), scale_load)
    # 8:self.wave            :scale
    df["wave"] = standardization(df[["wave"]], os.path.join(dir_scale, "wave_scale.pkl"), scale_load)
    # 9:curse.number        :one hot
    df["curse_number"] = df["curse_number"].apply(lambda x: get_vector(x, CSNMLABEL))
    # 10:curse.mortor        :scale
    df["mortor"] = standardization(df[["mortor"]], os.path.join(dir_scale, "mortor_scale.pkl"), scale_load)
    # 11:curse.boat          :scale
    df["boat"] = standardization(df[["boat"]], os.path.join(dir_scale, "boat_scale.pkl"), scale_load)
    # 12:curse.stime         :scale
    df["start_time"] = standardization(df[["start_time"]], os.path.join(dir_scale, "start_time_scale.pkl"), scale_load)
    # 13:curse.extime         :scale
    df["exhibition_time"] = standardization(df[["exhibition_time"]], os.path.join(dir_scale, "exhibition_time_scale.pkl"), scale_load)
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
    df["racer_rate1"] = standardization(df[["racer_rate1"]], os.path.join(dir_scale, "racer_rate1_scale.pkl"), scale_load)
    # 20:curse.racer.rate2   :scale
    df["racer_rate2"] = standardization(df[["racer_rate2"]], os.path.join(dir_scale, "racer_rate2_scale.pkl"), scale_load)
    # 21:curse.racer.rate3   :scale
    df["racer_rate3"] = standardization(df[["racer_rate3"]], os.path.join(dir_scale, "racer_rate3_scale.pkl"), scale_load)
    # 22:curse.racer.rate4   :scale
    df["racer_rate4"] = standardization(df[["racer_rate4"]], os.path.join(dir_scale, "racer_rate4_scale.pkl"), scale_load)
    # 23:curse.racer.report  :each reverse
    btcols = ["recent_battle_record" + str(i + 1) for i in range(12)]
    df[btcols[0]] = df[btcols].apply(calc_condition, axis = 1)
    df[btcols[0]] = standardization(df[[btcols[0]]], os.path.join(dir_scale, "recent_battle_record_scale.pkl"), scale_load)
    df = df.drop(btcols[1:], axis=1)
    # 24:curse.racer.other   :one hot
    df["racer_other_participation"] = df[["racer_other_participation","race_number"]].apply(lambda x: get_vector(calc_status(x), [0, 1, 2]), axis = 1)

    #print("--- Normalized DataFrame ---")
    #print(df)

    return df

def save_file(df, filepath):
    #print("Save File: " + filepath)
    #print("--- Save Target DataFrame(ALL) ---")
    #print(df)
    if "dividend" in df.columns:
        df = df.drop(["dividend"], axis=1)
    X = df.iloc[:,2:].apply(lambda x: flatten(x), axis=1).to_numpy().tolist()
    # print("--- Save Target DataFrame(X) ---")
    # print(X)
    y = df.iloc[:,0].values
    # print("--- Save Target DataFrame(y) ---")
    # print(y)
    qid = df.iloc[:,1].values
    # print("--- Save Target DataFrame(qid) ---")
    # print(qid)
    with open(filepath, "wb") as f:
        sklearn.datasets.dump_svmlight_file(X, y, f, zero_based=False, query_id=qid)
    if os.path.isfile(filepath):
        contents = []
        update = True
        with open(filepath, "rt") as f:
            for line in f.readlines():
                data = line.strip()
                if data.find("188:") < 0:
                    contents.append(data + " 188:0")
                else:
                    contents.append(data)
                    update = False
        if update:
            with open(filepath, "wt") as f:
                f.write("\n".join(contents))

def save_file_as_csv(table, filepath):
    # print("Save File: " + filepath)
    # print("--- Save Target Csv Data ---")
    # print(table)
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
    splited = str(val[0]).strip().split()
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

def standardization(df, pkl_path, scale_load):
    scaler = StandardScaler()
    if scale_load:
        scaler = load(open(pkl_path, "rb"))
    else:
        scaler.fit(df)
        dump(scaler, open(pkl_path, "wb"))
    return scaler.transform(df)

#==============================================================================

def download_past_data_all(src_dir):
    if not src_dir:
        return
    p = pathlib.Path(src_dir)
    if not p.is_absolute():
        src_dir = p.resolve()
    install_url_opener()
    download_all(src_dir)

def generate_train_csv(src_dir, csv_dir):
    races = parse_all(src_dir)
    if races:
        table = to_table(races)
        allcsv = os.path.join(csv_dir, "data.csv")
        if os.path.isfile(allcsv):
            os.remove(allcsv)
        save_file_as_csv(table, allcsv)

def csv_to_svmlight(data_dir):
    p = os.path.join(data_dir, "data.csv")
    if not os.path.isfile(p):
        return
    df_src = pd.read_csv(p)
    df_src_rct = df_src.query('1020000000000 <= id < 1970000000000')
    df_dst_rct = normalize(df_src_rct, os.path.join(data_dir, "scale"))
    df_dst_pt1 = df_dst_rct.query("dividend < 5000")
    df_dst_pt2 = df_dst_rct.query("5000 <= dividend < 10000")
    df_dst_pt3 = df_dst_rct.query("dividend >= 10000")
    for i, df in enumerate([df_dst_rct, df_dst_pt1, df_dst_pt2, df_dst_pt3]):
        pt_dir = os.path.join(data_dir, "pt" + str(i + 1))
        if not os.path.exists(pt_dir):
            os.mkdir(pt_dir)
        fold_dir = os.path.join(pt_dir, "Fold1")
        if not os.path.exists(fold_dir):
            os.mkdir(fold_dir)
        qid = df["id"].drop_duplicates().sample(frac=1).to_numpy()
        train_qid, test_qid = train_test_split(qid, test_size = 0.2)
        df_train = df[df["id"].isin(train_qid)]
        df_test = df[df["id"].isin(test_qid)]
        save_file(df_test, os.path.join(fold_dir, "test.txt"))
        save_file(df_train, os.path.join(fold_dir, "train.txt"))

def get_races_at(year, month, day, download_dir):
    bpath = download_bfile(year, month, day, download_dir)
    if bpath:
        races = parse_bfile(bpath)
        return races
    return None

def is_recommended(race):
    glst = [RCRGLABEL.index(x.racer.group) for x in sorted(race.curses, key=lambda x: x.number) if x.racer.group in RCRGLABEL]
    if glst == sorted(glst):
        return True
    return False

def is_recommended_place(race):
    if race.place in (8, 9, 24):
        return True
    return False

def is_recommended_number(race):
    if race.number in (5, 6, 7, 8, 11, 12):
        return True
    return False

def save_predict_text(race, predict_save_dir, scale_dir):
    if race:
        lst = [race]
        rslt = get_last_info(lst)
        if rslt and rslt[0]:
            datalst = []
            table = to_table(lst, True)
            for tg in table:
                for row in tg:
                    datalst.append(flatten(row))
            df_src = pd.DataFrame(datalst, columns=csvhead)
            df = normalize(df_src, scale_dir, True)
            svfile = os.path.join(predict_save_dir, "predict_.txt")
            if os.path.isfile(svfile):
                os.remove(svfile)
            save_file(df, svfile)
            return svfile
    return None

def get_odds(pcode, rnum, stdt):
    rslt = [0, 0, 0, 0, 0, 0]
    url = ourl.format(rnum, pcode, stdt)
    try:
        with urllib.request.urlopen(url) as response:
            response = urllib.request.urlopen(url)
            content = response.read()
            html = content.decode()
            soup = BeautifulSoup(html, "lxml")
            odds_table = soup.find("table", class_="is-w495")
            if odds_table:
                tbody_all = odds_table.findAll("tbody")
                if tbody_all:
                    for tbody in tbody_all:
                        curse_td = tbody.find("td", class_=lambda value: value and value.startswith("is_fs14"))
                        odds_td = tbody.find("td", class_="oddsPoint")
                        if curse_td and odds_td:
                            curse = to_number(curse_td.text, True)
                            odds = to_number(odds_td.text)
                            if curse >= 1 and curse <= 6 and odds > 0:
                                rslt[curse - 1] = odds
    except:
        pass
    return rslt

def get_race_results(pcode, rnum, stdt):
    rslt = {}
    url = surl.format(rnum, pcode, stdt)
    try:
        with urllib.request.urlopen(url) as response:
            response = urllib.request.urlopen(url)
            content = response.read()
            html = content.decode()
            soup = BeautifulSoup(html, "lxml")
            rslt_table = soup.findAll("table", class_="is-w495")
            if rslt_table and len(rslt_table) >= 2:
                tbody_all = rslt_table[1].findAll("tbody")
                if tbody_all:
                    for tbody in tbody_all:
                        tr = tbody.find("tr")
                        if tr:
                            td_all = tr.findAll("td")
                            if td_all and len(td_all) >= 3:
                                wtyp = td_all[0].text
                                if wtyp:
                                    wtyp = wtyp.strip()
                                wnnr = get_joined_text_in_span(td_all[1])
                                if wnnr:
                                    wnnr = wnnr.strip()
                                back = td_all[2].text
                                if back:
                                    back = back.strip()
                                if not wtyp in rslt.keys():
                                    rslt[wtyp] = [wnnr, back]
    except:
        pass
    return rslt

def get_joined_text_in_span(elem):
    rslt = ""
    span_all = elem.findAll("span")
    if span_all:
        for span in span_all:
            txt = span.text
            if txt:
                txt = txt.strip()
            if txt:
                rslt += txt
    return rslt

