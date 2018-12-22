#!/usr/bin/python3
# coding: utf-8


def fileprint(strdata, openfile=None, quiet=False, newline=True):
    """
    Usage:
        with open('f.txt', 'w') as f:
            fileprint('helloworld', f)
    """
    if newline:
        strdata += "\n"
    if not quiet:
        print(strdata, end="")
    if openfile is not None:
        openfile.write(strdata)
