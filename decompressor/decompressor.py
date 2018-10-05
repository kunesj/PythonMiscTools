#!/usr/bin/env python3
# encoding: utf-8

import logging
logger = logging.getLogger(__name__)

import os, io

# zipfile, tarfile lib is included in Python
from eam.decompressor.ziparchiver import ZipArchiver
from eam.decompressor.tararchiver import TarArchiver

try:
    from eam.decompressor.rararchiver import RarArchiver
except ImportError as e:
    logger.warning("Unable to load RarArchiver: %s" % (str(e),))
    RARLIB_INSTALLED = False
else:
    RARLIB_INSTALLED = True

try:
    from eam.decompressor.py7zarchiver import Py7zArchiver
except ImportError as e:
    logger.warning("Unable to load Py7zArchiver: %s" % (str(e),))
    PY7ZLIB_INSTALLED = False
else:
    PY7ZLIB_INSTALLED = True


class Decompressor(object):

    def __init__(self):
        self.archivers = []
        self.opened_archive = None
        self.extensions = []

        self.addArchiver(ZipArchiver())
        self.addArchiver(TarArchiver())
        if RARLIB_INSTALLED:
            self.addArchiver(RarArchiver())
        if PY7ZLIB_INSTALLED:
            self.addArchiver(Py7zArchiver())

        logger.info("Inited Decompressor, supported archive extensions: '%s'" % (", ".join(self.extensions),))

    def addArchiver(self, archiver):
        self.archivers.append(archiver)
        for e in archiver.getSupportedExtensions():
            if e not in self.extensions:
                self.extensions.append(e)
        logger.info("Archiver with supported extensions '%s' added" % (", ".join(archiver.getSupportedExtensions()),))

    def getSupportedExtensions(self):
        return self.extensions

    def archiveOpened(self):
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
        if self.archiveOpened():
            self.opened_archive.close()
        self.opened_archive = None

    def getFileList(self):
        """ Returns list of files in archive """
        if not self.archiveOpened():
            raise Exception("No archive openned!")
        return self.opened_archive.getFileList()

    def openFile(self, filepath):
        """ Returns stream """
        if not self.archiveOpened():
            raise Exception("No archive openned!")
        return io.BytesIO(self.opened_archive.openFile(filepath))

    def extractFile(self, filepath, extractpath):
        """ Extracts file to path """
        if not self.archiveOpened():
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
    [ print(x) for x in dec.getFileList() ]
    dec.close()
