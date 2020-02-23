#!/usr/bin/env python
# -*- coding: utf-8 -*-


class ArchiverInterface(object):
    """
    Base class that should be inherited by any classes that deal with reading archives
    """

    EXTENSIONS = set()

    def __init__(self, archive_path: str):
        self.opened_archive = None
        if archive_path:
            self.open(archive_path)

    def archive_opened(self) -> bool:
        """ Checks if there is any opened archive """
        return self.opened_archive is not None

    def open(self, archive_path: str) -> None:
        """ Opens archive """
        raise NotImplementedError

    def close(self) -> None:
        """ Closes currently opened archive """
        raise NotImplementedError

    def get_file_list(self) -> list:
        """ Returns list of files in archive """
        raise NotImplementedError

    def open_file(self, file_path: str) -> bytes:
        """ Returns stream """
        raise NotImplementedError

    def extract_file(self, file_path: str, extract_path: str) -> None:
        """ Extracts file to path """
        raise NotImplementedError
