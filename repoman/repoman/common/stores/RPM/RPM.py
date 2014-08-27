#!/usr/bin/env python%
# encoding: utf-8
"""
This module holds the helper classes to represent a repository, that in our
case (oVirt) is a set of repositories, in the form:

Base_dir
├── rpm
│   └── $dist
│       ├── repodata
│       ├── SRPMS
│       └── $arch
└── src
    └── $name
        ├── $name-$version-src.tar.gz
        └── $name-$version-src.tar.gz.sig


This module has the classess that manage a set of rpms, ina hierarchical
fashion, in the order:

    name 1-* version 1-* inode 1-* rpm-instance

So that translated to classes, with the first being the placeholder for the
whole data structure, is:

    RPMList 1-* RPMName 1-* RPMVersion 1-* RPMInode 1-* RPM

All except the RPM class are implemented as subclasses of the python dict, so
as key-value stores.

For clarification, here's a dictionary like diagram:

    RPMList{
        name1: RPMName{
            version1: RPMVersion{
                inode1: RPMInode[RPM, RPM, ...]
                inode2: RPMInode[...]
            },
            version2: RPMVersion{...}
        },
        name2: RPMName{...}
    }

"""
import os
import logging
import re


import rpm
import pexpect


from ...utils import (
    download,
    cmpfullver,
)
from ...artifact import (
    Artifact,
    ArtifactVersion,
    ArtifactList,
    ArtifactName,
)


class RPM(Artifact):
    def __init__(self, path, temp_dir='/tmp', distro_reg=r'\.(fc|el)\d+',
                 to_all_distros=(r'ovirt-release\d*', r'ovirt-guest-tools')):
        """
        :param path: Path or url to the rpm
        :param temp_dir: If url specified, will use that temporary dir to store
            it, the caller should take care of creating and deleting that
            temporary dir if needed
        :param distro_regs: Regular expression to match the distributions from
           the release string of the rpm.
        :param to_all_distros: Special rpm names that must go to all the
            distributions ignoring their release strings
        """
        trans = rpm.TransactionSet()
        # Do not fail for unsigned rpms
        trans.setVSFlags(rpm._RPMVSF_NOSIGNATURES)
        if path.startswith('http:') or path.startswith('https:'):
            name = path.rsplit('/', 1)[-1]
            if not name:
                raise Exception('Passed trailing slash in path %s, '
                                'unable to guess package name'
                                % path)
            fpath = temp_dir + '/' + name
            download(path, fpath)
            path = fpath
        self.path = path
        with open(path) as fdno:
            try:
                hdr = trans.hdrFromFdno(fdno)
            except Exception:
                logging.error("Failed to parse header for %s", path)
                raise
            self.inode = os.fstat(fdno.fileno()).st_ino
        self.is_source = hdr[rpm.RPMTAG_SOURCEPACKAGE] and True or False
        self.sourcerpm = hdr[rpm.RPMTAG_SOURCERPM]
        self._name = hdr[rpm.RPMTAG_NAME]
        self._version = hdr[rpm.RPMTAG_VERSION]
        self.release = hdr[rpm.RPMTAG_RELEASE]
        self.signature = hdr[rpm.RPMTAG_SIGPGP]
        self._raw_hdr = hdr
        # will be calculated if needed
        self._md5 = None
        # Check if this package has to go to all distros
        if any((self.name for nreg in to_all_distros if re.match(nreg,
                                                                 self.name))):
            self.distro = 'all'
        else:
            self.distro = self.get_distro(self.release, distro_reg)
        self.arch = hdr[rpm.RPMTAG_ARCH] or 'none'
        # this property should uniquely identify a rpm entity, in the sense
        # that if you have two rpms with the same full_name they must package
        # the same content or one of them is wrongly generated (the version was
        # not bumped or something)
        self.full_name = 'rpm(%s %s %s %s)' % (
            self.name, self.distro, self.arch,
            self.is_source and 'src' or 'bin',
        )
        # remove the distro from the release for the version string
        if self.distro:
            self.ver_release = re.sub(
                r'\.%s[^.]*' % self.distro,
                '',
                self.release,
                1
            )
        else:
            self.ver_release = self.release
        self.ver_rel = '%s-%s' % (self.version, self.ver_release)

    @property
    def name(self):
        return self._name

    @property
    def version(self):
        return self._version

    @property
    def extension(self):
        if self.is_source:
            return '.src.rpm'
        return '.rpm'

    @property
    def type(self):
        if self.is_source:
            return 'source_rpm'
        return 'rpm'

    @staticmethod
    def get_distro(release, distro_reg):
        match = re.search(distro_reg, release)
        if match:
            return match.group()[1:]
        raise Exception('Unknown distro for %s' % release)

    def generate_path(self):
        """
        Returns the theoretical path that the rpm should be, instead of the
        current path it is. As explained at the module docs.

        If the package has to go to all distros, a placeholder for it will be
        set in the string
        """
        if self.is_source:
            arch_path = 'SRPMS'
            arch_name = 'src'
        else:
            arch_path = self.arch
            arch_name = self.arch
        return 'rpm/%s/%s/%s-%s-%s.%s.rpm' % (
            self.distro == 'all' and '%s' or self.distro,
            arch_path,
            self.name,
            self.version,
            self.release,
            arch_name,
        )

    def sign(self, keyuid, passwd):
        logging.info("SIGNING: %s", self.path)
        # TODO: Did not find a nicer documented way to do this, might dig into
        # the rpmsign code itself to find out when having some time
        child = pexpect.spawn(
            'rpmsign',
            [
                '--resign',
                '-D', '_signature gpg',
                '-D', '_gpg_name %s' % keyuid,
                self.path,
            ],
        )
        child.expect('Enter pass phrase: ')
        child.sendline(passwd)
        child.expect(pexpect.EOF)
        child.close()
        if child.exitstatus != 0:
            raise Exception("Failed to sign package.")
        self.__init__(self.path)
        if not self.signature:
            raise Exception("Failed to sign rpm %s with key '%s'"
                            % (self.path, keyuid))

    def __str__(self):
        """
        This string uniquely identifies a rpm file, if two rpms have the same
        string representation, the must point to the same file or a copy of
        it, if not, you wrongly generated two rpms with the same
        version/release and different content, or you signed them with
        different keys
        """
        return 'rpm(%s %s %s %s %s %s)' % (
            self.name, self.version,
            self.release, self.arch,
            self.is_source and 'src' or 'bin',
            self.signature and 'signed' or 'unsigned',
        )

    def __repr__(self):
        return self.__str__()


class RPMName(ArtifactName):
    """List of available versions for a package name"""
    def add_pkg(self, pkg, onlyifnewer):
        if onlyifnewer and (
                pkg.ver_rel in self
                or next((ver for ver in self.keys()
                         if cmpfullver(ver, pkg.ver_rel) >= 0), None)):
            return False
        elif pkg.ver_rel not in self:
            self[pkg.ver_rel] = ArtifactVersion(pkg.ver_rel)
        return self[pkg.ver_rel].add_pkg(pkg)


class RPMList(ArtifactList):
    """
    List of rpms, separated by name
    """
    def __init__(self, name_class=RPMName):
        super(RPMList, self).__init__(self)
        self.name_class = name_class
