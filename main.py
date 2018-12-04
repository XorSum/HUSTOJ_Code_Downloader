# @author han777404
import sqlite3
import sys
import os
import threading
import time
import requests
import re
import codecs
import json
import queue
from bs4 import BeautifulSoup

from user import read_user_config
from utils import login, logout, save_file, headers

requests.adapters.DEFAULT_RETRIES = 5  # 增加重连次数
s = requests.session()
s.keep_alive = False  # 关闭多余连接

# 每次下载的间隔时间0.1秒，这个时间间隔请根据具体情况灵活调整
interva_time = 0.1

threadLock = threading.Lock()

sid_queue = queue.Queue()


def result_convert(num):
    con = {
        "-1": "All",
        "0": "waiting",
        "1": "rejudging",
        "2": "compiling",
        "3": "running",
        "4": "AC",
        "5": "PE",
        "6": "WA",
        "7": "TLE",
        "8": "MLE",
        "9": "OLE",
        "10": "RE",
        "11": "CE"
    }
    return con[num]

def create_table():
    conn = sqlite3.connect('test.db')
    c = conn.cursor()
    c.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='sids';")
    table_num = c.fetchone()[0]
    if table_num < 1:
        c.execute(''' create table sids (
                 sid int primary key not null ,
                 pid int not null ,
                 result char(20) not null ,
                 memory int not null ,
                 time int not null ,
                 language char(20) not null ,
                 length int not null ,
                 date_time datetime  not null 
              );''')
    #     print("create table")
    # else:
    #     print("already have")
    c.close()
    conn.commit()
    conn.close()




def get_sids(url, user_id, cookies):
    top_sid = "-1"
    flag1 = True
    flag2 = True

    while flag1:
        conn = sqlite3.connect('test.db')
        cursor = conn.cursor()
        page = requests.get(url=url + "/status.php?user_id=" + user_id + "&top=" + top_sid,
                            cookies=cookies, headers=headers)
        soup = BeautifulSoup(page.content, 'lxml')
        sids = []
        for trr in soup.find_all('tr', class_={"evenrow", "oddrow"}):
            lst = trr.find_all('td')
            content = {}
            content["sid"] = lst[0].string
            content["pid"] = lst[2].find('div').find('a').string
            content["result"] = result_convert(lst[3].find('span')['result'])
            content["memory"] = lst[4].find('div').string
            content["time"] = lst[5].find('div').string
            content["language"] = lst[6].find('a').string
            content["length"] = lst[7].string[0:-2]
            content["datetime"] = lst[8].string
            # content["datetime"] = time.mktime(time.strptime(lst[8].string, "%Y-%m-%d %H:%M:%S"))
            sids.append(content)
            print(content)
            print()

        if len(sids) > 0:
            if flag2:
                flag2 = False
            else:
                sids.remove(sids[0])
        if len(sids) > 0:
            for content in sids:
                sid_queue.put(content)
                cursor.execute("insert into sids values (?,?,?,?,?,?,?,?)",
                               (content["sid"],content["pid"],content["result"],content["memory"],content["time"],content["language"],content["length"],content["datetime"]) )
            top_sid = sids[-1]["sid"]
        else:
            flag1 = False
        cursor.close()
        conn.commit()
        conn.close()

def main():

    create_table()

    users = read_user_config("./config.json")
    for user in users:
        cookies = login(user.url, user.user_id, user.user_password)
        print("cookies=", cookies)
        get_sids(user.url, user.user_id, cookies)
        logout(user.url, cookies)




if __name__ == '__main__':
    main()
