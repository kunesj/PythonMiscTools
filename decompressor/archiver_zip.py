#!/usr/bin/env python
# -*- coding: utf-8 -*-

import zipfile
import logging

from .archiver_interface import ArchiverInterface

logger = logging.getLogger(__name__)


class ArchiverZip(ArchiverInterface):

    EXTENSIONS = {'zip', 'cbz'}

    def open(self, archive_path):
        self.close()
        self.opened_archive = zipfile.ZipFile(archive_path)

    def close(self):
        if self.archive_opened():
            self.opened_archive.close()
        self.opened_archive = None

    def get_file_list(self):
        filtered_paths = []  # filter out directories
        for fp in self.opened_archive.namelist():
            if fp.strip()[-1] in ['/', '\\']:
                continue
            filtered_paths.append(fp)
        return filtered_paths

    def open_file(self, file_path):
        return self.opened_archive.open(file_path).read()

    def extract_file(self, file_path, extract_path):
        self.opened_archive.extract(file_path, extract_path)
