#!/usr/bin/env python
import logging


from ..utils import get_plugins


__all__ = get_plugins(plugin_dir=__file__.rsplit('/', 1)[0])


logger = logging.getLogger(__name__)
FILTERS = {}


class ArtifactFilter(object):
    class __metaclass__(type):
        def __init__(cls, name, bases, attrs):
            type.__init__(cls, name, bases, attrs)
            # Don't register this base class
            if name != 'ArtifactFilter':
                FILTERS[name] = cls


# load all the plugins
from . import *  # noqa
