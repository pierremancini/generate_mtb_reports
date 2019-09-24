#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import shlex
import os
import subprocess

import redcap
import sqlite3
from jinja2 import Template
import report
import argparse
import yaml
import csv

import sys

from pprint import pprint




def call_cmd(cmd):
    """Call system command."""

    args = shlex.split(cmd)
    process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        universal_newlines=True, shell=False)
    return process.communicate()


def get_args():
    """Parse options."""
    opt_parser = argparse.ArgumentParser(description=__doc__)
    opt_parser.add_argument('-c', '--config', default="config.yml", help='config file.')
    opt_parser.add_argument('-s', '--secret', default="secret_config.yml", help='secret config file.')
    return opt_parser.parse_args()


def sample_id_to_export():
    """
        On a trois sources de données:
            - la base sqlite catalogue
            - extraction redcap des record avec fusion_done
            - extraction redcap des record avec not_exported
    """

    # On regarde la base catalogue pour chaque data type
    query = '''SELECT sample_name FROM samples WHERE "status" = "validated"
                                                AND "sample_category" = "MULTIPLI"'''
    sqlite_list = get_sqlite_data(query)

    # DEV - simule l'extraction de données de la base catalogue
    sqlite_list = [
        'T02-0002-DX-001O_VAR', 'T02-0002-DX-001O_CST', 'T02-0002-DX-001O_FUS', 'T02-0002-DX-001O_CNV',  # Fusion done dans redcap
        'T02-0018-BJ-002Q_VAR', 'T02-0018-BJ-002Q_CST', 'T02-0018-BJ-002Q_FUS', 'T02-0018-BJ-002Q_CNV',  # Fusion done redcap
        'T02-0006-CB-0029_VAR',  # Fusion pas done -> attente des CST, CNV, VAR
        'T02-0017-JM-002D_VAR', 'T02-0017-JM-002D_CST', 'T02-0017-JM-002D_CNV']  # Fusion done dans redcap -> attente du FUS

    # {samples_id: [dtypes]}
    samples_dtype = {}

    for sample_id in sqlite_list:
        dtype = sample_id.split('_')[-1]
        sample_id = sample_id.split('_')[:-1][0]
        samples_dtype.setdefault(sample_id, []).append(dtype)

    sample_list = []
    for id in samples_dtype:
        if id in not_exported:
            if len(samples_dtype[id]) == 4 and id in fusion_done:
                sample_list.append(id)
            elif len(samples_dtype[id]) == 3 and id not in fusion_done:
                sample_list.append(id)

    return sample_list


