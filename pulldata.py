"""
Created on 13 Jan 2015
@description: Module pulls data from S3, decrypts files, triggers ingest prep and notifies via email
@author: Pinaki Chandrasekhar
@modified: Tim Cavanagh	21/10/2015 Code cleanup, updated script to use my GPG key and email details.
           Tim Cavanagh 12/02/2016 Rewrite to extract ORA files
           Tim Cavanagh 02/03/2016 Added logging and replaced calls with python native code
           Tim Cavanagh 03/03/2016 Added config to control invoking ingest prep,
                                    control DL by deleting main zip file
"""
import logging
import zipfile
from subprocess import call, check_output

import shutil

import config
import ingestprep
import os
from notify import notifysubscribers

global ls_db_dest_dir
ls_db_dest_dir = []
global ls_cs_dest_dir
ls_cs_dest_dir = []
global filelist
filelist = []

logger = logging.getLogger(__name__)


def getbucket(key, year=0):
    bucket = config.s3_buckets.get(key)
    if year != 0:
        bucket = bucket + str(year) + "/"
    return bucket


def syncfiles(key, year=0):
    result = check_output(
        [config.path_to_aws, '--profile', config.s3_profile, 's3', 'sync', 's3://' + getbucket(key, year),
         config.storage_folders.get(key), '--exclude', '*', '--include', '*' + config.s3_profile + '*'])
    return result


def getsubpath(a):
    tmp = a.split('/')
    if len(tmp) > 4:
        tmp = a.split('s3://course-data/')
    return tmp[len(tmp) - 1]


def getdownloadedlist(response):
    # list of directories created
    fl = []
    response.sort()
    for a in response:
        if "s3://" in a:
            if ".zip" in a:
                name = getsubpath(a)
                # unzip the S3 file - will overwrite encrypted files if already exist
                try:
                    logger.info('Unzipping: %s', name)
                    with zipfile.ZipFile(config.storage_folders.get('database-data') + name) as s3zip:
                        s3zip.extractall(config.storage_folders.get('database-data-unzipped') + name[0:name.find(
                                        config.s3_profile)])
                except Exception:
                    logger.error('Failed unzip S3 File: %s', name, exc_info=True)
                    raise
                tmp2 = name.split('.zip')
                lst = []
                # set the dest dir for decrypted files
                db_dest_dir = config.storage_folder_decrypted.get('database-data') + tmp2[0]
                # add all root decrypted dirs to the ingest dir list
                ls_db_dest_dir.append(db_dest_dir)
                try:
                    if os.path.exists(db_dest_dir):
                        logger.info('Decrypted dir exists, deleting: %s', db_dest_dir)
                        shutil.rmtree(db_dest_dir)
                    # make the parent directory to hold all of the decrypted files
                    logger.debug('Creating decrypted dir: %s', db_dest_dir)
                    os.makedirs(db_dest_dir)
                except Exception, e:
                    logger.error('Failed to make directory: %s', db_dest_dir, exc_info=True)
                    # Send email
                    notifysubscribers(None, e)
                    raise
                for root, directories, filenames in os.walk(
                                        config.storage_folders.get('database-data-unzipped') + tmp2[0] + '/'):
                    for d in directories:
                        if d == 'ora' and not os.path.exists(db_dest_dir + '/ora'):
                            try:
                                os.makedirs(db_dest_dir + '/ora')
                            except Exception, e:
                                logger.error('Failed to make directory: %s', db_dest_dir + '/ora', exc_info=True)
                                # Send email
                                notifysubscribers(None, e)
                                raise
                    for f in filenames:
                        lst.append(os.path.join(root, f))
                # add the unzipped files and directories to the list to be decrypted
                filelist.extend(lst)
            else:
                tmp = a.split('/')
                if "edge/events/" in a:
                    fl = config.storage_folders.get("edge-event-data") + tmp[len(tmp) - 1]
                elif "edx/events/" in a:
                    fl = config.storage_folders.get("edx-event-data") + tmp[len(tmp) - 1]
                filelist.append(fl)


