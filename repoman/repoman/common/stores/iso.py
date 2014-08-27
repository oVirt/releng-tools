#!/usr/bin/env python
# encoding:utf-8
"""
This module holds the class and methods to manage an iso store.

repository_dir
└── iso
    ├── $project1
    │   │   ├── $iso1
    │   │   └── ...
    │   └── ...
    └── ...
"""
import os
import re
import logging
from getpass import getpass
from . import ArtifactStore
from ..utils import (
    save_file,
    download,
    list_files,
    sign_detached,
)
from ..artifact import (
    Artifact,
    ArtifactName,
    ArtifactList,
)


logger = logging.getLogger(__name__)


class Iso(Artifact):
    def __init__(self, path, temp_dir):
        self.temp_dir = temp_dir
        if path.startswith('http:') or path.startswith('https:'):
            fname = path.rsplit('/', 1)[-1]
            if not fname:
                raise Exception('Passed trailing slash in path %s, '
                                'unable to guess iso name'
                                % path)
            fpath = temp_dir + '/' + fname
            download(path, fpath)
            path = fpath
        with open(path) as fdno:
            self.inode = os.fstat(fdno.fileno()).st_ino
        self.path = path
        self._md5 = None
        self._name = None
        self._version = None

    @property
    def version(self):
        if not self._version:
            self._version = re.match(
                r'(.*/)?ovirt-(guest-tools|live)-(?P<version>.*).iso',
                self.path
            ).groupdict().get('version')
        return self._version

    @property
    def extension(self):
        return '.iso'

    @property
    def name(self):
        if not self._name:
            self._name = re.match(
                r'(.*/)?(?P<name>ovirt-guest-tools|ovirt-live).*',
                self.path
            ).groupdict().get('name')
        return self._name

    @property
    def type(self):
        return 'iso'

    def sign(self, key, passwd):
        with open(self.path + '.md5sum', 'w') as md5_fd:
            md5_fd.write(self.md5)
        sign_detached(self.path + '.md5sum', key=key, passphrase=passwd)


