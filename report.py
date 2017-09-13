#!/usr/bin/env python3#!/usr/bin/env python3
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
from redcap import Project
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
        """Function doc.

        Args:
            param (int): DESCRIPTION
            param (str): DESCRIPTION

        Returns:
            type: DESCRIPTION
        """
        table = []
        rows = self.get_data(dtype_suffix, columns, selectors, orders)
        for row in rows:
            row = list(row)
            if dtype_suffix == "_VAR":
                if row[1].startswith("NM_"):
                    row[1] = row[1].split(":")[0]
                    if "c." in row[1] and "c." in row[2]:
                        if row[2] != row[1].split(":")[2]:
                            raise ValueError("TRANSCRIPT %s and cDNA_Change %s do not match!" % (row[1].split(":")[2], row[2]))
                    if "p." in row[1] and "p." in row[3]:
                        if row[3] != row[1].split(":")[3]:
                            raise ValueError("TRANSCRIPT %s and Protein_Change %s do not match!" % (row[1].split(":")[3], row[3]))
                if row[5] == "1":
                    row[5] = "Oui"
                elif row[5] == "0":
                    row[5] = "Non"
                if row[6]:
                    row[6] = ":".join(row[6].split(":")[:-1])
            if dtype_suffix == "_CNV":
                row[1] = str(row[1])
                row[2] = str(row[2])
            if dtype_suffix == "_FUS":
                row[2] = str(row[2])
                row[4] = str(row[4])
            table.append(row)
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
    opt_parser.add_argument('-c', '--config', default="config.yml", help='config file.')
    opt_parser.add_argument('-s', '--secret', default="secret_config.yml", help='secret config file.')
    opt_parser.add_argument('-o', '--outfile', help='If no outfile given, default = sample name')
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

    sample = "T02-0002-DX-001O"
    report = Report(db_dir, protocol, sample)


    # -- File system configuration --
    if not args.outfile:
        outfile = sample + '.pdf'
    else:
        outfile = args.outfile

    data_folder = 'data'

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
            selectors = '"%s" = "%s"' % (left_selector ,category)
            table = report.get_table("_%s" % data_type, columns, selectors, orders)
            tables[data_type + category.replace(' ', '')] = table
            nb_columns[data_type + category.replace(' ', '')] = len(columns)

    mut_counts = report.mut_charge()
    tables['\*\*\*MutationalCharge\*\*\*'] = str(mut_counts)
    tables['\*\*\*MutationalChargeMb\*\*\*'] = "{0:.2f}".format(round(mut_counts/35.0, 2))

    tables['\*\*\*ID-patient\*\*\*'] = "T02-0002-DX"
    tables['\*\*\*Code barre ADN tumoral\*\*\*'] = "B00I1UL"
    tables['\*\*\*Code barre ARN tumoral\*\*\*'] = "B00I1VU"
    tables['\*\*\*Code barre ADN germinal\*\*\*'] = "B00I1UK"

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

    texfile = sample + '.tex'
    with open(os.path.join(data_folder, texfile), 'w') as texfile:
        texfile.write(content)

    # create_pdf() # => fcontion bash

    # pdflatex --file-line-error-style -interaction=batchmode  "%f"

    # %f correspond surement au fichier courant dans geany


if __name__ == "__main__" :
    __main__()
