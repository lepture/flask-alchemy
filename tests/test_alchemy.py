# coding: utf-8

import os
import tempfile
import unittest
import sqlite3
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


def query_tables(path):
    sql = "SELECT name from sqlite_master WHERE type = 'table';"
    conn = sqlite3.connect(path)
    cursor = conn.execute(sql)
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return list(map(lambda o: o[0], data))


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

        data = query_tables(self.db_default.db_file)
        assert 'user' in data
        assert 'topic' not in data

        data = query_tables(self.db_alt.db_file)
        assert 'topic' in data
        assert 'user' not in data

        db.drop_all()
        data = query_tables(self.db_default.db_file)
        assert len(data) == 0

        data = query_tables(self.db_alt.db_file)
        assert len(data) == 0

    def test_master_slave(self):
        db = Alchemy()
        config = {
            'ALCHEMY_MASTERS': {
                'default': self.db_default.uri,
            },
            'ALCHEMY_SLAVES': {
                'default': self.db_alt.uri
            }
        }
        db.init_app(config)
        db.register_base(Base)
        db.create_all()

        # make slave
        with open(self.db_default.db_file) as f:
            with open(self.db_alt.db_file, 'wb') as d:
                d.write(f.read())

        user = User(name='alchemy')
        db.session.add(user)
        db.session.commit()
        data = User.query.filter_by(name='alchemy').first()
        assert data is None

        # query from master
        db._config['ALCHEMY_SLAVES'] = None
        data = User.query.filter_by(name='alchemy').first()
        assert data.name == 'alchemy'


class MultipleSlaveTest(unittest.TestCase):
    def setUp(self):
        self.db_default = Database()
        self.db_slave_1 = Database()
        self.db_slave_2 = Database()

    def tearDown(self):
        self.db_default.close()
        self.db_slave_1.close()
        self.db_slave_2.close()

    def test_master_slave(self):
        db = Alchemy()
        config = {
            'ALCHEMY_MASTERS': {
                'default': self.db_default.uri,
            },
            'ALCHEMY_SLAVES': {
                'default': [
                    self.db_slave_1.uri,
                    self.db_slave_2.uri,
                ]
            }
        }
        db.init_app(config)
        db.register_base(Base)
        db.create_all()

        # make slave
        with open(self.db_default.db_file) as f:
            # create slave without data
            with open(self.db_slave_2.db_file, 'wb') as d:
                d.write(f.read())

        user = User(name='alchemy')
        db.session.add(user)
        db.session.commit()

        # copy one slave
        with open(self.db_default.db_file) as f:
            with open(self.db_slave_1.db_file, 'wb') as d:
                d.write(f.read())

        rv = []
        for i in range(40):
            rv.append(User.query.filter_by(name='alchemy').first())

        assert any(rv)
        assert not all(rv)
