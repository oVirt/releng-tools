#!/usr/bin/env python
import os
import sys
import shutil
import logging
import subprocess
import glob

import requests
import gnupg


logger = logging.getLogger(__name__)


class NotSamePackage(Exception):
    """Thrown when trying to compare different packages"""
    pass


def gpg_get_keyuid(key_path):
    gpg = gnupg.GPG(gnupghome=os.path.expanduser('~/.gnupg'))
    with open(key_path) as key_fd:
        skey = gpg.import_keys(key_fd.read())
        fprint = skey.results[0]['fingerprint']
    keyuid = None
    for key in gpg.list_keys(True):
        if key['fingerprint'] == fprint:
            keyuid = key['uids'][0]
    return keyuid


def get_plugins(plugin_dir=None):
    """
    Given a path, returns the importable files and directories in it
    """
    plugin_dir = plugin_dir or os.path.dirname(__file__)
    modules = []
    for module in glob.glob(plugin_dir + "/*"):
        if not module.endswith('.py') \
           and not os.path.isdir(module):
            continue
        if module.endswith('__init__.py'):
            continue
        if module.endswith('.py'):
            modules.append(os.path.basename(module)[:-3])
        elif (
            os.path.isdir(module)
            and os.path.isfile(module + '/__init__.py')
        ):
            modules.append(os.path.basename(module))
    return modules


def find_recursive(base_path, fmatch):
    """
    Walks a directory recursively and returns the list of files for which
    fmatch(filename) returns True
    """
    matched_files = []
    for root, _, files in os.walk(base_path):
        matched_files.extend([
            os.path.join(root, fname)
            for fname in files
            if fmatch(fname)
        ])
    return matched_files


def tryint(mayint):
    """
    Tries to cast to int, and returns the same object if failed.
    """
    try:
        return int(mayint)
    except ValueError:
        return mayint


def cmpver(ver1, ver2):
    """
    Compares two version in a natural sort ordering fashion (what you usually
    expect when comparing versions yourself).
    Thought for version strings in the form:
       x.y.z
    """
    ver1 = '.' in ver1 and ver1.split('.') or (ver1,)
    ver2 = '.' in ver2 and ver2.split('.') or (ver2,)
    ver1 = [tryint(i) for i in ver1]
    ver2 = [tryint(i) for i in ver2]
    if ver1 > ver2:
        return -1
    if ver1 == ver2:
        return 0
    else:
        return 1


def cmpfullver(fullver1, fullver2):
    """
    Compares version strings in the form:
       x.y.z-a.b.c
    """
    ver1, rel1 = split(fullver1, '-', 1)
    ver2, rel2 = split(fullver2, '-', 1)
    ver_res = cmpver(ver1, ver2)
    if ver_res != 0:
        return ver_res
    return cmpver(rel1, rel2)


def print_busy(prev_pos=0):
    """
    Shows a spinning bar when called like this:
    > i=0
    > while True:
    >    i = print_busy(i)
    """
    sys.stdout.write('\r')
    if prev_pos == 0:
        sys.stdout.write('-')
    elif prev_pos == 1:
        sys.stdout.write('/')
    elif prev_pos == 2:
        sys.stdout.write('|')
    else:
        sys.stdout.write('\\')
    sys.stdout.flush()
    return (prev_pos + 1) % 4


def to_human_size(fsize):
    """
    Pass a number from bytes, to human readable form, using 1024 multiples.
    """
    mb = fsize / (1024 * 1024)
    if mb >= 1:
        return '%dM' % mb
    kb = fsize / 1024
    if kb >= 1:
        return '%dK' % kb
    return '%dB' % fsize


def download(path, dest_path):
    """
    Download a package from a url.
    """
    headers = requests.head(path)
    chunk_size = 4096
    length = int(headers.headers.get('content-length', 0)) or 0
    logging.info('Downloading %s, length %s ...',
                 path,
                 length and to_human_size(length) or 'unknown')
    num_dots = 100
    dot_frec = (length / num_dots) or 1
    stream = requests.get(path, stream=True)
    prev_percent = 0
    progress = 0
    if length:
        sys.stdout.write('    %[')
    sys.stdout.flush()
    with open(dest_path, 'w') as rpm_fd:
        for chunk in stream.iter_content(chunk_size=chunk_size):
            if chunk:
                rpm_fd.write(chunk)
                progress += len(chunk)
                cur_percent = int(progress / dot_frec)
                if length and cur_percent > prev_percent:
                    for _ in xrange(cur_percent - prev_percent):
                        sys.stdout.write('=')
                    sys.stdout.flush()
                    prev_percent = cur_percent
                elif not length:
                    prev_percent = print_busy(prev_percent)
    if length:
        if cur_percent < num_dots:
            sys.stdout.write('=')
        sys.stdout.write(']')
    sys.stdout.write('\n')
    if not length:
        logging.info('    Done')


