#!/usr/bin/env python3
# encoding: utf-8

import unittest

import tempfile, shutil
import sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from genericdatabase import GenericDatabase

class GenericDatabaseTest(unittest.TestCase):

    def databaseNewOpenClose_test(self):
        """ Basic test for unexpected exceptions """
        # create test env
        tmp_dir = tempfile.mkdtemp()
        db_path = os.path.join(tmp_dir, "database.db")

        # test new, open close
        GenericDatabase.new(db_path)
        gd = GenericDatabase()
        gd.open(db_path)
        gd.close()

        # destroy test env
        shutil.rmtree(tmp_dir)

