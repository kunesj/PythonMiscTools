#!/usr/bin/python3
# coding: utf-8
import logging
import pickle
from collections import OrderedDict, namedtuple
from typing import Union, Tuple, Iterable
import os

from ..binarydatastream import BinaryDataStream
from ..caseinsensitivedict import CaseInsensitiveDict
from ..fileprint import fileprint

from .storage_interface import StorageInterface
from .storage_directory import StorageDirectory
from .storage_memory import StorageMemory
from . import vfs_utils

_logger = logging.getLogger(__name__)

VFSIndexItem = namedtuple('VFSIndexItem', 'storage storage_path')


class VirtualFileSystem(object):

    STORAGE_CLASSES = {StorageMemory, StorageDirectory, }

    def __init__(self, case_sensitive=False):
        self.case_sensitive = case_sensitive
        self.storage_list = set()
        self.index = {} if self.case_sensitive else CaseInsensitiveDict()

    # storage

    @classmethod
    def add_storage_class(cls, storage_class: type) -> None:
        assert issubclass(storage_class, StorageInterface)
        # noinspection PyTypeChecker
        cls.STORAGE_CLASSES.add(storage_class)

    def add_storage(self, storage_object: StorageInterface) -> None:
        self.storage_list.add(storage_object)

    def remove_storage(self, storage_object: StorageInterface) -> None:
        if storage_object in self.storage_list:
            self.storage_list.remove(storage_object)

    def load_storage_uri(self, uri: str) -> None:
        _logger.info(f'Loading VFS storage URI: {uri}')
        if any(storage.uri == uri for storage in self.storage_list):
            _logger.warning(f'Duplicate VFS storage URI detected: {uri}')

        for storage_class in self.STORAGE_CLASSES:
            if storage_class.validate_uri(uri):
                storage = storage_class(uri)
                self.add_storage(storage)
                return

        raise Exception(f'Unsupported storage URI: {uri}')

    # paths

    def normalize_path(self, path: str) -> str:
        """
        Used on paths before they are processed into index and before they are searched in index
        :param path: VFS path
        :return: normalized VFS path
        """
        # windows path to unix path
        path = path.replace('\\', '/')
        return path

    def parse_path(self, path: str) -> Tuple[str, Union[str, None]]:
        """
        :param path: VFS path
        :return: tuple(normalized path without file extension, lowercase file extension or None)
        """
        normalized_path = self.normalize_path(path)
        dir_name = os.path.dirname(normalized_path)
        file_name = os.path.basename(normalized_path)

        # get file type (extension)
        file_type = vfs_utils.parse_file_type(file_name)

        # get common file name
        if file_type is None:
            common_file_name = file_name
        else:
            common_file_name = file_name[:-(len(file_type)+1)]

        # get common path
        common_path = os.path.join(dir_name, common_file_name)

        return common_path, file_type

    # index

    def build_index(self):
        """
        self.index[common_path][file_type] = VFSIndexItem(storage=storage, storage_path=storage_path)

        Example:
            storage = StorageInterface object
            storage_path = 'Img/Player/Hand.PNG'
            common_path = 'Img/Player/Hand'
            file_type = 'png'

        - If file_type in Storage index is different from file_type (extension) detected from storage_path, file_type from Storage index will be used.
        - This means that created VFS path might have different extension than storage_path.
        - File type is always lowercase.
        - Everything after first '.' is converted into file type (extension)
        """
        _logger.info('Building VFS index')
        self.index = {} if self.case_sensitive else CaseInsensitiveDict()
        for storage in self.storage_list:
            for storage_path in storage.index:
                # parse common path
                common_path, _ = self.parse_path(storage_path)
                if common_path not in self.index:
                    self.index[common_path] = OrderedDict()
                # use file type (extension) defined by Storage
                file_type = storage.index[storage_path].file_type
                # ensure correct order (oldest file to newest)
                if file_type in self.index[common_path]:
                    del(self.index[common_path][file_type])
                # save
                self.index[common_path][file_type] = VFSIndexItem(storage=storage, storage_path=storage_path)

    # files

    def exists(self, path: str, alt_types: Union[Iterable, None] = None) -> Tuple[bool, Union[str, None]]:
        """
        :param path: VFS path
        :param alt_types: list of alternative file types
        :return: tuple(True if found, file type of found file)
        """
        common_path, ft = self.parse_path(path)
        alt_types = [(x.lower() if isinstance(x, str) else x) for x in set((alt_types or []) + [ft, ])]
        if common_path in self.index:
            for file_type in alt_types:
                if file_type in self.index[common_path]:
                    return True, file_type
        return False, None

    def get(self, path: str, alt_types: Union[Iterable, None] = None) -> Tuple[BinaryDataStream, Union[str, None]]:
        """
        :param path: VFS path
        :param alt_types: list of alternative file types
        :return: tuple(BinaryDataStream, file type of found file)
        """
        found, file_type = self.exists(path, alt_types=alt_types)
        if found:
            common_path, _ = self.parse_path(path)
            index_item = self.index[common_path][file_type]
            return index_item.storage.get(index_item.storage_path), file_type
        else:
            raise FileNotFoundError(path)

    # Debugging

    def dump_structure(self, quiet=True, tofile=True):
        f = open('vfs_dump.txt', 'w') if tofile else None

        fileprint('---|VFS-Dump.Storages|------------------------------------------', openfile=f, quiet=quiet)
        for i, s in enumerate(self.storage_list):
            fileprint(f'{i}: {s}', openfile=f, quiet=quiet)
        fileprint('---|VFS-Dump.Files|---------------------------------------------', openfile=f, quiet=quiet)
        for common_path in sorted(self.index.keys()):
            for file_type in self.index[common_path]:
                if file_type is None:
                    full_path = common_path
                else:
                    full_path = f'{common_path}.{file_type}'
                fileprint(f'{full_path: <50}{self.index[common_path][file_type]}', openfile=f, quiet=quiet)
        fileprint('---|VFS-Dump.End|-----------------------------------------------', openfile=f, quiet=quiet)

        if f:
            f.close()
            print('Dumped VFS index to vfs_dump.txt')

    def get_memory_usage(self):
        _logger.info('[VFS-MEM] Analyzing VFS memory usage')
        sum_usage = 0

        # storage memory usage
        for i, storage in enumerate(self.storage_list):
            try:
                usage = storage.get_memory_usage()
                sum_usage += usage
            except Exception:
                _logger.exception(f'[VFS-MEM] Storage {i}: {storage}: Error when getting memory usage!')
            else:
                _logger.info(f'[VFS-MEM] Storage {i}: {storage}: {usage} bytes')

        # index memory usage
        usage_index = len(pickle.dumps(self.index))
        sum_usage += usage_index
        _logger.info(f'[VFS-MEM] Index: {usage_index} bytes')

        # total
        _logger.info(f'[VFS-MEM] Total: {sum_usage} bytes')

        return sum_usage


if __name__ == '__main__':
    logging.basicConfig()
    _logger = logging.getLogger()
    _logger.setLevel(logging.INFO)

    vfs = VirtualFileSystem()
    vfs.load_storage_uri('file://~/Desktop')
    vfs.build_index()

    vfs.dump_structure(quiet=False, tofile=False)
    vfs.get_memory_usage()
