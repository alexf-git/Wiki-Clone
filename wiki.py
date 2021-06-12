"""Wiki  Copyright (C) 2021  See AUTHORS.txt
This program comes with ABSOLUTELY NO WARRANTY; for details type `show w'.
    This is free software, and you are welcome to redistribute it
    under certain conditions; type `show c' for details.

"""
import os
import csv
import typing
import flask
from flask import Flask
from flask import render_template, redirect, url_for, request
from datetime import datetime

app = Flask(__name__)

states: typing.Dict[str, list] = {}

current_dir = os.getcwd()


@app.route("/api/v1/pages/<page_name>/get")
def page_api_get(page_name):
    format = flask.request.args.get("format", "all")
    # TODO: implement response
    json_response = {}
    raw_state = page_name.split(", ")
    given_state = raw_state[1]
    status_code = 200

    if states.get(given_state) is None or raw_state[0] not in states[given_state]:
        status_code = 404
        json_response["success"] = False
        json_response["reason"] = "Page does not exist."

    elif format == "raw":
        json_response["success"] = True
        with open("pages/" + page_name + ".txt", "r") as f:
            json_response["raw"] = f.read()

    elif format == "html":
        json_response["success"] = True
        json_response["html"] = city_request(page_name)

    elif format == "all":
        json_response["success"] = True
        with open("pages/" + page_name + ".txt", "r") as f:
            json_response["raw"] = f.read()
        json_response["html"] = city_request(page_name)

    elif format != "raw" or format != "html":
        status_code = 400
        json_response["success"] = False
        json_response["reason"] = "Unsupported format"

    return json_response, status_code


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
        "home2.html",
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
    page_dir = current_dir + f"/pages/{city_name}.txt"
    # retreive info from form
    if request.method == "POST":
        posted_content = request.form["text_area"]
        content_lst = posted_content.split("\n")
        if len(content_lst) > 2:
            page_title = content_lst[1]
            page_title = page_title.rstrip()
        if city_name == "add":
            city_name = page_title
        edit_description = request.form["descript_edit"]
        usr_name = request.form["fname"]
        usr_email = request.form["e_email"]
        # validate information (user name, email, description)
        valid_code = validate_information(
            posted_content, edit_description, usr_name, usr_email, page_title
        )
        if valid_code == 0:
            # write new content to file
            write_to_page(page_title, posted_content)
            # update history
            update_history(edit_description, usr_name, usr_email, city_name)
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
    elif city_name == "add":
        return render_template(
            "form.html", page_content="", page_name="", error=form_errors(0)
        )
    else:
        # get page content
        content = get_page_content(page_dir)
        # send page content to html form
        return render_template(
            "form.html", page_content=content, page_name=city_name, error=form_errors(0)
        )


def add_page():
    os.path.join(current_dir, "temp.txt")


def get_page_content(page_dir):
    with open(page_dir, "r") as f:
        content = f.read()
    return content


def validate_information(content, edit_description, usr_name, usr_email, page_title):
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
    if page_title is None:
        return -5
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
    elif num == -4:
        return "error: missing email"
    else:
        return "error: missing page title"


def write_to_page(page_title, content):
    with open(current_dir + f"/pages/{page_title}.txt", "w") as f:
        f.write(content)


def update_history(edit_description, usr_name, usr_email, city_name):
    time = datetime.now()
    date_time_string = time.strftime("%m/%d/%Y %H:%M:%S")

    myRow = [date_time_string, usr_name, usr_email, edit_description]

    with open(current_dir + f"/history/{city_name}.csv", "a") as fd:
        writer = csv.writer(fd)
        writer.writerow(myRow)


@app.route("/history/<city_name>")
def get_history(city_name):
    city_name = city_name.rstrip()
    full_path = current_dir + f"/history/{city_name}.csv"
    edit_history = []
    if os.path.exists(full_path):
        with open(full_path, "r") as fd:
            for line in reversed(list(csv.reader(fd))):
                edit_history.append(
                    {
                        "date": line[0],
                        "description": line[3],
                        "author": line[1],
                        "email": line[2],
                    }
                )
        return render_template(
            "history.html", city_name=city_name, edit_content=edit_history, error=""
        )
    else:
        error = "No history has been found for this page"
        return (
            render_template(
                "history.html", city_name=city_name, edit_content="", error=error
            ),
            404,
        )


def backup():
    import os

    inputdir = "pages/"
    outputdir = "TestPages/"

    files = os.listdir(inputdir)

    for i in files:
        with open(inputdir + i, "r") as r:
            with open(outputdir + i, "w") as w:
                w.write(r.read())
