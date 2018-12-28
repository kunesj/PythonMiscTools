#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import sys
import os
try:
    import colorlog
except ImportError:
    pass


def setup_logging():
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    format = '%(levelname)s:%(name)s:%(lineno)d: %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    if 'colorlog' in sys.modules and os.isatty(2):
        cformat = '%(log_color)s' + format + '%(reset)s'
        f = colorlog.ColoredFormatter(
            cformat,
            date_format,
            log_colors={
                'DEBUG': 'reset',
                'INFO': 'reset',
                'WARNING': 'bold_yellow',
                'ERROR': 'bold_red',
                'CRITICAL': 'bold_red',
            }
        )
    else:
        f = logging.Formatter(format, date_format)
    ch = logging.StreamHandler()
    ch.setFormatter(f)
    root.addHandler(ch)
