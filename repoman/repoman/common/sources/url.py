#!/usr/bin/env python
"""
Parse a url, recursively or not.

URL -> Will parse the url and get all the packages in that page
rec:URL -> Will parse the urls recursively
"""
import logging
import re


import requests
from urlparse import (
    urljoin,
    urlsplit,
)


from . import ArtifactSource
from ..stores import has_store


logger = logging.getLogger(__name__)


class URLSource(ArtifactSource):

    DEFAULT_CONFIG = {}
    CONFIG_SECTION = 'URLSource'

    @classmethod
    def formats_list(cls):
        return (
            "URL",
            "rec:URL"
        )

    @classmethod
    def expand(cls, source_str, config):
        urls = set()
        # for some reason it requires two chars in the last group
        source_match = re.match(
            r'(?P<recursive>rec:)?(?P<url>https?://[^:]*):?(?P<filters>..*)?',
            source_str,
        )
        if not source_match:
            return set(), urls
        source = source_match.groupdict()
        if source['recursive']:
            urls = urls.union(cls.expand_recursive(source['url']))
        elif has_store(source['url']):
            urls.add(source['url'])
        else:
            urls = urls.union(cls.expand_page(source['url']))
        return source['filters'], urls

    @classmethod
    def expand_page(cls, page_url):
        logger.info('Parsing URL: %s', page_url)
        data = requests.get(page_url).text
        link_reg = re.compile(r'(?<=href=")[^"]+')
        art_list = set()
        for line in data.splitlines():
            links = link_reg.findall(line)
            art_list = art_list.union(set([
                cls.get_link(page_url, link)
                for link in links
                if has_store(link)
            ]))
        for art_url in art_list:
            logger.info('    Got artifact URL: %s', art_url)
        return art_list

    @staticmethod
    def strip_qs(url):
        split_url = urlsplit(url)
        if split_url.scheme:
            return "{0}://{1}{2}".format(*split_url)
        else:
            return "{2}".format(*split_url)

    @staticmethod
    def get_link(page_url, link, internal=False):
        page_url = URLSource.strip_qs(page_url)
        link_url = URLSource.strip_qs(link)
        if not re.match('https?://', link_url):
            link_url = urljoin(page_url, link_url)
        if link_url.startswith(page_url):
            return link_url
        else:
            if internal:
                return False
            else:
                return link_url

    @classmethod
    def expand_recursive(cls, page_url, level=0):
        if level > 0:
            logger.debug('Recursively fetching URL (level %d): %s',
                         level, page_url)
        else:
            logger.info('Recursively fetching URL (level %d): %s', level,
                        page_url)
        pkg_list = []
        data = requests.get(page_url).text
        url_reg = re.compile(
            r'(?<=href=")(/|%s|(?![^:]+?://))[^"]+/(?=")' % page_url)
        next_urls = (
            cls.get_link(page_url, match.group(), internal=True)
            for match in url_reg.finditer(data)
            if match.group() != page_url
        )
        for next_url in next_urls:
            if not next_url:
                continue
            pkg_list.extend(cls.expand_recursive(next_url, level + 1))
        pkg_list.extend(cls.expand_page(page_url))
        return pkg_list
