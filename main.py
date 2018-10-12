# @author han777404

import sys
import os
import time
import requests
import re
import codecs
import json

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


class HtmlReplace:
    """ 用于替换html文档中的转义符"""
    entities = {
        ("&quot;",'"'),
        ("&apos;","'"),
        ("&amp;","&"),
        ("&lt;","<"),
        ("&gt;",">"),
        ("&#039;","'")
    }

    def replace(self,source):
        for first,second in self.entities:
            source = source.replace(first,second)
        return source

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
    pass
    # # 读取配置
    # user=User()
    # user.read("config.json")
    #
    # print(user.user_id,user.user_password,user.url,user.dir)
    #
    # # 创建文件夹
    # if not os.path.exists(user.dir):
    #     os.mkdir(user.dir)
    # cookies = login( user.url + "/login.php",user.user_id,user.user_password)
    # # 在用户信息页获取已通过的题号
    # userinfo = download(user.url + "/userinfo.php?user="+user.user_id, cookies)
    # pids = re.findall(pattern_pid, userinfo)
    # print("您总共AC了"+str(len(pids))+"道题")
    # print("pid  sid")
    # problemNum=0
    # submitNum=0
    #
    # for pid in pids:
    #     # print("正在下载第" + pid + "题")
    #     # 获取提交记录
    #     url_status = user.url + "/status.php?user_id=" + user.user_id + "&problem_id=" + pid
    #     status = download(url_status, cookies)
    #     sids = re.findall(pattern_sid, status)
    #     # 每个题目放在一个文件夹里
    #     dir_save = user.dir + "/" + str(pid) + "/"
    #     if not os.path.exists(dir_save):
    #         os.mkdir(dir_save)
    #         problemNum=problemNum+1
    #     for sid in sids:
    #         print(pid+" "+sid)
    #         url_source = user.url + "/showsource.php?id=" + sid
    #         # url_source =  url+"/submitpage.php?id="+pid+"&sid="+sid
    #         source = download(url_source, cookies)
    #
    #             filename = dir_save + "/" + sid + ".cpp"
    #             if os.path.isfile(filename):
    #                 continue
    #             source = re.findall(pattern_code,source,re.DOTALL)
    #         # print(code)
    #         for code in source:
    #             submitNum = submitNum + 1
    #             code = HtmlReplace.Replace(code)
    #             # 保存
    #             with codecs.open(filename, "w", "utf-8") as f:
    #                 f.write(code)
    #                 f.close()
    #                 # print("已下载第" + sid + "次提交")
    #             time.sleep(interva_time)
    # print("下载完成,更新了"+str(problemNum)+"道新题,下载了"+str(submitNum)+"份代码")


if __name__ == '__main__':
    main()
