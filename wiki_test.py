import pytest  # type: ignore
import pathlib
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
    assert b"<title>Historia Morbosa</title>" in resp.data


def test_El_Paso_Data(client):
    resp = client.get("/city_request/El Paso, Texas")
    assert resp.status_code == 200
    assert b"<h1>El Paso, Texas\n</h1>" in resp.data


def test_no_path_city_request(client):
    resp = client.get("/city_request/El Paso, California")
    assert resp.status_code == 200


def test_edit_route_integration(client, monkeypatch):
    test_dir = pathlib.Path(__file__).parent
    test_dir = test_dir / "test_dir/"
    monkeypatch.setattr(wiki, "current_dir", test_dir)
    
    client.post(f"/edit/add", data={
        "text_area": """test_img.jpg
test city, test state
Test Morbid Event
The test killer cheated on a test
:;:
testing
discussion posts are required to not crash the page from a non iterable""",
        "descript_edit": "test edit",
        "fname": "Test Name",
        "e_email": "testing@test.com"
    })

    response_get = client.get(f"/edit/{'test city, test state'}")
    assert response_get.status_code == 200
    assert b"test state" in response_get.data