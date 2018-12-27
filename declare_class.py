#!/usr/bin/env python
# -*- coding: utf-8 -*-


class Meta(type):
    """
    When creating subclass, return updated parent class instead.
    """

    _clsregistry = {}

    def __new__(cls, name, bases, dct, _declarative_base=False):
        if _declarative_base:
            # init of Base class
            new_class = super().__new__(cls, name, bases, dct)

        else:
            # Can only inherit from one class  # TODO: inherit from multiple classes
            if len(bases) > 1:
                raise Exception('Can only inherit from one class. Creating new Base class might help?')

            # add class name variable if missing. Try to parse from base class, if that fails set it to 'name'.
            if '__declared_class_name__' not in dct:
                class_name = name
                for class_var in bases:
                    if hasattr(class_var, '__declared_class_name__'):
                        class_name = class_var.__declared_class_name__
                        break
                dct['__declared_class_name__'] = class_name

            # build new class and save for next request
            if dct['__declared_class_name__'] not in cls._clsregistry:
                new_class = super().__new__(cls, name, bases, dct)
                cls._clsregistry[dct['__declared_class_name__']] = new_class

            # update attributes of old class
            else:
                new_class = cls._clsregistry[dct['__declared_class_name__']]
                for attr_key in dct:
                    if attr_key in ['__module__', '__qualname__']:
                        continue
                    setattr(new_class, attr_key, dct[attr_key])

        return new_class


def declarative_base(base=None):
    """
    Tries to do what sqlalchemy.ext.declarative.declarative_base does with classes.
    But without any SQL or database table stuff. Just changing how Python inherits a class.

    >>> Base = declarative_base()
    """
    bases = (base, ) if base else ()
    dct = {}
    return Meta('Base', bases, dct, _declarative_base=True)
