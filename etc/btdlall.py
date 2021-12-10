import sys
import os
import os.path
import re
import time
import lhafile
import traceback
import datetime
import urllib.request
import pandas as pd
from sklearn.preprocessing import StandardScaler,MinMaxScaler
from sklearn.model_selection import train_test_split
from bs4 import BeautifulSoup

burl = "https://www.boatrace.jp/owpc/pc/race/beforeinfo?rno={0}&jcd={1}&hd={2}"
wreg1 = re.compile(r"weather.*is-wind([0-9]+)")
wreg2 = re.compile(r"([0-9]+).*")

ksavfile = downdir + "/k{0}{1:02}{2:02}.lzh"
kurlbase = "http://www1.mbrace.or.jp/od2/K/{0}{1:02}/"

bsavfile = downdir + "/b{0}{1:02}{2:02}.lzh"
burlbase = "http://www1.mbrace.or.jp/od2/B/{0}{1:02}/"

kssign = "STARTK"
kesign = "FINALK"
kreg1 = re.compile(r"^([0-9]+)KBGN$")
kreg2 = re.compile(r"^([0-9]+)KEND$")
kreg3 = re.compile(r"^[ ]+([0-9]+)R[ ]+([^ ]+)[ ]+H([0-9]+)m[ ]+([^ ]+)[ ]+風[ ]+([^ ]+)[ ]+([-.0-9]+)m[ ]+波[^ ]*[ ]+([-.0-9]+)cm$")
kreg4 = re.compile(r"^[ ]+([0-9]+)[ ]+([1-6])[ ]+([0-9]+)[ ]+([^ ]+)[ ]+([0-9]+)[ ]+([0-9]+)[ ]+([.0-9]+)[ ]+([0-9]+)[ ]+([.0-9]+)[ ]+([.0-9]+)$")
# kreg5 = re.compile(r"^[ ]+([^-. 0-9]+)[ ]+([-0-9]+)[ ]+([0-9]+)[ ]*$")
# kreg6 = re.compile(r"^[ ]+([^-. 0-9]+)[ ]+([-0-9]+)[ ]+([0-9]+)[ ]+([-0-9]+)[ ]+([0-9]+)[ ]*$")
# kreg7 = re.compile(r"^[ ]+([^-. 0-9]+)[ ]+([-0-9]+)[ ]+([0-9]+)[ ]+([^-. 0-9]+)[ ]+([0-9]+)[ ]*$")
# kreg8 = re.compile(r"^[ ]+([-0-9]+)[ ]+([0-9]+)[ ]+([^ ]+)[ ]+([0-9]+)[ ]*$")

bssign = "STARTB"
besign = "FINALB"
breg1 = re.compile(r"^([0-9]+)BBGN$")
breg2 = re.compile(r"^([0-9]+)BEND$")
breg3 = re.compile(r"^[ ]+([0-9]+)R[ ]+([^ ]+)[ ]+H([0-9]+)m.*$")
breg4 = re.compile(r"^[ ]*([1-6])[ ]+([0-9]{4})([^-. 0-9]{1,4})([0-9]{2})([^-. 0-9]{1,2})([0-9]{2})([A-Z0-9]{2})[ ]+([.0-9]+)[ ]+([.0-9]+)[ ]+([.0-9]+)[ ]+([.0-9]+)[ ]+([0-9]+)[ ]+([.0-9]+)[ ]+([0-9]+)[ ]+([.0-9]+)[ ]+(.*)$")

svlfmt = "{0} qid:{1} 1:{2} 2:{3} 3:{4} 4:{5} 5:{6} 6:{7} 7:{8} 8:{9} 9:{10} 10:{11} 11:{12} 12:{13} 13:{14} 14:{15} 15:{16} 16:{17} 17:{18} 18:{19} 19:{20} 20:{21} 21:{22} 22:{23}"

