from flask import Flask, request
import logging
import json


app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

sessionStorage = {}
animals = ['слон', 'кролик']
animalChanged = True


def getSuggests(userId):
    print(userId)
    session = sessionStorage[userId]
    suggests = [{'title': suggest, 'hide': True} for suggest in session['suggests'][:2]]
    session['suggests'] = session['suggests'][1:]
    sessionStorage[userId] = session
    if len(suggests) < 2:
        suggests.append({
            'title': 'Ладно',
            'url': f'https://market.yandex.ru/search?text={animals[0]}',
            'hide': True
        })
    return suggests


def handleDialog(req, res):
    global animalChanged
    userId = req['session']['user_id']
    if animalChanged:
        sessionStorage[userId] = {'suggests': ['Не хочу.', 'Не буду.', 'Отстань.']}
        res['response']['text'] = f'Привет! Купи {animals[0]}а!'
        res['response']['buttons'] = getSuggests(userId)
        animalChanged = False
        return
    if any(argree in req['request']['original_utterance'].lower() for argree in ['ладно', 'куплю', 'покупаю', 'хорошо']):
        res['response']['text'] = f'{animals[0][0].upper() + animals[0][1:]}а можно найти на Яндекс.Маркете!'
        animals.pop(0)
        res['response']['end_session'] = len(animals) == 0
        animalChanged = True
        return
    res['response']['text'] = f"Все говорят '{req['request']['original_utterance']}', а ты купи {animals[0]}а!"
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
