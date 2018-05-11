# @author han777404

import os
import time
import requests
import re
import codecs


# 账号
user_id=""

# 密码
user_passworsd=""

# OJ网址
url = ""

# 存放代码的文件夹
dir = ".\\code\\"

# 每次下载的间隔时间0.1秒，这个时间间隔请根据具体情况灵活调整
interva_time = 0.1


url_login=url + "/login.php"
url_userinfo=url + "/userinfo.php?user="+user_id

headers = {"Accept": "text/html,application/xhtml+xml,application/xml;",
           "Accept-Encoding": "gzip",
           "Accept-Language": "zh-CN,zh;q=0.8",
           "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36"
           }

# 用于匹配题号
pattern_pid = "p\((\d+),\d\);"

# 用于匹配提交记录
pattern_sid = "<tr class='evenrow'><td>(\d+)</td>"

def login():
    res = requests.post(url_login, data={"user_id": user_id, "password": user_passworsd}, headers=headers)
    return res.cookies.get_dict()

def download(url,cookies):
    r=requests.get(url,cookies=cookies,headers=headers)
    return r.content.decode("utf-8")

def main():
    # 创建文件夹
    if not os.path.exists(dir):
        os.mkdir(dir)
    cookies=login()
    # 在用户信息页获取已通过的题号
    userinfo = download(url_userinfo,cookies)
    pids = re.findall(pattern_pid,userinfo)
    for pid in pids:
        print("正在下载第"+pid+"题")
        # 获取提交记录
        url_status = url + "/status.php?user_id=" + user_id + "&problem_id=" + pid
        status = download(url_status,cookies)
        sids = re.findall(pattern_sid,status)
        for sid in sids:
            # 获取代码
            url_source = url + "/showsource.php?id="+sid
            # url_source =  url+"/submitpage.php?id="+pid+"&sid="+sid
            source = download(url_source,cookies)
            # 每个题目放在一个文件夹里
            dir_save = dir +"\\" + str(pid)+"\\"
            if not os.path.exists(dir_save):
                os.mkdir(dir_save)
            # 保存
            filename = dir_save +"\\" + sid + ".html"
            with codecs.open(filename, "w", "utf-8") as f:
                f.write(source)
                f.close()
            print("已下载第"+sid+"次提交")
            time.sleep(interva_time)

if __name__ == '__main__':
    main()