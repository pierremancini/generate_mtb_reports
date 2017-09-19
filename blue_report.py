#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
Module call report.py (python3)
"""

from flask import Blueprint, send_file


get_report_page = Blueprint('get_report_page', __name__)


@get_report_page.route('/')
def get_report():

    return send_file('data/T02-0002-DX-001O.pdf', mimetype='application/pdf')


