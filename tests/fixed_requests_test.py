#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from fixed_requests import FixedRequests

class FixedRequestsTest(unittest.TestCase):

    def getsetupdate_test(self):
        # test values
        headers1 = {'user-agent':'Firefox', 'referer': '127.0.0.1'}
        headers2 = {'user-agent':'Chrome'}
        headers_updated = dict(headers1); headers_updated.update(headers2)
        cookies1 = {'CAKE':'IS A', 'LIE':'!'}
        cookies2 = {'CAKE':'IS NOT A'}
        cookies_updated = dict(cookies1); cookies_updated.update(cookies2)
        timeout1 = 666

        fr = FixedRequests()

        # test headers
        fr.set_headers(headers1)
        get = fr.get_headers()
        self.assertEqual(get['user-agent'], headers1['user-agent'])
        self.assertEqual(get['referer'], headers1['referer'])
        self.assertEqual(len(get), 2)

        fr.update_headers(headers2)
        get = fr.get_headers()
        self.assertEqual(get['user-agent'], headers_updated['user-agent'])
        self.assertEqual(get['referer'], headers_updated['referer'])
        self.assertEqual(len(get), 2)

        # test cookies
        fr.set_cookies(cookies1)
        get = fr.get_cookies()
        self.assertEqual(get['CAKE'], cookies1['CAKE'])
        self.assertEqual(get['LIE'], cookies1['LIE'])
        self.assertEqual(len(get), 2)

        fr.update_cookies(cookies2)
        get = fr.get_cookies()
        self.assertEqual(get['CAKE'], cookies_updated['CAKE'])
        self.assertEqual(get['LIE'], cookies_updated['LIE'])
        self.assertEqual(len(get), 2)

        # test timeout
        fr.set_timeout(timeout1)
        get = fr.get_timeout()
        self.assertEqual(get, timeout1)
