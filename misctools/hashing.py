#!/usr/bin/env python3
# encoding: utf-8

import logging
logger = logging.getLogger(__name__)

import os, hashlib

def getSHA1Hash(filepath):
    """
    Returns sha1 hash of file.
    """
    afile = open(filepath, 'rb')
    filehash = getSHA1HashFromStream(afile)
    afile.close()

    return filehash

def getSHA1HashFromStream(stream):
    """
    Returns sha1 hash of stream.
    """
    stream.seek(0, os.SEEK_SET)
    hasher = hashlib.sha1()
    hasher.update(stream.read())
    filehash = hasher.hexdigest()

    return filehash

def getFastHash(filepath):
    """
    Returns:
        sha1(first_KB+middle_KB+last_KB)
    """
    afile = open(filepath, 'rb')
    fasthash = getFastHashFromStream(afile)
    afile.close()
    return fasthash

def getFastHashFromStream(stream):
    """
    Returns:
        sha1(first_KB+middle_KB+last_KB)
    """
    bites_to_hash = 1024 # 1KB at both ends and middle

    stream.seek(-1, os.SEEK_END)
    file_length = stream.tell()

    # get first KB
    stream.seek(0, os.SEEK_SET)
    buf_start = stream.read(bites_to_hash)

    # get mid KB
    start_read = int(file_length/2)
    stream.seek(start_read, os.SEEK_SET)
    buf_mid = stream.read(bites_to_hash)

    # get last KB
    start_read = file_length - bites_to_hash
    if start_read<0:
        start_read = 0
    stream.seek(start_read, os.SEEK_SET)
    buf_end = stream.read(bites_to_hash)

    # hash everything
    hasher = hashlib.sha1()

    hasher.update(buf_start)
    hasher.update(buf_mid)
    hasher.update(buf_end)

    fasthash = hasher.hexdigest()

    return fasthash
