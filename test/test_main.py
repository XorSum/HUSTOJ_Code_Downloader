from unittest import TestCase
from main import *


class TestMain(TestCase):
    url = "http://icpc.upc.edu.cn"
    user_name = "123"
    user_password = "123"


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

