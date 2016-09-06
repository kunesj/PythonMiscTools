#!/usr/bin/python3
#coding: utf-8

import logging
logger = logging.getLogger(__name__)

import csv

def readCSV(filepath):
    with open(filepath, "r") as f:
        csvdicts = readCSVStream(f)
    return csvdicts

def readCSVStream(stream):
    return csv.DictReader(stream)

def writeCSV(filepath, csvdicts):
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
