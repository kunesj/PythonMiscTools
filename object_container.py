#!/usr/bin/env python
# -*- coding: utf-8 -*-


class ObjectContainer:
    """
    Useful for having global reference to object/variable that might not be definable at import,
    or might need to be replaced by different object/variable later.
    """

    def __init__(self, obj=None):
        self._wrapped_object = obj

    def replace_wrapped_object(self, obj):
        """ Name of this function MUST NOT have any conflicts with function names of wrapped object """
        self._wrapped_object = obj

    def __str__(self):
        return str(self._wrapped_object)

    def __getattr__(self, attr):
        if attr in self.__dict__:
            return getattr(self, attr)
        return getattr(self._wrapped_object, attr)
