from unittest import TestCase
from main import *

class TestMain(TestCase):
    url = "http://exam.upc.edu.cn/"

    def test_save_file(self):
        save_file("../code",123,456,"py","123456")

    def test_login(self):
        cookies = login(self.url,"WC011","cprimer")
        print(cookies)
        logout(self.url,cookies)

    def test_read_user_config(self):
        users = read_user_config("../config.json")
        for user in users:
            print(user)

    def testDownLoad(self):
        cookies = login(self.url, "WC011", "cprimer")
        page = download(self.url+"/running.php",cookies)
        print(page)
        logout(self.url, cookies)

    def testGetPid(self):
        cookies = login(self.url, "WC011", "cprimer")
        pids = get_pids(self.url,"WC011", cookies)
        print(pids)
        logout(self.url, cookies)
