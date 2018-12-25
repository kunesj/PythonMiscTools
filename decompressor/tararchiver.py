#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tarfile

from .archiver import Archiver

import logging
logger = logging.getLogger(__name__)


class TarArchiver(Archiver): # TODO - not tested
    """ Functions are documented in Archiver class """

    def __init__(self):
        Archiver.__init__(self)
        self.extensions = ["tar", "cbt"]

    def open(self, archivepath):
        self.close()
        self.opened_archive = tarfile.open(archivepath, 'r')

    def close(self):
        if self.archive_opened():
            self.opened_archive.close()
        self.opened_archive = None

    def get_file_list(self):
        return self.opened_archive.getmembers() # TODO - check if returns only files (not directories)

    def open_file(self, filepath):
        return self.opened_archive.open(filepath).read()

    def extract_file(self, filepath, extractpath):
        self.opened_archive.extract(filepath, extractpath)
