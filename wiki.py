from flask import Flask
from flask import render_template

app = Flask(__name__)

@app.route("/")
def main():
    backup()
    return home_request('pages/home.txt')

@app.route("/city_request/")
@app.route("/city_request/<this_page>")
def city_request(this_page):                                # receive the request
    # TODO: load the desired page content
    payload = None
    with open(this_page, 'r') as f:
        payload = f.readlines()

    name = payload[1]
    fact = payload[2]
    payload = payload[3:]
    contents = None
    comments = None
    for row  in range(len(payload)):
        if ':;:' in payload[row]:
            contents = payload[:row]
            if row < len(payload)-1:
                comments = payload[row+1:]
            break
    return render_template(                                 # return page_name and payload
        'city.html',
        city_name=name,
        city_fact=fact,
        city_content=str(contents).strip('["').strip('"]'),
        city_posts=comments,
    )

@app.route("/home_request/")
@app.route("/home_request/<home_page>")
def home_request(home_page):
    payload = None
    with open(home_page, 'r') as f:
        payload = f.readlines()
    states = dict()
    for raw in payload:
        data = raw.split('=')
        states[data[0]] = [x for x in data[1:]]

    return render_template(
        'home.html',
        page_name = 'City Browser',
        state_dict = states,
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
                
