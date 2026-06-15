import json
import os
import importlib.util
import pytest

# Import app module by file path to avoid PYTHONPATH issues during test runs
_app_path = os.path.join(os.path.dirname(__file__), '..', 'app.py')
spec = importlib.util.spec_from_file_location('backend.app', os.path.abspath(_app_path))
flask_app_module = importlib.util.module_from_spec(spec)
import sys
import types

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
_backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
_repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
# Ensure repo root is on sys.path so `import backend.*` works
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)
spec.loader.exec_module(flask_app_module)


class FakeCollection:
    def __init__(self):
        self.inserted = []

    def insert_one(self, doc):
        self.inserted.append(doc)
        class R:
            inserted_id = 1
        return R()

    def find(self, query=None):
        return self.inserted


class FakeDB:
    def __init__(self):
        self.feedbacks = FakeCollection()
        self.sentiment_analysis = FakeCollection()


@pytest.fixture
def client():
    app = flask_app_module.create_app()
    app.config['TESTING'] = True
    return app.test_client()


def test_analyze_sentiment_rules():
    # Ensure ML-based sentiment service is available and returns expected labels
    from backend.services import sentiment_service as ss
    if ss is None or getattr(ss, 'predict', None) is None:
        pytest.skip("sentiment_service not available")

    assert ss.predict('I love this product')[0] == 'positive'
    assert ss.predict('This is terrible and awful')[0] == 'negative'
    assert ss.predict('')[0] == 'neutral'


def test_submit_feedback_inserts(client, monkeypatch):
    fake_db = FakeDB()

    # Monkeypatch get_db used in controller
    import controllers.feedback_controller as fc
    monkeypatch.setattr(fc, 'get_db', lambda: fake_db)

    payload = {
        "logoQuality": "excellent logo quality",
        "videoQuality": "very satisfied with videos",
        "generationTime": "satisfied with time",
        "scheduling": "scheduler works well",
        "comments": "The video quality is excellent and amazing"
    }

    resp = client.post('/api/submit-feedback', data=json.dumps(payload), content_type='application/json')
    assert resp.status_code == 200
    data = resp.get_json()
    assert data.get('sentiment') == 'positive'
    # ensure inserts happened
    assert len(fake_db.feedbacks.inserted) == 1
    assert len(fake_db.sentiment_analysis.inserted) == 1

def test_get_feedbacks(client, monkeypatch):
    fake_db = FakeDB()
    
    # Pre-populate mock collections
    fake_db.feedbacks.inserted = [
        {"_id": "fb123", "logoQuality": "excellent logo quality", "videoQuality": "very satisfied", "generationTime": "satisfied", "scheduling": "great scheduling", "comments": "great platform"}
    ]
    fake_db.sentiment_analysis.inserted = [
        {"feedback_id": "fb123", "sentiment_label": "positive", "sentiment_score": 0.98}
    ]

    import controllers.feedback_controller as fc
    monkeypatch.setattr(fc, 'get_db', lambda: fake_db)

    resp = client.get('/api/feedbacks')
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data) == 1
    assert data[0]["id"] == "fb123"
    assert data[0]["sentiment"] == "positive"
    assert data[0]["logoQuality"] == "excellent logo quality"
    assert data[0]["comments"] == "great platform"
