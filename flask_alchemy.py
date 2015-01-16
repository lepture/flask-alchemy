"""
    Flask-Alchemy
    ~~~~~~~~~~~~~

    Flask-Alchemy is designed to work with SQLAlchemy default declarative_base,
    with powerful master-slave and separated databases support.
"""

import random
from threading import Lock
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm.session import Session as SessionBase
from sqlalchemy.sql.expression import Select

#: TODO
text_types = (str, unicode)


class Session(SessionBase):
    def __init__(self, db, autocommit=False, autoflush=True, **options):
        self.db = db
        super(Session, self).__init__(
            bind=db.get_engine(),
            autocommit=autocommit,
            autoflush=autoflush,
            **options
        )

    def get_bind(self, mapper, clause=None):
        if mapper is not None:
            key = mapper.mapped_table.__tablename__
            if isinstance(clause, Select):
                # get slave engine
                return self.db.get_table_engine(key, slave=True)
            return self.db.get_table_engine(key, slave=False)
        return SessionBase.get_bind(self, mapper, clause)


class Alchemy(object):
    def __init__(self, app=None, session_options=None):
        self._bases = []
        self._binds = {}
        self._bind_keys = {}
        self._engines = {}
        self._engine_lock = Lock()

        if session_options is None:
            session_options = {}
        self.session = self.create_session(session_options)
        self.app = app

        if app:
            self.init_app(app)

    def init_app(self, app):
        """Init application with configuration.
        """
        #: can work without Flask
        if isinstance(app, dict):
            config = app
        else:
            self.app = app
            config = app.config

        #: {"bind_key": "URI"}
        config.setdefault('ALCHEMY_MASTERS', {'default': 'sqlite://'})
        #: {"bind_key": ["URI"]}
        config.setdefault('ALCHEMY_SLAVES', None)
        #: {"table_name": "bind_key"}
        config.setdefault('ALCHEMY_BIND_KEYS', None)

        master = config.get('ALCHEMY_MASTERS')
        if isinstance(master, text_types):
            master = {'default': master}
            config['ALCHEMY_MASTERS'] = master
        assert 'default' in master, 'default is required in ALCHEMY_MASTERS'

        slave = config.get('ALCHEMY_SLAVES')
        if isinstance(master, text_types):
            slave = {'default': slave}
            config['ALCHEMY_SLAVES'] = slave

        self._config = config
        self._bind_keys = config.get('ALCHEMY_BIND_KEYS', {})

        @app.teardown_appcontext
        def remove_session(response_or_exc):
            self.session.remove()
            return response_or_exc

    def create_session(self, options):
        scopefunc = options.pop('scopefunc', None)

        def session_maker():
            return Session(self, options)

        return scoped_session(session_maker, scopefunc=scopefunc)

    def get_bind_key(self, table_name):
        return self._bind_keys.get(table_name, 'default')

    def get_slave_uri(self, bind_key):
        slave_uris = self._config['ALCHEMY_SLAVES']
        if not slave_uris:
            return None
        uris = slave_uris.get(bind_key)
        if not uris:
            # TODO warning
            return None
        return random.choice(uris)

    def get_engine(self, bind_key='default', slave=False):
        with self._engine_lock:
            uri = None
            if slave:
                uri = self.get_slave_uri(bind_key)
            if not uri:
                uri = self._config['ALCHEMY_MASTERS'].get(bind_key)
            engine = self._engines.get(uri)
            if engine is not None:
                return engine
            engine = self.make_engine(uri)
            self._engines[uri] = engine
            return engine

    def get_table_engine(self, table_name, slave=False):
        bind_key = self.get_bind_key(table_name)
        return self.get_engine(bind_key, slave)

    def register_base(self, Base, bind_key=None):
        Base.query = self.session.query_property()
        self._bases.append(Base)
        if bind_key:
            # register table for bind_keys
            for name in Base.metadata.tables:
                if name not in self._bind_keys:
                    self._bind_keys[name] = bind_key

    def create_all(self, bind_key=None):
        pass

    def drop_all(self, bind_key=None):
        pass
