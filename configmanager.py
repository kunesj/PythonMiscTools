#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Part of PythonMiscTools
# https://github.com/kunesj/PythonMiscTools

# how to import:
# from configmanager import CONFIG_MANAGER

import configparser


class ConfigManager(object):

    def __init__(self):
        self.config = None
        self.clear_config()

    @classmethod
    def get_object(cls):
        return cls()

    def clear_config(self):
        self.config = configparser.ConfigParser(interpolation=None, inline_comment_prefixes=('#',))
        # make case sensitive
        self.config.optionxform = lambda option: option

    def load_config(self, path, update=True):
        if not update:
            self.clear_config()

        try:
            self.config.read(path, encoding="utf-8")
        except Exception:
            print("Couldn't load config file '%s'!" % path)

    def get(self, section, option, lowercase=False):
        val = self.config.get(section, option)
        if isinstance(val, list):  # remove list container
            val = val[0]
        if lowercase:
            val = val.lower()
        return val

    def get_boolean(self, section, option):
        return self.config.getboolean(section, option)

    def get_int(self, section, option):
        str_num = self.get(section, option).strip()
        if str_num.startswith("0x"):
            return int(str_num, 16)
        else:
            return self.config.getint(section, option)

    def get_float(self, section, option):
        return self.config.getfloat(section, option)

    def get_list(self, section, option, lowercase=False):
        str_list = [x.strip() for x in self.get(section, option, lowercase=lowercase).strip().split(",")]
        if len(str_list) == 1 and str_list[0] == "":
            str_list = []
        return str_list

    def get_list_int(self, section, option):
        return [int(x) for x in self.get_list(section, option)]

    def get_list_float(self, section, option):
        return [float(x) for x in self.get_list(section, option)]

    def sections(self):
        return self.config.sections()

    def has_section(self, section):
        return self.config.has_section(section)

    def options(self, section):
        return self.config.options(section)

    def has_option(self, section, option):
        return self.config.has_option(section, option)


CONFIG_MANAGER = ConfigManager.get_object()
