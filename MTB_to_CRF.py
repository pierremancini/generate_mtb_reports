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


def hasher():
  return defaultdict(hasher)


def write_report(path, tables, charge_mut):

    # header du fichier de sortie
    header = ['Patient id',
            'Occurence',
            'Charge mutationnelle',
            'GeneSymbol',
            'TRANSCRIPT first',
            'HGVSc',
            'HGVSp',
            'MTBConclusion',
            'CTBConclusion',
            'GeneSymbol',
            'MTBConclusion',
            'MTBConclusion bis',
            'CTBConclusion',
            'GeneSymbol',
            'TRANSCRIPT first',
            'HGVSc',
            'HGVSp',
            'CD_GENOTYPE__THRESH_0_05',
            'MTBConclusion',
            'FusionGene',
            'FrameShiftClass3prime',
            'MTBConclusion',
            'CTBConclusion']

    map_col = {
             'Patient id': 'Patient id',
             'Occurence': 'Occurence',
             'Charge mutationnelle': 'Charge mutationnelle',
             'VAR1': 'GeneSymbol',
             'VAR2': 'TRANSCRIPT first',  # first part of transcript
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

    # Nombre de colones nécessaire par dtype
    col_num = {'VAR': 6,
               'CNV': 4,
               'CST': 6,
               'FUS': 4}

    """
    - faire un fichier qui rassemble les rapports de (potentiellement) plusieurs patient_id.
    - blinder le nombre max de ligne pas dtype
        -> raise error, kill script si le nombre ligne dépasse ?
    - mettre en place un peuplement des lignes du .csv en fonction du nouveau format donnée par
        Delphine.

    """

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

        # Check si il y à une ligne à remplir (même partiellement)
        i = 0
        while any([tables[id][dtype][i] is not None for dtype in tables[id]]):

            for index in map_col:
                if not index in ['Patient id', 'Occurence', 'Charge mutationnelle']:
                    dtype = index[:-1]
                    for i in tables[id][dtype]:
                        try:
                            file_matrix[index] = tables[id][map_col[index]][i]
                        except KeyError as e:
                            empty_cell = True
                            print('Empty cell for id: {}, dtype: {}, i: {}'.format(id, map_col[index]), i)

            # Check si toute la ligne est vide  (utiliser un flag pour le check ?)
            #   si oui on ne met rien
            #   si non remplissage de la cellue Patient id

            file_matrix['Patient id'].append(id) # TODO: split pour avoir le patient_id simplifié
            file_matrix['Charge mutationnelle'].append(tables[id]['Charge mutationnelle'])

            i += 1
            file_matrix['Occurence'] = i



if __name__ == "__main__":

    args = get_args()

    logger = set_logger('MTB_logger', 'MTB_to_CRF.log', logging.DEBUG)

    # Configurations
    with open(args.config, 'r') as ymlfile:
        config = yaml.load(ymlfile)
    with open(args.secret, 'r') as ymlfile:
        secret_config = yaml.load(ymlfile)
    config.update(secret_config)

    sys.path.append(config['path_to_utils'])
    from redcap_utils import get_clinical_data  # TODO: Utilisé ?

    db_dir = config['db_dir']
    protocol = config['protocol']

    request_param = OrderedDict([('VAR', {'columns': ['GeneSymbol', 'TRANSCRIPTS', 'MTBConclusion', 'CTBConclusion'],
                      'orders': 'GeneSymbol ASC'}),
             ('CNV', {'columns': ['GeneSymbol', 'MTBConclusion', 'CTBConclusion'],
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

    for sample_id in sample_list:

        report_instance = report.Report(db_dir, protocol, sample_id)

        charge_mut = report_instance.mut_charge()

        tables[sample_id] = {}

        for data_type in request_param:
            columns = request_param[data_type]['columns']
            order = request_param[data_type]['orders']

            # Il est possible qu'une des tables ne soit pas présente. Par exemple pas de table
            # FUS pour T01-0001.
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

    write_report('data/MTBreport_occurence_version.csv', tables, charge_mut)
