import json
import time

import requests

import openweather

TICKET_CODE = 4
TEXT = "Я с женой и двумя детьми хотим полететь в Москву из Новосибирска в 10:00 через неделю"

NLP_FIRST_LAYER_LINK = 'https://pinter.thelacker.ru/bot/s7'
NLP_SECOND_LAYER_LINK = 'http://plp.thelacker.ru/facts'

print('Отправка запроса на первый этап обработки - векторизация и классификация')
first_layer_response = requests.post(NLP_FIRST_LAYER_LINK, json=dict(text=TEXT, access_token='s7bot')).json()
print()
print('Полный ответ первого слоя:')
print(first_layer_response)
print()
first_layer_answer = first_layer_response['answer']
answer_code = first_layer_answer['class']

print('Проверка на необходимость дальнейшего анализа запроса в случае сценария покупки билета')
print()
if answer_code == TICKET_CODE:
    print('Дальнейшая проверка вторым слоем nlp модуля')
    print()
    api_response = requests.post(
        url=NLP_SECOND_LAYER_LINK,
        json=dict(text=TEXT)
    )
    print('Полный ответ второго слоя:')
    second_layer_response = json.loads(api_response.content.decode())
    print(second_layer_response)
    print()

    print('Анализ полученных данных со второго слоя')
    print()
    success, answer = second_layer_response['success'], second_layer_response['answer'][0]
    if success:
        from_city = answer.get('from')
        if isinstance(from_city, list):
            from_city = from_city[0] if len(from_city) > 0 else None

        to_city = answer.get('to', [])
        if isinstance(to_city, list):
            to_city = to_city[0] if len(to_city) > 0 else None

        who = answer.get('who', [])
        with_person = answer.get('with', [])
        numbers = answer.get('numbers', [])

        time_mark = answer.get('time_mark')
        if isinstance(time_mark, list):
            time_mark = time_mark[0] if len(time_mark) > 0 else None

        first_layer_answer['params'] = dict(
            from_city=from_city,
            to_city=to_city,
            who=who,
            with_person=with_person,
            numbers=numbers,
            time_mark=time_mark
        )

        if to_city in openweather.cities:
            forecast = openweather.get_forecast(
                to_city,
                when=time_mark
            )[0]
            first_layer_answer['params']['forecast'] = dict(
                date=time.mktime(forecast.date.timetuple()),
                temperature=forecast.temperature,
                weather=forecast.weather
            )
    else:
        pass

print('Итоговый ответ от сервиса:')
print(first_layer_answer)
