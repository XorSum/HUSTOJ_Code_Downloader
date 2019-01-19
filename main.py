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


def get_sids(url, user_id, cookies):
    top_sid = "-1"
    isEnd = False
    isFirstPage = True
    while isEnd == False:
        page = requests.get(url=url + "/status.php", params={"user_id": user_id, "top": top_sid},
                            cookies=cookies, headers=headers)
        soup = BeautifulSoup(page.content, 'lxml')
        submits = []
        for row in soup.find_all('tr', class_={"evenrow", "oddrow"}):
            cols = row.find_all('td')
            submit = {}
            submit["sid"] = cols[0].string
            submit["uid"] = cols[1].find('a').string
            submit["pid"] = cols[2].find('div').find('a').string
            submit["result"] = result_convert(cols[3].find('span')['result'])
            if cols[4].find('div') == None:
                submit["memory"] = "-1"
                submit["time"] = "-1"
                submit["language"] = "-1"
                submit["length"] = "-1"
            else:
                submit["memory"] = cols[4].find('div').string
                submit["time"] = cols[5].find('div').string
                if cols[6].find('a') == None:
                    submit["language"] = cols[6].string
                else:
                    submit["language"] = cols[6].find('a').string
                submit["length"] = cols[7].string[0:-2]

            submit["submit_time"] = cols[8].string
            # submit["datetime"] = time.mktime(time.strptime(cols[8].string, "%Y-%m-%d %H:%M:%S"))
            submits.append(submit)
            print(submit)
        if len(submits) > 0: # 如果不是首页，则需要去除重复的第一项
            if isFirstPage == True:
                isFirstPage = False
            else:
                submits.remove(submits[0])

        if len(submits) > 0:
            sid_queue.put(submits)
            top_sid = submits[-1]["sid"]
        else:   # 没爬到数据，则结束
            isEnd = True


def main():
    users = read_user_config("./config.json")
    for user in users:
        cookies = login(user.url, user.user_id, user.user_password)
        print("cookies=", cookies)
        get_sids(user.url, user.user_id, cookies)


        logout(user.url, cookies)


if __name__ == '__main__':
    main()
