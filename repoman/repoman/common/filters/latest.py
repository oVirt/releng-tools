#!/usr/bin/env python
"""
source:latest
source:latest=N

Get's the latest N rpms (1 by default)
"""
import re
from . import ArtifactFilter
from ..stores import STORES
from ..utils import split


class LatestFilter(ArtifactFilter):

    DEFAULT_CONFIG = {}
    CONFIG_SECTION = 'LatestFilter'

    @classmethod
    def filter(cls, source_str, art_list, config):
        match = re.match(r'latest(=(?P<num>\d+))?(:.*)?$', source_str)
        if not match or not art_list:
            return source_str, art_list
        filters_str = split(source_str, ':', 1)[-1]
        latest = match.groupdict().get('num', 1) or 1
        # get the configurad stores list
        stores = {
            store_name: store_cls(
                config=config.get_section(
                    section='store.' + store_cls.CONFIG_SECTION
                )
            )
            for store_name, store_cls
            in STORES.iteritems()
            if store_name in config.getarray('stores')
        }
        # populate them with the artifacts
        for artifact in art_list:
            store_name = next(
                (
                    s_name
                    for (s_name, s_cls) in stores.iteritems()
                    if s_cls.handles_artifact(artifact)
                ),
                None
            )
            if store_name:
                stores[store_name].add_artifact(artifact)
        # gather the latest artifacts from each store
        filtered_arts = set()
        for store in stores.itervalues():
            filtered_arts = filtered_arts.union(
                store.get_latest(num=int(latest)))
        return filters_str, filtered_arts
