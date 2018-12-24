#!/usr/bin/env python
# -*- coding: utf-8 -*-

from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run_flow
import httplib2
import requests

import os
import pkg_resources
import json


class GoogleAPI(object):
    """
    Requirements
    ------------
    pip install oauth2client requests

    How to get valid 'client_secret.json'
    -------------------------------------
    1. go to 'https://console.developers.google.com/'
    2. create project and OAuth2.0 credentials (type: web_application/other)
    3. add 'http://localhost:8080' to redirect urls (if type is web_application)
    4. enable google APIs
    5. enable all availible scopes in project (OAuth consent screen)
    6. download 'client_secret.json'

    API reference
    -------------
    https://developers.google.com/gmail/api/v1/reference/
    https://developers.google.com/calendar/v3/reference/

    Examples
    --------
    Basic usage
    >>> api = GoogleAPI()
    >>> api.authorize_credentials()
    >>> print( api.call('GET', 'https://www.googleapis.com/gmail/v1/users/me/profile') )

    Extending class
    >>> class GmailAPI(GoogleAPI):
    >>>     BASE_URL = 'https://www.googleapis.com/gmail/v1/users'
    >>>     def users_getprofile(self, user_id='me', **kwargs):
    >>>         return self.call('GET', url=self.BASE_URL+'/{}/profile'.format(user_id), **kwargs)
    """

    def __init__(self, client_secret=None, credentials=None, scopes=None):
        """
        client_secret : string
            Path to json with app OAuth2.0 info
        credentials : string
            Path to json file with user OAuth2.0 credentials
        scopes : list
            List of google api scopes (strings)
        """
        # init default values
        self.client_secret = pkg_resources.resource_filename(__name__, 'client_secret.json')
        self.credentials = pkg_resources.resource_filename(__name__, 'credentials.json')
        self.scopes = [
            # GMail
            'https://www.googleapis.com/auth/gmail.readonly',
            # Calendar
            'https://www.googleapis.com/auth/calendar.readonly',
            'https://www.googleapis.com/auth/calendar.events.readonly',
            # Keep # TODO: cant be enabled?
            'https://www.googleapis.com/auth/memento',
            'https://www.googleapis.com/auth/reminders',
        ]
        # set user defined values
        self.client_secret = client_secret if client_secret else self.client_secret
        self.credentials = credentials if credentials else self.credentials
        self.scopes = scopes if scopes else self.scopes

    def authorize_credentials(self, reauth=False):
        """
        Returns OAuth2 credentials(tokens, etc.).
        If they don't exist generates them (opens web browser, requires google login).
        Use this only once! After use refresh_access_token() and/or get_credentials()!

        reauth : boolean
            If True, delete old credential and authorize new ones.
        """
        if reauth and os.path.exists(self.credentials):
            os.remove(self.credentials)
        storage = Storage(self.credentials)
        credentials = storage.get()
        if credentials is None or credentials.invalid:
            # use prompt='consent' to always return refresh_token
            flow = flow_from_clientsecrets(self.client_secret, scope=self.scopes, prompt='consent')
            http = httplib2.Http()
            run_flow(flow, storage, http=http)

    def refresh_access_token(self):
        """
        Access token expires after about 1 hour. That's why it must be remade from refresh token.

        returns : access_token
        """
        with open(self.credentials, 'r') as f:
            data = json.loads(f.read())
            client_id = data['client_id']
            client_secret = data['client_secret']
            refresh_token = data['refresh_token']
        request = requests.post(
            'https://accounts.google.com/o/oauth2/token',
            data={
                'grant_type':    'refresh_token',
                'client_id':     client_id,
                'client_secret': client_secret,
                'refresh_token': refresh_token
            },
            headers={
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json'
            }
        )
        response = json.loads(request.text)
        return response['access_token']

    def call(self, verb, url, params=None, headers=None):
        """
        verb : string
            Could be 'GET', 'POST', 'DELETE', ...
        url : string
            Url of API call. Example: 'https://www.googleapis.com/gmail/v1/users/me/profile'
        params : dict
            Aditional API call parameters. Example: {'prettyPrint': 'true'}
        headers : dict
            Headers replacement (updates default ones)
        """
        params = dict({
            'prettyPrint': 'false'
        }, **(params if params else {}))

        access_token = self.refresh_access_token()
        headers = dict({
            'Authorization': 'OAuth {}'.format(access_token)
        }, **(headers if headers else {}))

        r = requests.request(verb, url=url, params=params, headers=headers, timeout=30)
        return json.loads(r.text)


if __name__ == "__main__":
    api = GoogleAPI()
    api.authorize_credentials(reauth=True)
    print(api.call('GET', 'https://www.googleapis.com/gmail/v1/users/me/profile'))
