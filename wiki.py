import os
import pathlib
from flask import Flask
from flask import render_template, redirect, url_for, request

app = Flask(__name__)
current_dir = pathlib.Path(__file__).parent
states = dict()


@app.route("/")
def main():
    backup()
    home_page = "pages/home.txt"
    payload = None
    with open(home_page, "r") as f:
        payload = f.readlines()
    for raw in payload:
        data = raw.split("=")
        state = data[0]
        city_string = data[1]
        city_list = city_string.split(",")
        states[state] = [city.strip("\n") for city in city_list]
    return home_request(home_page)


@app.route("/home_request/<home_page>")
def home_request(home_page: str) -> str:
    return render_template(
        "home.html",
        page_name="Historia Morbosa",
        state_dict=states,
        city_request=city_request,
    )


@app.route("/city_request/<this_page>")
def city_request(this_page: str):
    payload = None
    full_path = "pages/" + this_page + ".txt"
    if os.path.exists(full_path):
        with open(full_path, "r") as f:
            payload = f.readlines()
        img = payload[0]
        name = payload[1]
        fact = payload[2]
        payload = payload[3:]
        contents = None
        comments = None
        for row in range(len(payload)):
            if ":;:" in payload[row]:
                contents = payload[:row]
                if row < len(payload) - 1:
                    index = row + 1
                    comments = payload[index:]
                break
        return render_template(
            "city.html",
            img_path=img,
            city_name=name,
            city_fact=fact,
            city_content=str(contents).strip("['").strip("\n']"),
            city_posts=comments,
        )
    return "Path is not forming " + full_path


@app.route("/edit/<city_name>", methods=["GET", "POST"])
def edit(city_name):
    city_name = city_name.replace("\n", "")
    page_dir = current_dir / f"pages/{ city_name }.txt"
    # retreive info from form
    if request.method == "POST":
        posted_content = request.form["text_area"]
        edit_description = request.form["descript_edit"]
        usr_name = request.form["fname"]
        usr_email = request.form["e_email"]
        # validate information (user name, email, description)
        valid_code = validate_information(
            posted_content, edit_description, usr_name, usr_email
        )
        if valid_code == 0:
            # write new content to file
            write_to_page(page_dir, posted_content)
            # update history
            update_history(edit_description, usr_name, usr_email)
            # redirect to "current page"
            return redirect(url_for("city_request", this_page=city_name))
        else:
            return (
                render_template(
                    "form.html",
                    page_content=posted_content,
                    page_name=city_name,
                    error=form_errors(valid_code),
                ),
                400,
            )
    else:
        # get page content
        content = get_page_content(page_dir)
        # send page content to html form
        return render_template(
            "form.html", page_content=content, page_name=city_name, error=form_errors(0)
        )


def get_page_content(page_dir):
    with open(page_dir, "r") as f:
        content = f.read()
    return content


def validate_information(content, edit_description, usr_name, usr_email):
    # Verify content is not empty
    if len(content) == 0:
        return -1
    # Verify edit description was added
    if len(edit_description) == 0:
        return -2
    # Verify user name was added
    if len(usr_name) == 0:
        return -3
    # Verify email
    if "@" not in usr_email:
        return -4
    return 0


def form_errors(num):
    if num == 0:
        return ""
    elif num == -1:
        return "error: post content empty"
    elif num == -2:
        return "error: missing description"
    elif num == -3:
        return "error: missing user name"
    else:
        return "error: missing email"


def write_to_page(page_dir, content):
    with open(page_dir, "w") as f:
        f.write(content)


def update_history(edit_description, usr_name, usr_email):
    pass


def backup():
    import os

    inputdir = "pages/"
    outputdir = "TestPages/"

    files = os.listdir(inputdir)

    for i in files:
        with open(inputdir + i, "r") as r:
            with open(outputdir + i, "w") as w:
                w.write(r.read())
