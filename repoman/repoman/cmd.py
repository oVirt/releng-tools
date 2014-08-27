#!/usr/bin/env python
"""
This program is a helper to repo management

Started as specific for rpm files, but was modified to be able to support
different types of artifacts
"""
import argparse
import logging
from urllib3 import connectionpool
from getpass import getpass
from .common.config import Config
from .common.repo import Repo
from .common.stores import STORES
from .common.sources import SOURCES


logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('-n', '--noop', action='store_true')
    parser.add_argument('-c', '--config', action='store', default=None,
                        help='Configuration file to use')
    subparsers = parser.add_subparsers(dest='action')

    par_rm_dups = subparsers.add_parser(
        'rm-dups', help='Remove duplicated packages and create hard links.')
    par_rm_dups.add_argument(
        '-d', '--dir', required=True,
        help='Directory to remove dplicates from.')

    par_repo = subparsers.add_parser('repo', help='Repository management.')
    par_repo.add_argument(
        '-s', '--stores', required=False, default=STORES.keys(),
        help='Store classes to take into account when loading the '
        'repo. Available ones are %s' % ', '.join(STORES.keys()))
    par_repo.add_argument('-d', '--dir', required=True,
                          help='Directory of the repo.')
    par_repo.add_argument('-k', '--key', required=False,
                          help='Path to the key to use when signing, will '
                          'not sign any rpms if not passed.')
    par_repo.add_argument('--passphrase', required=False,
                          help='Passphrase to unlock the singing key')
    repo_subparser = par_repo.add_subparsers(dest='repoaction')
    add_rpm = repo_subparser.add_parser('add', help='Add an artifact')
    add_rpm.add_argument(
        '-t', '--temp-dir', action='store', default=None,
        help='Temporary dir to use when downloading artifacts'
    )
    add_rpm.add_argument(
        'artifact_source', nargs='+',
        help=(
            'An artifact source to add, it can be one of: '
            + ', '.join(', '.join(source.formats_list())
                        for source in SOURCES.itervalues())
        )
    )

    generate_src = repo_subparser.add_parser(
        'generate-src',
        help='Populate the src dir with the tarballs from the src.rpm '
        'files in the repo')
    generate_src.add_argument('-p', '--with-patches', action='store_true',
                              help='Include the patch files')

    repo_subparser.add_parser(
        'createrepo',
        help='Run createrepo on each distro repository.')

    remove_old = repo_subparser.add_parser(
        'remove-old',
        help='Remove old versions of packages.')
    remove_old.add_argument('-k', '--keep', action='store',
                            default=1, help='Number of versions to '
                            'keep')
    return parser.parse_args()


def main():
    args = parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
        logging.root.level = logging.DEBUG
        #  we want connectionpool debug logs
        connectionpool.log.setLevel(logging.DEBUG)
        logging.debug('Enabled verbose mode')
    else:
        logging.basicConfig(level=logging.INFO)
        logger.root.level = logging.INFO
        #  we don't want connectionpool info logs
        connectionpool.log.setLevel(logging.WARN)

    if args.config:
        config = Config(path=args.config)
    else:
        config = Config()

    if args.action == 'rm-dups':
        if args.dir.endswith('/'):
            path = args.dir[:-1]
        else:
            path = args.dir
        # TODO(dcaro)
        raise Exception('comming soon')
    elif args.action == 'repo':
        if args.dir.endswith('/'):
            path = args.dir[:-1]
        else:
            path = args.dir
        # handle the temporary dir setting
        if args.temp_dir:
            config.set('temp_dir', args.temp_dir)
        # handle the signing_key and passphrase
        if args.key:
            config.set('signing_key', args.key)
            config.set('signing_passphrase', args.passphrase)
        if args.stores:
            config.set('stores', args.stores)
        repo = Repo(path=path, config=config)
        logger.info('')
        if args.repoaction == 'add':
            logger.info('Adding artifacts to the repo %s', repo.path)
            for art_src in args.artifact_source:
                repo.add_source(art_src)
            logger.info('')
            repo.save()
        elif args.repoaction == 'generate-src':
            if args.key and args.passphrase == 'ask':
                passphrase = getpass('Key passphrase: ')
            else:
                passphrase = args.passphrase
            repo.generate_sources(args.with_patches, args.key, passphrase)
        elif args.repoaction == 'createrepo':
            repo.createrepo()
        elif args.repoaction == 'remove-old':
            repo.delete_old(keep=int(args.keep), noop=args.noop)
        elif args.repoaction == 'sign-rpms':
            if args.passphrase == 'ask':
                passphrase = getpass('Key passphrase: ')
            else:
                passphrase = args.passphrase
            repo.sign_rpms(key=args.key, passphrase=passphrase)
