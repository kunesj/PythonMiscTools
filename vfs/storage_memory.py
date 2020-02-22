#!/usr/bin/python3
# coding: utf-8

import logging
from typing import Union
import os
import io

from ..binarydatastream import BinaryDataStream

from .storage_interface import StorageInterface, StorageIndexItem
from . import vfs_utils

_logger = logging.getLogger(__name__)


class StorageMemory(StorageInterface):

    def __init__(self, *args, **kwargs):
        self.binary_data = {}
        super().__init__(*args, **kwargs)

    @classmethod
    def validate_uri(cls, uri: Union[str, None]) -> bool:
        return uri is None

    def build_index(self) -> None:
        self.index = {}
        for path in self.binary_data:
            file_type = vfs_utils.parse_file_type(os.path.basename(path))
            self.index[path] = StorageIndexItem(file_type=file_type)

    # Files

    def get(self, path: str) -> BinaryDataStream:
        if not self.exists(path):
            raise FileNotFoundError(path)
        return BinaryDataStream(self.binary_data[path])

    def set(self, path: str, data: BinaryDataStream) -> None:
        last_pos = self.tell()  # remember last position
        data.seek(0x0, io.SEEK_SET)  # move to start of stream
        self.binary_data[path] = data.read()  # save bytes
        data.seek(last_pos, io.SEEK_SET)  # move back to last position
        # update index
        file_type = vfs_utils.parse_file_type(os.path.basename(path))
        self.index[path] = StorageIndexItem(file_type=file_type)

    def delete(self, path: str) -> None:
        if not self.exists(path):
            raise FileNotFoundError(path)
        del(self.binary_data[path])
        # update index
        del(self.index[path])
