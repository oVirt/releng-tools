#!/usr/bin/env python
import logging
import re
import requests
from ..stores import has_store
from ..utils import split
from . import ArtifactSource


logger = logging.getLogger(__name__)


class JenkinsSource(ArtifactSource):

    DEFAULT_CONFIG = {
        'jenkins_host_re': r'jenkins\.ovirt\.org',
    }
    CONFIG_SECTION = 'JenkinsSource'

    @classmethod
    def formats_list(cls):
        return (
            "https?://{JenkinsSource[jenkins_host_re]/*}",
        )

    @classmethod
    def expand(cls, source_str, config):
        art_list = []
        if not re.match('https?://%s/' % config.get('jenkins_host_re'),
                        source_str):
            return source_str, art_list
        filters_str = split(source_str, ':', 2)[-1]
        source_str = ':'.join(source_str.split(':', 2)[:2])
        lvl1_page = requests.get(source_str + '/api/json?depth=3').json()
        url = lvl1_page['url']
        logger.info('Parsing jenkins URL: %s', source_str)
        if url.endswith('/'):
            url = url[:-1]
        # handle multicongif jobs
        for run in lvl1_page.get('runs', (lvl1_page,)):
            if run.get('number', None) != lvl1_page.get('number', None):
                continue
            for artifact in run.get('artifacts', []):
                if not has_store(artifact['relativePath']):
                    continue
                new_url = '%s/artifact/%s' % (run['url'],
                                              artifact['relativePath'])
                art_list.append(new_url)
                logger.info('    Got URL: %s', new_url)
        if not art_list:
            logging.warn('    No artifacts found')
        logging.info('    Done')
        return filters_str, art_list
