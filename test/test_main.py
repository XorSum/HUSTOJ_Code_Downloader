from unittest import TestCase
from main import *

class TestMain(TestCase):
    url = "http://exam.upc.edu.cn/"
    user_name = "WC011"
    user_password = "cprimer"


    def test_save_file(self):
        save_file("../code",123,456,"py","123456")

    def test_login(self):
        cookies = login(self.url,self.user_name,self.user_password)
        print(cookies)
        logout(self.url,cookies)

    def test_read_user_config(self):
        users = read_user_config("../config.json")
        for user in users:
            print(user)

    def testDownLoad(self):
        cookies = login(self.url, self.user_name, self.user_password)
        page = download(self.url+"/running.php",cookies)
        print(page)
        logout(self.url, cookies)

    def testGetPid(self):
        cookies = login(self.url, self.user_name, self.user_password)
        pids = get_pids(self.url,self.user_name, cookies)
        print(pids)
        logout(self.url, cookies)

    def testget_sids_by_uid_and_pid(self):
        cookies = login(self.url, self.user_name, self.user_password)
        sids = get_sids_by_uid_and_pid(self.url,self.user_name,"9458",cookies)
        print(sids)
        logout(self.url, cookies)

    def test_get_code_by_sid(self):
        cookies = login(self.url, self.user_name, self.user_password)
        codes = get_code_by_sid(self.url,472557,cookies)
        print(codes)
        logout(self.url, cookies)
