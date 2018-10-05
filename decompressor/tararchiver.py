#!/usr/bin/env python3
# encoding: utf-8

import logging
logger = logging.getLogger(__name__)

import tarfile

from eam.decompressor.archiver import Archiver

class TarArchiver(Archiver): # TODO - not tested
    """ Functions are documented in Archiver class """

    def __init__(self):
        Archiver.__init__(self)
        self.extensions = ["tar", "cbt"]

    def open(self, archivepath):
        self.close()
        self.opened_archive = tarfile.open(archivepath, 'r')

    def close(self):
        if self.archiveOpened():
            self.opened_archive.close()
        self.opened_archive = None

    def getFileList(self):
        return self.opened_archive.getmembers() # TODO - check if returns only files (not directories)

    def openFile(self, filepath):
        return self.opened_archive.open(filepath).read()

    def extractFile(self, filepath, extractpath):
        self.opened_archive.extract(filepath, extractpath)
