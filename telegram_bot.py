import requests

class Telegram_Bot:

    def __init__(self, file_name):
        self.token = self.read_token(file_name)
        self.base_url = "https://api.telegram.org/bot{}/".format(self.token)

    def send_message(self, m, chat_id):
        url = self.base_url + "sendMessage?chat_id={}&text={}".format(chat_id, m)
        if m is not None:
            requests.get(url)

    # reading access key from a separate file
    def read_token(self, file_name):
        with open(file_name, "r") as key:
            for token in key:
                return token


