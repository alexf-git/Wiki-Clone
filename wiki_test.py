import pytest # type: ignore
import wiki


@pytest.fixture
def client():
    wiki.app.config["TESTING"] = True

    with wiki.app.test_client() as client:
        yield client


def test_import():
    assert wiki is not None


def test_homepage(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert b'<title>City Browser</title>' in resp.data


def test_El_Paso_Data(client):
    resp = client.get('/city_request/El Paso, Texas')
    assert resp.status_code == 200
    assert b'<h1>El Paso, Texas\n</h1>' in resp.data
