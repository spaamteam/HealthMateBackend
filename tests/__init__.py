#!/usr/bin/python

import unittest

class InitializationTests(unittest.TestCase):

    def test_initialization(self):
        """
        Check the test suite runs by affirming 2+2=4
        """
        self.assertEqual(2+2, 4)


    def test_patient_login(self):
        """
        Checks for object creation for class in Problem 1
        """
        from pymongo import MongoClient