def decryptfiles():
    for l in filelist:
        tmp = l.split('/')
        encrypted_file = tmp[len(tmp) - 1]
        if 'database-data' in l:
            if '/legacy' in l:
                logger.info('DB data: %s', encrypted_file[0:encrypted_file.find('.gpg')])
                # decrypted_file = config.storage_folder_decrypted.get('database-data-legacy') + tmp[
                #     len(tmp) - 2] + '/' + encrypted_file[0:encrypted_file.find('.gpg')]
            elif '/test' in l:
                logger.info('DB data: %s', encrypted_file[0:encrypted_file.find('.gpg')])
                # decrypted_file = config.storage_folder_decrypted.get('database-data-test') + tmp[
                #     len(tmp) - 2] + '/' + encrypted_file[0:encrypted_file.find('.gpg')]
            elif '/ora' in l:
                if os.path.isfile(l):
                    decrypted_file = config.storage_folder_decrypted.get('database-data') + tmp[-3] + '/' + tmp[
                        -2] + '/' + encrypted_file[0:encrypted_file.find('.gpg')]
            else:
                decrypted_file = config.storage_folder_decrypted.get('database-data') + tmp[
                    len(tmp) - 2] + '/' + encrypted_file[0:encrypted_file.find('.gpg')]
        elif '/event-data/edge/' in l:
            decrypted_file = config.storage_folder_decrypted.get('edge-event-data') + encrypted_file[
                                                                                      0:encrypted_file.find('.gpg')]
        elif '/event-data/edx/' in l:
            decrypted_file = config.storage_folder_decrypted.get('edx-event-data') + encrypted_file[
                                                                                     0:encrypted_file.find('.gpg')]
            ls_cs_dest_dir.append(decrypted_file)
        if os.path.isfile(l):
            try:
                # FIXME: replace this call with python-gnupg wrapper
                call(
                    'echo ' + config.passphrase + '|' + config.path_to_gpg + ' --batch --yes --passphrase-fd 0 --output ' + decrypted_file +
                    ' --decrypt ' + l, shell=True)
                logger.debug('Decrypting: %s', decrypted_file)
            except IOError:
                logger.warning('IOError on decrypt (maybe ok): %s', decrypted_file)
            except Exception:
                logger.error('Failed to decrypt file: %s', decrypted_file)


def initialise():
    """
    Created on 01 March 2016
    @description: Main application stub
    @author: Tim Cavanagh
    @modified: Tim Cavanagh 02 March 2016 tidied config
    """
    logger.info('Starting File Sync')

    # FIXME: make this an iterative using config
    getdownloadedlist((syncfiles("database-data", 0)).split(' '))
    getdownloadedlist((syncfiles("edge-event-data", 2014)).split(' '))
    getdownloadedlist((syncfiles("edge-event-data", 2015)).split(' '))
    getdownloadedlist((syncfiles("edge-event-data", 2016)).split(' '))
    getdownloadedlist((syncfiles("edx-event-data", 2014)).split(' '))
    getdownloadedlist((syncfiles("edx-event-data", 2015)).split(' '))
    getdownloadedlist((syncfiles("edx-event-data", 2016)).split(' '))

    logger.info('Starting Decrypt Files')
    decryptfiles()

    logger.info('Starting Move Files')

    # control invoking ingest file prep or not
    if config.enable_ingest:
        # database directories of files
        for d in ls_db_dest_dir:
            logger.info('Preparing db files for ingestion: %s', d)
            ingestprep.movefiles(d)
        # click-stream logs
        for f in ls_cs_dest_dir:
            logger.info('Preparing cs files for ingestion: %s', f)
            ingestprep.movefiles(f)

    if len(filelist) > 0:
        logger.info('Sending email')
        notifysubscribers(filelist, None)
