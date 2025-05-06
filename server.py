from flask import Flask, request, jsonify
import logging

# Создаем приложение
app = Flask(__name__)
count = 1
flag = 0

# Устанавливаем уровень логирования
logging.basicConfig(level=logging.INFO)

# Хранение состояния каждого пользователя
sessionStorage = {}


@app.route('/post', methods=['POST'])
def main():
    logging.info(f'Request: {request.json!r}')

    # Формируем базовый ответ
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }

    # Обрабатываем входящий запрос
    handle_dialog(request.json, response)
    logging.info(f'Response:  {response!r}')

    return jsonify(response)


def handle_dialog(req, res):
    global count, flag
    user_id = req['session']['user_id']
    if req['session']['new'] or flag == 1:
        # Новый пользователь — приветствие и предложение первой покупки
        sessionStorage[user_id] = {
            'suggests': [
                "Не хочу.",
                "Не буду.",
                "Отстань!",
                'Я покупаю',
                'Я куплю'
            ]
        }
        flag = 0
        if count % 2 == 1:
            s = 'Слона'
        else:
            s = 'Кролика'
        res['response']['text'] = f'Привет! Купи {s.lower()}!'
        res['response']['buttons'] = get_suggests(user_id)
        return

    # Проверяем согласие пользователя на покупку
    data = ['ладно', 'куплю', 'покупаю', 'хорошо', 'я покупаю', 'я куплю']
    if any(i in req['request']['original_utterance'].lower() for i in data):
        # Покупатель согласился — сообщаем, где искать животное
        if count % 2 == 1:
            s = 'Слона'
        else:
            s = 'Кролика'
        res['response']['text'] = f'{s} можно найти на Яндекс.Маркете!'

        # Обнуляем цикл и начинаем заново
        count += 1
        flag = 1
        sessionStorage[user_id]['suggests'] = [
            "Не хочу.",
            "Не буду.",
            "Отстань!",
            'Я покупаю',
            'Я куплю'
        ]
        res['response']['buttons'] = get_suggests(user_id)
        return

    # Если пользователь отказался покупать, продолжаем уговаривать
    if count % 2 == 1:
        s = 'Слона'
    else:
        s = 'Кролика'
    res['response']['text'] = f"Все говорят '{req['request']['original_utterance']}', а ты купи {s.lower()}!"
    res['response']['buttons'] = get_suggests(user_id)


# Возвращает список кнопок-подсказок
def get_suggests(user_id):
    session = sessionStorage[user_id]
    suggests = [
        {'title': suggest, 'hide': True}
        for suggest in session['suggests'][:2]
    ]

    # Меняем подсказки динамически
    session['suggests'] = session['suggests'][1:] + session['suggests'][:1]
    sessionStorage[user_id] = session
    # Добавляем ссылку на маркет, если меньше двух подсказок
    if len(suggests) < 2:
        suggests.append({
            "title": "Купить",
            "url": "https://market.yandex.ru/",
            "hide": True
        })
    return suggests


if __name__ == '__main__':
    app.run()