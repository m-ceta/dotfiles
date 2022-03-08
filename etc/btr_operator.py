# -*- coding: utf-8 -*-
import os
import os.path
import sys
import re
import time
import datetime
import schedule
import numpy as np
import pandas as pd
from contextlib import redirect_stdout
from selenium import webdriver
import btdlall
import btranking

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

dir_bt = "~/"
dir_data = os.path.join(dir_bt, "rdata/")
dir_src = os.path.join(dir_bt, "src/")
dir_json = os.path.join(dir_bt, "json/")
dir_out = os.path.join(dir_bt, "out/")
dir_param = os.path.join(dir_bt, "param/")
dir_pred = os.path.join(dir_bt, "pred/")
dir_scale = os.path.join(dir_data, "scale")
model_save_path = os.path.join(os.path.join(dir_param, "pt2"), "net_params.pkl")

debug = False
vali_k = 3
cutoffs = [1, 3, 6]
epochs = 5
batch_size = 1
cuda = None
layers = 3
model_name = "RankMSE"

PLCODE_MAP = {'23': '唐津', '20': '若松', '17': '宮島', '16': '児島', '12': '住之江', '09': '津', '08': '常滑', '07': '蒲郡', '06': '浜名湖', '04': '平和島', '02': '戸田', '22': '福岡', '18': '徳山', '11': '琵琶湖', '10': '三国', '05': '多摩川', '03': '江戸川', '01': '桐生', '24': '大村', '19': '下関', '15': '丸亀', '14': '鳴門', '21': '芦屋', '13': '尼崎'}

def init():
    dt = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
    with redirect_stdout(open(os.devnull, 'w')):
        races = btdlall.get_races_at(dt.year, dt.month, dt.day, dir_src)
        for race in races:
            dtr = datetime.datetime(dt.year, dt.month, dt.day, race.hour, race.minute, 0, 0)
            if dt >= dtr:
                continue
            dtr2 = dtr - datetime.timedelta(minutes = 10)
            schedule.every().day.at(dtr2.strftime("%H:%M")).do(predict_and_buy, race=race).tag("btr")

def predict_and_buy(race):
    if not os.path.isfile(model_save_path):
        return
    svfile = btdlall.save_predict_text(race, dir_pred, dir_scale)
    if not os.path.isfile(svfile):
        return
    dt = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
    stdate = dt.strftime("%Y%m%d")
    stdatetime = dt.strftime("%Y%m%d %H:%M")
    pred = btranking.predict(model_name, model_save_path, svfile, dir_json, dir_data, dir_out, \
            vali_k, cutoffs, debug, epochs, batch_size, layers, cuda)
    ranks, sorted_ndcg = get_ranking(pred.to('cpu').detach().numpy().copy())
    d = 1.0 - sorted_ndcg[0] + sorted_ndcg[1]
    if btdlall.is_recommended(race):
        log_output("{0},{1},{2}R,{3}-{4}-{5}".format(stdatetime, PLCODE_MAP[str(race.place).zfill(2)], race.number, ranks[0], ranks[1], ranks[2]), "btr.logs")
    if d < 0 and (btdlall.is_recommended_place(race) or btdlall.is_recommended_number(race)):
        odds = btdlall.get_odds(race, stdate)
        if odds and len(odds) >= ranks[0] and odds[ranks[0] - 1] > 2.0:
            log_output("{0},{1},{2}R,{3}".format(stdatetime, PLCODE_MAP[str(race.place).zfill(2)], race.number, ranks[0]), "btr.logs")
    return schedule.CancelJob()

def clear():
    schedule.clear("btr")

def get_ranking(pred_results):
    sorted_ndcg = np.sort(pred_results[0])[::-1]
    ranks = []
    for val1 in sorted_ndcg:
        rank = -1
        for num, val2 in enumerate(pred_results[0]):
            if val1 == val2:
                rank = num + 1
                break
        ranks.append(rank)
    return ranks, sorted_ndcg

def buy_ticket(pcode, rnum, bet, amount):
    driver = webdriver.Chrome()
    driver.get('https://ib.mbrace.or.jp/')
    time.sleep(5)

    # Login
    form_mno = driver.find_element_by_xpath('//form[@id="loginForm"]//input[@id="memberNo"]')
    form_pin = driver.find_element_by_xpath('//form[@id="loginForm"]//input[@id="pin"]')
    form_ath = driver.find_element_by_xpath('//form[@id="loginForm"]//input[@id="authPassword"]')
    form_btn = driver.find_element_by_xpath('//form[@id="loginForm"]//input[@id="loginButton"]')
    form_mno.send_keys('08211069')
    form_pin.send_keys('0422')
    form_ath.send_keys('fQ4P3C')
    form_btn.click()
    time.sleep(5)

    # Select Place
    form_anc = driver.find_element_by_xpath('//ul[@class="selectBox"]/li[@id="jyo{0}"]/a'.format(rnum))
    form_anc.click()
    time.sleep(5)

    # Select Race

    # Buy

    driver.close()

def log_output(msg, filepath):
    with open(filepath, "at") as f:
        f.write(msg + "\n")

def run():
    schedule.every().day.at("08:00").do(init)
    schedule.every().day.at("21:00").do(clear)
    dt = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
    dt_init = datetime.datetime(dt.year, dt.month, dt.day, 8, 0, 0, 0)
    if dt > dt_init:
        init()
    while True:
        schedule.run_pending()
        time.sleep(10)

if __name__ == '__main__':
    run()

