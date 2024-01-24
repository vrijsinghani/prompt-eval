# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

import os, random, string
from django.urls import path
from django.conf import settings
import requests
from django.core.cache import cache


def h_random(aLen=32):
    letters = string.ascii_letters
    digits  = string.digits
    chars   = '_<>,.+'
    return ''.join(random.choices( letters + digits + chars, k=aLen))

def h_random_ascii(aLen=32):
    letters = string.ascii_letters
    digits  = string.digits
    return ''.join(random.choices( letters + digits, k=aLen))

def get_models():
    data = cache.get('models')
    if not data:
        url = f'{settings.API_BASE_URL}/models'
        headers = {'accept': 'application/json'}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()['data']
            cache.set('models', data, 60 * 60) # Cache data for 1 hour
        else:
            return None
    return [item['id'] for item in data]
