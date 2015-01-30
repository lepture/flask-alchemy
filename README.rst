Flask-Alchemy
=============

**WIP**

Flask-Alchemy is designed to work with SQLAlchemy default declarative_base,
with powerful master-slave and separated databases support.

.. image:: https://img.shields.io/badge/flask-unregistered-red.svg?style=flat
   :target: https://github.com/pocoo/metaflask
   :alt: Meta Flask
.. image:: https://pypip.in/wheel/flask-alchemy/badge.svg?style=flat
   :target: https://pypi.python.org/pypi/flask-alchemy/
   :alt: Wheel Status
.. image:: https://pypip.in/version/flask-alchemy/badge.svg?style=flat
   :target: https://pypi.python.org/pypi/flask-alchemy/
   :alt: Latest Version
.. image:: https://travis-ci.org/lepture/flask-alchemy.svg?branch=master
   :target: https://travis-ci.org/lepture/flask-alchemy
   :alt: Travis CI Status
.. image:: https://coveralls.io/repos/lepture/flask-alchemy/badge.svg?branch=master
   :target: https://coveralls.io/r/lepture/flask-alchemy
   :alt: Coverage Status


Getting Started
---------------

Flask-Alchemy is designed to work with plain SQLAlchemy models, if describe
it in code, a plain model should be something like::

    from sqlalchemy import Column, Integer, String
    from sqlalchemy.ext.declarative import declarative_base

    Base = declarative_base()

    class User(Base):
        __tablename__ = 'user'
        id = Column(Integer, primary_key=True)
        name = Column(String(20))


And then we can register the ``Base`` with Flask-Alchemy::

    from your_project import app
    from flask_alchemy import Alchemy

    db = Alchemy(app)
    db.register_base(Base)

With this ``db.register_base``, your ``User`` module can query like::

    baba = User.query.filter_by(name='baba').first()


Advanced Topics
---------------

Flask-Alchemy is more than that, it can bind each table to its own database,
it can send the SELECT query to your slave databases.
