#!/usr/bin/env python3
# encoding: utf-8

import os
import hashlib

import logging
logger = logging.getLogger(__name__)


def get_sha1_hash(filepath):
    """
    Returns sha1 hash of file.
    """
    afile = open(filepath, 'rb')
    filehash = get_sha1_hash_from_stream(afile)
    afile.close()

    return filehash


def get_sha1_hash_from_stream(stream):
    """
    Returns sha1 hash of stream.
    """
    stream.seek(0, os.SEEK_SET)
    hasher = hashlib.sha1()
    hasher.update(stream.read())
    filehash = hasher.hexdigest()

    return filehash
