#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
Module description
"""



from flask import Blueprint, render_template, abort
from jinja2 import TemplateNotFound

simple_page = Blueprint('simple_page', __name__)


@simple_page.route('/')
def hello_world():
    return 'Hello, blue!'
