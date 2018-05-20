# @author han777404

import sys
import os
import time
import requests
import re
import codecs
from xml.sax.saxutils import unescape

# 账号
user_id = ""

# 密码
user_passworsd = ""

# OJ网址
url = ""

# 存放代码的文件夹
dir = "./code/"

# 每次下载的间隔时间0.1秒，这个时间间隔请根据具体情况灵活调整
interva_time = 0.1

url_login = url + "/login.php"
url_userinfo = url + "/userinfo.php?user=" + user_id

headers = {"Accept": "text/html,application/xhtml+xml,application/xml;",
           "Accept-Encoding": "gzip",
           "Accept-Language": "zh-CN,zh;q=0.8",
           "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36"
           }

# 用于匹配题号
pattern_pid = "p\((\d+),\d\);"

# 用于匹配提交记录
pattern_sid = "<tr class='evenrow'><td>(\d+)</td>"


pattern_code = '<pre class="brush:c\+\+;">(.*)</pre>'


def login():
    res = requests.post(url_login, data={"user_id": user_id, "password": user_passworsd}, headers=headers)
    return res.cookies.get_dict()


def download(url, cookies):
    r = requests.get(url, cookies=cookies, headers=headers)
    return r.content.decode("utf-8")

entities={
    ("&quot;",'"'),
    ("&apos;","'"),
    ("&amp;","&"),
    ("&lt;","<"),
    ("&gt;",">"),
}

def htmlReplace(source):
    for first,second in entities:
        source = source.replace(first,second)
    return source

class ShowProcess():
    """
    显示处理进度的类
    调用该类相关函数即可实现处理进度的显示
    """
    i = 0 # 当前的处理进度
    max_steps = 0 # 总共需要处理的次数
    max_arrow = 50 #进度条的长度

    # 初始化函数，需要知道总共的处理次数
    def __init__(self, max_steps):
        self.max_steps = max_steps
        self.i = 0

    # 显示函数，根据当前的处理进度i显示进度
    # 效果为[>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>]100.00%
    def show_process(self, i=None):
        if i is not None:
            self.i = i
        else:
            self.i += 1
        num_arrow = int(self.i * self.max_arrow / self.max_steps) #计算显示多少个'>'
        num_line = self.max_arrow - num_arrow #计算显示多少个'-'
        percent = self.i * 100.0 / self.max_steps #计算完成进度，格式为xx.xx%
        process_bar = '[' + '>' * num_arrow + '-' * num_line + ']'\
                      + '%.2f' % percent + '%' + '\r' #带输出的字符串，'\r'表示不换行回到最左边
        sys.stdout.write(process_bar) #这两句打印字符到终端
        sys.stdout.flush()

    def close(self, words='done'):
        print('')
        print(words)
        self.i = 0




def main():
    # 创建文件夹
    if not os.path.exists(dir):
        os.mkdir(dir)
    cookies = login()
    # 在用户信息页获取已通过的题号
    userinfo = download(url_userinfo, cookies)
    pids = re.findall(pattern_pid, userinfo)
    procss_bar = ShowProcess(len(pids)+1)
    print("您总共AC了"+str(len(pids))+"道题")
    problemNum=0
    submitNum=0
    for pid in pids:
        procss_bar.show_process()
        # print("正在下载第" + pid + "题")
        # 获取提交记录
        url_status = url + "/status.php?user_id=" + user_id + "&problem_id=" + pid
        status = download(url_status, cookies)
        sids = re.findall(pattern_sid, status)
        # 每个题目放在一个文件夹里
        dir_save = dir + "/" + str(pid) + "/"
        if not os.path.exists(dir_save):
            os.mkdir(dir_save)
            problemNum=problemNum+1
        for sid in sids:
            filename = dir_save + "/" + sid + ".cpp"
            if os.path.isfile(filename):
                continue
            print(pid+" "+sid)
            # 获取代码
            url_source = url + "/showsource.php?id=" + sid
            # url_source =  url+"/submitpage.php?id="+pid+"&sid="+sid
            source = download(url_source, cookies)
            source = re.findall(pattern_code,source,re.DOTALL)
            # print(code)
            for code in source:
                submitNum = submitNum + 1
                code = htmlReplace(code)
                # 保存
                with codecs.open(filename, "w", "utf-8") as f:
                    f.write(code)
                    f.close()
                    # print("已下载第" + sid + "次提交")
                time.sleep(interva_time)
    print("下载完成,更新了"+str(problemNum)+"道新题,下载了"+str(submitNum)+"份代码")


if __name__ == '__main__':
    main()
