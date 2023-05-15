import yaml


class CheckPointDatabase:
    def __init__(self, name):
        self.name = name or 'default'
        self._cache = None
        self.load()

    def __str__(self):
        return f'CheckPointDatabase({self.name})'

    def __del__(self):
        self.save()

    @property
    def filename(self):
        return f'./db/chkpt_{self.name}.yaml'

    def load(self):
        try:
            with open(self.filename) as f:
                self._cache = yaml.load(f, Loader=yaml.SafeLoader)
        except FileNotFoundError:
            self._cache = {}

    def save(self):
        with open(self.filename, 'w') as f:
            yaml.dump(self._cache, f, default_flow_style=False)

    def set_checkpoint(self, key, value):
        self._cache[key] = value
        self.save()

    def get_checkpoint(self, key):
        return self._cache.get(key)
