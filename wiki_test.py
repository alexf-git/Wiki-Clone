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
