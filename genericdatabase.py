#!/usr/bin/env python3
# encoding: utf-8

import logging
logger = logging.getLogger(__name__)

import os
import sqlite3

from caseinsensitivedict import CaseInsensitiveDict

class GenericDatabase(object):

    def __init__(self, databasepath=None):
        self.databasepath = None
        self.liteconnection = None
        self.litecursor = None

        if databasepath is not None:
            self.open(databasepath)

    ###
    # Open/Close/New Database
    ###

    def open(self, databasepath):
        """ Creates connection with existing database """
        if not os.path.isfile(databasepath) or not os.path.exists(databasepath):
            raise Exception("Bad database path: %s" % databasepath)
        self.databasepath = databasepath
        self.liteconnection = sqlite3.connect(self.databasepath)
        self.litecursor = self.liteconnection.cursor()
        logger.info("Openned connection with database: path=%s, SQLite_version=%s" % (self.databasepath, sqlite3.sqlite_version))

    def close(self):
        """ Safely close connection to database """
        self.liteconnection.commit()
        self.liteconnection.close()
        self.databasepath = None
        self.liteconnection = None
        self.litecursor = None
        logger.info('Closed connection with database')

    @classmethod
    def new(cls, databasepath):
        """ Creates new empty database file. Does nothing if database already exists. """
        logger.info("Creating new database at path: %s" % databasepath)
        if os.path.isfile(databasepath) and os.path.exists(databasepath):
            logger.info("There is already existing database file at given path. Will do nothing!" % databasepath)
            return
        liteconnection = sqlite3.connect(databasepath)
        liteconnection.commit()
        liteconnection.close()

    ###
    # Tools
    ###

    def executeSQLScriptFile(self, script_file):
        """ Input: File object """
        self.litecursor.executescript(script_file.read())

    def executeSQLScriptFilepath(self, script_path):
        """ Input: Path of script file """
        with open(script_path, 'r') as f:
            self.executeSQLScriptFile(f)

    def _rowsToDict(self, rows):
        """ Input: list of rows from last query via self.litecursor.fetchall() etc.. """
        result = []
        for row in rows:
            row_dict = {}
            for i, column in enumerate(self.litecursor.description):
                column_name = column[0]
                row_dict[column_name] = row[i]
            result.append(row_dict)
        return result

    def _fetchOneDict(self):
        """ Replaces self.litecursor.fetchone(), returns dict() """
        return self._rowsToDict([self.litecursor.fetchone()])

    def _fetchManyDict(self, size):
        """ Replaces self.litecursor.fetchmany(size), returns [dict(), dict(), ...] """
        return self._rowsToDict(self.litecursor.fetchmany(size))

    def _fetchAllDict(self):
        """ Replaces self.litecursor.fetchall(), returns [dict(), dict(), ...] """
        return self._rowsToDict(self.litecursor.fetchall())

    def getColumnNames(self, table_name):
        """ Returns list of column names for in a table """
        self.litecursor.execute("PRAGMA table_info(%s)" % table_name)
        column_names = []
        for column in self.litecursor.fetchall():
            column_names.append(column[1])
        return column_names

    def stripDict(self, table_name, data_dict):
        """ removing keys that do not have columns in table """
        data_dict = CaseInsensitiveDict(data_dict) # case insensitive
        column_names = self.getColumnNames(table_name)

        stripped_dict = {}
        for colname in column_names:
            if colname in data_dict:
                stripped_dict[colname] = data_dict[colname]

        return stripped_dict

    def processConditions(self, conditions):
        """
        conditions = [ {"column":"column_name", "type":"=", "value":value/values}, ... ]

        supported condition types: "=", "!=", "<>", "<", ">", "<=", ">=", IN, NOT IN

        sort type: {"column":"column_name", "type":"ORDER BY", "value":"desc"/"asc"}


        type defaults to "="

        returns: cond_str"", cond_values[]
        """
        if len(conditions)==0:
            return "", []

        cond_values = []; cond_list = []
        sort_str = ""; sort_value = ""

        for x in conditions:
            if "type" not in x:
                x["type"] = "=" # default to this condition type

            if x["type"] in ["=", "!=", "<>", "<", ">", "<=", ">="]:
                cond_list.append("%s%s?" % (x["column"], x["type"]))
                cond_values.append(x["value"])

            elif x["type"].lower() in ["in", "not in"]: # not tested
                negation_str = "NOT " if x["type"].lower().startswith("not ") else ""
                cond_list.append("%s %sIN (%s)" % (x["column"], negation_str, ", ".join("?"*len(list(x["value"]))) ))
                cond_values+list(x["value"])

            # TODO - BETWEEN, NOT BETWEEN, LIKE, NOT LIKE

            elif x["type"].lower() in ["order by", "sort"]:
                x["value"] = "ASC" if x["value"].lower()=="asc" else "DESC"
                sort_str = "ORDER BY ? %s" % x["value"]
                sort_value = x["column"]

            else:
                raise Exception("Unsupported condition error '%s'!" % x["type"])

        cond_str = "WHERE "+" AND ".join(cond_list)

        # add sort data
        if sort_str != "":
            cond_str += " %s" % sort_str
            cond_values.append(sort_value)

        return cond_str, cond_values

    ###
    # Get/Set Generic
    ###

    def addRow(self, table_name, data_dict):
        stripped_dict = self.stripDict(table_name, data_dict)

        # create sql query command
        value_str = ", ".join([ "?" for x in range(len(stripped_dict))])
        column_names = []
        arg_list = []
        for key in stripped_dict:
            column_names.append(key)
            arg_list.append(stripped_dict[key])
        query_str = "INSERT INTO %s (%s) VALUES (%s)" % (table_name, ", ".join(column_names), value_str)
        arg_tuple = tuple(arg_list)

        # excute query
        self.litecursor.execute(query_str, arg_tuple)
        self.liteconnection.commit()

        # return added row id
        return self.litecursor.lastrowid

    def addRows(self, table_name, data_dict_list):
        for data_dict in data_dict_list:
            self.addRow(table_name, data_dict)

    def updateRows(self, table_name, data_dict, condition_string="", condition_values=[]):
        """
        Use self.processConditions() method to prepare condition_string, condition_values variables.
        """
        stripped_dict = self.stripDict(table_name, data_dict)

        # create sql query command
        arg_list = []
        set_list = []
        for key in stripped_dict:
            set_list.append(key)
            arg_list.append(stripped_dict[key])
        set_str = ", ".join([ k+"=?" for k in set_list ])
        arg_tuple = tuple(arg_list+condition_values)
        query_str = "UPDATE %s SET %s %s" % (table_name, set_str, condition_string)

        # excute query
        self.litecursor.execute(query_str, arg_tuple)
        self.liteconnection.commit()

    def selectRows(self, table_name, condition_string="", condition_values=[]):
        """
        Use self.processConditions() method to prepare condition_string, condition_values variables.
        """
        self.litecursor.execute("SELECT * FROM %s %s" % (table_name, condition_string), tuple(condition_values))
        return self._fetchAllDict()

    def deleteRows(self, table_name, condition_string="", condition_values=[]):
        """
        Use self.processConditions() method to prepare condition_string, condition_values variables.
        """
        if condition_string == "":
            raise Exception("Tried to call deleteRows without any conditions!")
        self.litecursor.execute("DELETE FROM %s %s" % (table_name, condition_string), tuple(condition_values))
        self.liteconnection.commit()
