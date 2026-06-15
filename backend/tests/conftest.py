import os
import sys
import types
import importlib

# Insert repo root so `import backend` works in tests
_backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
_repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)


# Provide a lightweight fake `pymongo` to avoid network calls during imports
if 'pymongo' not in sys.modules:
    pymongo_mod = types.ModuleType('pymongo')

    class FakeCollection:
        def __init__(self):
            self._data = []

        def insert_one(self, doc):
            self._data.append(doc)
            class R: pass
            R.inserted_id = str(len(self._data))
            return R()

        def find_one(self, query=None):
            query = query or {}
            for d in self._data:
                match = True
                for k, v in query.items():
                    if d.get(k) != v:
                        match = False
                        break
                if match:
                    return d
            return None

        def find(self, query=None):
            return list(self._data)

        def update_one(self, q, update):
            for d in self._data:
                match = True
                for k, v in q.items():
                    if d.get(k) != v:
                        match = False
                        break
                if match:
                    set_ops = update.get('$set', {})
                    d.update(set_ops)
                    return type('R', (), {'modified_count': 1})()
            return type('R', (), {'modified_count': 0})()

        def find_one_and_update(self, q, update, return_document=None):
            for d in self._data:
                match = True
                for k, v in q.items():
                    if d.get(k) != v:
                        match = False
                        break
                if match:
                    set_ops = update.get('$set', {})
                    d.update(set_ops)
                    return d
            return None

        def delete_one(self, q):
            for i, d in enumerate(self._data):
                match = True
                for k, v in q.items():
                    if d.get(k) != v:
                        match = False
                        break
                if match:
                    self._data.pop(i)
                    return type('R', (), {'deleted_count': 1})()
            return type('R', (), {'deleted_count': 0})()

    class FakeDB:
        def __init__(self):
            self.users = FakeCollection()
            self.subusers = FakeCollection()
            self.feedbacks = FakeCollection()
            self.sentiment_analysis = FakeCollection()
            self.videos = FakeCollection()
            self.templates = FakeCollection()

        def get_collection(self, name):
            return getattr(self, name, FakeCollection())

    class FakeMongoClient:
        def __init__(self, *args, **kwargs):
            self._db = FakeDB()

        def __getitem__(self, name):
            return self._db

        def get_database(self, name=None):
            return self._db

    pymongo_mod.MongoClient = FakeMongoClient
    class _ReturnDocument:
        AFTER = 'AFTER'
    pymongo_mod.ReturnDocument = _ReturnDocument
    sys.modules['pymongo'] = pymongo_mod


# Lightweight fake `bson` with ObjectId wrapper used in the codebase
if 'bson' not in sys.modules:
    bson_mod = types.ModuleType('bson')

    class ObjectId:
        def __init__(self, val=None):
            # keep simple: store string form
            self._val = str(val) if val is not None else ''

        def __str__(self):
            return self._val

        def __repr__(self):
            return f"ObjectId('{self._val}')"

        def __eq__(self, other):
            if isinstance(other, ObjectId):
                return self._val == other._val
            return self._val == str(other)

    bson_mod.ObjectId = ObjectId
    sys.modules['bson'] = bson_mod
    # also provide bson.objectid module used by some imports
    obj_mod = types.ModuleType('bson.objectid')
    obj_mod.ObjectId = ObjectId
    sys.modules['bson.objectid'] = obj_mod


def _import_app():
    # Import the app after shimming pymongo so database initialization is safe
    import backend.app as appmod
    return appmod


import pytest


@pytest.fixture(scope='session')
def flask_app():
    appmod = _import_app()
    app = appmod.create_app()
    app.config['TESTING'] = True
    return app


@pytest.fixture
def client(flask_app):
    return flask_app.test_client()


@pytest.fixture
def fake_db():
    # Return the FakeDB instance created by our FakeMongoClient
    client = sys.modules['pymongo'].MongoClient()
    return client.get_database()
