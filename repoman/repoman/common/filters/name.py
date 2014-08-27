#!/usr/bin/env python
"""
source:name~regexp

Filter packges by file name, for example:

http://myhost.com/packages/:name~vdsm.*

Will match all the packages in that url that have vdsm.* as name (will not
match any previous patch in the url)
"""
import re
from . import ArtifactFilter
from ..utils import split


class NameFilter(ArtifactFilter):

    DEFAULT_CONFIG = {}
    CONFIG_SECTION = 'NameFilter'

    @classmethod
    def filter(cls, source_str, art_list, config):
        filtered_arts = set()
        if source_str.startswith('name~'):
            name_reg, filters_str = split(source_str, ':', 1)
            name_match = re.compile(name_reg.split('~', 1)[-1])
            for art in art_list:
                if name_match.match(art.rsplit('/', 1)[-1]):
                    filtered_arts.add(art)
            return filters_str, filtered_arts
        else:
            return source_str, art_list
