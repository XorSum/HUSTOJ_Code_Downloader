import os
import threading
import time
import requests
import codecs
import queue

from bs4 import BeautifulSoup

from user import read_user_config
import utils


class Producer(threading.Thread):

    def __init__(self, submit_queue, url, user_id, cookies):
        threading.Thread.__init__(self)
        self.submit_queue = submit_queue
        self.url = url
        self.user_id = user_id
        self.cookies = cookies
        self.start()

    def run(self):
        top_sid = "-1"
        isEnd = False
        isFirstPage = True
        while isEnd == False:
            page = requests.get(url=self.url + "/status.php", params={"user_id": self.user_id, "top": top_sid},
                                cookies=self.cookies, headers=utils.headers)
            soup = BeautifulSoup(page.content, 'lxml')
            submits = []
            for row in soup.find_all('tr', class_={"evenrow", "oddrow"}):
                cols = row.find_all('td')
                submit = {}
                submit["sid"] = cols[0].string
                submit["uid"] = cols[1].find('a').string
                submit["pid"] = cols[2].find('div').find('a').string
                submit["result"] = utils.result_convert(cols[3].find('span')['result'])
                if cols[4].find('div') == None:
                    submit["memory"] = "?"
                    submit["time"] = "?"
                    submit["language"] = "?"
                    submit["length"] = "?"
                else:
                    submit["memory"] = cols[4].find('div').string
                    submit["time"] = cols[5].find('div').string
                    if cols[6].find('a') == None:
                        submit["language"] = cols[6].string
                    else:
                        submit["language"] = cols[6].find('a').string
                    submit["length"] = cols[7].string[0:-2]
                submit["submit_time"] = cols[8].string
                submits.append(submit)

            if len(submits) > 0:  # 如果不是首页，则需要去除重复的第一项
                if isFirstPage == True:
                    isFirstPage = False
                else:
                    submits.remove(submits[0])

            if len(submits) > 0:
                for submit in submits:
                    self.submit_queue.put(submit)
                    # print("producer", submit)
                top_sid = submits[-1]["sid"]
            else:  # 没爬到数据，则结束
                self.submit_queue.put("produceDone") # 队列中置入毒丸
                isEnd = True
            # time.sleep(interva_time)


class Customer(threading.Thread):

    def __init__(self, submit_queue, url, dir, cookies):
        threading.Thread.__init__(self)
        self.submit_queue = submit_queue
        self.url = url
        self.cookies = cookies
        self.dir = dir
        self.start()

    def run(self):
        while True:
            try:
                submit = self.submit_queue.get(block=True,timeout=1)
                if submit == "produceDone":
                    self.submit_queue.put("produceDone")
                    break
                    # 取到毒丸则向队列中置入毒丸并结束
                else :
                    code = self.get_code(submit)
                    self.save_code(submit, code)
                    print(submit)
            except Exception as e:
                print(repr(e))
            # time.sleep(interva_time)

    def get_code(self, submit):
        page = requests.get(url=self.url + "/showsource.php?id=" + submit["sid"], cookies=self.cookies, headers=utils.headers)
        soup = BeautifulSoup(page.content, 'lxml')
        if soup.find('pre') == None:
            code = ""
            print("no code")
        else:
            code = soup.find('pre').string
        return code

    def save_code(self, submit, code):
        if not os.path.exists(self.dir):
            os.mkdir(self.dir)
        problem_dir = self.dir + "/" + submit["pid"] + "/"
        if not os.path.exists(problem_dir):
            os.mkdir(problem_dir)
        file_path = problem_dir + submit["sid"] + "-" + submit["result"]
        if submit["language"] == "C++":
            file_path = file_path + ".cpp"
        elif submit["language"] == "C":
            file_path = file_path + ".c"
        elif submit["language"] == "Java":
            file_path = file_path + ".java"
        else:
            file_path = file_path + ".txt"
        with codecs.open(file_path, "w", "utf-8") as f:
            f.write(code)
            f.close()


def main():
    requests.adapters.DEFAULT_RETRIES = 5  # 增加重连次数
    s = requests.session()
    s.keep_alive = False  # 关闭多余连接
    users = read_user_config("./config.json")
    for user in users:
        cookies = utils.login(user.url, user.user_id, user.user_password)
        print("cookies=", cookies)
        submit_queue = queue.Queue()
        producer = Producer(submit_queue, user.url, user.user_id, cookies)
        time.sleep(0.3)
        customers = []
        for i in range(10):
            customers.append( Customer(submit_queue, user.url, user.dir, cookies) )
        producer.join()
        for customer in customers:
            customer.join()
        utils.logout(user.url, cookies)
    print("download complete")

if __name__ == '__main__':
    main()
