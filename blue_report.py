#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
Module call report.py (python3)
"""

from flask import Blueprint, render_template, abort
from jinja2 import TemplateNotFound


get_report_page = Blueprint('get_report_page', __name__)


@get_report_page.route('/')
def get_report():
    return 'Test'
