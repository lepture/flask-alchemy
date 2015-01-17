# coding: utf-8

import os
import tempfile
import unittest
from flask_alchemy import Alchemy
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Database(object):
    def __init__(self):
        self.db_fd, self.db_file = tempfile.mkstemp()

    def __enter__(self):
        return self.db_file

    def __exit__(self, type, value, traceback):
        self.close()

    @property
    def uri(self):
        return 'sqlite:///%s' % self.db_file

    def close(self):
        os.close(self.db_fd)
        os.unlink(self.db_file)


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(20))


class Topic(Base):
    __tablename__ = 'topic'
    id = Column(Integer, primary_key=True)
    title = Column(String(20))


class AlchemyTest(unittest.TestCase):
    def setUp(self):
        self.db_default = Database()
        self.db_alt = Database()

    def tearDown(self):
        self.db_default.close()
        self.db_alt.close()

    def test_create_all(self):
        db = Alchemy()
        config = {
            'ALCHEMY_MASTERS': {
                'default': self.db_default.uri,
                'alt': self.db_alt.uri
            },
            'ALCHEMY_BIND_KEYS': {
                'topic': 'alt'
            }
        }
        db.init_app(config)
        db.register_base(Base)
        db.create_all()
