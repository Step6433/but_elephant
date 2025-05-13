from flask import Flask, request, jsonify
import logging
import time

# Создаем приложение
app = Flask(__name__)
cur_animal = "слона"  # Начальное животное

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
    handle_dialog(request.json, response)
    logging.info(f'Response:  {response!r}')
    return jsonify(response)


def handle_dialog(req, res):
    global cur_animal
    user_id = req['session']['user_id']

    if req['session']['new']:
        # Новое начало диалога — предлагаем первое животное
        sessionStorage[user_id] = {
            'suggests': [
                "Не хочу.",
                "Не буду.",
                "Отстань!",
                'Я покупаю',
                'Я куплю'
            ]
        }

        res['response']['text'] = f'Привет! Купи {cur_animal.lower()}!'
        res['response']['buttons'] = get_suggests(user_id)
        return

    # Проверяем согласие пользователя на покупку
    data = ['ладно', 'куплю', 'покупаю', 'хорошо', 'я покупаю', 'я куплю']
    if any(i in req['request']['original_utterance'].lower() for i in data):
        # Пользователь согласился — сообщаем, где искать животное
        animal = cur_animal
        res['response']['text'] = f'{animal.capitalize()} можно найти на Яндекс.Маркете!'
        res['response']['buttons'] = get_suggests(user_id)

        # Переключаемся на следующее животное
        if cur_animal == "слона":
            cur_animal = "кролика"
        elif cur_animal == "кролика":
            cur_animal = "слона"

        # Начинаем следующий цикл покупки с новым животным
        res['response']['text'] += f'\n\nКупи теперь {cur_animal.lower()}!'
        return

    # Если пользователь отказался покупать, продолжаем уговаривать
    res['response'][
        'text'] = f"Все говорят '{req['request']['original_utterance']}', а ты купи {cur_animal.lower()}!"
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
    while True:
        app.run()