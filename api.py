# coding: utf-8
# Импортирует поддержку UTF-8.
from __future__ import unicode_literals

# Импортируем модули для работы с JSON и логами.
import json
import logging

# Импортируем подмодули Flask для запуска веб-сервиса.
from flask import Flask, request

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)

# Хранилище данных о сессиях.
sessionStorage = {}


# Задаем параметры приложения Flask.
@app.route("/", methods=['POST'])
def main():
    # Функция получает тело запроса и возвращает ответ.
    logging.info('Request: %r', request.json)

    response = {
        "version": request.json['version'],
        "session": request.json['session'],
        "response": {
            "end_session": False
        }
    }

    handle_dialog(request.json, response)

    logging.info('Response: %r', response)

    return json.dumps(
        response,
        ensure_ascii=False,
        indent=2
    )

stage0_buttons = \
            [
                {
                    "title": "Давай",
                    "hide": True
                },
                {
                    "title": "Не сегодня",
                    "hide": True
                }
            ]

# Функция для непосредственной обработки диалога.
def handle_dialog(req, res):
    user_id = req['session']['user_id']

    if req['session']['new']:
        # Это новый пользователь.
        # Инициализируем сессию и поприветствуем его.

        sessionStorage[user_id] = {
            'stage': 0
        }
        hello = 'Привет! Я могу рассказать о твоем расписании занятий в Высшей Школе Экономики. \n Но сначала нам нужно познакомиться.'
        res['response']['text'] = hello
        res['response']['buttons'] = stage0_buttons
        return

    if sessionStorage[user_id]['stage'] == 0:
        stage0(user_id, req, res)
    elif sessionStorage[user_id]['stage'] == 1:
        stage1(user_id, req, res)
    elif sessionStorage[user_id]['stage'] == 2:
        stage2(user_id, req, res)
    elif sessionStorage[user_id]['stage'] == 3:
        stage3(user_id, req, res)

    # Обрабатываем ответ пользователя.
    # if req['request']['original_utterance'].lower() in [
    #     'ладно',
    #     'куплю',
    #     'покупаю',
    #     'хорошо',
    # ]:
    #     # Пользователь согласился, прощаемся.
    #     res['response']['text'] = 'Слона можно найти на Яндекс.Маркете!'
    #     return
    #
    # # Если нет, то убеждаем его купить слона!
    # res['response']['text'] = 'Все говорят "%s", а ты купи слона!' % (
    #     req['request']['original_utterance']
    # )
    # res['response']['buttons'] = get_suggests(user_id)


def stage0(user_id, req, res):
    # Обрабатываем ответ пользователя.
    if req['request']['original_utterance'].lower() in [
        'давай',
        'ладно',
        'ок',
        'хорошо',
        'ага',
    ]:
        # Пользователь согласился, идем на стадию 1.
        sessionStorage[user_id] = {
            'stage': 1
        }
        res['response']['text'] = 'Для начала мне нужен твой E-mail, заканчивающийся на @edu.hse.ru'
        return
    if req['request']['original_utterance'].lower() in [
        'не хочу',
        'нет',
        'не',
        'не сегодня',
    ]:
        res['response']['text'] = 'Жаль. Приходи еще.'
        res['response']['end_session'] = True
        return
    # Если нет, то убеждаем его купить слона!
    res['response']['text'] = 'Я вас не поняла'
    res['response']['buttons'] = stage0_buttons
    return

stage1_buttons = \
            [
                {
                    "title": "Сегодня",
                    "hide": True
                },
                {
                    "title": "Завтра",
                    "hide": True
                },
                {
                    "title": "На неделю",
                    "hide": True
                }
            ]


def stage1(user_id, req, res):
    email = req['request']['original_utterance'].lower()

    if str(email).endswith("@edu.hse.ru"):  # todo check email is valid
        sessionStorage[user_id] = {
            'stage': 2,
            'email': str(email)
        }
        res['response']['text'] = f"Ваш email: {email}. На какие даты показать расписание?"
        res['response']['buttons'] = stage1_buttons
        return
    res['response']['text'] = 'Я вас не поняла. Чтобы показать расписание мне нужен твой E-mail, заканчивающийся на @edu.hse.ru'


def stage2(user_id, req, res):
    pass


def stage3(user_id, req, res):
    pass

# # Функция возвращает две подсказки для ответа.
# def get_suggests(user_id):
#     session = sessionStorage[user_id]
#
#     # Выбираем две первые подсказки из массива.
#     suggests = [
#         {'title': suggest, 'hide': True}
#         for suggest in session['suggests'][:2]
#     ]
#
#     # Убираем первую подсказку, чтобы подсказки менялись каждый раз.
#     session['suggests'] = session['suggests'][1:]
#     sessionStorage[user_id] = session
#
#     # Если осталась только одна подсказка, предлагаем подсказку
#     # со ссылкой на Яндекс.Маркет.
#     if len(suggests) < 2:
#         suggests.append({
#             "title": "Ладно",
#             "url": "https://market.yandex.ru/search?text=слон",
#             "hide": True
#         })
#
#     return suggests
