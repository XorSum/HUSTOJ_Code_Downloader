import codecs
import json


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