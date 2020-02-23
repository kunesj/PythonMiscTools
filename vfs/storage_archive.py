#!/usr/bin/python3
# coding: utf-8

import os
import logging

from ..binarydatastream import BinaryDataStream
from ..decompressor.decompressor import Decompressor

from .storage_interface import StorageInterface, StorageIndexItem
from . import vfs_utils

_logger = logging.getLogger(__name__)


class StorageArchive(StorageInterface):

    def __init__(self, *args, **kwargs):
        self.fs_path = None
        self.decompressor = Decompressor()
        super().__init__(*args, **kwargs)

    @classmethod
    def validate_uri(cls, uri: str) -> bool:
        path = vfs_utils.convert_uri_to_fs_path(uri)
        if not (path and os.path.isfile(path) and os.path.exists(path)):
            return False
        file_type = vfs_utils.parse_file_type(os.path.basename(path))
        return file_type in [x.lower() for x in Decompressor().EXTENSIONS]

    def build_index(self) -> None:
        # validate path
        if not self.validate_uri(self.uri):
            raise NotADirectoryError(self.uri)
        # build index
        self.index = {}
        self.fs_path = vfs_utils.convert_uri_to_fs_path(self.uri)
        self.decompressor.close()
        self.decompressor.open(self.fs_path)
        for file_path in self.decompressor.get_file_list():
            file_type = vfs_utils.parse_file_type(os.path.basename(file_path))
            self.index[file_path] = StorageIndexItem(file_type=file_type)

    # Files

    def get(self, path: str) -> BinaryDataStream:
        if not self.exists(path):
            raise FileNotFoundError(path)
        return BinaryDataStream(self.decompressor.open_file(path))
