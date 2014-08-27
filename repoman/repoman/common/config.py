#!/usr/bin/env python
from six.moves import StringIO
from six.moves import configparser as cp
import os
from .stores import STORES
from .filters import FILTERS
from .sources import SOURCES


DEFAULT_CONFIG = """
[main]
allowed_repo_paths = /var/www/html/pub
temp_dir = generate
singing_key =
signing_passphrase = ask
stores = all
filters = all
sources = all
"""


def update_conf_from_plugin(config, plugins, prefix):
    # load all the configs from the sotres, on their sections
    for plugin in plugins.itervalues():
        conf_section = prefix + '.' + plugin.CONFIG_SECTION
        if not config.has_section(conf_section):
            config.add_section(conf_section)
        for opt_name, opt_value in plugin.DEFAULT_CONFIG.iteritems():
            if not config.has_option(conf_section, opt_name):
                config.set(conf_section, opt_name, opt_value)
            else:
                print config.get(conf_section, opt_name)


class Config(object):
    """
    Configuration object to wrap some config values.
    It keeps the configuration objects, one with the default values for all the
    sections and one with all the custom ones (from config files or set after).

    The resolution order is:
       custom_config(current_section -> main_section) ->
       default_config(current_section -> main_section)
    """
    def __init__(self, path=None, section='main'):
        self.section = section
        # load the specified file, if any
        self.config = cp.SafeConfigParser()
        self.config.add_section(self.section)
        if path:
            self.load(path)
        self.default_config = cp.SafeConfigParser()
        self.default_config.readfp(StringIO(DEFAULT_CONFIG))
        self.load_plugins()

    def load_plugins(self):
        # load all the configs from the plugins, on their sections
        update_conf_from_plugin(self.default_config, STORES, 'store')
        update_conf_from_plugin(self.default_config, FILTERS, 'filter')
        update_conf_from_plugin(self.default_config, SOURCES, 'source')

    def load(self, path):
        return self.config.read((os.path.expanduser(path),))

    def __getattr__(self, what):
        try:
            val = getattr(self.config, what)
        except AttributeError:
            val = getattr(self.default_config, what)
        return val

    def set(self, entry, value):
        if not self.config.has_section(self.section):
            self.config.add_section(self.section)
        return self.config.set(self.section, entry, value)

    def _resolve_retrieval(self, entry, func_name):
        try:
            val = getattr(self.config, func_name)(self.section, entry)
        except (cp.NoOptionError, cp.NoSectionError):
            try:
                val = getattr(self.config, func_name)('main', entry)
            except (cp.NoOptionError, cp.NoSectionError):
                try:
                    val = getattr(
                        self.default_config, func_name
                    )(self.section, entry)
                except (cp.NoOptionError, cp.NoSectionError):
                    val = getattr(
                        self.default_config, func_name
                    )('main', entry)
        return val

    def get(self, entry):
        return self._resolve_retrieval(entry, 'get')

    def getboolean(self, entry):
        return self._resolve_retrieval(entry, 'getboolean')

    def getint(self, entry):
        return self._resolve_retrieval(entry, 'getint')

    def getfloat(self, entry):
        return self._resolve_retrieval(entry, 'getfloat')

    def getarray(self, entry):
        val = self.get(entry)
        val = [elem.strip() for elem in val.split(',')]
        return val

    def get_section(self, section):
        new_config = Config(section=section)
        new_config.config = self.config
        new_config.default_config = self.default_config
        return new_config
