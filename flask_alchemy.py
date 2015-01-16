"""
    Flask-Alchemy
    ~~~~~~~~~~~~~

    Flask-Alchemy is designed to work with SQLAlchemy default declarative_base,
    with powerful master-slave and separated databases support.
"""

import random
from threading import Lock
from sqlalchemy.orm.session import Session as SessionBase
from sqlalchemy.sql.expression import Select

#: TODO
text_types = (str, unicode)


class Session(SessionBase):
    def __init__(self, db, autocommit=False, autoflush=True, **options):
        self.db = db
        super(Session, self).__init__(
            bind=db.bind,
            autocommit=autocommit,
            autoflush=autoflush,
            **options
        )

    def get_bind(self, mapper, clause=None):
        if mapper is not None:
            key = mapper.mapped_table.__tablename__
            if isinstance(clause, Select):
                # get slave engine
                return self.db.get_engine(key, slave=True)
            return self.db.get_engine(key, slave=False)
        return SessionBase.get_bind(self, mapper, clause)


class Alchemy(object):
    def __init__(self, app=None):
        self._bases = []
        self._binds = {}
        self._bind_keys = {}
        self._engines = {}
        self._engine_lock = Lock()
        self.session = self.create_session()
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

    def create_session(self):
        pass

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

    def get_engine(self, table_name, slave=False):
        with self._engine_lock:
            bind_key = self.get_bind_key(table_name)
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

    def register_base(self, Base):
        Base.query = self.session.query_property()
        # TODO
        for name in Base.metadata.tables:
            bind_key = self.get_bind_key(name)
            table = Base.metadata.tables[name]
        self._bases.append(Base)
