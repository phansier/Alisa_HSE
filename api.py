# coding: utf-8
# Импортирует поддержку UTF-8.
from __future__ import unicode_literals

# Импортируем модули для работы с JSON и логами.
import json
import logging
import datetime

# Импортируем подмодули Flask для запуска веб-сервиса.
# from flask import Flask, request

from ruz import get_lessons, add_months, add_years

debug = False

# app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)


# Задаем параметры приложения Flask.
# @app.route("/", methods=['POST'])
# def main():
#     # Функция получает тело запроса и возвращает ответ.
#     logging.info('Request: %r', request.json)
# 
#     response = {
#         "version": request.json['version'],
#         "session": request.json['session'],
#         "response": {
#             "end_session": False
#         }
#     }
# 
#     handle_dialog(request.json, response)
# 
#     logging.info('Response: %r', response)
# 
#     return json.dumps(
#         response,
#         ensure_ascii=False,
#         indent=2
#     )

# Starter function for Yandex.Cloud.Functions
def handler(event, context):
    response = {
        "version": event['version'],
        "session": event['session'],
        "response": {
            "end_session": False
        }
    }
    handle_dialog(event, response)
    return response


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
    if 'user' in req['session']:
        user_id = req['session']['user']['user_id']
    else:
        user_id = req['session']['user_id']

    if handle_exit(user_id, req, res):
        return
    if handle_logoff(user_id, req, res):
        return
    if handle_help(user_id, req, res):
        return

    stage = 0

    if req['session']['new']:  # or user_id not in sessionStorage:
        # Это новый пользователь.
        # Инициализируем сессию и поприветствуем его.
        debg = "!!!" if debug else "!"

        email = None

        if 'state' in req and 'user' in req['state'] and 'email' in req['state']['user']:
            email = req['state']['user']['email']
        if email is not None:
            res['user_state_update'] = {'email': email}
            hello = f'Привет{debg} Я могу рассказать о твоем расписании занятий в Высшей Школе Экономики. \n ' \
                    f'Ваш email: {email}. На какие даты показать расписание?'
            res['response']['text'] = hello
            res['response']['buttons'] = stage1_buttons
            res['user_state_update'] = {'stage': 2}
            stage = 2
            return

        res['user_state_update'] = {'stage': 0}
        stage = 0

        hello = f'Привет{debg} Я могу рассказать о твоем расписании занятий в Высшей Школе Экономики. \n Но сначала ' \
                f'нам нужно познакомиться. '
        res['response']['text'] = hello
        res['response']['buttons'] = stage0_buttons
        return

    if 'state' in req and 'user' in req['state'] and 'stage' in req['state']['user']:
        stage = req['state']['user']['stage']

    if stage == 0:
        stage0(user_id, req, res)
    elif stage == 1:
        stage1(user_id, req, res)
    elif stage == 2:
        stage2(user_id, req, res)


def handle_exit(user_id, req, res):
    if req['request']['original_utterance'].lower() in [
        'не хочу',
        'нет',
        'не',
        'не сегодня',
    ] or 'nlu' in req['request'] and 'intents' in req['request']['nlu'] and 'no' in req['request']['nlu']['intents']:
        res['response']['text'] = 'Жаль. Приходи еще.'
        res['response']['end_session'] = True
        return True
    return False


def handle_logoff(user_id, req, res):
    if req['request']['original_utterance'].lower() in [
        'выйти',
        'выйди',
    ]:
        get_login_text(user_id, req, res)
        res['user_state_update'] = {'stage': 1}
        res['user_state_update'] = {'email': None}
        return True


def handle_help(user_id, req, res):
    if req['request']['original_utterance'].lower() in [
        'помощь',
        'что ты умеешь?',
        'что ты умеешь',
    ]:
        res['response'][
            'text'] = 'Привет! Я могу рассказать о твоем расписании занятий в Высшей Школе Экономики. \n Но сначала ' \
                      'нам нужно познакомиться. '
        res['response']['end_session'] = True
        return True
    return False


def get_login_text(user_id, req, res):
    if "screen" in req["meta"]["interfaces"]:
        res['response']['text'] = 'Для начала мне нужен твой E-mail, заканчивающийся на @edu.hse.ru'
    else:
        res['response']['text'] = 'Для начала мне нужен твой E-mail, заканчивающийся на @edu.hse.ru. Поговори со ' \
                                  'мной с устройства с клавиатурой. И не перепутай аккаунты. '


