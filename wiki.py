from flask import Flask
from flask import render_template

app = Flask(__name__)

@app.route("/")
def main():
    return handle_request('FrontPage.txt')

@app.route("pages/<this_page>")
def handle_request(this_page=None):                  # receive the request
    # TODO: load the desired page content
    payload = None
    with open(this_page, 'r') as f:
        payload = f.read()

    return render_template(                 # return page_name and payload
        "main",
        page_name=this_page,
        page_content=payload,
    )