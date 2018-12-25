#!/usr/bin/env python
# -*- coding: utf-8 -*-


class Archiver(object):
    """
    Base class that should be inherited by any classes that deal with reading archives
    """

    def __init__(self):
        self.extensions = []
        self.opened_archive = None

    def get_supported_extensions(self):
        return self.extensions

    def archive_opened(self):
        """ Checks if there is any opened archive """
        return self.opened_archive is not None

    def open(self, archivepath):
        """ Opens archive """
        raise NotImplementedError

    def close(self):
        """ Closes currently opened archive """
        raise NotImplementedError

    def get_file_list(self):
        """ Returns list of files in archive """
        raise NotImplementedError

    def open_file(self, filepath):
        """ Returns stream """
        raise NotImplementedError

    def extract_file(self, filepath, extractpath):
        """ Extracts file to path """
        raise NotImplementedError
