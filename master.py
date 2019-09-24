#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Module"""


from flask import Flask
from blue_report import get_report_page

app = Flask(__name__)
app.register_blueprint(get_report_page, url_prefix='/get_report')

@app.route('/')
def hello_world():
    return 'Hello, master!'


if __name__ == "__main__":
    app.run(debug=True)
