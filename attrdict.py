#!/usr/bin/python3
# coding: utf-8


class AttrDict(dict):
    """
    Modified dictionary that allows accessing data with attributes instead of keys.
    Example: foo['bar'] => foo.bar

    Some pros:
        - It actually works!
        - No dictionary class methods are shadowed (e.g. .keys() work just fine)
        - Attributes and items are always in sync
        - Trying to access non-existent key as an attribute correctly raises AttributeError instead of KeyError

    Cons:
        - Methods like .keys() will not work just fine if they get overwritten by incoming data
        - Causes a memory leak in Python < 2.7.4 / Python3 < 3.2.3
        - Pylint goes bananas with E1123(unexpected-keyword-arg) and E1103(maybe-no-member)
        - For the uninitiated it seems like pure magic.
    """
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self
