import requests
import json


def pairs(count):
    if count == 0:
        return "нет пар"
    elif count == 1:
        return "будет одна пара:"
    elif 2 <= count <= 4:
        return f"будет {count} пары:"
    elif 5 <= count <= 20:
        return f"будет {count} пар:"


def get_lessons(email, start_date, end_date):
    # response = requests.get(f'http://mlk.hse.ru/mlk-0.5.1/ruz/oldapi/personlessons?fromdate={start_date}&todate={end_date}&email={email}&receivertype=1&language=2')
    response = requests.get(
        f'http://mlk.hse.ru/mlk-0.5.1/ruz/api/schedule/student?start={start_date}&finish={end_date}&email={email}&lng=1')
    resp = json.loads(response.content.decode("utf-8"))
    try:
        count = len(resp)
        res = pairs(count) + "\n"
        for i in resp:
            res += f"{i['discipline']}\n"
        return res
    except TypeError as e:
        return "Не нашла расписания для этого Email"
    except Exception as e:
        return "Сервер расписаний не доступен"


# print(get_lessons("tvtibilov@edu.hse.ru", "2020.02.29", "2020.02.29"))

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


# print(try_parse_date(
# json.loads(
# """[
#         {
#           "type": "YANDEX.DATETIME",
#           "value": {
#             "day": 3,
#             "day_is_relative": true
#           },
#           "tokens": {
#             "start": 0,
#             "end": 3
#           }
#         },
#         {
#           "type": "YANDEX.NUMBER",
#           "value": 3,
#           "tokens": {
#             "start": 1,
#             "end": 2
#           }
#         }
#       ]"""
# )))

import datetime
import calendar


def add_months(sourcedate, months):
    month = sourcedate.month - 1 + months
    year = sourcedate.year + month // 12
    month = month % 12 + 1
    day = min(sourcedate.day, calendar.monthrange(year, month)[1])
    return datetime.date(year, month, day)


from calendar import isleap


def add_years(d, years):
    new_year = d.year + years
    try:
        return d.replace(year=new_year)
    except ValueError:
        if (d.month == 2 and d.day == 29 and  # leap day
                isleap(d.year) and not isleap(new_year)):
            return d.replace(year=new_year, day=28)
        raise
