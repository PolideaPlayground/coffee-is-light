import os
import json

import flask

import config

app = flask.Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0


def get_state():
    try:
        with open(config.DATA_JSON_PATH) as json_file:
            return json.load(json_file)
    except (IOError, json.JSONDecodeError) as e:
        logging.warning(e)


@app.after_request
def add_header(r):
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r


@app.route('/api')
def api():
    return flask.jsonify(get_state())


@app.route('/')
def animation():
    return flask.render_template('demo.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