if __name__ == "__main__":

    args = get_args()

    # Configurations
    with open(args.config, 'r') as ymlfile:
        config = yaml.load(ymlfile)
    with open(args.secret, 'r') as ymlfile:
        secret_config = yaml.load(ymlfile)
    config.update(secret_config)

    db_dir = config['db_dir']
    protocol = config['protocol']

    # TODO: dépalce dans un fichier config
    path_template = os.path.join('template_bioreport', 'table.rst')
    path_rst = os.path.join('data', 'bio', 'bioreport.rst')

    path_pdf = os.path.join('data', 'bio', 'bioreport.pdf')
    path_css = os.path.join('template_bioreport', 'table.css')

    report = report.Report(db_dir, protocol, 'T02-0002-DX-001O')

    request_param = {'VAR': {'categories': ["Pathogenic", "Likely pathogenic", "Uncertain significance"],
        'columns': ["GeneSymbol", "TRANSCRIPTS", "HGVSc", "HGVSp", "TYPE", "PASSING_ALLELIC_EXP",
             "ALL_GENOTYPES", "gStart", "Ref", "Alt"], 'left_selector': 'MTBConclusion', 'orders': 'GeneSymbol ASC' },

        'CNV': {'categories': ["Actionable", "Likely actionable", "Not actionable"],
        'columns': ["GeneSymbol", "SegSize_Exon", "CopyNb_Exon", "SegStatus_Exon", "MTBComment"],
        'left_selector': 'CTBConclusion', 'orders': 'GeneSymbol ASC' }, 

        'FUS': {'categories': ["Actionable", "Likely actionable", "Not actionable"], 
        'columns': ["FusionGene", "KnownTranscriptStrand5p", "RegName5p", "KnownTranscriptStrand3p", "RegName3p", "FrameShiftClass3prime", "MTBComment"],
        'left_selector': 'CTBConclusion', 'orders': 'FusionGene ASC' }, 

        'CST': {'categories': ["Pathogenic", "Likely pathogenic", "Uncertain significance"],
        'columns': ["GeneSymbol", "TRANSCRIPTS", "HGVSc", "HGVSp", "TYPE", "PASSING_ALLELIC_EXP", "ALL_GENOTYPES", "MTBComment"],
        'left_selector': 'MTBConclusion', 'orders': 'GeneSymbol ASC'}}

    tables = {}
    nb_columns = {}

    for data_type in request_param:
        columns = request_param[data_type]['columns']
        orders = request_param[data_type]['orders']
        left_selector = request_param[data_type]['left_selector']
        for category in request_param[data_type]['categories']:
            selectors = '"%s" = "%s"' % (left_selector, category)
            table = report.get_table("_%s" % data_type, columns, selectors, orders)
            tables[data_type + category.replace(' ', '')] = table
            nb_columns[data_type + category.replace(' ', '')] = len(columns)


    # VAR, varations_pathogenes, varations probablement pathogenes et varations de signification
    # cliniques indeterminee : -> MTB_conculsion = pathogenicité, CTB_conclusion = actionnabilité
    # Gène, g., NM, c., p., LOH, Actionnabilité, Fréquence allélique

    dict_VAR = [{'Gène': 'RFC4', 'g.': 'g.186506928G>T', 'NM': 'NM_001967.3', 'c.': 'c.1094G>T',
        'p.': 'p.(Gly365Val)', 'LOH': 'homozygous', 'Actionnabilité': 'Actionable', 'Fréquence allélique': '0.64'},
        {'Gène': 'KRAS', 'g.': 'g.186956506928GA>TC', 'NM': 'NM_5551967.3', 'c.': 'c.7794G>T',
        'p.': 'p.(Gly365Val)', 'LOH': 'homozygous', 'Actionnabilité': 'Actionable',
        'Fréquence allélique': '0.64'}]

    # CNV, Copy number
    # Gène, type de cnv, Nombre de copies, Taille maximale, Pathogénicité, Actionnabilité

    # FUS, Transcrits du Fusion
    # Fusion, 5', NM, 5', Exon impliqué, 3', NM, 3', Exon impliqué, Pathogénicté, Actionnabilité

    # CST, etude constitutionnelle
    # rs, Gene, g., NM, c., p., Génotype


    def format_jinja(tables, header):
        """ Format dictonnaries response from sqlite to lists addapt to jinja
            templating.

            :param tables: dictionnaire avec
            :param header: header souhaité dans la table rst

            :return: list of list of values (without column names)
        """

        print(header)
        matrix = []

        for i in range(len(tables)):
            matrix.append([])
            for column in header:
                try:
                    tables[i][column]
                except KeyError as e:
                    matrix[i].append('')
                else:
                    matrix[i].append(tables[i][column])

        return matrix


    variations_pathogenes = 'fezfez ,ezfe,fez,fze,fze,zfe,fez,zfe'

    headers = {}

    # {Template_col: database_col}
    headers['VARLikelypathogenic'] = ["Gene", "HGVSg", "HGVSc", "HGVSp", "NM", "LOH", "Freq", "Actionability"]

    with open(path_template, 'r') as f:

        template = f.read()
        t = Template(template)

        dict = {'code_patient': "A99-T01-0701",
                'sex_patient': 'male',
                'var_pathogenes': variations_pathogenes,
                'var_probablement_pathogenes': format_jinja(tables['VARLikelypathogenic'],
                                                            headers['VARLikelypathogenic'])}

        rst_content = t.render(dict)

        print(rst_content)


    with open(path_rst, 'w') as f:

        f.write(rst_content)


    cmd = 'rst2pdf -s {} {} {}'.format(path_css, path_rst, path_pdf)

    stdout, stderr = call_cmd(cmd)

    print(stdout)
    print(stderr)

