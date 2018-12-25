#!/usr/bin/env python
# -*- coding: utf-8 -*-

import rarfile

from .archiver import Archiver

import logging
logger = logging.getLogger(__name__)


class RarArchiver(Archiver):
    """ Functions are documented in Archiver class """

    def __init__(self):
        Archiver.__init__(self)
        self.extensions = ["rar", "cbr"]

    def open(self, archivepath):
        self.close()
        self.opened_archive = rarfile.RarFile(archivepath)

    def close(self):
        if self.archive_opened():
            self.opened_archive.close()
        self.opened_archive = None

    def get_file_list(self):
        filtered_paths = [] # filter out directories
        for fp in self.opened_archive.namelist():
            try:
                self.open_file(fp)
            except TypeError:
                continue
            filtered_paths.append(fp)
        return filtered_paths

    def open_file(self, filepath):
        return self.opened_archive.open(filepath).read()

    def extract_file(self, filepath, extractpath):
        self.opened_archive.extract(filepath, extractpath)
