import requests
import json

def get_lessons(email, start_date, end_date):
    # response = requests.get(f'http://mlk.hse.ru/mlk-0.5.1/ruz/oldapi/personlessons?fromdate={start_date}&todate={end_date}&email={email}&receivertype=1&language=2')
    response = requests.get(f'http://mlk.hse.ru/mlk-0.5.1/ruz/api/schedule/student?start={start_date}&finish={end_date}&email={email}&lng=1')
    resp = json.loads(response.content.decode("utf-8"))
    # if resp["error"] == "zero-id-request":
    #     return "No such user"
    count = len(resp)
    # print(count)
    res = f"{count} пар: \n"
    for i in resp:
        res+=f"{i['discipline']}\n"
        #print(i["discipline"])
    print(res)
    return res
    #print(response.content.decode("utf-8"))#json.load()

get_lessons("tvtibilov@edu.hse.ru", "2020.02.29", "2020.02.29")
