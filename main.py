import joblib
import re
from telegram_bot import Telegram_Bot
from vacancy_transformation import Vacancy
from flask import Flask, request, jsonify
from flask_sslify import SSLify

app = Flask(__name__)
sslify = SSLify(app)

# model building
model = joblib.load('/home/boa00/bot/final_model.sav')
pattern = re.compile(r'hh.ru/vacancy/\d{8}')
error_message = 'Неверный формат. Введите /help для большей информации'
help_message = 'Чтобы получить прогноз по зарплате, нужно ввести "/predict https://hh.ru/vacancy/<vacancy_id>", где vacancy_id - это уникальный код вакансии, состоящий из 8 цифр. Само URL может быть длиннее, но формат обязан оставаться таким'

def predict_salary(vacancy_id):
    v = Vacancy(vacancy_id)
    data = v.transform()
    if data is not None:
        predicted_salary_floor = int(model.predict(data)*0.8)
        predicted_salary_ceiling = int(model.predict(data)*1.2)
        return 'Прогнозируемая зарплата: {}-{} RUB'.format(predicted_salary_floor, predicted_salary_ceiling)
    else:
        return 'Вакансии с таким id не существует'

# replying to messages
def make_reply(message):
    if message is not None:
        if message[:8] == '/predict':
            found = pattern.search(message)
            if found is None:
                return error_message
            vacancy_id = found.group()[-8:]
            reply = predict_salary(vacancy_id)
            return reply
        elif message[:5] == '/help':
            return help_message
        else:
            return error_message

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        r = request.get_json()
        bot = Telegram_Bot('/home/boa00/bot/key.txt')
        message = r['message']['text']
        from_id = r['message']['from']['id']
        reply = make_reply(message)
        if reply is not None:
            bot.send_message(reply, from_id)
        return jsonify(r)
    return '<b>Hello There!</b>'


if __name__ == '__main__':
    app.run()
















