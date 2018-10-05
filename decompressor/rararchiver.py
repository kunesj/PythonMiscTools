#!/usr/bin/env python3
# encoding: utf-8

import logging
logger = logging.getLogger(__name__)

import rarfile

from eam.decompressor.archiver import Archiver

class RarArchiver(Archiver):
    """ Functions are documented in Archiver class """

    def __init__(self):
        Archiver.__init__(self)
        self.extensions = ["rar", "cbr"]

    def open(self, archivepath):
        self.close()
        self.opened_archive = rarfile.RarFile(archivepath)

    def close(self):
        if self.archiveOpened():
            self.opened_archive.close()
        self.opened_archive = None

    def getFileList(self):
        filtered_paths = [] # filter out directories
        for fp in self.opened_archive.namelist():
            try:
                self.openFile(fp)
            except TypeError:
                continue
            filtered_paths.append(fp)
        return filtered_paths

    def openFile(self, filepath):
        return self.opened_archive.open(filepath).read()

    def extractFile(self, filepath, extractpath):
        self.opened_archive.extract(filepath, extractpath)
