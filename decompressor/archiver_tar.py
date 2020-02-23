#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tarfile
import logging

from .archiver_interface import ArchiverInterface

logger = logging.getLogger(__name__)


class ArchiverTar(ArchiverInterface):  # TODO: create support for tar.gz

    EXTENSIONS = {'tar', 'cbt'}

    def open(self, archive_path):
        self.close()
        self.opened_archive = tarfile.open(archive_path, 'r')

    def close(self):
        if self.archive_opened():
            self.opened_archive.close()
        self.opened_archive = None

    def get_file_list(self):
        filtered_paths = []  # filter out directories
        for member in self.opened_archive.getmembers():
            if member.isfile():
                filtered_paths.append(member.name)
        return filtered_paths

    def open_file(self, file_path):
        member = self.opened_archive.getmember(file_path)
        return self.opened_archive.extractfile(member).read()

    def extract_file(self, file_path, extract_path):
        member = self.opened_archive.getmember(file_path)
        self.opened_archive.extract(member, extract_path)
