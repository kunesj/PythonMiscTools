#!/usr/bin/env python3
# encoding: utf-8

class Archiver(object):
    """
    Base class that should be inherited by any classes that deal with reading archives
    """

    def __init__(self):
        self.extensions = []
        self.opened_archive = None

    def getSupportedExtensions(self):
        return self.extensions

    def archiveOpened(self):
        """ Checks if there is any opened archive """
        return self.opened_archive is not None

    def open(self, archivepath):
        """ Opens archive """
        raise NotImplementedError

    def close(self):
        """ Closes currently opened archive """
        raise NotImplementedError

    def getFileList(self):
        """ Returns list of files in archive """
        raise NotImplementedError

    def openFile(self, filepath):
        """ Returns stream """
        raise NotImplementedError

    def extractFile(self, filepath, extractpath):
        """ Extracts file to path """
        raise NotImplementedError
