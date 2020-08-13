#!/usr/bin/python3

import argparse
import configparser
import dnf
import functools
import glob
import hawkey
import os
import rpm
import sys

debug = False
strict = False
versions = ['3.6.', '4.0.', '4.1.', '4.2.', '4.3.', '4.4.']


def to_include(milestone_file, target_milestone_file):
    if milestone_file == target_milestone_file:
        return False

    milestone = os.path.splitext(os.path.basename(milestone_file))[0]
    target_milestone = os.path.splitext(
        os.path.basename(target_milestone_file)
    )[0]

    nvr1 = get_NVR(milestone)
    nvr2 = get_NVR(target_milestone)

    if strict:
        nvr_version = nvr2.version.split('.')

        version_idx = versions.index(nvr_version[0]+'.'+nvr_version[1]+'.')
        if nvr_version[2] != '0':
            versions_to_check = versions[version_idx]
        else:
            versions_to_check = (
                versions[version_idx-1], versions[version_idx]
            )

        if (
            nvr1.version.startswith(versions_to_check) and
            version_compare(nvr1, nvr2) < 0
        ):
            return True
    else:
        if version_compare(nvr1, nvr2) < 0:
            return True


def version_compare(nvr1, nvr2):
    if (
        type(nvr1) != type(nvr2) or
        (type(nvr1) != str and type(nvr1) != hawkey.NEVRA)
    ):
        raise ValueError(
            'Both parameters must be of the same type, '
            'and must be either String or hawkey.NEVRA'
        )

    if type(nvr1) == str:
        milestone1 = os.path.splitext(os.path.basename(nvr1))[0]
        milestone2 = os.path.splitext(os.path.basename(nvr2))[0]
        nvr1 = get_NVR(milestone1)
        nvr2 = get_NVR(milestone2)

    return rpm.labelCompare(
        (
            None,
            nvr1.version,
            None,
        ),
        (
            None,
            nvr2.version,
            None,
        )
    )


def get_NVR(filename):
    subject = dnf.subject.Subject(filename)
    nvr = subject.get_nevra_possibilities(forms=hawkey.FORM_NEVR)
    if not nvr:
        nvr = subject.get_nevra_possibilities(forms=hawkey.FORM_NEV)
    else:
        raise RuntimeError('Wrong milestone filename format.')

    if len(nvr) > 1:
        raise RuntimeError('Non definitive milestone decoding.')

    nvr = nvr[0]

    if nvr.name != 'ovirt':
        raise RuntimeError(
            'Non-oVirt milestone file comparison - (%s)' % nvr.name
        )

    if nvr.epoch:
        raise RuntimeError(
            'Wrong milestone filename format - (%s)' % filename
        )

    if len(nvr.version.split('.')) != 3:
        raise RuntimeError(
            'Wrong milestone version format - (%s)' % nvr.version
        )
    return nvr


parser = argparse.ArgumentParser()
parser.add_argument('config')
parser.add_argument(
    '--debug',
    action='store_true',
    help='output more debug information'
)
parser.add_argument(
    '--strict',
    action='store_true',
    help='use strict rules for milestone comparison'
)
args = parser.parse_args()
debug = args.debug
strict = args.strict

if not os.path.exists(args.config):
    raise RuntimeError("Configuration file doesn't exist")

current_config = configparser.ConfigParser()
current_config.read(args.config)

base_dir = os.path.dirname(args.config)

old_conf = [x for x in glob.glob(os.path.join(base_dir, '*'))
            if to_include(x, args.config)]
old_conf = sorted(old_conf, key=functools.cmp_to_key(version_compare))
if debug:
    print('\nVerifying the following milestone conf. file:')
    print('\t%s' % args.config)
    print('\nUsing the following milestone conf. files for verification:')
    for milestone in old_conf:
        print('\t%s' % milestone)
    print('')

old_config = configparser.ConfigParser(strict=False)
old_config.read(old_conf)
exit_status = 0
for section in current_config.sections():
    if section == "default":
        continue
    try:
        previous = current_config.get(section, "previous")
    except configparser.NoOptionError:
        pass
    else:
        known_last = old_config.get(section, "current")
        if previous != known_last:
            print("%s has previous set to %s while last known is %s" % (
                section, previous, known_last))
            exit_status = 1

sys.exit(exit_status)
