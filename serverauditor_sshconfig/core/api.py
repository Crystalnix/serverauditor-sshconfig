# coding: utf-8

"""
Copyright (c) 2013 Crystalnix.
License BSD, see LICENSE for more details.
"""
import six
import hashlib
import requests
from requests.auth import AuthBase


class ServerauditorAuth(AuthBase):

    def __init__(self, username, apikey):
        self.username = username
        self.apikey = apikey

    @property
    def auth_header(self):
        return "ApiKey {username}:{apikey}".format(
            username=self.username, apikey=self.apikey
        )

    def __call__(self, request):
        request.headers['Authorization'] = self.auth_header
        return request


def hash_password(password):
    password = six.b(password)
    return hashlib.sha256(password).hexdigest()


class API(object):

    host = 'serverauditor.com'
    base_url = 'https://{}/api/'.format(host)

    def __init__(self, username=None, apikey=None):
        if username and apikey:
            self.auth = ServerauditorAuth(username, apikey)
        else:
            self.auth = None

    def set_auth(self, username, apikey):
        self.auth = ServerauditorAuth(username, apikey)

    def request_url(self, endpoint):
        return self.base_url + endpoint

    def login(self, username, password):
        """Returns user's auth token."""
        password = hash_password(password)
        response = requests.get(self.request_url("v1/token/auth/"),
                                auth=(username, password))
        assert response.status_code == 200

        response_payload = response.json()
        apikey = response_payload['key']
        self.set_auth(username, apikey)
        return response_payload

    def post(self, endpoint, data):
        response = requests.post(self.request_url(endpoint),
                                 json=data, auth=self.auth)
        assert response.status_code == 201
        return response.json()

    def get(self, endpoint, data):
        response = requests.get(self.request_url(endpoint), auth=self.auth)
        assert response.status_code == 200
        return response.json()

    def delete(self, endpoint, data):
        response = requests.delete(self.request_url(endpoint), auth=self.auth)
        assert response.status_code in (200, 204)
        return response.json()

    def put(self, endpoint, data):
        response = requests.put(self.request_url(endpoint), json=data, auth=self.auth)
        assert response.status_code in (200, 204)
        return response.json()
