"""
Created on 16 Feb 2016
@description: Moves selected data files to ingester directories, untars and renames if required.
@author: Tim Cavanagh
@modified: Tim Cavanagh 17/02/2016 integrated into pull package
"""

import errno
import glob
import logging
import os
import shutil
import tarfile
import gzip

from config import remove
from config import storage_folder_ingestor
from notify import notifysubscribers

logger = logging.getLogger(__name__)


def movefiles(src):
    # decide on the db or log files by text in path
    tmp = src.split('/')
    ddir = tmp[- 1]
    if 'database' in src:
        # database files
        dest = storage_folder_ingestor.get('database_state') + "latest/"
        ignfl = []
        logger.debug('Processing db files and directories')
        # clear the latest directory, exclude ora for now
        dl = [d for d in os.listdir(dest) if not d.startswith('.') and not ('ora' in d)]
        for i in dl:
            # move the processed dirs to the archive ingestor directories
            movedir(dest, storage_folder_ingestor.get('database_state'), i)
        # prepare the ignore list of files
        logger.info('Processing ignore list')
        for fn in remove:
            ignfl.append(fn + '*')
            logger.debug('Ignoring: %s', fn)

        # copy the new files to the ingestor directories and ignore files we don't want
        copy(src, dest + ddir, ignfl)
        # unpack the files we need for ingestor
        unpack(dest + ddir)
        # rename files that will cause issues for ingestor
        rename(dest + ddir)
    elif 'event-data' in src:
        # copy the new files to the ingestor directories
        copy(src, storage_folder_ingestor.get('clickstream-logs'), '')
        # unpack the files we need for ingestor
        unpack(storage_folder_ingestor.get('clickstream-logs'))


def rename(ingestdir):
    """

    :param ingestdir:
    """
    dl = [d for d in os.listdir(ingestdir) if not d.startswith('.')]
    for fn in dl:
        try:
            fp = os.path.join(ingestdir + "/" + fn)
            # rename directory that has . in name
            if os.path.isdir(fp) and "." in fn:
                shutil.move(fp, os.path.join(ingestdir + "/" + fn.replace(".", "-")))
                logger.info('Processing directory rename: %s', fn)
            # rename filename that has . in name
            if os.path.isfile(fp):
                # filename and extension name (extension in [1])
                filename_split = os.path.splitext(fn)
                filename = filename_split[0]
                extension = filename_split[1]
                if "." in filename and not filename.startswith('.'):
                    logger.info('Processing file rename: %s', fn)
                    os.rename(fp, os.path.join(ingestdir + "/" + filename.replace(".", "-") + extension))
        except Exception:
            logger.error('Failed rename: %s', fn, exc_info=True)


def unpack(ingestdir):
    # gunzip the files that are we want to keep that are still on in the directory
    tarlist = glob.glob(ingestdir + '/*tar.gz')
    gzlist = glob.glob(ingestdir + '/*log.gz')
    for fn in tarlist:
        try:
            tar = tarfile.open(fn)
            tar.extractall(path=ingestdir)
            tar.close()
            # delete the .gz file
            os.remove(fn)
        except Exception, e:
            logger.error('Unpacking tar db: %s', fn, exc_info=True)
        else:
            logger.debug('Uncompressed tar db: %s', fn)
    for fn in gzlist:
        try:
            with gzip.open(fn, 'rb') as in_file:
                s = in_file.read()
            # remove the '.gz' from the filename
            path_to_store = fn[:-3]
            with open(path_to_store, 'w') as f:
                    f.write(s)
            # delete the .gz file
            os.remove(fn)
        except Exception, e:
            logger.error('Unpacking gzip cs: %s', fn, exc_info=True)
        else:
            logger.debug('Uncompressed gzip cs: %s', fn)


def movedir(src, dest, dirname):
    """
    Description: If the directory exists it will be overwritten
    :param dirname: the directory name
    :param src: the directory path to be moved
    :param dest: the directory path to move the directory to
    """
    try:
        # move the processed dirs to the archive ingestor directories
        if os.path.exists(os.path.join(dest, dirname)):
            logger.debug('Removing duplicate dir to archive: %s', dirname)
            shutil.rmtree(os.path.join(dest, dirname))
        logger.info('Moving: %s to: %s', dirname, dest)
        shutil.move(os.path.join(src, dirname), dest)
    except shutil.Error as e:
        logger.error('Directory not moved: %s', e, exc_info=True)
        raise
    except OSError as e:
        # If the error was caused because the source wasn't a directory
        if e.errno == errno.ENOTDIR:
            logger.warning('Not a directory to move: %s', e)
        else:
            logger.error('Directory not moved: %s', e, exc_info=True)
            # Send email
            notifysubscribers(None, e)
            raise


def copy(src, dest, ignfl):
    """

    :param src:
    :param dest:
    :param ignfl:
    """
    try:
        # ignore patterns can be '*.py', '*.sh', 'specificfile.file'
        # pass in as positional arguments *
        logger.info('Copying from: %s', src)
        shutil.copytree(src, dest, ignore=shutil.ignore_patterns(*ignfl))
    except OSError as e:
        # If the error was caused because the source wasn't a directory
        if e.errno == errno.ENOTDIR:
            # copy files will overwrite
            logger.debug('Copying files from: %s', src)
            shutil.copy(src, dest)
        else:
            logger.warning('Directory not copied: %s', e)
    except shutil.Error as e:
        logger.warning('Directory not copied: %s', e)
