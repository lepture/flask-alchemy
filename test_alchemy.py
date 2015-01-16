# coding: utf-8

import os
import tempfile
import unittest
from flask_alchemy import Alchemy
from sqlalchemy import Column, Integer
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Database(object):
    def __init__(self):
        self.db_fd, self.db_file = tempfile.mkstemp()

    def __enter__(self):
        return self.db_file

    def __exit__(self, type, value, traceback):
        self.close()

    def close(self):
        os.close(self.db_fd)
        os.unlink(self.db_file)


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)


class AlchemyTest(unittest.TestCase):
    def test_master_slave():
        master = Database()
        slave = Database()
        db = Alchemy({
            'ALCHEMY_MASTERS': master.db_file,
            'ALCHEMY_SLAVES': slave.db_file,
        })
        db.create_all()
