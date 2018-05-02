#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Génère un fichier texte contenant les informations d'un pre-MTB.

    Ce fichier est à destination d'ennov pour qu'il soit intégrer dans l'outil de
    traçabilité.
"""


import argparse
import report
import yaml
import sys
import csv
from collections import OrderedDict, defaultdict
import logging
import sqlite3

from pprint import pprint

def get_args():
    """Parse options."""
    opt_parser = argparse.ArgumentParser(description=__doc__)
    opt_parser.add_argument('-id', '--patient-id', required=False)
    opt_parser.add_argument('-c', '--config', default="config.yml", help='config file.')
    opt_parser.add_argument('-s', '--secret', default="secret_config.yml", help='secret config file.')
    opt_parser.add_argument('-o', '--outfile', help='Do not give extension.')
    return opt_parser.parse_args()


def set_logger(logger_name, file_name, level):
    """ Set un logger en fonction du nom de fichier de log donné.

        :param level: exemple logging.DEBUG

    """

    # Création d'un formateur qui va ajouter le n°process, le temps et le niveau
    # à chaque message de log
    formatter = logging.Formatter('%(process)d :: %(asctime)s :: %(levelname)s :: %(message)s')

    # Création du logger
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)

    # FileHandler
    handler = logging.FileHandler(file_name)
    handler.setLevel(level)
    handler.setFormatter(formatter)

    # StreamHandler
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(level)
    stream_handler.setFormatter(formatter)

    logger.addHandler(handler)
    logger.addHandler(stream_handler)

    return logger


def dict_err_handling(element, list):
    """
    Wraping function to handle IndexError when using comprension list.

    Args:
        element : list's element
    """

    try:
        return list[element]
    except IndexError:
        return None


def write_report(path, tables, charge_mut):

    # header du fichier de sortie
    # garder un ordre on utilise une liste comme structure de données
    header_order = [('Patient id', 'Patient id'),
                ('Occurence', 'Occurence'),
                ('Charge mutationnelle', 'Charge mutationnelle'),
                ('VAR1', 'GeneSymbol'),
                ('VAR2', 'TRANSCRIPTS First'),  # first part of transcript
                ('VAR3', 'HGVSc'),
                ('VAR4', 'HGVSp'),
                ('VAR5', 'MTBConclusion'),
                ('VAR6', 'CTBConclusion'),
                ('CNV1', 'GeneSymbol'),
                ('CNV2', 'SegStatus_Exon'),  # CopyNb_Exon -> 0, homo 1, hétéro & SegStatus_Exon
                ('CNV3', 'MTBConclusion'),
                ('CNV4', 'CTBConclusion'),
                ('CST1', 'GeneSymbol'),
                ('CST2', 'TRANSCRIPTS first'),
                ('CST3', 'HGVSc'),
                ('CST4', 'HGVSp'),
                ('CST5', 'CD_GENOTYPE__THRESH_0_05'),  # Mapping à appliquer AA BB -> homozygote, AB -> hétérozygote
                ('CST6', 'MTBConclusion'),
                ('FUS1', 'FusionGene'),
                ('FUS2', 'FrameShiftClass3prime'),
                ('FUS3', 'MTBConclusion'),
                ('FUS4', 'CTBConclusion')]

    map_col = {
             'Patient id': 'Patient id',
             'Occurence': 'Occurence',
             'Charge mutationnelle': 'Charge mutationnelle',
             'VAR1': 'GeneSymbol',
             'VAR2': 'TRANSCRIPTS First',  # first part of transcript
             'VAR3': 'HGVSc',
             'VAR4': 'HGVSp',
             'VAR5': 'MTBConclusion',
             'VAR6': 'CTBConclusion',
             'CNV1': 'GeneSymbol',
             'CNV2': 'SegStatus_Exon',  # CopyNb_Exon -> 0: homo 1: hétéro & SegStatus_Exon
             'CNV3': 'MTBConclusion',
             'CNV4': 'CTBConclusion',
             'CST1': 'GeneSymbol',
             'CST2': 'TRANSCRIPT first',
             'CST3': 'HGVSc',
             'CST4': 'HGVSp',
             'CST5': 'CD_GENOTYPE__THRESH_0_05',  # Mapping à appliquer AA BB -> homozygote, AB -> hétérozygote
             'CST6': 'MTBConclusion',
             'FUS1': 'FusionGene',
             'FUS2': 'FrameShiftClass3prime',
             'FUS3': 'MTBConclusion',
             'FUS4': 'CTBConclusion'}

    # Nombre de lignes maximum par dtype
    max_line = {'VAR': 15,
                'CNV': 15,
                'CST': 10,
                'FUS': 10}

    # Lignes et colonnes du fichiers
    file_matrix = {'Patient id': [],
            'Occurence': [],
            'Charge mutationnelle': [],
            'VAR1': [],
            'VAR2': [],
            'VAR3': [],
            'VAR4': [],
            'VAR5': [],
            'VAR6': [],
            'CNV1': [],
            'CNV2': [],
            'CNV3': [],
            'CNV4': [],
            'CST1': [],
            'CST2': [],
            'CST3': [],
            'CST4': [],
            'CST5': [],
            'CST6': [],
            'FUS1': [],
            'FUS2': [],
            'FUS3': [],
            'FUS4': []}


    for id in tables:

        print('id: {}'.format(id))

        # Ressemblera à par exmple {VAR: 2, CNV:1, CST:2, FUS: 0}
        lines_dtype = {'VAR': 0,
                    'CNV': 0,
                    'CST': 0,
                    'FUS': 0}

        i = 0
        # Check si il y à une ligne à remplir (même partiellement)
        while True:
            empty_line = []
            # Check si la ligne est vide
            for dtype in tables[id]:
                try:
                    tables[id][dtype][i]
                except IndexError:
                    empty_line.append(True)
                else:
                    empty_line.append(False)

            if all(empty_line):
                break

            for dtype in tables[id]:
                try:
                    tables[id][dtype][i]
                except IndexError as e:
                    # empty line for the part of this dtype
                    print('Notice : {}'.format(e))
                    for index in map_col:
                        if dtype == index[:-1]:
                            file_matrix[index].append('')
                else:
                    for index in map_col:
                        if dtype == index[:-1]:
                            try:
                                if tables[id][dtype][i][map_col[index]]:
                                    file_matrix[index].append(tables[id][dtype][i][map_col[index]])
                            except KeyError:
                                file_matrix[index].append(None)
                        else:
                            # On ne regarde pas le bon data type
                            pass

            # split pour avoir le patient_id simplifié
            file_matrix['Patient id'].append('-'.join(id.split('-')[:-2]))
            file_matrix['Charge mutationnelle'].append(charge_mut[id])
            i += 1
            file_matrix['Occurence'].append(i)

    with open(path, 'w') as f:
        writer = csv.writer(f, delimiter=',')

        line = ['init']
        i = 0

        writer.writerow([k[0] for k in header_order])

        while any(j for j in line):

            line = [dict_err_handling(i, file_matrix[k[0]]) for k in header_order]
            writer.writerow(line)

            i += 1


if __name__ == "__main__":

    args = get_args()

    logger = set_logger('MTB_logger', 'MTB_to_CRF.log', logging.DEBUG)

    # Configurations
    with open(args.config, 'r') as ymlfile:
        config = yaml.load(ymlfile)
    with open(args.secret, 'r') as ymlfile:
        secret_config = yaml.load(ymlfile)
    config.update(secret_config)

    db_dir = config['db_dir']
    protocol = config['protocol']

    request_param = OrderedDict([('VAR', {'columns': ['GeneSymbol', 'TRANSCRIPTS', 'MTBConclusion', 'CTBConclusion'],
                      'orders': 'GeneSymbol ASC'}),
             ('CNV', {'columns': ['GeneSymbol', 'MTBConclusion', 'CTBConclusion', 'CopyNb_Exon', 'SegStatus_Exon'],
                      'orders': 'GeneSymbol ASC'}),
             ('FUS', {'columns': ['FusionGene', 'MTBConclusion', 'CTBConclusion', 'FrameShiftClass3prime'],
                      'orders': 'FusionGene ASC'}),
             ('CST', {'columns': ['GeneSymbol', 'TRANSCRIPTS', 'CD_GENOTYPE__THRESH_0_05', 'MTBConclusion'],
                      'orders': 'GeneSymbol ASC'})])

    selector = '"MTBReport" == "Yes"'

    # Structure:
    # {sample_id: {dtype: {colomn: value}}}
    tables = {}

    # Liste des samples dont le sample_id doit être de le fichier de sortie du script
    sample_list = ['T02-0002-DX-001O', 'T01-0001-NP-001S', 'T02-0003-BN-001T']
    charge_mut = {}

    for sample_id in sample_list:

        report_instance = report.Report(db_dir, protocol, sample_id)

        c = report_instance.mut_charge()
        s = '{} variations somatiques non synonymes ({} mutations/Mb codantes)'.format(c, round(c / 35.0, 2))
        charge_mut[sample_id] = s

        tables[sample_id] = {}

        for data_type in request_param:
            columns = request_param[data_type]['columns']
            order = request_param[data_type]['orders']

            # Il est possible qu'une des tables ne soit pas présente.
            # Par exemple pas de table FUS pour T01-0001.
            try:
                table = report_instance.get_table("_%s" % data_type, columns, selector, order)
            except sqlite3.OperationalError as e:
                logger.warning(e)

            tables[sample_id][data_type] = table

        # Découpage de la valeur de la colonne TRANSCRIPTS
        # début : exon : HGVSc : HGVSp
        for dtype in tables[sample_id]:
            for i in range(len(tables[sample_id][dtype])):

                # transcripts = tables[dtype]['TRANSCRIPTS']
                try:
                    first, exon, HGVSc, HGVSp = tables[sample_id][dtype][i]['TRANSCRIPTS'].split(':')

                    tables[sample_id][dtype][i]['TRANSCRIPTS First'] = first
                    tables[sample_id][dtype][i]['HGVSc'] = HGVSc
                    tables[sample_id][dtype][i]['HGVSp'] = HGVSp
                # CNV et DUS n'ont pas de champs TRANSCRIPTS
                except KeyError as e:
                    pass

        # Transformations:
        # Correspondance index 0 -> homozygote et index 1 -> heterozygote
        CopyNb = ('homozygote', 'heterozygote')

        for i in range(len(tables[sample_id]['CNV'])):
            if (tables[sample_id]['CNV'][i]['SegStatus_Exon'] == 'Deletion'):
                tables[sample_id]['CNV'][i]['SegStatus_Exon'] = 'Deletion ' + CopyNb[tables[sample_id]['CNV'][i]['CopyNb_Exon']]

        for i in range(len(tables[sample_id]['CST'])):

            if tables[sample_id]['CST'][i]['CD_GENOTYPE__THRESH_0_05'] == 'AB':
                tables[sample_id]['CST'][i]['CD_GENOTYPE__THRESH_0_05'] = 'heterozygote'
            else:
                tables[sample_id]['CST'][i]['CD_GENOTYPE__THRESH_0_05'] = 'homozygote'

    write_report('data/MTBreport_occurence_version.csv', tables, charge_mut)
