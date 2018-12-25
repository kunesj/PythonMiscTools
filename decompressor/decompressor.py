#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)

import os, io

# zipfile and tarfile lib are included in Python
from .ziparchiver import ZipArchiver
from .tararchiver import TarArchiver

try:
    from .rararchiver import RarArchiver
    RARLIB_INSTALLED = True
except ImportError as e:
    logger.warning("Unable to load RarArchiver: %s" % (str(e),))
    RarArchiver = None
    RARLIB_INSTALLED = False

try:
    from .py7zarchiver import Py7zArchiver
    PY7ZLIB_INSTALLED = True
except ImportError as e:
    logger.warning("Unable to load Py7zArchiver: %s" % (str(e),))
    Py7zArchiver = None
    PY7ZLIB_INSTALLED = False


class Decompressor(object):

    def __init__(self):
        self.archivers = []
        self.opened_archive = None
        self.extensions = []

        self.add_archiver(ZipArchiver())
        self.add_archiver(TarArchiver())
        if RARLIB_INSTALLED:
            self.add_archiver(RarArchiver())
        if PY7ZLIB_INSTALLED:
            self.add_archiver(Py7zArchiver())

        logger.info("Inited Decompressor, supported archive extensions: '%s'" % (", ".join(self.extensions),))

    def add_archiver(self, archiver):
        self.archivers.append(archiver)
        for e in archiver.get_supported_extensions():
            if e not in self.extensions:
                self.extensions.append(e)
        logger.info("Archiver with supported extensions '%s' added" % (", ".join(archiver.get_supported_extensions()),))

    def get_supported_extensions(self):
        return self.extensions

    def archive_opened(self):
        """ Checks if there is any opened archive """
        return self.opened_archive is not None

    def open(self, archivepath, extension=None):
        """ Opens archive """
        # close any opened archives
        self.close()

        # get extension
        if extension is None:
            filename, extension = os.path.splitext(archivepath)
            extension = extension.replace(".", "")

        # get supported archiver and open archive with it
        for a in self.archivers:
            if extension in a.getSupportedExtensions():
                a.open(archivepath)
                self.opened_archive = a

        # check if found archiver that supports extension
        if self.opened_archive is None:
            raise Exception("Archive extension '%s' not supported!" % (extension,))

    def close(self):
        """ close any opened archives """
        if self.archive_opened():
            self.opened_archive.close()
        self.opened_archive = None

    def get_file_list(self):
        """ Returns list of files in archive """
        if not self.archive_opened():
            raise Exception("No archive openned!")
        return self.opened_archive.getFileList()

    def open_file(self, filepath):
        """ Returns stream """
        if not self.archive_opened():
            raise Exception("No archive openned!")
        return io.BytesIO(self.opened_archive.openFile(filepath))

    def extract_file(self, filepath, extractpath):
        """ Extracts file to path """
        if not self.archive_opened():
            raise Exception("No archive openned!")
        return self.opened_archive.extractFile(filepath, extractpath)


if __name__ == "__main__":
    import argparse

    # Parasing input prarmeters
    parser = argparse.ArgumentParser(
        description='eam.decompressor'
    )
    parser.add_argument(
        'path',
        help='Path to archive')
    parser.add_argument(
        '-l', '--list', action='store_true',
        help='List files in archive')
    parser.add_argument(
        '-d', '--debug', type=int, choices=[50, 40, 30, 20, 10, 1], default=None,
        help='Set global debug level [CRITICAL=50, ERROR=40, WARNING=30, INFO=20, DEBUG=10, SPAM=1]. Default level is WARNING.')
    args = parser.parse_args()

    # Logger configuration
    logger = logging.getLogger()
    if args.debug is not None:
        logger.setLevel(args.debug)
        logger.info("Set global debug level to: %i" % (args.debug,))
    else:
        logger.setLevel(30)

    # process archive
    dec = Decompressor()
    dec.open(args.path)
    [print(x) for x in dec.get_file_list()]
    dec.close()
