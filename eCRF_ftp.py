#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import ftplib
import socket
import sys
import hashlib
import os

from contextlib import redirect_stdout
import io


""" Module to interact with eCRF's FTP serveur. """

# Logging
logger = logging.getLogger(__name__)

null_handler = logging.NullHandler()
logger.addHandler(null_handler)


def get_ftp_md5(ftp, remote_path):
    m = hashlib.md5()
    ftp.retrbinary('RETR %s' % remote_path, m.update)
    return m.hexdigest()


def md5(fpath):
    hash_md5 = hashlib.md5()
    with open(fpath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def upload_file(local_path, remote_path, connection, timeout=5, max_tries=2):
    """ Upload file on ftp server.

        :param remote_path: Head + tail file path
        :param connection: Dictonnary {host: '', login: '', password: ''}
    """

    local_head, local_fname = os.path.split(local_path)
    remote_head, remote_fname = os.path.split(remote_path)

    for count in range(max_tries):
        # Capture du stdout de storbinary pour le logger
        alt_stream = io.StringIO()
        with redirect_stdout(alt_stream):
            try:
                try:
                    with ftplib.FTP_TLS(connection['host'], timeout=timeout) as ftps:

                        ftps.set_debuglevel(1)

                        ftps.login(connection['login'], connection['password'])
                        # Encrypt all data, not only login/password
                        ftps.prot_p()
                        # Déclare l'IP comme étant de la famille v6 pour être compatible avec ftplib (même si on reste en v4)
                        # cf: stackoverflow.com/questions/35581425/python-ftps-hangs-on-directory-list-in-passive-mode
                        ftps.af = socket.AF_INET6
                        ftps.cwd(remote_head)

                        # Copie sur le remote
                        with open(os.path.join(local_path), 'rb') as file:
                            ftps.storbinary('STOR {}'.format(local_fname), file)

                # Si on a un timeout ça se passe comme prévu.
                except socket.timeout as e:
                    logger.debug(e)
                    logger.debug('stdout of storbinary :\n' + alt_stream.getvalue())
                    # On vérifié l'intégrité du fichier transféré
                    with ftplib.FTP_TLS(connection['host']) as ftps:
                        ftps.login(connection['login'], connection['password'])
                        ftps.prot_p()
                        ftps.af = socket.AF_INET6
                        ftp_md5 = get_ftp_md5(ftps, remote_path)

                    if ftp_md5 == md5(local_path):
                        logger.info('md5 ok')
                        return True
                    else:
                        logger.warning('{} Wrong md5.'.format(local_path))
                        logger.debug('FTP upload: Attemp n°{} , failed to upload {}'.format(count + 1, local_fname))

            # FileNotFoundError
            except FileNotFoundError as e:
                # On log l'erreur pour le débug sans bloquer
                logger.debug(e)
                raise
            except ftplib.all_errors as e:
                logger.error(e)
                logger.debug('FTP upload: Attemp n°{} , failed to upload {}'.format(count + 1, local_fname))

    return False
