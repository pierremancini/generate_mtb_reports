#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
    Display pre-MTB pdf file.
"""

from flask import Blueprint, send_file, request

import flask.json

import subprocess
import shlex


get_report_page = Blueprint('get_report_page', __name__)


def call_cmd(cmd):
    """Call system command."""

    args = shlex.split(cmd)
    process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        universal_newlines=True, shell=False)
    stdout, stderr = process.communicate()
    print(stderr)
    print(stdout)


@get_report_page.route('/', methods=['GET'])
def get_report():

    patient_id = request.args.get("patient_id")

    call_cmd('python3 report.py -id {}'.format(patient_id))

    return send_file('data/{}.pdf'.format(patient_id), mimetype='application/pdf')
