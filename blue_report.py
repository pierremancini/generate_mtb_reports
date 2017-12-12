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
    
    return process.communicate()


@get_report_page.route('/', methods=['GET'])
def get_report():

    patient_id = request.args.get("patient_id")

    stdout, stderr = call_cmd('python3 report.py -id {}'.format(patient_id))

    # L'erreur du script report doit bloqué la suite de la blueprint
    if stderr:
        print(stderr)
        return stderr

    return send_file('data/{}.pdf'.format(patient_id), mimetype='application/pdf')
