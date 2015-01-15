"""
    Flask-Alchemy
    ~~~~~~~~~~~~~

    Flask-Alchemy is designed to work with SQLAlchemy default declarative_base,
    with powerful master-slave and seprated databases support.
"""

text_types = (str, unicode)


class Alchemy(object):
    def __init__(self, app=None):
        self._bases = []
        self._binds = {}
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

        #: {"bind_name": "URI"}
        config.setdefault('ALCHEMY_MASTERS', {'default': 'sqlite://'})
        #: {"bind_name": ["URI"]}
        config.setdefault('ALCHEMY_SLAVES', None)
        #: {"table_name": "bind_name"}
        config.setdefault('ALCHEMY_BINDS', None)

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
        self._binds = config.get('ALCHEMY_BINDS', {})

    def get_bind(self, table):
        return self._binds.get(table, 'default')

    def register_base(self, Base):
        # TODO: patch Base model
        self._bases.append(Base)
