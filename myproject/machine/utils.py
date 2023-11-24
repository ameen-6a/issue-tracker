import json
from collections import Counter
import re

from django.core.exceptions import ViewDoesNotExist


def get_request_body(req_body) -> dict:
    try:
        body_unicode = req_body.body.decode('utf-8')
        return json.loads(body_unicode)
    except TypeError as err:
        print('Error while parsing request body: {}'.format(err))


def get_response_body(resp_body) -> dict:
    try:
        body_unicode = resp_body.content.decode('utf-8')
        return json.loads(body_unicode)
    except TypeError as err:
        print('Error while parsing request body: {}'.format(err))


def check_post_method(request):
    if request.method != 'POST':
        raise ViewDoesNotExist("This method have not been implemented yet")


def check_get_method(request):
    if request.method != 'GET':
        raise ViewDoesNotExist("This method have not been implemented yet")


def check_put_method(request):
    if request.method != 'PUT':
        raise ViewDoesNotExist("This method have not been implemented yet")


def get_top_k_common_words(issues, top_k: int = 5):
    words = re.findall(r'\b\w+\b', issues.lower())

    word_counter = Counter(words)

    top_k_words = word_counter.most_common(top_k)

    return top_k_words
