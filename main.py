# @author han777404

import sys
import os
import time
import requests
import re
import codecs
import json

requests.adapters.DEFAULT_RETRIES = 5 # 增加重连次数
s = requests.session()
s.keep_alive = False # 关闭多余连接

# 每次下载的间隔时间0.1秒，这个时间间隔请根据具体情况灵活调整
interva_time = 0.1


headers = {"Accept": "text/html,application/xhtml+xml,application/xml;",
           "Accept-Encoding": "gzip",
           "Accept-Language": "zh-CN,zh;q=0.8",
           "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36"
           }


# 用于匹配题号
pattern_pid = "p\((\d+),\d\);"

# 用于匹配提交记录
pattern_sid = "<tr class='(even|odd)row'><td>(\d+)</td>"

# 用于匹配代码
pattern_codes = {'cpp': '<pre class="brush:c\+\+;">(.*)</pre>',
                 'java': '<pre class="brush:java;">(.*)</pre>',
                 'py': '<pre class="brush:python;">(.*)</pre>',
                 'c': '<pre class="brush:c;">(.*)</pre>'
                 }

def replace(source):
    """ 用于替换html文档中的转义符"""
    entities = {
        ("&quot;", '"'),
        ("&apos;", "'"),
        ("&amp;", "&"),
        ("&lt;", "<"),
        ("&gt;", ">"),
        ("&#039;", "'")
    }
    for first,second in entities:
        source = source.replace(first,second)
    return source


def save_file(root_dir,pid,sid,type,code):
    if not os.path.exists(root_dir):
        os.mkdir(root_dir)
    problem_dir = root_dir + "/" + str(pid) + "/"
    if not os.path.exists(problem_dir):
        os.mkdir(problem_dir)
    file_path = problem_dir+str(sid)+"."+type
    with codecs.open(file_path, "w", "utf-8") as f:
        f.write(code)
        f.close()

def login(url,user_id,user_passworsd):
    res = requests.post(url+"/login.php", data={"user_id": user_id, "password": user_passworsd}, headers=headers)
    return res.cookies.get_dict()

def logout(url,cookies):
    requests.post(url+"/logout.php", headers=headers,cookies=cookies)


def download(url, cookies):
    r = requests.get(url, cookies=cookies, headers=headers)
    return r.content.decode("utf-8")

def get_pids(url,user_id,cookies):
    userinfo = download(url + "/userinfo.php?user=" + user_id, cookies)
    pids = re.findall(pattern_pid, userinfo)
    return pids

def get_sids_by_uid_and_pid(url,user_name,pid,cookies):
    url_status = url + "/status.php?user_id=" + user_name + "&problem_id=" + pid
    status = download(url_status, cookies)
    sids = re.findall(pattern_sid, status)
    return [ i[1] for i in sids]

def get_code_by_sid(url,sid,cookies):
    ans = []
    url_source = url + "/showsource.php?id=" + str(sid)
    html_source = download(url_source,cookies)
    for type in pattern_codes:
        pattern = pattern_codes[type]
        codes = re.findall(pattern, html_source, re.DOTALL)
        for code in codes:
            if re.search("Result: 正确",code)!=None:
                code = replace(code)
                ans.append((code,type))
    if len(ans)>0:
        return ans[0]
    else:
        return None

class User:
    user_id = ""
    user_password = ""
    url= ""
    dir= ""
    def __init__(self, data):
        # print(data)
        self.user_id = data["user_id"]
        self.user_password = data["user_passworsd"]
        self.url = data["url"]
        self.dir = data["dir"]
    def __str__(self):
        return "{'user_id':'"+self.user_id+"','user_passworsd':'"+self.user_password+"','url':'"+self.url+"','dir':'"+self.dir+"'}"


def read_user_config(file_name):
    with codecs.open(file_name, "r", "utf-8") as f:
        config = json.load(f)
        # print(config)
        datas = config["user"]
        users = []
        for data in datas:
            # print(data)
            users.append(User(data))
        return users


def main():
    users = read_user_config("./config.json")
    for user in users:
        cookies = login(user.url,user.user_id,user.user_password)
        pids = get_pids(user.url,user.user_id,cookies)
        for pid in pids:
            sids = get_sids_by_uid_and_pid(user.url,user.user_id,pid,cookies)
            for sid in sids:
                code = get_code_by_sid(user.url,sid,cookies)
                if code!=None:
                    save_file(user.dir,pid,sid,code[1],code[0])
                    print("saved",pid,sid)
                time.sleep(interva_time)
        logout(user.url,cookies)
if __name__ == '__main__':
    main()
