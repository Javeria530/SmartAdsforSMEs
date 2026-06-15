import json
import os
import importlib.util
import pytest

# Import app module by file path to avoid PYTHONPATH issues during test runs
_app_path = os.path.join(os.path.dirname(__file__), '..', 'app.py')
spec = importlib.util.spec_from_file_location('backend.app', os.path.abspath(_app_path))
import sys
import types
flask_app_module = importlib.util.module_from_spec(spec)

# Inject a lightweight fake `pymongo` module to avoid network calls during imports
if 'pymongo' not in sys.modules:
    pymongo_mod = types.ModuleType('pymongo')

    class FakeCollection:
        def __init__(self):
            self._data = []

        def insert_one(self, doc):
            self._data.append(doc)
            class R: pass
            R.inserted_id = len(self._data)
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
            return type('R', (), {'modified_count': 0})()

        def delete_one(self, q):
            return type('R', (), {'deleted_count': 0})()

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

    class FakeDB:
        def __init__(self):
            self.users = FakeCollection()
            self.subusers = FakeCollection()
            self.feedbacks = FakeCollection()
            self.sentiment_analysis = FakeCollection()
            self.videos = FakeCollection()

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
# Ensure backend package-relative imports (controllers, config, etc.) resolve
import sys
_backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
_repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
# Ensure repo root is on sys.path so `import backend.*` works
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)
spec.loader.exec_module(flask_app_module)


@pytest.fixture
def client(monkeypatch):
    app = flask_app_module.create_app()
    app.config['TESTING'] = True
    return app.test_client()


def test_signup_success(client, monkeypatch):
    import importlib
    ac = importlib.import_module('controllers.auth_controller')
    # Stub out DB dependent methods on the controller's AuthService reference
    monkeypatch.setattr(ac.AuthService, 'get_user_by_email', staticmethod(lambda e: None))
    monkeypatch.setattr(ac.AuthService, 'create_user', staticmethod(lambda full, email, pw, role='User': {"id": "abc123"}))

    payload = {
        "fullName": "Test User",
        "email": "test@example.com",
        "password": "password123",
        "confirmPassword": "password123",
        "role": "User"
    }

    resp = client.post('/api/signup', data=json.dumps(payload), content_type='application/json')
    assert resp.status_code == 201
    data = resp.get_json()
    assert data.get('success') is True


def test_signup_missing_fields(client):
    payload = {"email": "a@b.com"}
    resp = client.post('/api/signup', json=payload)
    assert resp.status_code == 400


def test_login_success(client, monkeypatch):
    import importlib
    ac = importlib.import_module('controllers.auth_controller')

    fake_user = {"_id": "u1", "email": "a@b.com", "password": "hashed"}
    monkeypatch.setattr(ac.AuthService, 'get_user_by_email', staticmethod(lambda e: fake_user))
    monkeypatch.setattr(ac.AuthService, 'verify_password', staticmethod(lambda pw, h: True))
    monkeypatch.setattr(ac.AuthService, 'update_last_login', staticmethod(lambda uid: None))
    monkeypatch.setattr(ac.AuthService, 'format_user_response', staticmethod(lambda u: {"id": "u1", "email": u["email"]}))

    resp = client.post('/api/login', json={"email": "a@b.com", "password": "pw"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data.get('success') is True


def test_login_invalid_credentials(client, monkeypatch):
    from backend.services.auth_service import AuthService
    monkeypatch.setattr(AuthService, 'get_user_by_email', staticmethod(lambda e: None))

    resp = client.post('/api/login', json={"email": "noone@example.com", "password": "pw"})
    assert resp.status_code == 401
