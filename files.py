#!/usr/bin/python3
#coding: utf-8

import os

def getFilenameExtension(fname):
    """ Returns extension of filename or None if the is none. """
    ext = os.path.splitext(fname)[1].lower()
    if ext.startswith("."):
        ext = ext[1:]
    if ext == "":
        ext = None
    return ext

def getFilenameExtensionless(fname):
    """ Returns filename without extension """
    ext = getFilenameExtension(fname)
    if ext is None:
        common_fname = fname
    else:
        common_fname = fname[:-(len(ext)+1)]
    return common_fname

def getPathExtension(path):
    """ Returns extension from path """
    return getFilenameExtension(os.path.basename(path))

def getPathExtensionless(path):
    """ Returns path to file without extension """
    fname_extensionless = getFilenameExtensionless(os.path.basename(path))
    common_path = os.path.join(os.path.dirname(path), fname_extensionless)
    return common_path
