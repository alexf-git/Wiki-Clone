import os
from flask import Flask
from flask import render_template

app = Flask(__name__)

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


def backup():
    import os

    inputdir = "pages/"
    outputdir = "TestPages/"

    files = os.listdir(inputdir)

    for i in files:
        with open(inputdir + i, "r") as r:
            with open(outputdir + i, "w") as w:
                w.write(r.read())
