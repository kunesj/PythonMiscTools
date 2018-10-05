#!/usr/bin/env python3
# encoding: utf-8

import logging
logger = logging.getLogger(__name__)

import os
import tempfile, shutil, subprocess

from eam.decompressor.archiver import Archiver

class External7zLib(object):

    def __init__(self, archive_path):
        self.work_dir = tempfile.mkdtemp()
        self.archive_path = os.path.abspath(archive_path)

        # try to open 7z file
        p = subprocess.Popen(['7z', 'x', '-o%s' % self.work_dir, '%s' % self.archive_path],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        out, err = p.communicate()

        # check if went ok
        out_spl = out.strip().split("\n")
        ok = False
        for i in range(1, len(out_spl)+1):
            if out_spl[-i].strip().lower() == "Everything is Ok".lower():
                ok = True; break
        if not ok:
            self.close()
            raise Exception("Failed to open 7z file '%s' with external tool:\n%s" % (self.archive_path, out))

    def close(self):
        shutil.rmtree(self.work_dir)

    def getfilelist(self):
        path_list = []
        for dirName, subdirList, fileList in os.walk(self.work_dir):
            for fname in fileList:
                full_path = os.path.join(dirName, fname)
                archive_path = os.path.relpath(full_path, self.work_dir)
                path_list.append(archive_path)
        return path_list

    def openfile(self, path):
        with open(os.path.join(self.work_dir, path), "rb") as f:
            data = f.read()
        return data

class Py7zArchiver(Archiver):
    """ Functions are documented in Archiver class """

    def __init__(self):
        Archiver.__init__(self)
        self.extensions = ["7z", "cb7"]

    def open(self, archivepath):
        self.close()
        self.opened_archive = External7zLib(archivepath)

    def close(self):
        if self.archiveOpened():
            self.opened_archive.close()
        self.opened_archive = None

    def getFileList(self):
        # doesnt list directories
        return self.opened_archive.getfilelist()

    def openFile(self, filepath):
        """ Returns Bytes """
        return self.opened_archive.openfile(filepath)

    def extractFile(self, filepath, extractpath):
        with open(extractpath, 'wb') as f:
            f.write(self.openFile(filepath))