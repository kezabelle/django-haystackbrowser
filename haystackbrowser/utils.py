# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.management.commands.diffsettings import module_to_dict
import logging
from django.core.exceptions import ImproperlyConfigured
from django.template.defaultfilters import yesno
from haystack.constants import VALID_FILTERS
from django.utils.translation import ugettext_lazy as _
try:
    from django.utils.encoding import force_text
except ImportError:  # Django < 1.4 didn't have force_text because it predates 1.4-1.5 py3k support
    from django.utils.encoding import force_unicode as force_text


logger = logging.getLogger(__name__)


class HaystackConfig(object):
    __slots__ = (
        'version',
    )

    def __init__(self):
        if self.is_version_2x():
            logger.debug("Guessed Haystack 2.x")
            self.version = 2
        elif self.is_version_1x():
            logger.debug("Guessed Haystack 1.2.x")
            self.version = 1
        else:
            self.version = None


    def __repr__(self):
        return '<%(module)s.%(cls)s version=%(version)d, ' \
               'multiple_connections=%(conns)s ' \
               'supports_faceting=%(facets)s>' % {
            'module': self.__class__.__module__,
            'cls': self.__class__.__name__,
            'conns': yesno(self.has_multiple_connections()),
            'facets': yesno(self.supports_faceting()),
            'version': self.version,
        }

    def is_version_1x(self):
        return getattr(settings, 'HAYSTACK_SEARCH_ENGINE', None) is not None

    def is_version_2x(self):
        return getattr(settings, 'HAYSTACK_CONNECTIONS', None) is not None

    def supports_faceting(self):
        if self.version == 1:
            engine_1x = getattr(settings, 'HAYSTACK_SEARCH_ENGINE', None)
            return engine_1x in ('solr', 'xapian')
        elif self.version == 2:
            engine_2x = getattr(settings, 'HAYSTACK_CONNECTIONS', {})
            try:
                engine_2xdefault = engine_2x['default']['ENGINE']
                ok_engines = (
                    'solr' in engine_2xdefault,
                    'xapian' in engine_2xdefault,
                    'elasticsearch' in engine_2xdefault,
                )
                return any(ok_engines)
            except KeyError as e:
                raise ImproperlyConfigured("I think you're on Haystack 2.x without "
                                           "a `HAYSTACK_CONNECTIONS` dictionary")
        # I think this is unreachable, but for safety's sake we're going to
        # assume that if it got here, we can't know faceting is OK and working
        # so we'll disable the feature.
        return False

    def get_facets(self, sqs=None):
        if self.version == 2:
            from haystack import connections
            facet_fields = connections['default'].get_unified_index()._facet_fieldnames
            return tuple(sorted(facet_fields.keys()))
        elif self.version == 1:
            assert sqs is not None, "Must provide a SearchQuerySet " \
                                    "to get the site from"
            possible_facets = []
            for k, v in sqs.site._field_mapping().items():
                if v['facet_fieldname'] is not None:
                    possible_facets.append(v['facet_fieldname'])
            return tuple(sorted(possible_facets))
        return ()

    def supports_multiple_connections(self):
        if self.version == 1:
            return False
        elif self.version == 2:
            return True
        return False

    def has_multiple_connections(self):
        if self.supports_multiple_connections():
            engine_2x = getattr(settings, 'HAYSTACK_CONNECTIONS', {})
            return len(engine_2x) > 1
        return False

    def get_connections(self):
        def consumer():
            engine_2x = getattr(settings, 'HAYSTACK_CONNECTIONS', {})
            for engine, values in engine_2x.items():
                engine_name = force_text(engine)
                if 'TITLE' in values:
                    title = force_text(values['TITLE'])
                else:
                    title = engine_name
                yield (engine_name, title)
        return tuple(consumer())

    def get_valid_filters(self):
        filters = sorted(VALID_FILTERS)
        names = {
            'contains': _('contains'),
            'exact': _('exact'),
            'gt': _('greater than'),
            'gte': _('greater than or equal to'),
            'lt': _('less than'),
            'lte': _('less than or equal to'),
            'in': _('in'),
            'startswith': _('starts with'),
            'range': _('range (inclusive)'),
            'fuzzy': _('similar to (fuzzy)')
        }
        return tuple((filter, names[filter])
                     for filter in filters
                     if filter in names)


def get_haystack_settings():
    """
    Find all settings which are prefixed with `HAYSTACK_`
    """
    filtered_settings = []
    connections = getattr(settings, 'HAYSTACK_CONNECTIONS', {})
    try:
        # 2.x style (one giant dictionary)
        connections['default']  #: may be a KeyError, in which case, 1.x style.
        for named_backend, values in connections.items():
            for setting_name, setting_value in values.items():
                setting_name = setting_name.replace('_', ' ')
                filtered_settings.append((setting_name, setting_value, named_backend))
    except KeyError as e:
        # 1.x style, where everything is a separate setting.
        searching_for = u'HAYSTACK_'
        all_settings = module_to_dict(settings._wrapped)
        for setting_name, setting_value in all_settings.items():
            if setting_name.startswith(searching_for):
                setting_name = setting_name.replace(searching_for, '').replace('_', ' ')
                filtered_settings.append((setting_name, setting_value))
    return filtered_settings
