#!/usr/bin/python3
# coding: utf-8

import os
import ntpath


def get_filename_extension(fname):
    """ Returns extension of filename or None if the is none. """
    ext = os.path.splitext(fname)[1].lower()
    if ext.startswith("."):
        ext = ext[1:]
    if ext == "":
        ext = None
    return ext


def get_filename_extensionless(fname):
    """ Returns filename without extension """
    ext = get_filename_extension(fname)
    if ext is None:
        common_fname = fname
    else:
        common_fname = fname[:-(len(ext)+1)]
    return common_fname


def get_path_extension(path):
    """ Returns extension from path """
    return get_filename_extension(os.path.basename(path))


def get_path_extensionless(path):
    """ Returns path to file without extension """
    fname_extensionless = get_filename_extensionless(os.path.basename(path))
    common_path = os.path.join(os.path.dirname(path), fname_extensionless)
    return common_path


def get_universal_basename(path):
    """
    Works for both Windows (\) and Unix (/) paths
    Warning: Will return only part of filename on Linux IF there is '\' in it
    """
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)
