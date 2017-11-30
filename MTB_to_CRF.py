#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Génère un fichier texte contenant les informations d'un pre-MTB.

    Ce fichier est à destination d'ennov pour qu'il soit intégrer dans l'outil de
    traçabilité.
"""

import report
import yaml
import sys
import csv
from collections import OrderedDict

from pprint import pprint


def write_list_xlsx(filepath, liste):

    # Pas de valeur dupliquées
    set_list = set(liste)
    workbook = xlsxwriter.Workbook(filepath)
    worksheet = workbook.add_worksheet()
    row = 0
    for item in set_list:
        worksheet.write(row, 0, item)
        row += 1

    workbook.close()


if __name__ == "__main__":

    args = report.get_args()

    # Configurations
    with open(args.config, 'r') as ymlfile:
        config = yaml.load(ymlfile)
    with open(args.secret, 'r') as ymlfile:
        secret_config = yaml.load(ymlfile)
    config.update(secret_config)

    sys.path.append(config['path_to_utils'])
    from python_utils.redcap_utils import get_clinical_data

    db_dir = config['db_dir']
    protocol = config['protocol']

    sample = 'T02-0002-DX-001O'

    # Utile ?
    patient_id = 'T02-0002'

    report = report.Report(db_dir, protocol, sample)

    charge_mut = report.mut_charge()

    request_param = OrderedDict([('VAR', {'columns': ['GeneSymbol', 'TRANSCRIPTS', 'MTBConclusion', 'CTBConclusion'],
                          'orders': 'GeneSymbol ASC'}),
                 ('CNV', {'columns': ['GeneSymbol', 'MTBConclusion', 'CTBConclusion'],
                          'orders': 'GeneSymbol ASC'}),
                 ('FUS', {'columns': ['FusionGene', 'MTBConclusion', 'CTBConclusion', 'FrameShiftClass3prime'],
                          'orders': 'FusionGene ASC'}),
                 ('CST', {'columns': ['GeneSymbol', 'TRANSCRIPTS', 'MTBConclusion'],
                          'orders': 'GeneSymbol ASC'})])

    selector = '"MTBReport" == "Yes"'

    tables = {}

    for data_type in request_param:
        columns = request_param[data_type]['columns']
        order = request_param[data_type]['orders']
        table = report.get_table("_%s" % data_type, columns, selector, order)
        tables[data_type] = table

    # Découpage de la valeur de la colonne TRANSCRIPTS
    # début : exon : HGVSc : HGVSp
    transcripts = "NM_000546:exon5:c.517G>A:p.V173M"
    first, exon, HGVSc, HGVSp = transcripts.split(':')

    header = ''
    with open('data/MTBreport{}.csv'.format(patient_id), 'w') as f:
        writer = csv.writer(f, delimiter=',',  quotechar='"', quoting=csv.QUOTE_MINIMAL)

        # On commence par écrire la charge mutationelle
        writer.writerow(['Charge mutationelle', charge_mut])
        writer.writerow([])

        for dtype in tables:
            writer.writerow([dtype, *request_param[dtype]['columns']])
            for row in tables[dtype]:

                writer.writerow(['', *row])

            writer.writerow([])

    # TODO: après copil voir si une colonne hétérozygocie a été ajoutée pour CNV et CST -> [ ]
    #       après copil -> que faire du "Variant associé à une LOH" dans VAR / MTBComment