ZEN = "".join(chr(0xff01 + i) for i in range(94)) + "　"
HAN = "".join(chr(0x21 + i) for i in range(94)) + " "
ZEN2HAN = str.maketrans(ZEN, HAN)
RANKLABEL = [v for v in range(5, -1, -1)]
WINDLABEL = ["北","北北東","北東","東北東","東","東南東","南東","南南東","南","南南西","南西","西南西","西","西北西","北西","北北西","無風"]

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

    def to_list(self):
        lst = []
        for curse in self.curses:
            row = [ curse.ranking, self.ids, self.place, self.number, self.kinds, \
                    self.around, self.weather, self.wind_direction, self.wind, self.wave, \
                    curse.number, curse.mortor, curse.boat, curse.racer.id, curse.racer.age, \
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
        self.ranking = -1

    def set_ranking(self, ranking):
        self.ranking = ranking

    def set_number(self, number):
        self.number = number

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
    for y in range(1998, 2021):
        sty = str(y)
        for m in range(1, 12):
            for d in range(1, 31):
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
        urllib.request.urlretrieve(url, sav)
        if os.path.isfile(sav):
            lzhf = lhafile.Lhafile(sav)
            info = lzhf.infolist()
            name = info[0].filename
            txtf = os.path.join(ddir, name)
            open(txtf, "w").write(lzhf.read(name))
            os.remove(sav)
            return True
    except:
        traceback.print_exc()
    return False

def parse_all(ddir):
    races_all = []
    datalst = os.listdir(ddir)
    for filename in datalist:
        if filename.lower().endswith("txt"):
            bfilepath = os.path.join(ddir, "B" + filename[1:])
            kfilepath = os.path.join(ddir, "K" + filename[1:])
            races = parse_bfile(bfilepath)
            if races:
                parse_kfile(kfilepath, races)
                races_all.append(races)
                print("file: {0}, {1} --> Done".format(bfilepath, kfilepath))
    return races_all

def parse_bfile(filepath):
    filename = os.path.basename(filepath)
    filepref = os.path.splitext(filename)[0]
    races = []
    start = False
    plcode = None
    race = None
    with open(filepath, "r", encoding="shift_jis") as f:
        for line in iter(f.readline, ""):
            hline = line.translate(ZEN2HAN)
            if hline.find(bssign) >= 0:
                start = True
            elif hline.find(besign) >= 0:
                start = False
            elif start:
                matched = breg1.match(hline)
                if matched:
                    plcode = to_number(matched.group(1))
                    continue
                matched = breg2.match(hline)
                if matched:
                    plcode = -1
                    continue
                if plcode > 0:
                    matched = breg3.match(hline)
                    if matched:
                        rnum = to_number(matched.group(1))
                        rids = filepref[1:] + str(plcode) + str(rnum)
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
                            age = to_number(matched.group(4))
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
    return races

def parse_kfile(filepath, races):

    if not races:
        return

    filename = os.path.basename(filepath)
    filepref = os.path.splitext(filename)[0]
    start = False
    plcode = 0
    race = None
    with open(filepath, "r", encoding="shift_jis") as f:
        for line in iter(f.readline, ""):
            if line.find(kssign) >= 0:
                start = True
            elif line.find(kesign) >= 0:
                start = False
            elif start:
                matched = kreg1.match(line)
                if matched:
                    plcode = to_number(matched.group(1))
                    continue
                matched = kreg2.match(line)
                if matched:
                    plcode = -1
                    continue
                if plcode > 0:
                    matched = kreg3.match(line)
                    if matched:
                        rnum = to_number(matched.group(1))
                        rids = filepref[1:] + str(plcode) + str(rnum)
                        race = [v for _, v in enumerate(races) if v.ids == rids]
                        if race:
                            weather = matched.group(4)
                            wdir = matched.group(5)
                            wind = to_number(matched.group(6))
                            wave = to_number(matched.group(7))
                            race[0].set_weather(weather, wdir, wind, wave)
                        continue
                    if race:
                        matched = kreg4.match(line)
                        if matched:
                            res = to_number(matched.group(1), True)
                            if res <= 6 and res >= 1:
                                num = to_number(matched.group(2))
                                ids = matched.group(3)
                                curse = [v for _, v in enumerate(race.curses) if v.racer.ids == ids]
                                if curse:
                                    if curse.number != num:
                                        curse[0].set_number(num)
                                    curse[0].set_ranking(res)

def get_weather(races):

    if not races:
        return

    today = datetime.date.today().strftime("%Y%m%d")

    weather = ""
    wind = ""
    wind_direction = ""
    wave = ""

    for race in races:
        time.sleep(1)
        url = burl.format(race.number, race.place, today)
        try:
            response = urllib.request.urlopen(url)
            content = response.read()
            response.close()
            html = content.decode()
            soup = BeautifulSoup(html, "lxml")
            weather_div = soup.find("div", class="weather1_bodyUnit is-weather")
            if weather_div:
                label_div = weather_div.find("div", class="weather1_bodyUnitLabel")
                if label_div:
                    data_span = label_div.find("span", class="weather1_bodyUnitLabelTitle")
                    if data_span:
                        weather = data_span.text
            winddir_div = soup.find("div", class="weather1_bodyUnit is-windDirection")
            if winddir_div:
                image_p = winddir_div.find("p")
                if image_p:
                    clstxt = image_p.attrs["class"]
                    matched = wreg1.match(clstxt)
                    if matched:
                        num = to_number(matched.group(1))
                        if num >= 1 and num <= 17:
                            wind_direction = WINDLABEL[num - 1]
            wind_div = soup.find("div", class="weather1_bodyUnit is-wind")
            if wind_div:
                label_div = weather_div.find("div", class="weather1_bodyUnitLabel")
                if label_div:
                    data_span = label_div.find("span", class="weather1_bodyUnitLabelData")
                    if data_span:
                        matched = wreg2.match(data_span.text)
                        if matched:
                            wind = to_number(matched.group(1))
            wave_div = soup.find("div", class="weather1_bodyUnit is-wave")
            if wave_div:
                label_div = weather_div.find("div", class="weather1_bodyUnitLabel")
                if label_div:
                    data_span = label_div.find("span", class="weather1_bodyUnitLabelData")
                    if data_span:
                        matched = wreg2.match(data_span.text)
                        if matched:
                            wave = to_number(matched.group(1))

            race.set_weather(weather, wind_direction, wind, wave)

        except:
            traceback.print_exc()

def gen_datatable(races, sdir = None):
    if not races:
        return

    table = []
    for race in races:
        lst = race.to_list()
        if lst:
            table.append(lst)

    # 0:curse.ranking        :reverse
    change_ranking(table, 0)
    # 1:self.ids             :
    # 2:self.place           :one hot
    change_one_hot(table, 2, sdir)
    # 3:self.number          :one hot
    change_one_hot(table, 3, sdir)
    # 4:self.kinds           :one hot
    change_one_hot(table, 4, sdir)
    # 5:self.around          :scale
    change_scale(table, 5)
    # 6:self.weather         :one hot
    change_one_hot(table, 6, sdir)
    # 7:self.wind_direction  :one hot
    # change_one_hot(table, 7, sdir)
    for tg in table:
        for row in tg:
            idx = WINDLABEL.index(row[7])
            if idx >= 0:
                row[7] = gen_one_hot_vec(idx, 17)
    # 8:self.wind            :scale
    change_scale(table, 8)
    # 9:self.wave            :scale
    change_scale(table, 9)
    # 10:curse.number        :one hot
    change_one_hot(table, 10, sdir)
    # 11:curse.mortor        :scale
    change_scale(table, 11)
    # 12:curse.boat          :scale
    change_scale(table, 12)
    # 13:curse.racer.id      :one hot
    change_one_hot(table, 13, sdir)
    # 14:curse.racer.age     :one hot
    change_one_hot(table, 14, sdir)
    # 15:curse.racer.weight  :one hot
    change_one_hot(table, 15, sdir)
    # 16:curse.racer.base    :one hot
    change_one_hot(table, 16, sdir)
    # 17:curse.racer.group   :one hot
    change_one_hot(table, 17, sdir)
    # 18:curse.racer.rate1   :scale
    change_scale(table, 18)
    # 19:curse.racer.rate2   :scale
    change_scale(table, 19)
    # 20:curse.racer.rate3   :scale
    change_scale(table, 20)
    # 21:curse.racer.rate4   :scale
    change_scale(table, 21)
    # 22:curse.racer.report  :each reverse
    change_grade(table, 22)
    # 23:curse.racer.other   :one hot
    change_one_hot(table, 23, sdir)

    return table

def create_train_file(table, sdir):

    if not table:
        return

    train1, test = train_test_split(table, test_size = 0.15)
    train2, valid = train_test_split(train1, test_size = len(test))

    test_file = os.path.join(sdir, "test.txt")
    if os.path.isfile(test_file):
        os.remove(test_file)
    train1_file = os.path.join(sdir, "train1.txt")
    if os.path.isfile(train1_file):
        os.remove(train1_file)
    train2_file = os.path.join(sdir, "train2.txt")
    if os.path.isfile(train2_file):
        os.remove(train2_file)
    valid_file = os.path.join(sdir, "valid.txt")
    if os.path.isfile(valid_file):
        os.remove(valid_file)
    save_file(test, test_file)
    save_file(train1, train1_file)
    save_file(train2, train2_file)
    save_file(valid, valid_file)

def save_file(table, filepath):
    with open(filepath, "wt") as f:
        for tg in table:
            for row in table:
                f.write(svlfmt.format(*row) + os.linesep)

def to_number(st, integer = False):
    try:
        if integer:
            return int(st)
        else:
            return float(st)
    except:
        return -1

def change_one_hot(table, num, sdir):
    filepath = os.path.join(sdir, str(num) + ".dat")
    grps = None
    if os.path.isfile(filepath):
        grps = load_one_hot_group(filepath)
    if not grps:
        cols = [row[num] for tg in table for row in tg]
        grps = list(set(cols))
        save_one_hot_group(grps, filepath)
    if grps:
        grps.sort()
        maxl = len(grps)
        for tg in table:
            for row in tg:
                col = row[num]
                idx = grps.index(col)
                row[num] = gen_one_hot_vec(idx, maxl)

def save_one_hot_group(groups, filepath):
    with open(filepath, "wt", encoding = "utf_8") as f:
        f.write(os.linesep.join(groups))

def load_one_hot_group(filepath):
    groups = []
    with open(filepath, "rt", encoding = "utf_8") as f:
        for line in f.readlines():
            data = line.strip()
            if data:
                groups.append(data)
    return groups

def gen_one_hot_vec(idx, length):
    vec = []
    for i in range(length):
        if i == idx:
            vec.append(1.0)
        else:
            vec.append(0.0)
    return vec

def change_scale(table, num):
    cols = [row[num] for tg in table for row in tg]
    mmsc = MinMaxScaler()
    newcols = mmsc.fit_transform(cols)
    i = 0
    for tg in table:
        for row in tg:
            table[i][num] = newcols[i]
            i += 1

def change_ranking(table, num):
    for tg in table:
        for row in tg:
            ranking = row[num]
            if ranking >= 1 and ranking <= 6:
                row[num] = RANKLABEL[ranking - 1]
            else:
                row[num] = 0

def change_grade(table, num):
    for tg in table:
        for row in tg:
            ranking = row[num]
            for i, v in enumerate(ranking):
                if v >= 1 and v <= 6:
                    ranking[i] = RANKLABEL[v - 1] / 6.0
                else:
                    ranking[i] = 0

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
                    burl = burlbase.format(sty, m) + ksav
                    time.sleep(1)
                    print("url: {0}, sav: {1}".format(burl, bsav))
                    download(burl, bsav, ddir)

def run():

    if len(sys.argv) <= 1:
        return

    downall = False
    gentrain = False
    genpdict = False
    idir = downdir
    odir = outdir
    rnum = 0
    pnum = ""

    i = 1
    while i < len(sys.argv):
        v = sys.argv[i]
        if v == "-d":
            downall = True
        elif v == "-t":
            gentrain = True
        elif v == "-p":
            genpdict = True
        elif v == "-i":
            if i + 1 == len(sys.argv):
                return
            idir = sys.argv[i + 1]
            i += 1
        elif v == "-o":
            if i + 1 == len(sys.argv):
                return
            odir = sys.argv[i + 1]
            i += 1
        elif v == "-pr":
            if i + 1 == len(sys.argv):
                return
            rnum = to_number(sys.argv[i + 1])
            i += 1
        elif v == "-pp":
            if i + 1 == len(sys.argv):
                return
            pnum = sys.argv[i + 1]
            i += 1
        i += 1

    if downall:
        download_all_test(idir)

    if gentrain:
        races = parse_all(idir)
        if races:
            create_train_file(gen_datatable(races), odir)

    if genpdict and rnum > 0 and pnum:
        today = datetime.date.today() 
        y1 = today.strftime("%Y")
        y2 = today.strftime("%y")
        m = today.strftime("%m")
        d = today.strftime("%d")
        bsav = bsavfile.format(y2, m, d)
        bsavpath = os.path.join(idir, bsav)
        if not os.path.isfile(bsavpath):
            burl = burlbase.format(y1, m) + bsav
            download(burl, bsav, idir)
        if os.path.isfile(basvpath):
            races = parse_bfile(bsavpath)
            if races:
                race = [v for v in races if v.place == pnum and v.number == rnum]
                if race:
                    get_weather(race)
                    svfile = os.path.join(odir, "predict.txt")
                    if os.path.isfile(svfile):
                        os.remove(svfile)
                    save_file(gen_datatable(race[0].to_list(), odir), svfile)

if __name__ == '__main__':
    run()

