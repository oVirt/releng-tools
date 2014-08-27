#!/usr/bin/env python
"""
When specifying a source for an artifact, you have to do it in this format:

source_type:value[:filter[:filter[...]]]

For each source, it will be expanded, and filtered. An example:

repo:master-nightly:name~ovirt-engine.*:latest=2

"""
import logging
from . import (
    sources,
    filters,
)


logger = logging.getLogger(__name__)


class Parser(object):
    def __init__(self, config):
        self.config = config
        self.filters = config.getarray('filters')
        self.filters = {
            key: val()
            for key, val in filters.FILTERS.iteritems()
            if key in self.filters or 'all' in self.filters}
        self.sources = config.getarray('sources')
        self.sources = {
            key: val()
            for key, val in sources.SOURCES.iteritems()
            if key in self.sources or 'all' in self.sources}

    def parse(self, full_source_str):
        art_list = set()
        for aname, source in self.sources.iteritems():
            source_str = full_source_str
            logger.debug('Checking source %s with %s', aname, source_str)
            result = source.expand(
                source_str,
                self.config.get_section(
                    section='source.' + source.CONFIG_SECTION)
            )
            filters_str, art_list = result
            # If we have nothing to filter, keep try next source parser
            if not art_list:
                continue
            # check if there were any filters in the source definition, finish
            # if not
            if not filters_str:
                break
            # check all the filters until finished or we can't resolve any more
            # of the filters strings
            prev_filters_str = ''
            while filters_str and filters_str != prev_filters_str:
                prev_filters_str = filters_str
                for fname, fclass in self.filters.iteritems():
                    logger.info('Filtering filter %s with %s',
                                filters_str, fname)
                    result = fclass.filter(
                        filters_str,
                        art_list,
                        self.config.get_section(
                            section='filter.' + fclass.CONFIG_SECTION)
                    )
                    filters_str, art_list = result
                if not filters_str:
                    break
            # We skip all other sources if we found the matching one
            break
        return art_list