def stage0(user_id, req, res):
    # Обрабатываем ответ пользователя.
    if req['request']['original_utterance'].lower() in [
        'давай',
        'ладно',
        'ок',
        'хорошо',
        'ага',
    ] or 'nlu' in req['request'] and 'intents' in req['request']['nlu'] and 'yes' in req['request']['nlu']['intents']:
        # Пользователь согласился, идем на стадию 1.
        res['user_state_update'] = {'stage': 1}

        get_login_text(user_id, req, res)

        if debug:
            res['response']['buttons'] = [
                {
                    "title": "tvtibilov@edu.hse.ru",
                    "hide": True
                }]
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
        res['user_state_update'] = {'email': str(email), 'stage': 2}

        res['response']['text'] = f"Ваш email: {email}. На какие даты показать расписание?"
        res['response']['buttons'] = stage1_buttons
        return

    if 'state' in req and 'user' in req['state'] and 'email' in req['state']['user']:
        email = req['state']['user']['email']
        res['response']['text'] = f"Ваш email: {email}. На какие даты показать расписание?"
        res['response']['buttons'] = stage1_buttons
        return

    if "screen" in req["meta"]["interfaces"]:
        res['response'][
            'text'] = 'Я вас не поняла. Чтобы показать расписание мне нужен твой E-mail, заканчивающийся на @edu.hse.ru'
    else:
        res['response']['text'] = 'Для начала мне нужен твой E-mail, заканчивающийся на @edu.hse.ru. Поговори со ' \
                                  'мной с устройства с клавиатурой. И не перепутай аккаунты. '


stage2_buttons = \
    [
        {
            "title": "А сегодня",
            "hide": True
        },
        {
            "title": "А завтра",
            "hide": True
        },
        {
            "title": "А на неделю",
            "hide": True
        }
    ]


def stage2(user_id, req, res):
    date = try_parse_date(req['request']['nlu']['entities'])
    if 'state' in req and 'user' in req['state'] and 'email' in req['state']['user']:
        email = req['state']['user']['email']
        if date is not None:
            response = get_lessons(email, date, date)
            user_date = req['request']['original_utterance'].title()
            res['response']['text'] = user_date + " " + response
            res['response']['buttons'] = stage2_buttons
            return
        if req['request']['original_utterance'].lower() in [
            'на неделю',
            'а на неделю',
        ]:
            d = datetime.datetime.now()
            start = datetime_format(d)
            d += datetime.timedelta(days=7)
            end = datetime_format(d)
            response = get_lessons(email, start, end)
            res['response']['text'] = response
            res['response']['buttons'] = stage2_buttons[:2]
            return

    res['response']['text'] = 'Я вас не поняла. На какие даты показать расписание?'
    res['response']['buttons'] = stage1_buttons
    return


def try_parse_date(entities):
    date = None
    for i in entities:
        if i["type"] == "YANDEX.DATETIME":
            v = i["value"]
            d = datetime.datetime.now()
            is_relative = False
            day = d.day
            if "day" in v:
                if "day_is_relative" in v and v["day_is_relative"]:
                    is_relative = True
                    d += datetime.timedelta(days=v["day"])
                    day += v["day"]
                else:
                    day = v["day"]
            if day < 10:
                day = f"0{day}"
            month = d.month
            if "month" in v:
                if "month_is_relative" in v and v["month_is_relative"]:
                    is_relative = True
                    d = add_months(d, v["month"])
                    month += v["month"]
                else:
                    month = v["month"]
            if month < 10:
                month = f"0{month}"
            year = d.year
            if "year" in v:
                if "year_is_relative" in v and v["year_is_relative"]:
                    is_relative = True
                    d = add_years(d, v["year"])
                    year += v["year"]
                else:
                    year = v["year"]
            if is_relative:
                month = d.month
                if d.month < 10:
                    month = f"0{month}"
                day = d.day
                if d.day < 10:
                    day = f"0{day}"
                date = f"{d.year}.{month}.{day}"
            else:
                date = f"{year}.{month}.{day}"
    return date


def datetime_format(d):
    day = d.day
    if day < 10:
        day = f"0{day}"
    month = d.month
    if month < 10:
        month = f"0{month}"
    year = d.year
    return f"{year}.{month}.{day}"
