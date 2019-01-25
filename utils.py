import requests


headers = {"Accept": "text/html,application/xhtml+xml,application/xml;",
           "Accept-Encoding": "gzip",
           "Accept-Language": "zh-CN,zh;q=0.8",
           "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36"
           }



def login(url,user_id,user_passworsd):
    res = requests.post(url+"/login.php", data={"user_id": user_id, "password": user_passworsd}, headers=headers)
    return res.cookies.get_dict()

def logout(url,cookies):
    requests.post(url+"/logout.php", headers=headers,cookies=cookies)


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