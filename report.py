#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""
MULTIPLI report module
"""

import argparse
import sqlite3
import os
import re
import sys
import yaml
import redcap
import requests
import json
import subprocess
import shlex
#from collections import OrderedDict


__author__ = "Yec'han Laizet"
__version__ = "0.1.0"


class Report(object):
    """Report manager."""

    def __init__ (self, db_dir, protocol, sample):
        """Class initialiser"""
        self.db_dir = db_dir
        self.protocol = protocol
        self.sample = sample

    def _sql_query(self, table, columns, selectors, orders):
        """Create and return sql.

        Args:
            param (int): DESCRIPTION
            param (str): DESCRIPTION

        Returns:
            type: DESCRIPTION
        """
        columns_sql = '"%s"' % '", "'.join(columns)
        table_sql = '"%s"' % (table)
        where_sql = ""
        if selectors:
            where_sql = " WHERE %s" % selectors
        order_sql = ""
        if orders:
            order_sql = " ORDER BY %s" % orders
        sql_query = "SELECT {columns_sql} FROM {table_sql}{where_sql}{order_sql};".format(
                                            columns_sql=columns_sql,
                                            table_sql=table_sql,
                                            where_sql=where_sql,
                                            order_sql=order_sql)

        return sql_query

    def mut_charge(self, suffix="_VAR"):
        """Function doc.

        Args:
            param (int): DESCRIPTION
            suffix (str): data_type suffix ex.: '_VAR'

        Returns:
            type: DESCRIPTION
        """
        db_file = os.path.join(self.db_dir, "%s.sqlite" % self.protocol)
        conn = sqlite3.connect(db_file)
        table = "%s%s" % (self.sample, suffix)
        sql = 'SELECT count("PASSING_ARTEFACT") from "{table}" WHERE "PASSING_ARTEFACT" = "PASS_SOMATIC"'.format(table=table)
        c = conn.cursor()
        c.execute(sql)
        mut_counts = c.fetchone()
        conn.close()
        return mut_counts[0]

    def get_data(self, suffix, columns, selectors, orders):
        """Function doc.

        Args:
            param (int): DESCRIPTION
            suffix (str): data_type suffix ex.: '_VAR'

        Returns:
            type: DESCRIPTION
        """
        db_file = os.path.join(self.db_dir, "%s.sqlite" % self.protocol)
        conn = sqlite3.connect(db_file)
        table = "%s%s" % (self.sample, suffix)
        sql = self._sql_query(table, columns, selectors, orders)
        c = conn.cursor()
        rows = list(c.execute(sql))
        conn.close()
        return rows

    def get_table(self, dtype_suffix, columns, selectors, orders):
        """ Get data from SQLite database table.

            For pre-MTB report there is filtering and value maping.
            If concerned column are not requested filterinf and mapping won't be used.

        """
        table = []
        rows = self.get_data(dtype_suffix, columns, selectors, orders)

        for row in rows:

            # info de la ligne avec nom des colonnes en clé
            dict_row = {columns[i]: row[i] for i in range(len(columns))}
            try:
                if dtype_suffix == "_VAR":
                    if dict_row['TRANSCRIPTS'].startswith("NM_"):

                        if "c." in dict_row['TRANSCRIPTS'] and "c." in dict_row['HGVSc']:
                            if dict_row['HGVSc'] != dict_row['TRANSCRIPTS'].split(":")[2]:
                                raise ValueError("TRANSCRIPT %s and cDNA_Change %s do not match!" % (dict_row['TRANSCRIPTS'].split(":")[2], dict_row['HGVSc']))
                        if "p." in dict_row['TRANSCRIPTS'] and "p." in dict_row['HGVSp']:
                            if dict_row['HGVSp'] != dict_row['TRANSCRIPTS'].split(":")[3]:
                                raise ValueError("TRANSCRIPT %s and Protein_Change %s do not match!" % (dict_row['TRANSCRIPTS'].split(":")[3], dict_row['HGVSp']))
                        # Si le script est appelé de l'extérieur on garde l'info complète
                        if __name__ != '__main__':
                            dict_row['TRANSCRIPTS'] = dict_row
                    if dict_row['PASSING_ALLELIC_EXP'] == "1":
                        dict_row['PASSING_ALLELIC_EXP'] = "Oui"
                    elif dict_row['PASSING_ALLELIC_EXP'] == "0":
                        dict_row['PASSING_ALLELIC_EXP'] = "Non"
                    if dict_row['ALL_GENOTYPES']:
                        dict_row['ALL_GENOTYPES'] = ":".join(dict_row['ALL_GENOTYPES'].split(":")[:-1])
                if dtype_suffix == "_CNV":
                    dict_row['SegSize_Exon'] = str(dict_row['SegSize_Exon'])
                    dict_row['CopyNb_Exon'] = str(dict_row['CopyNb_Exon'])
                if dtype_suffix == "_FUS":
                    dict_row['RegName5p'] = str(dict_row['RegName5p'])
                    dict_row['RegName3p'] = str(dict_row['RegName3p'])
            except KeyError:
                # KeyError is due to the checkings corresponding to wrong type of report
                # (not pre-MTB report)
                pass

            # Si le script est appelé de l'extérieur on garde le nom des colonnes
            if __name__ != '__main__':
                table.append(dict_row)
            else:
                table.append(list(dict_row.values()))

        return table

    def table_to_tex(self, table, header=None):
        """Function doc.

        Args:
            param (int): DESCRIPTION
            param (str): DESCRIPTION

        Returns:
            type: DESCRIPTION
        """
        """
        \begin{tabular}{|c|c|}

        \hline

        1 & 2 \\

        \hline

        3 & 4 \\

        \hline

        \end{tabular}
        """

        if header:
            tex_table = ["\\begin{tabular}{|%s|}" % "|".join(["l"] * len(header))]
            tex_table.append("\\hline")
            tex_table.append("%s \\\\" % " & ".join(header))
            tex_table.append("\\hline")
            for row in table:
                tex_table.append("%s \\\\" % " & ".join(row))
                tex_table.append("\\hline")
            tex_table.append("\\end{tabular}")
            return "\n".join([r.replace("_", "\_") for r in tex_table])

        else:

            latex_code_buffer = ''
            for row in table:
                row = [r'\url{' + cell + '}' for cell in row]
                latex_row = r'\\scriptsize '
                latex_row += r' &\\scriptsize '.join(row) # .replace("_", "\_")
                latex_row += r'\\tabularnewline\n\hline\n'
                latex_code_buffer += latex_row
            
            # On supprime le dernier retour à la ligne
            latex_code_buffer = latex_code_buffer[:-2]

            return latex_code_buffer

    def empty_table_to_tex(self, nb_columns):
        """:return: Tex code to complete an empty tablular."""

        row = r''
        for i in range(nb_columns - 1):
            row += r' &'
        row += r' \\tabularnewline\n\hline'

        return row


def inject_to_template(template, var, value):
    """
        :param template: LaTeX template to complete
        :type template: String, du texte .tex compilable en LaTeX

        :return: Full LaTeX code
    """

    return re.sub(var, value, template)


def tex_escape(text):
    """
        :param text: a plain text message
        :return: the message escaped to appear correctly in LaTeX
    """

    # Ajouter d'autre symboles si nécessaire
    conversion = {
        '%': r'\%'
    }


    for key in conversion:
        text = re.sub(key, conversion[key], text)

    return text


def call_cmd(cmd):
    """Call system command."""

    args = shlex.split(cmd)
    process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        universal_newlines=True, shell=False)
    stdout, stderr = process.communicate()
    print(stderr)
    print(stdout)


def get_args():
    """Parse options."""
    opt_parser = argparse.ArgumentParser(description=__doc__)
    opt_parser.add_argument('-id', '--patient-id', required=False)
    opt_parser.add_argument('-c', '--config', default="config.yml", help='config file.')
    opt_parser.add_argument('-s', '--secret', default="secret_config.yml", help='secret config file.')
    opt_parser.add_argument('-o', '--outfile', help='Do not give extension.')
    return opt_parser.parse_args()


def __main__():

    args = get_args()

    with open(args.config, 'r') as ymlfile:
        config = yaml.load(ymlfile)
    with open(args.secret, 'r') as ymlfile:
        secret_config = yaml.load(ymlfile)
    config.update(secret_config)


    sys.path.append(config['path_to_utils'])
    from python_utils.redcap_utils import get_clinical_data


    #db_dir = "/home/ylaizet/Informatique/genVarXplorer/gvxrestapi/db/SQLite/"
    db_dir = config['db_dir']
    protocol = config['protocol']
    
    sample = args.patient_id # "T02-0002-DX-001O"

    patient_id = args.patient_id.rsplit('-', 1)[0] # ['T02-0002-DX', '001O'][0]


    report = Report(db_dir, protocol, sample)

    data_folder = 'data'
    outputdir = data_folder

    request_param = {'VAR': {'categories':["Actionable", "Likely actionable", "Not actionable"],
        'columns': ["GeneSymbol", "TRANSCRIPTS", "HGVSc", "HGVSp", "TYPE", "PASSING_ALLELIC_EXP",
             "ALL_GENOTYPES", "MTBComment"], 'left_selector': 'CTBConclusion', 'orders': 'GeneSymbol ASC' },

        'CNV': {'categories': ["Actionable", "Likely actionable", "Not actionable"], 
        'columns': ["GeneSymbol", "SegSize_Exon", "CopyNb_Exon", "SegStatus_Exon", "MTBComment"], 
        'left_selector': 'CTBConclusion', 'orders': 'GeneSymbol ASC' }, 

        'FUS': {'categories': ["Actionable", "Likely actionable", "Not actionable"], 
        'columns': ["FusionGene", "KnownTranscriptStrand5p", "RegName5p", "KnownTranscriptStrand3p", "RegName3p", "FrameShiftClass3prime", "MTBComment"],
        'left_selector': 'CTBConclusion', 'orders': 'FusionGene ASC' }, 

        'CST': {'categories': ["Pathogenic", "Likely pathogenic", "Uncertain significance"],
        'columns': ["GeneSymbol", "TRANSCRIPTS", "HGVSc", "HGVSp", "TYPE", "PASSING_ALLELIC_EXP", "ALL_GENOTYPES", "MTBComment"], 
        'left_selector': 'MTBConclusion', 'orders': 'GeneSymbol ASC' }}

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

    mut_counts = report.mut_charge()
    tables['\*\*\*MutationalCharge\*\*\*'] = str(mut_counts)
    tables['\*\*\*MutationalChargeMb\*\*\*'] = "{0:.2f}".format(round(mut_counts/35.0, 2))

    tables['\*\*\*ID-patient\*\*\*'] = patient_id
    tables['\*\*\*Code barre ADN tumoral\*\*\*'] = "B00I1UL"
    tables['\*\*\*Code barre ARN tumoral\*\*\*'] = "B00I1VU"
    tables['\*\*\*Code barre ADN germinal\*\*\*'] = "B00I1UK"

    # Clinical data
    response = get_clinical_data(patient_id, config['redcap_api_url'], config['redcap_key'])

    if not response:
        print('Did not find clinical_data for patient_id: {}'.format(patient_id))

    tables['\*\*\*Organe\*\*\*'] = response['tumor_type']

    tables['\*\*\*Type histologique\*\*\*'] = response['histotype']

    # ARN
    tables['\*\*\*Cellularité tumorale ADN\*\*\*'] = tex_escape(response['tumorcellularity_adn'])
   

    tables['\*\*\*Type d\'évenement ADN\*\*\*'] = response['tumorpathologyevent_type_adn']

    tables['\*\*\*Mode de fixation ADN\*\*\*'] = response['samplenature_adn']

    # ADN
    tables['\*\*\*Cellularité tumorale ARN\*\*\*'] = tex_escape(response['tumorcellularity_arn'])
    print(tables['\*\*\*Cellularité tumorale ARN\*\*\*'])

    tables['\*\*\*Type d\'évenement ARN\*\*\*'] = response['tumorpathologyevent_type_arn']

    tables['\*\*\*Mode de fixation ARN\*\*\*'] = response['samplenature_arn']

    with open(config['template'], 'r') as templatefile:
        content = templatefile.read()

    for tex_variable in tables:
        if isinstance(tables[tex_variable], list):
            if not tables[tex_variable]:
                # Tableau vide
                value = report.empty_table_to_tex(nb_columns[tex_variable])
            else:
                # Tableau avec des lignes
                value = report.table_to_tex(tables[tex_variable])
        # Texte simple
        elif isinstance(tables[tex_variable], str):
            value = tables[tex_variable]
        else:
            raise TypeError

        content = inject_to_template(content, tex_variable, value)

    if not args.outfile:
        texfile = sample + '.tex'
    else:
        texfile = args.outfile + '.tex'

    texfile = sample + '.tex'
    texfile_path = os.path.join(data_folder, texfile)
    with open(texfile_path, 'w') as texfile:
        texfile.write(content)

    # create_pdf() # => fonction bash

    call_cmd("pdflatex --file-line-error-style -interaction=batchmode -output-directory {} {}".format(outputdir, texfile_path))

    # %f correspond surement au fichier courant dans geany


if __name__ == "__main__" :
    __main__()