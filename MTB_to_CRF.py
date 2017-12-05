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

    for dtype in tables:
        for i in range(len(tables[dtype])):

            # transcripts = tables[dtype]['TRANSCRIPTS']
            try:
                first, exon, HGVSc, HGVSp = tables[dtype][i]['TRANSCRIPTS'].split(':')
                # Où faire la convertion TRANSCRIT
                tables[dtype][i]['TRANSCRIPTS'] = '({}): {} {}'.format(first, HGVSc, HGVSp)
            except KeyError:
                pass


    def write_csv_MTB(csv_path, tables, col_by_dtype):
        """
            Write MTB in csv format.

            :param col_by_dtype: ordered dict. {dtype: {'columns': ['col1', 'col2', ...]}}
            :param tables: Data from SQLite database

        """

        header = ''
        with open(csv_path, 'w') as f:
            writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

            # On commence par écrire la charge mutationelle
            writer.writerow(['Charge mutationelle', charge_mut])
            writer.writerow([])

            for dtype in tables:
                writer.writerow([dtype, *request_param[dtype]['columns']])
                for dict_row in tables[dtype]:

                    writer.writerow(['', *dict_row.values()])

                writer.writerow([])


    # write_csv_MTB('data/MTBreport{}test.csv'.format(patient_id), tables, request_param)


    def write_txt_MTB(txt_path, tables):
        """
            Write MTB in text format.

            :param tables: Data from SQLite database
        """

        with open(txt_path, 'w') as f:

            f.write('Charge mutationnelle: {} variations somatiques non synonymes ({} mutations/ Mb codantes)\n\n'.format(charge_mut, round(charge_mut/35.0, 2)))
            
            f.write('Variations somatiques :\n')
            for row in tables['VAR']:
                f.write('{} {} / {} / {}\n'.format(row['GeneSymbol'],
                                                   row['TRANSCRIPTS'],
                                                   row['MTBConclusion'],
                                                   row['CTBConclusion']))
            f.write('\n')

            f.write('CNV:\n')
            for row in tables['CNV']:
                f.write('{}: délétion hétérozygote / {} / {}\n'.format(row['GeneSymbol'],
                                                    row['MTBConclusion'],
                                                    row['CTBConclusion']))
            f.write('\n')


            print('FUS\n')
            f.write('Transcrit de fusion:\n')
            for row in tables['FUS']:
                f.write('{}: {} / {} / {}\n'.format(row['FusionGene'],
                                  row['MTBConclusion'],
                                  row['CTBConclusion'],
                                  row['FrameShiftClass3prime']))
            f.write('\n')

            print('CST\n')
            f.write('Variations constitutionnelles:\n')
            for row in tables['CST']:
                f.write('{} {} / {}\n'.format(row['GeneSymbol'],
                                              row['TRANSCRIPTS'],
                                              row['MTBConclusion']))
            f.write('\n')


    write_txt_MTB('data/MTBreport{}.txt'.format(patient_id), tables)

    # TODO: après copil voir si une colonne hétérozygocie a été ajoutée pour CNV et CST -> [ ]
    #       après copil -> que faire du "Variant associé à une LOH" dans VAR / MTBComment

    # Système de log nécessaire ?
    # Demander à yechan si on appplique une règles pour affihcier "délétion hétérozygote"