def copy(what, where):
    """Try to link, try to copy if cross-device"""
    try:
        os.link(what, where)
    except OSError as oerror:
        if oerror.errno == 18:
            shutil.copy2(what, where)
        else:
            raise


def extract_sources(rpm_path, dst_dir, with_patches=False):
    """
    Extract the source files fro  a srcrpm, uses rpm2cpio
    :param rpm_path: Path to the srcrpm
    :param dst_dir: Destination directory to hold the sources, will create it
        if it does not exist
    :param with_patches: if set to True, extract also the .patch files if any
    """
    if not os.path.isdir(dst_dir):
        os.makedirs(dst_dir)
    oldpath = os.getcwd()
    if not dst_dir.startswith('/'):
        dst_dir = oldpath + '/' + dst_dir
    if not rpm_path.startswith('/'):
        rpm_path = oldpath + '/' + rpm_path
    dst_path = dst_dir + '/' + rpm_path.rsplit('/', 1)[-1]
    copy(rpm_path, dst_path)
    os.chdir(dst_dir)
    try:
        rpm2cpio = subprocess.Popen(['rpm2cpio', dst_path],
                                    stdout=subprocess.PIPE)
        cpio_cmd = ['cpio', '-iv', '*gz', '*.zip', '*.7z']
        if with_patches:
            cpio_cmd.append('*.patch')
        with open(os.devnull, 'w') as devnull:
            cpio = subprocess.Popen(
                cpio_cmd,
                stdin=rpm2cpio.stdout,
                stdout=devnull,
                stderr=devnull,
            )
        rpm2cpio.stdout.close()
        cpio.communicate()
    finally:
        os.chdir(oldpath)
        os.remove(dst_path)


def sign_detached(src_dir, key, passphrase=None):
    """
    Create the detached signatures for the files in the specified dir.
    :param src_dir: Sources directory
    :param key: Key to sign the sources with
    :param passphrase: Passphrase for the given key
    """
    oldpath = os.getcwd()
    if not src_dir.startswith('/'):
        src_dir = oldpath + '/' + src_dir
    gpg = gnupg.GPG(gnupghome=os.path.expanduser('~/.gnupg'))
    with open(key) as key_fd:
        skey = gpg.import_keys(key_fd.read())
    fprint = skey.results[0]['fingerprint']
    keyid = None
    for user_key in gpg.list_keys(True):
        if user_key['fingerprint'] == fprint:
            keyid = user_key['keyid']
    if os.path.isdir(src_dir):
        for dname, _, files in os.walk(src_dir):
            for fname in files:
                if fname.endswith('.sig'):
                    continue
                fname = os.path.join(dname, fname)
                with open(fname) as fd:
                    signature = gpg.sign_file(
                        fd,
                        keyid=keyid,
                        passphrase=passphrase,
                        detach=True,
                    )
                if not signature.data:
                    raise Exception("Failed to sign file %s: \n%s",
                                    file,
                                    signature.stderr)
                with open(fname + '.sig', 'w') as sfd:
                    sfd.write(signature.data)
    else:
        fname = src_dir
        with open(key) as fd:
            signature = gpg.sign_file(
                fd,
                keyid=keyid,
                passphrase=passphrase,
                detach=True,
            )
            if not signature.data:
                raise Exception("Failed to sign file %s: \n%s",
                                file,
                                signature.stderr)
            with open(fname + '.sig', 'w') as sfd:
                sfd.write(signature.data)


def save_file(src_path, dst_path):
    """
    Save a file to a specific new path if not there already. Will create the
    path tree if it does not exist already.
    :param src_path: Source path for the package
    :param dst_path: New path to save the package to
    """
    if os.path.exists(dst_path):
        logging.debug('Not saving %s, already exists', dst_path)
        return
    logging.info('Saving %s', dst_path)
    if not os.path.exists(dst_path.rsplit('/', 1)[0]):
        os.makedirs(dst_path.rsplit('/', 1)[0])
    copy(src_path, dst_path)


def list_files(path, extension):
    '''Find all the files with the given extension under the given dir'''
    files_found = []
    for root, _, files in os.walk(path):
        for fname in files:
            if fname.endswith(extension):
                files_found.append(root + '/' + fname)
    return files_found


def split(what, separator, num_results=None):
    if num_results is None:
        return what.split(separator)
    res = what.split(separator, num_results)
    res.extend([''] * (num_results - len(res) + 1))
    return res


def rsplit(what, separator, num_results=None):
    if num_results is None:
        return what.rsplit(separator)
    res = what.rsplit(separator, num_results)
    res.extend([''] * (num_results - len(res) + 1))
    return res


def get_last(what, num):
    if len(what) >= num:
        return what[:num]
    else:
        what = what[:]
        what.extend([None] * (num - len(what)))
        return what
