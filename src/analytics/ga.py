# Copyright (c) 2014, Guillermo López-Anglada. Please see the AUTHORS file for details.
# All rights reserved. Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.)

'''
Google Analytics
'''

import uuid
import os

import urllib.parse
import urllib.request
import random


class GaService(object):

    _endpoint = "https://ssl.google-analytics.com/collect"

    def __init__(self, tracking_id, user_agent):
        # Dart: UA-55288482-1
        self.tracking_id = tracking_id
        self.user_agent = user_agent
        self.protocol_version = 1

        self.client_id = str(uuid.uuid4())

    def encode(self, post_data):
        return urllib.parse.urlencode(post_data)

    @property
    def initial_payload(self):
        return {
            'v': self.protocol_version,
            'tid': self.tracking_id,
            'aip': 1,
            'cid': self.client_id,
            't': None, # type
        }

    def send_event(self, event_data):
        payload = self.initial_payload
        payload.update(event_data)

        url_encoded_data = self.encode(payload)
        # Bust through cache. This param should come last.
        url_encoded_data += '&z=' + str(int(random.random() * 10000))

        utf8_encoded_data = url_encoded_data.encode('utf-8')

        request = urllib.request.Request(GaService._endpoint, data=utf8_encoded_data)
        request.add_header('User-Agent', str(self.user_agent))

        try:
            response = urllib.request.urlopen(request)
            if response.status <= 199 or response.status >= 300:
                raise SyntaxError('bad request')
        except Exception as e:
            pass # bad


class UserAgent(object):

    def __init__(self, name, version, os, language=None):
        self.name = name
        self.version = version
        self.os = os
        self.language = language

    def __str__(self):
        # FIXME(guillermooo): This is probably wrong.
        # ua = "ST-Dart-Plugin/{version} ({os}; {os}; {os}; {language})"
        ua = "{name}/{version} ({os}; {os}; {os}; {language})"
        data = {
            'name': self.name,
            'os': os.name,
            'language': self.language or os.environ.get('LANG', 'unknown'),
            'version': self.version,
        }
        return ua.format(**data)


class GaEvent(object):

    def __init__(self, category, action, label, value):

        assert isinstance(value, int), 'wrong args'
        assert value > 0

        self.hit_type = 'event'

        self.category = category
        self.action = action
        self.label = label
        self.value = value

    def to_dict(self):
        data = {
        'ec': self.category,
        'ea': self.action,
        'el': self.label,
        'ev': self.value,
        't': self.hit_type
        }
        return data
