from flask import Flask
from flask import render_template

app = Flask(__name__)

@app.route("/")
def main():
    backup()
    return handle_request('pages/FrontPage.txt')

@app.route("/handle_request/")
@app.route("/handle_request/<this_page>")
def handle_request(this_page):                  # receive the request
    # TODO: load the desired page content
    payload = None
    with open(this_page, 'r') as f:
        payload = f.readlines()


    return render_template(                 # return page_name and payload
        'city.html',
        city_name=payload[0],
        city_fact=payload[1],
        city_content=payload[2:],
    )

def backup():
    import os
    import pathlib
    from os import walk
    files = []
    for (dirpath, dirnames, filenames) in walk(os.path.abspath('pages')):
        files.extend(filenames)
    inputdir = 'pages/'
    outputdir = 'TestPages/'

    for i in files:
        with open(inputdir+i, 'r') as r:
            with open(outputdir+i, 'w') as w:
                w.write(r.read())
                
