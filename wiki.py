from flask import Flask
from flask import render_template

app = Flask(__name__)

@app.route("/")
def main():
    return handle_request('pages/FrontPage.txt')

@app.route("/handle_request/")
@app.route("/handle_request/<this_page>")
def handle_request(this_page):                  # receive the request
    # TODO: load the desired page content
    raw = this_page.split('/')
    name = raw[-1]
    name = name.strip('.txt')
    payload = None
    with open(this_page, 'r') as f:
        payload = f.read()

    return render_template(                 # return page_name and payload
        "main.html",
        page_name=name,
        page_content=payload,
    )