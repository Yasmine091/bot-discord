import flask
import requests
import json

app = flask.Flask(__name__)
app.config["DEBUG"] = True

def get_api(identifier):
   with open("assets/api.json", encoding="utf8") as readFile:
    api = json.load(readFile)
    if(identifier == 'all'):
        return(api)
    else:
        return(api[identifier])

@app.route('/', methods=['GET'])
def home():
    return get_api('all')

@app.route('/chatting', methods=['GET'])
def chatting():
    return get_api('chatting')

@app.route('/settings', methods=['GET'])
def basicSettings():
    return get_api('basic settings')

app.run()