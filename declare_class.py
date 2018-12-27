#!/usr/bin/env python
# -*- coding: utf-8 -*-

clsregistry = dict()


class Meta(type):
    """ Make new classes always inherit from newest subclass """
    def __new__(cls, name, bases, dct):
        if name != 'Base':
            # add class name variable if missing. Try to parse from base class, if that fails set it to 'name'.
            if '__declared_class_name__' not in dct:
                class_name = name
                for class_var in bases:
                    if hasattr(class_var, '__declared_class_name__'):
                        class_name = class_var.__declared_class_name__
                        break
                dct['__declared_class_name__'] = class_name

            # update base classes to newest child class
            tmp = []
            for class_var in bases:
                if hasattr(class_var, '__declared_class_name__') and class_var.__declared_class_name__ in clsregistry:
                    class_var = clsregistry[class_var.__declared_class_name__]
                tmp.append(class_var)
            bases = tuple(tmp)

            # build new class and save for next request
            new_class = super().__new__(cls, name, bases, dct)
            clsregistry[dct['__declared_class_name__']] = new_class

        else:
            # init of Base class
            new_class = super().__new__(cls, name, bases, dct)

        return new_class


def declarative_base(base=None):
    """
    Tries to do what sqlalchemy.ext.declarative.declarative_base does with classes.
    But without any SQL or database table stuff. Just changing how Python inherits a class.
    """
    bases = (base, ) if base else ()
    dct = {}
    return Meta('Base', bases, dct)


Base = declarative_base()

