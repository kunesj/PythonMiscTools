#!/usr/bin/python3
# coding: utf-8

import logging
from typing import Union
import pickle

from ..binarydatastream import BinaryDataStream

_logger = logging.getLogger(__name__)


class StorageIndexItem(object):

    def __init__(self, file_type=None, **kwargs):
        self.file_type = file_type
        for key in kwargs:
            setattr(self, key, kwargs[key])


class StorageInterface(object):
    """
    Base class that should be inherited by any classes that deal with accessing data from filesystem, archives,
    memory, etc..
    Paths inside Storage are always case sensitive. Case sensitivity/insensitivity is decided at VFS level.

    Attributes:
        uri         str; Uniform Resource Identifier (https://en.wikipedia.org/wiki/Uniform_Resource_Identifier)
        index       dict; {path: IndexItem(type=resource_type), path: IndexItem(type=resource_type), ...}
    """

    def __init__(self, uri: Union[str, None] = None):
        """
        :param uri: Uniform Resource Identifier
        """
        self.uri = uri
        self.index = {}
        self.build_index()

    def __str__(self):
        return f'{self.__class__.__name__}({repr(self.uri)})'

    def __repr__(self):
        return self.__str__()

    def __getattribute__(self, name):
        # Force logging decorators in child classes
        attr = object.__getattribute__(self, name)
        if hasattr(attr, '__call__') and name in ['load_uri', 'get']:
            def wrapper(*args, **kwargs):
                if name == 'load_uri':
                    _logger.debug(f'Loading {self.__class__.__name__}: {self.uri}')
                elif name == 'get':
                    path = args[0] if args else kwargs.get('path')
                    _logger.debug(f'Loading file: {path}')
                return attr(*args, **kwargs)
            return wrapper
        else:
            return attr

    def get_memory_usage(self):
        return len(pickle.dumps(self))

    @classmethod
    def validate_uri(cls, uri: Union[str, None]) -> bool:
        """
        :param uri: Uniform Resource Identifier
        :return: True, if uri points to valid source
        """
        raise NotImplementedError

    def build_index(self) -> None:
        """
        Executing this method should enable usage of all member methods
        """
        raise NotImplementedError

    # Files

    def exists(self, path: str) -> bool:
        """
        :param path:
        :return: True, if path was found in storage
        """
        return path in self.index

    def get(self, path: str) -> BinaryDataStream:
        """
        :param path: path to file inside storage
        :return: BinaryDataStream
        """
        raise NotImplementedError

    def set(self, path: str, data: BinaryDataStream) -> None:
        """
        :param path: path to file inside storage
        :param data: BinaryDataStream
        """
        raise RuntimeError(f'Storage {self.__class__.__name__} is read only!')

    def delete(self, path: str) -> None:
        """
        :param path: path to file inside storage
        """
        raise RuntimeError(f'Storage {self.__class__.__name__} is read only!')
