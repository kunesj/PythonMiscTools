#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
import io
from typing import Union

from .archiver_interface import ArchiverInterface

logger = logging.getLogger(__name__)


class Decompressor(object):

    ARCHIVERS = set()
    EXTENSIONS = set()

    def __init__(self, path: Union[str, None] = None, extension: Union[str, None] = None):
        self.opened_archive = None
        if path:
            self.open(path, extension=extension)

    @classmethod
    def add_archiver(cls, archiver: type) -> None:
        assert issubclass(archiver, ArchiverInterface)
        cls.ARCHIVERS.add(archiver)
        cls.EXTENSIONS |= archiver.EXTENSIONS
        logger.info(f'Added archiver {archiver.__class__.__name__} supporting file types: {archiver.EXTENSIONS}')

    def archive_opened(self) -> bool:
        """ Checks if there is any opened archive """
        return self.opened_archive is not None

    def open(self, archive_path: str, extension: Union[str, None] = None) -> None:
        """ Opens archive """
        # close any opened archives
        self.close()

        # get extension
        if extension is None:
            filename, extension = os.path.splitext(archive_path)
            extension = extension.replace('.', '')

        # get supported archiver and open archive with it
        for archiver in self.ARCHIVERS:
            if extension in archiver.EXTENSIONS:
                self.opened_archive = archiver(archive_path)

        # check if found archiver that supports extension
        if self.opened_archive is None:
            raise Exception(f'Archive extension "{extension}" not supported!')

    def close(self) -> None:
        """ close any opened archives """
        if self.archive_opened():
            self.opened_archive.close()
        self.opened_archive = None

    def get_file_list(self) -> list:
        """ Returns list of files in archive """
        if not self.archive_opened():
            raise Exception('No archive opened!')
        return self.opened_archive.get_file_list()

    def open_file(self, file_path: str) -> io.BytesIO:
        """ Returns stream """
        if not self.archive_opened():
            raise Exception('No archive opened!')
        return io.BytesIO(self.opened_archive.open_file(file_path))

    def extract_file(self, file_path: str, extract_path: str) -> None:
        """ Extracts file to path """
        if not self.archive_opened():
            raise Exception('No archive opened!')
        self.opened_archive.extract_file(file_path, extract_path)


# Add default archivers

from .archiver_zip import ArchiverZip
Decompressor.add_archiver(ArchiverZip)

from .archiver_tar import ArchiverTar
Decompressor.add_archiver(ArchiverTar)

try:
    from .archiver_rar import ArchiverRar
    Decompressor.add_archiver(ArchiverRar)
except ImportError as e:
    logger.warning(f'Unable to load archiver for rar files: {e}')
    ArchiverRar = None

try:
    from .archiver_7z import Archiver7z
    Decompressor.add_archiver(Archiver7z)
except ImportError as e:
    logger.warning(f'Unable to load archiver for 7z files: {e}')
    Archiver7z = None


if __name__ == '__main__':
    import argparse

    # Parsing input parameters
    parser = argparse.ArgumentParser(
        description='decompressor'
    )
    parser.add_argument(
        'path',
        help='Path to archive'
    )
    parser.add_argument(
        '-l', '--list', action='store_true',
        help='List files in archive'
    )
    parser.add_argument(
        '-d', '--debug', type=int, choices=[50, 40, 30, 20, 10, 1], default=None,
        help='Set global debug level [CRITICAL=50, ERROR=40, WARNING=30, INFO=20, DEBUG=10, SPAM=1]. '
             'Default level is WARNING.'
    )
    args = parser.parse_args()

    # Logger configuration
    logger = logging.getLogger()
    if args.debug is not None:
        logger.setLevel(args.debug)
        logger.info(f'Set global debug level to: {args.debug}')
    else:
        logger.setLevel(30)

    # process archive
    dec = Decompressor()
    dec.open(args.path)
    file_list = dec.get_file_list()
    for file_path in file_list:
        print(file_path)
    print(f'first_file: {dec.open_file(file_list[0])}')
    dec.close()
