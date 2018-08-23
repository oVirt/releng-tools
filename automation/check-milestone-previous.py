#!/usr/bin/python3

import argparse
import configparser
import glob
import os

parser = argparse.ArgumentParser()
parser.add_argument('config')
args = parser.parse_args()

current_config = configparser.ConfigParser()
current_config.read(args.config)

base_dir = os.path.dirname(args.config)

old_conf = [x for x in glob.glob(os.path.join(base_dir, '*'))
            if x < args.config]
old_conf.sort()

old_config = configparser.ConfigParser(strict=False)
old_config.read(old_conf)

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
