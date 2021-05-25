from flask import Flask
from flask import render_template

app = Flask(__name__)

@app.route("/")
def main():
    return "Hello, World!\n"

@app.route(...)
def handle_request(...):                    # receive the request
    # TODO: load the desired page content   # traverse pages to find requested page
                                            # read page contents into payload
    return render_template(                 # return page_name and payload
        "main",
        page_name=...,
        page_content=...,
    )