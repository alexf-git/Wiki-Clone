import pytest  # type: ignore
import wiki
import json


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
    assert b"<title>Historia Morbosa</title>" in resp.data


def test_El_Paso_Data(client):
    resp = client.get("/city_request/El Paso, Texas")
    assert resp.status_code == 200
    assert b"<h1>El Paso, Texas\n</h1>" in resp.data


def test_no_path_city_request(client):
    resp = client.get("/city_request/El Paso, California")
    assert resp.status_code == 200


def test_page_api_get(client):
    resp = client.get("/api/v1/pages/El Paso, Texas/get")
    assert resp.status_code == 200
    assert json.loads(resp.data)["success"] is True
    assert "raw" in json.loads(resp.data).keys()
    assert "html" in json.loads(resp.data).keys()


def test_page_api_get_no_page(client):
    resp = client.get("/api/v1/pages/El Po, Texas/get?format=raw")
    assert resp.status_code == 404
    assert json.loads(resp.data)["success"] is False
    assert "reason" in json.loads(resp.data).keys()


def test_page_api_get_raw(client):
    resp = client.get("/api/v1/pages/El Paso, Texas/get?format=raw")
    assert resp.status_code == 200
    assert json.loads(resp.data)["success"] is True
    assert "raw" in json.loads(resp.data).keys()


def test_page_api_get_html(client):
    resp = client.get("/api/v1/pages/El Paso, Texas/get?format=html")
    assert resp.status_code == 200
    assert json.loads(resp.data)["success"] is True
    assert "html" in json.loads(resp.data).keys()


def test_page_api_get_unsupported(client):
    resp = client.get("/api/v1/pages/El Paso, Texas/get?format=pdf")
    assert resp.status_code == 400
    assert json.loads(resp.data)["success"] is False
    assert "pdf" not in json.loads(resp.data).keys()
