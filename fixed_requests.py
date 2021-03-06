#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import requests

import logging
logger = logging.getLogger(__name__)
# disable messages from requests lib
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)


class FixedRequests(object):
    DEFAULT_HEADERS = {'user-agent': "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:48.0) Gecko/20100101 Firefox/48.0"}

    def __init__(self, use_cookies=True, max_errors=5, cloudscraper=False):
        self.use_cookies = use_cookies
        self.max_errors = max_errors
        self.error_sleep_time = 1

        # cloudscraper
        self.cloudscraper = cloudscraper
        if self.cloudscraper:
            import cloudscraper as cs
            self.requests_class = cs
            self.requests_session = cs.create_scraper(browser={
                'browser': 'chrome',
                'platform': 'windows',
                'mobile': False,
                'desktop': True,
            })
        else:
            self.requests_class = requests
            self.requests_session = requests.Session()

        # requests arguments
        self.args_timeout = 30
        self.args_headers = dict(self.DEFAULT_HEADERS)

        # request delay
        self.request_delay = 0  # min time delay between requests
        self.last_request_time = 0

    ###
    # Getters, Setters, Updaters
    ###

    def get_headers(self):
        return self.args_headers

    def set_headers(self, new_headers):
        self.args_headers = dict(new_headers)

    def update_headers(self, new_headers):
        self.args_headers.update(new_headers)

    def get_cookies(self):
        return dict(self.requests_session.cookies)

    def set_cookies(self, new_cookies):
        self.requests_session.cookies = new_cookies

    def update_cookies(self, new_cookies):
        self.requests_session.cookies.update(new_cookies)

    def get_timeout(self):
        return self.args_timeout

    def set_timeout(self, new_timeout):
        self.args_timeout = new_timeout

    def set_request_delay(self, delay):
        self.request_delay = delay

    ###
    # Methods from requests library
    ###

    def get(self, **kwargs):
        """ Only accepts keyword arguments """
        kwargs["req_type"] = "get"
        return self._request(**kwargs)

    def post(self, **kwargs):
        """ Only accepts keyword arguments """
        kwargs["req_type"] = "post"
        return self._request(**kwargs)

    ###
    # Private methods
    ###

    def _request(self, **kwargs):
        """
        * Generic request function
        * Only accepts keyword arguments
        * Needs to have "req_type": "get"/"post"
        """
        kwargs = self._fill_kwargs(**kwargs)

        if "req_type" not in kwargs:
            kwargs["req_type"] = "get"
        req_type = kwargs["req_type"]
        del(kwargs["req_type"])

        r = None
        error_num = 0
        while True:
            if error_num >= self.max_errors:
                raise Exception("Request failed too many times ("+str(error_num)+" times).")

            response_ok = True
            try:
                self._delay_requests(error_num=error_num)
                if req_type == "get":
                    r = self.requests_session.get(**kwargs)
                elif req_type == "post":
                    r = self.requests_session.post(**kwargs)
                else:
                    raise Exception("Unknown request type!")

                self._log_status_code(r.status_code)
                if r.status_code == 429:  # too many requests
                    response_ok = False
                elif r.status_code == 503:  # service unavailable
                    response_ok = False

            except requests.exceptions.ConnectionError:
                logger.warning("Connection refused")
                response_ok = False

            if response_ok:
                break
            else:
                error_num += 1
                time.sleep(self.error_sleep_time)
                continue

        # update cookies
        if not self.use_cookies:
            self.set_cookies({})

        return r

    def _delay_requests(self, error_num):
        """ makes sure that self.request_delay is obeyed """
        if error_num != 0:
            sleep_time = 2**error_num
            time.sleep(sleep_time)

        elif self.request_delay > 0:
            deltat = time.time() - self.last_request_time
            if deltat < self.request_delay:
                time.sleep(float(self.request_delay)-deltat)

    def _fill_kwargs(self, **kwargs):
        if "timeout" not in kwargs:
            kwargs["timeout"] = self.args_timeout
        if "headers" not in kwargs:
            kwargs["headers"] = self.args_headers
        return kwargs

    @staticmethod
    def _log_status_code(status_code):
        # specific status codes messages
        codes = {
                200: "OK",
                301: "Moved Permanently",
                403: "Forbidden",
                404: "Not Found",
                503: "Service Unavailable"
                }

        # detect status code type
        if 100 <= status_code < 200:
            code_type = "Informational"
        elif 200 <= status_code < 300:
            code_type = "Success"
        elif 300 <= status_code < 400:
            code_type = "Redirection"
        elif 400 <= status_code < 500:
            code_type = "Client Error"
        elif 500 <= status_code < 600:
            code_type = "Server Error"
        else:
            code_type = "Unknown"

        # get status code info
        if status_code in codes:
            code_info = codes[status_code]
        else:
            code_info = ""

        # log status code
        logger.debug("{} - {} {}".format(code_type, status_code, code_info))
