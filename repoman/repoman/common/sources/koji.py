#!/usr/bin/env python
"""
https?://${koji_host}/*

Handles koji build urls
TODO: Improve the second level detections (now filtering buildArch and
      buildSRPM
links only)
"""
import logging
import re


import requests


from . import ArtifactSource
from .url import URLSource
from ..utils import split


logger = logging.getLogger(__name__)


class KojiSource(ArtifactSource):

    DEFAULT_CONFIG = {
        'koji_host_re': r'koji\.fedoraproject\.org',
    }
    CONFIG_SECTION = 'KojiSource'

    @classmethod
    def formats_list(cls):
        return (
            "https?://{KojiSource[koji_host_re]}/*",
        )

    @classmethod
    def expand(cls, source_str, config):
        art_list = []
        if not re.match('https?://%s/' % config.get('koji_host_re'),
                        source_str):
            return '', art_list
        # remove filters
        proto, url = source_str.split('://', 1)
        url, filters_str = split(url, ':', 1)
        lvl1_url = '%s://%s' % (proto, url)
        lvl1_page = requests.get(lvl1_url).text
        lvl2_reg = re.compile(r'(?<=href=")[^"]+(?=.*(buildArch|buildSRPM))')
        logger.info('Parsing Koji URL: %s', lvl1_url)
        lvl2_urls = [
            URLSource.get_link(lvl1_url, match.group())
            for match in (lvl2_reg.search(i) for i in lvl1_page.splitlines())
            if match
        ]
        for url in lvl2_urls:
            logger.info('    Got 2nd level URL: %s', url)
            art_list.extend(URLSource.expand_page(url))
        if not art_list:
            logger.warn('    No packages found')
            logger.info('    Done')
        return filters_str, art_list
