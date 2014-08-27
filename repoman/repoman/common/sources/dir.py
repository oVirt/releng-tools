#!/usr/bin/env python
"""
dir_path
file_path
dir:repo_name

Will find all the matching artifacts under the specified dir or the given
file.
If relative path passed, it will be relative to the base_repos_path config
value
"""
import os
import logging


from . import ArtifactSource
from ..stores import has_store
from ..utils import (
    find_recursive,
    split,
)


logger = logging.getLogger(__name__)


class DirSource(ArtifactSource):

    DEFAULT_CONFIG = {
        'allowed_dir_paths': '/var/www/html/pub,/var/www/html/repos',
    }
    CONFIG_SECTION = 'DirSource'

    @classmethod
    def formats_list(cls):
        return (
            "dir_path",
            "file_path",
            "dir:repo_path"
        )

    @classmethod
    def expand(cls, source_str, config):
        allowed_paths = config.getarray('allowed_dir_paths')
        if source_str.startswith('dir:'):
            source_str = source_str.split(':', 1)[-1]
        # get rid of any trailing filters
        source_str, filters_str = split(source_str, ':', 1)
        # handle relative paths, that is, the ones relative to the
        # base_repo_path
        if not source_str.startswith('/'):
            for path in allowed_paths:
                full_source_str = os.path.abspath(
                    path + '/' + source_str
                )
                if os.path.isdir(full_source_str):
                    source_str = full_source_str
                    break
            else:
                raise Exception('Unable to find non-existing source %s'
                                % source_str)
        if not any(path for path in allowed_paths
                   if source_str.startswith(path)):
            print allowed_paths
            raise Exception('Source %s outside the base path' % source_str)
        if not os.path.isdir(source_str) \
           and has_store(source_str):
            return filters_str, [source_str]
        return filters_str, find_recursive(source_str, has_store)
