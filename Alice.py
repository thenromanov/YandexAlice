from flask import Flask, request
import logging
import json


app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

sessionStorage = {}


def getSuggests(userId):
    print(userId)
    session = sessionStorage[userId]
    suggests = [{'title': suggest, 'hide': True} for suggest in session['suggests'][:2]]
    session['suggests'] = session['suggests'][1:]
    sessionStorage[userId] = session
    if len(suggests) < 2:
        suggests.append({
            'title': 'Ладно',
            'url': 'https://market.yandex.ru/search?text=слон',
            'hide': True
        })
    return suggests


def handleDialog(req, res):
    userId = req['session']['user_id']
    if req['session']['new']:
        sessionStorage[userId] = {'suggests': ['Не хочу.', 'Не буду.', 'Отстань.']}
        res['response']['text'] = 'Привет! Купи слона!'
        res['response']['buttons'] = getSuggests(userId)
        return
    if req['request']['original_utterance'].lower() in ['ладно', 'куплю', 'покупаю', 'хорошо']:
        res['response']['text'] = 'Слона можно найти на Яндекс.Маркете!'
        res['response']['end_session'] = True
        return
    res['response']['text'] = f"Все говорят '{req['request']['original_utterance']}', а ты купи слона!"
    res['response']['buttons'] = getSuggests(userId)


@app.route('/post', methods=['POST'])
def main():
    logging.info(f'Request: {request.json!r}')
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {'end_session': False}
    }
    handleDialog(request.json, response)
    logging.info(f'Response: {response!r}')
    return json.dumps(response)


if __name__ == '__main__':
    app.run()
