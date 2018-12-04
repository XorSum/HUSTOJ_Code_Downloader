import codecs
import os
import requests


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
