#!/usr/bin/env python
import logging
from abc import (
    ABCMeta,
    abstractmethod,
    abstractproperty,
)
from ..utils import get_plugins


__all__ = get_plugins(plugin_dir=__file__.rsplit('/', 1)[0])


logger = logging.getLogger(__name__)
STORES = {}


class ArtifactStore(object):
    class __metaclass__(ABCMeta):
        def __init__(cls, name, bases, attrs):
            """
            Metaclass in charge of the registering, inherits from ABCMeta
            because ArtifactStore is an abstract class too.
            """
            ABCMeta.__init__(cls, name, bases, attrs)
            # Don't register this base class
            if name != 'ArtifactStore':
                STORES[name] = cls

    @classmethod
    def get_conf_section(cls):
        return 'store.' + cls.CONFIG_SECTION

    @abstractproperty
    def DEFAULT_CONFIG(self):
        """
        Default configuration values for that store
        """
        pass

    @abstractproperty
    def CONFIG_SECTION(self):
        """
        Configuration section name for this store
        """
        pass

    @abstractmethod
    def handles_artifact(self, artifact_str):
        """
        This method must return True if the given artifact (as a path or url)
        can be handled by the implemented store

        :param artifact_str: full path or url to the artifact
        """
        pass

    @abstractmethod
    def add_artifact(self, artifact, **args):
        """
        This method adds an artifact to the store

        :param artifact: full path or url to the artifact
        """
        pass

    @abstractproperty
    def path_prefix(self):
        """
        Returns the path prefis of the store, that is, the first level after
        the root of the repo (for example, iso, exe, src or rpm)
        """
        pass

    @abstractmethod
    def save(self, **args):
        """
        Realizes the changes made to the store, usually writing the artifacts
        to disk or any other operation required to persist the store state
        """
        pass

    @abstractmethod
    def get_latest(self, num=1, **args):
        """
        Returns the latest num versions for each artifact in the store.

        :param num: number of newest versions to return
        """


def has_store(artifact):
    """
    Check if any of the registered stores can handle the given artifact

    :param artifact: full path or url to the artifact
    """
    return any(
        store.handles_artifact(artifact)
        for store in STORES.itervalues()
    )

# Force the load of all the plugins
from . import *  # noqa
