import pytest  # type: ignore
import pathlib
import json
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


@pytest.mark.parametrize(
    ["content", "edit_description", "usr_name", "usr_email", "page_title", "expected"],
    [
        (
            "page_1 content img\ncity, state\nbody content",
            "Added a page",
            "Jeff Bergman",
            "bunny@google.com",
            "Los Angeles, California",
            0,
        ),
        ("", "Page edit", "Mel Blanc", "daffy@gmail.com", "Portland, Oregon", -1),
        (
            "page_3 content img\ncity, state\nbody content",
            "",
            "Joe Dougherty",
            "porkey@gmail.com",
            "Los Angeles, California",
            -2,
        ),
        (
            "page_4 content img\ncity, state\nbody content",
            "Page added",
            "",
            "sylvercat@looney.com",
            "Pratt, Kansas",
            -3,
        ),
        (
            "page_4 content img\ncity, state\nbody content",
            "Page edit",
            "Greg Burson",
            "",
            "Anaheim, California",
            -4,
        ),
        (
            "page_5 content img\ncity, state\nbody content",
            "Page edit",
            "Joe Alaskey",
            "fogleghorn@gmail.com",
            None,
            -5,
        ),
    ],
)
def test_validate_information(
    content, edit_description, usr_name, usr_email, page_title, expected
):
    error_code = wiki.validate_information(
        content, edit_description, usr_name, usr_email, page_title
    )
    assert error_code == expected


@pytest.mark.parametrize(
    ["error_code", "expected"],
    [
        (0, ""),
        (-1, "error: post content empty"),
        (-2, "error: missing description"),
        (-3, "error: missing user name"),
        (-4, "error: missing email"),
        (-5, "error: missing page title"),
    ],
)
def test_form_errors(error_code, expected):
    error_msg = wiki.form_errors(error_code)
    assert error_msg == expected


# Test functions for writing to and reading from a page
def test_page_rw(monkeypatch):
    test_dir = pathlib.Path(__file__).parent
    test_dir = test_dir / "test_dir/"
    monkeypatch.setattr(wiki, "current_dir", test_dir)

    wiki.write_to_page("test city, test state", "success")
    content = wiki.get_page_content(test_dir / f"pages/{'test city, test state'}.txt")
    assert content == "success"


def test_edit_route_integration(client, monkeypatch):
    test_dir = pathlib.Path(__file__).parent
    test_dir = test_dir / "test_dir/"
    monkeypatch.setattr(wiki, "current_dir", test_dir)

    client.post(
        "/edit/add",
        data={
            "text_area": """test_img.jpg
test city, test state
Test Morbid Event
The test killer cheated on a test
:;:
testing
discussion posts are required to not crash the page from a non iterable""",
            "descript_edit": "test edit",
            "fname": "Test Name",
            "e_email": "testing@test.com",
        },
    )

    response_get = client.get(f"/edit/{'test city, test state'}")
    assert response_get.status_code == 200
    assert b"test state" in response_get.data


def test_get_history(client, monkeypatch):
    test_dir = pathlib.Path(__file__).parent
    test_dir = test_dir / "test_dir/"
    monkeypatch.setattr(wiki, "current_dir", test_dir)

    response_get = client.get(f"/history/{'test city, test state'}")
    assert response_get.status_code == 200
    assert b"06/08/2021" in response_get.data


def test_file_not_found(client, monkeypatch):
    test_dir = pathlib.Path(__file__).parent
    test_dir = test_dir / "test_dir/"
    monkeypatch.setattr(wiki, "current_dir", test_dir)

    response_get = client.get(f"/history/{'random city, test state'}")
    assert response_get.status_code == 404
    assert b"No history has been found for this page" in response_get.data


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
