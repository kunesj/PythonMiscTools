#!/usr/bin/env python3
# encoding: utf-8

import logging
logger = logging.getLogger(__name__)

import os
import sqlite3

from caseinsensitivedict import CaseInsensitiveDict

class GenericDatabase(object):
    """
    Very basic database class, that should ease working with SQL databases.
    """

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
    # Tables
    ###

    # TODO - working with tables

    ###
    # Fetch row dictionary methods
    ###

    def _rowsToDict(self, rows):
        """
        Input: list of rows from last query via self.litecursor.fetchall() etc..
        Private method
        """
        result = []
        for row in rows:
            row_dict = {}
            for i, column in enumerate(self.litecursor.description):
                column_name = column[0]
                row_dict[column_name] = row[i]
            result.append(row_dict)
        return result

    def fetchOneDict(self):
        """ Replaces self.litecursor.fetchone(), returns dict() """
        return self._rowsToDict([self.litecursor.fetchone()])

    def fetchManyDict(self, size):
        """ Replaces self.litecursor.fetchmany(size), returns [dict(), dict(), ...] """
        return self._rowsToDict(self.litecursor.fetchmany(size))

    def fetchAllDict(self):
        """ Replaces self.litecursor.fetchall(), returns [dict(), dict(), ...] """
        return self._rowsToDict(self.litecursor.fetchall())

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

    def dict2Lists(self, data_dict):
        """ Splits dictionary into 2 lists with keys and values separated """
        keys = []; values = []
        for key in data_dict:
            keys.append(key)
            values.append(data_dict[key])
        return keys, values

    def buildCondition(self, column_name, column_value, comparison_type): # TODO - BETWEEN, NOT BETWEEN, LIKE, NOT LIKE
        """
        Input:
            column_name - name of column to compare
            column_value - value to compare with (can be list for IN, NOT IN)
            comparison_type - type of comparision (supported types: =, !=, <>, <, >, <=, >=, IN, NOT IN)

        Returns:
            condition_string => "column_name NOT IN (?,?,?)"
            condition_values => [5, 6, 7]

        Returns "1=1", [] if column_name is None
        """
        if column_name is None:
            return "1=1", []

        # list of values to compare with
        condition_values = column_value if type(list()) == type(column_value) else [column_value,]

        if comparison_type in ["=", "!=", "<>", "<", ">", "<=", ">="]:
            return "%s%s?" % (column_name, comparison_type), condition_values

        elif comparison_type.strip().upper() == "IN":
            return "%s IN (%s)" % ( column_name, ", ".join("?"*len(condition_values)) ), condition_values

        elif comparison_type.strip().upper() == "NOT IN":
            return "%s NOT IN (%s)" % ( column_name, ", ".join("?"*len(condition_values)) ), condition_values

        else:
            raise Exception("Unsupported Comparison Type! : '%s'" % comparison_type)

    ###
    # Generic Row Operations
    ###

    def addRow(self, table_name, row_dict):
        row_dict = self.stripDict(table_name, row_dict) # strip dict

        # create sql query command
        column_names, column_values = self.dict2Lists(row_dict)
        query_str = "INSERT INTO %s (%s) VALUES (%s)" % ( table_name, ", ".join(column_names),
            ", ".join([ "?" for x in range(len(row_dict))]) )
        query_vals = tuple(column_values)

        # excute query
        self.litecursor.execute(query_str, query_vals)
        self.liteconnection.commit()

        # return added row id
        return self.litecursor.lastrowid

    def getRowsBy(self, table_name, column_name=None, column_value=None, comparison_type="="):
        """ column_value - can be list """
        # create sql query command
        condition_string, condition_values = self.buildCondition(column_name, column_value, comparison_type)
        query_str = "SELECT * FROM %s WHERE %s" % (table_name, condition_string)
        query_vals = tuple(condition_values)

        # excute query
        self.litecursor.execute(query_str, query_vals)
        return self.fetchAllDict()

    def updateRowsBy(self, row_dict, table_name, column_name=None, column_value=None, comparison_type="="):
        """ column_value - can be list """
        row_dict = self.stripDict(table_name, row_dict) # strip dict

        # create sql query command
        condition_string, condition_values = self.buildCondition(column_name, column_value, comparison_type)
        column_names, column_values = self.dict2Lists(row_dict)
        query_str = "UPDATE %s SET %s WHERE %s" % ( table_name,
            ", ".join([ k+"=?" for k in column_names ]), condition_string )
        query_vals = tuple(column_values+condition_values)

        # excute query
        self.litecursor.execute(query_str, query_vals)
        self.liteconnection.commit()

    def deleteRowsBy(self, table_name, column_name=None, column_value=None, comparison_type="="):
        """ column_value - can be list """
        # create sql query command
        condition_string, condition_values = self.buildCondition(column_name, column_value, comparison_type)
        query_str = "DELETE FROM %s WHERE %s" % (table_name, condition_string)
        query_vals = tuple(condition_values)

        # excute query
        self.litecursor.execute(query_str, query_vals)
        self.liteconnection.commit()
