#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)

import zipfile

from .archiver import Archiver

class ZipArchiver(Archiver):
    """ Functions are documented in Archiver class """

    def __init__(self):
        Archiver.__init__(self)
        self.extensions = ["zip", "cbz"]

    def open(self, archivepath):
        self.close()
        self.opened_archive = zipfile.ZipFile(archivepath)

    def close(self):
        if self.archiveOpened():
            self.opened_archive.close()
        self.opened_archive = None

    def getFileList(self):
        filtered_paths = [] # filter out directories
        for fp in self.opened_archive.namelist():
            if fp.strip()[-1] in ["/", "\\"]:
                continue
            filtered_paths.append(fp)
        return filtered_paths

    def openFile(self, filepath):
        return self.opened_archive.open(filepath).read()

    def extractFile(self, filepath, extractpath):
        self.opened_archive.extract(filepath, extractpath)