class IsoStore(ArtifactStore):
    """
    Represents the repository sctructure, it does not require that the repo has
    the structure specified in the module doc when loading it, but when adding
    new isos it will create the new files in that directory structure.

    Configuration options:

      temp_dir
        Temporary dir to store any transient downloads (like rpms from
        urls). The caller should make sure it exists and clean it up if needed.

      path_prefix
        Prefixes of this store inside the globl artifact repository, separated
        by commas

      signing_key
        Path to the gpg keey to sign the rpms with, will not sign them if not
        set

      signing_passphrase
        Passphrase for the above key
    """

    CONFIG_SECTION = 'IsoStore'
    DEFAULT_CONFIG = {
        'temp_dir': 'generate',
        'path_prefix': 'iso',
        'signing_key': '',
        'signing_passphrase': 'ask',
    }

    def __init__(self, config, repo_path=None):
        """
        :param path: Path to the repository directory, if passed it will
            automatically add all the isos under it to the repo if any.
        """
        self.name = self.__class__.__name__
        self.config = config
        self.isos = ArtifactList('isos')
        self._path_prefix = self.config.get('path_prefix').split(',')
        self.path = repo_path
        self.to_copy = []
        self.sign_key = config.get('signing_key')
        self.sign_passphrase = config.get('signing_passphrase')
        if self.sign_key and self.sign_passphrase == 'ask':
            self.sign_passphrase = getpass('Key passphrase: ')
        if repo_path:
            logger.info('Loading repo %s', repo_path)
            for iso in list_files(repo_path, '.iso'):
                self.add_artifact(
                    iso,
                    to_copy=False,
                    hidelog=True,
                )
            logger.info('Repo %s loaded', repo_path)

    @property
    def path_prefix(self):
        return self._path_prefix

    @classmethod
    def handles_artifact(cls, artifact_str):
        return re.match(r'(.+/)?ovirt-(live|guest-tools).*\.iso', artifact_str)

    def add_artifact(self, iso, **args):
        self.add_iso(iso, **args)

    def add_iso(self, iso, onlyifnewer=False, to_copy=True, hidelog=False):
        """
        Generic functon to add an rpm package to the repo.

        :param iso: path or url to the iso file to add
        :param onlyifnewer: If set to True, will only add the package if it's
            not there already or the version is newer than the on already
            there.
        :param to_copy: If set to True, will add that package to the list of
            packages to copy into the repo when saving, usually used when
            adding new packages to the repo.
        :param hidelog: If set to True will not show the extra information
            (used when loading a repository to avoid verbose output)
        """
        iso = Iso(
            iso,
            temp_dir=self.config.get('temp_dir'),
        )
        if self.isos.add_pkg(iso, onlyifnewer):
            if to_copy:
                self.to_copy.append(iso)
            if not hidelog:
                logger.info('Adding iso %s to repo %s', iso.path, self.path)
        else:
            if not hidelog:
                logger.info("Not adding %s, there's already an equal or "
                            "newer version", iso)

    def save(self, **args):
        self._save(**args)

    def _save(self, onlylatest=False):
        """
        Copy all the extra isos added to the repository and save it's state.

        :param onlylatest: Only copy the latest version of the added rpms.
        """
        logger.info('Saving new added isos into %s', self.path)
        for iso in self.to_copy:
            if onlylatest and not self.is_latest_version(iso):
                logger.info('Skipping %s a newer version is already '
                            'in the repo.', iso)
                continue
            dst_path = os.path.join(self.path,
                                    self.path_prefix[0],
                                    iso.generate_path())
            save_file(iso.path, dst_path)
            iso.path = dst_path
        if self.sign_key:
            logger.info('')
            logger.info('Signing isos')
            self.sign_isos()
        logger.info('')
        logger.info('Saved %s\n', self.path)

    def is_latest_version(self, iso):
        """
        Check if the given iso is the latest version in the repo
        :pram iso: ISO instance of the package to compare
        """
        verlist = self.isos.get(iso.full_name, {})
        if not verlist or iso.version in verlist.get_latest():
            return True
        return False

    def delete_old(self, keep=1, noop=False):
        """
        Delete the oldest versions for each package from the repo
        :param keep: Maximium number of versions to keep of each package
        :param noop: If set, will only log what will be done, not actually
            doing anything.
        """
        new_isos = ArtifactList(self.isos)
        for name, versions in self.isos.iteritems():
            if len(versions) <= keep:
                continue
            to_keep = ArtifactName()
            for _ in range(keep):
                latest = versions.get_latest()
                to_keep.update(latest)
                versions.pop(latest.keys()[0])
            new_isos[name] = to_keep
            for version in versions.keys():
                logger.info('Deleting %s version %s', name, version)
                versions.del_version(version, noop)
        self.isos = new_isos

    def get_artifacts(self, regmatch=None, fmatch=None, latest=0):
        """
        Get the list of rpms, filtered or not.
        :param regmatch: Regular expression that will be applied to the path of
            each package to filter it
        :param fmatch: Filter function that must return True for a package to
            be selected, will be passed the RPM object as only parameter
        :param latest: If set to N>0, it will return only the N latest versions
            for each package
        """
        return self.isos.get_artifacts(
            regmatch=regmatch,
            fmatch=fmatch,
            latest=latest)

    def get_latest(self, num=1):
        """
        Return the num latest versions for each rpm in the repo
        :param num: number of latest versions to return
        """
        return [iso.path for iso in self.get_artifacts(latest=num)]

    def sign_isos(self):
        """
        Sign all the isos in the repo.
        """
        passphrase = self.sign_passphrase
        for iso in self.get_artifacts():
            iso.sign(self.sign_key, passphrase)
        logger.info("Done signing")
