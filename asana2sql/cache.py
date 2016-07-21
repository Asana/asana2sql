class Cache(object):
    """A cache with a backing store.

    """

    def __init__(self, seed_fn, insert_fn, key_name="id"):
        self._seed_fn = seed_fn
        self._insert_fn = insert_fn
        self._key_name = key_name

        self._cache = None
        self._touched = set()

    @staticmethod
    def _row_to_dict(row):
        """Converts a PyODBC row into a dictionary."""
        # (name, type_code, display_size, internal_size, precision, scale,
        # null_ok)
        return {name: getattr(row, name)
                for (name, _, _, _, _, _, _) in row.cursor_description}

    def _prime_cache(self):
        self._cache = {}
        for row in self._seed_fn():
            dict_row = self._row_to_dict(row)
            self._cache[dict_row[self._key_name]] = dict_row

    def _insert_and_cache(self, key, value):
        self._insert_fn(value)
        self._cache[key] = value

    def _touch(self, key):
        self._touched.add(key)

    def get(self, key):
        if self._cache is None:
            self._prime_cache()

        self._touch(key)

        return self._cache.get(key)

    def add(self, new_value):
        if self._cache is None:
            self._prime_cache()

        key = new_value[self._key_name]
        old_value = self._cache.get(key)

        self._touch(key)

        if old_value != new_value:
            self._insert_and_cache(key, new_value)

