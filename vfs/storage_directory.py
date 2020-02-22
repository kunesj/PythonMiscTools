#!/usr/bin/python3
# coding: utf-8

import os
import io
import logging

from ..binarydatastream import BinaryDataStream

from .storage_interface import StorageInterface, StorageIndexItem
from . import vfs_utils

_logger = logging.getLogger(__name__)


class StorageDirectory(StorageInterface):

    def __init__(self, *args, **kwargs):
        self.fs_path = None
        super().__init__(*args, **kwargs)

    @classmethod
    def validate_uri(cls, uri: str) -> bool:
        path = vfs_utils.convert_uri_to_fs_path(uri)
        return path and os.path.isdir(path) and os.path.exists(path)

    def build_index(self) -> None:
        # validate path
        if not self.validate_uri(self.uri):
            raise NotADirectoryError(self.uri)
        # build index
        self.index = {}
        self.fs_path = vfs_utils.convert_uri_to_fs_path(self.uri)
        for dir_name, subdir_list, file_list in os.walk(self.fs_path):
            for file_name in file_list:
                full_path = os.path.join(dir_name, file_name)
                storage_path = os.path.relpath(full_path, self.fs_path)
                file_type = vfs_utils.parse_file_type(file_name)
                self.index[storage_path] = StorageIndexItem(file_type=file_type)

    # Files

    def get(self, path: str) -> BinaryDataStream:
        if not self.exists(path):
            raise FileNotFoundError(path)
        with io.open(os.path.join(self.fs_path, path), 'rb') as f:
            return BinaryDataStream(f.read())
