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
import pymysql
from bs4 import BeautifulSoup

from user import read_user_config
from utils import login, logout, save_file, headers

requests.adapters.DEFAULT_RETRIES = 5  # 增加重连次数
s = requests.session()
s.keep_alive = False  # 关闭多余连接

# 每次下载的间隔时间0.1秒，这个时间间隔请根据具体情况灵活调整
interva_time = 0.1

threadLock = threading.Lock()

# sid_queue = queue.Queue()


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
    # conn = sqlite3.connect('test.db')
    conn = pymysql.connect("localhost","root","123456","icpc")
    c = conn.cursor()
    # c.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='sids';")
    # table_num = c.fetchone()[0]
    # if table_num < 1:
    c.execute("drop table if exists sids")
    c.execute(''' create table sids (
             sid int primary key not null ,
             uid char(50) not null,
             pid int not null ,
             result char(20) not null ,
             memory int not null ,
             time int not null ,
             language char(20) not null ,
             length int not null ,
             submit_time datetime  not null 
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
    isFirstPage = True
    conn = pymysql.connect("localhost", "root", "123456", "icpc")

    # earlest_time = time.mktime(time.strptime("2011-01-17 20:48:07", "%Y-%m-%d %H:%M:%S"))
    earlest_time =  "2018-02-16 00:00:00"

    while flag1:
        
        cursor = conn.cursor()
        page = requests.get(url=url + "/status.php?top=" + top_sid,
                            cookies=cookies, headers=headers)
        soup = BeautifulSoup(page.content, 'lxml')
        sids = []
        for trr in soup.find_all('tr', class_={"evenrow", "oddrow"}):
            lst = trr.find_all('td')
            content = {}
            content["sid"] = lst[0].string
            content["uid"] = lst[1].find('a').string
            content["pid"] = lst[2].find('div').find('a').string
            content["result"] = result_convert(lst[3].find('span')['result'])
            if lst[4].find('div') == None:
                content["memory"] = "-1"
                content["time"] = "-1"
                content["language"] = "-1"
                content["length"] = "-1"
            else:
                content["memory"] = lst[4].find('div').string
                content["time"] = lst[5].find('div').string
                if lst[6].find('a') == None:
                    content["language"] = lst[6].string
                else:
                    content["language"] = lst[6].find('a').string
                content["length"] = lst[7].string[0:-2]

            content["submit_time"] = lst[8].string
            # content["datetime"] = time.mktime(time.strptime(lst[8].string, "%Y-%m-%d %H:%M:%S"))
            sids.append(content)
            print(content)
            print()

        if len(sids) > 0:
            if isFirstPage == True:
                isFirstPage = False
            else:
                sids.remove(sids[0])
        if len(sids) > 0:
            for content in sids:
                # sid_queue.put(content)
                # current_time = time.mktime(time.strptime(content["datetime"], "%Y-%m-%d %H:%M:%S"))

                if content["submit_time"] < earlest_time :
                    flag1 = False
                    break
                try:
                    cursor.execute("insert into sids(sid,uid,pid,result,memory,time,language,length,submit_time) values (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                                (content["sid"],content["uid"],content["pid"],content["result"],content["memory"],content["time"],content["language"],content["length"],content["submit_time"]) )
                except :
                    print("database insert error")
            top_sid = sids[-1]["sid"]
        else:
            flag1 = False
        cursor.close()
        conn.commit()
    conn.close()

def main():

    # create_table()

    users = read_user_config("./config.json")
    for user in users:
        cookies = login(user.url, user.user_id, user.user_password)
        print("cookies=", cookies)
        get_sids(user.url, user.user_id, cookies)
        logout(user.url, cookies)




if __name__ == '__main__':
    main()
