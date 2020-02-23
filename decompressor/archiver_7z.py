#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import tempfile
import shutil
import subprocess
import logging

from .archiver_interface import ArchiverInterface

logger = logging.getLogger(__name__)


class External7zLib(object):

    def __init__(self, archive_path):
        self.work_dir = tempfile.mkdtemp()
        self.archive_path = os.path.abspath(archive_path)

        # try to open 7z file
        p = subprocess.Popen(
            ['7z', 'x', f'-o{self.work_dir}', f'{self.archive_path}'],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True
        )
        out, err = p.communicate()

        # check if went ok
        out_spl = out.strip().split('\n')
        ok = False
        for i in range(1, len(out_spl)+1):
            if out_spl[-i].strip().lower() == 'Everything is Ok'.lower():
                ok = True
                break
        if not ok:
            self.close()
            raise Exception(f'Failed to open 7z file "{self.archive_path}" with external tool:\n{out}')

    def close(self):
        shutil.rmtree(self.work_dir)

    def get_file_list(self):
        path_list = []
        for dir_name, subdir_list, file_list in os.walk(self.work_dir):
            for file_name in file_list:
                full_path = os.path.join(dir_name, file_name)
                archive_path = os.path.relpath(full_path, self.work_dir)
                path_list.append(archive_path)
        return path_list

    def open_file(self, path):
        with open(os.path.join(self.work_dir, path), 'rb') as f:
            data = f.read()
        return data


class Archiver7z(ArchiverInterface):

    EXTENSIONS = {'7z', 'cb7'}

    def open(self, archive_path):
        self.close()
        self.opened_archive = External7zLib(archive_path)

    def close(self):
        if self.archive_opened():
            self.opened_archive.close()
        self.opened_archive = None

    def get_file_list(self):
        # doesnt list directories
        return self.opened_archive.get_file_list()

    def open_file(self, file_path):
        """ Returns Bytes """
        return self.opened_archive.open_file(file_path)

    def extract_file(self, file_path, extract_path):
        with open(extract_path, 'wb') as f:
            f.write(self.open_file(file_path))
