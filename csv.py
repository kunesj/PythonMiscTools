#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv

import logging
logger = logging.getLogger(__name__)


def read_csv(filepath):
    with open(filepath, "r") as f:
        csvdicts = read_csv_stream(f)
    return csvdicts


def read_csv_stream(stream):
    return csv.DictReader(stream)


def write_csv(filepath, csvdicts):
    """ csvdicts => list(dict(), dict(), ...)"""
    # get headers
    headers = []
    for key in csvdicts[0]:
        headers.append(key)

    # write to csv
    with open(filepath, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        for row in csvdicts:
            writer.writerow(row)
