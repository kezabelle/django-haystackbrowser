import logging
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.forms import (MultipleChoiceField, CheckboxSelectMultiple,
                          ChoiceField, HiddenInput)
try:
    from django.utils.encoding import force_text
except ImportError:  # < Django 1.5
    from django.utils.encoding import force_unicode as force_text
from haystack.forms import ModelSearchForm, FacetedModelSearchForm

logger = logging.getLogger(__name__)


class PreSelectedModelSearchForm(FacetedModelSearchForm):
    possible_facets = MultipleChoiceField(widget=CheckboxSelectMultiple,
                                          choices=(), required=False)
    connection = ChoiceField(choices=(), required=False)

    def __init__(self, *args, **kwargs):
        """
        If we're in a recognised faceting engine, display and allow faceting.
        """
        super(PreSelectedModelSearchForm, self).__init__(*args, **kwargs)
        # provide support for discovering the version installed.
        self.version = self.guess_haystack_version()
        if self.should_allow_faceting():
            self.fields['possible_facets'].choices = self.configure_faceting()

        if self.has_multiple_connections():
            self.fields['connection'].choices = self.get_possible_connections()
            self.fields['connection'].initial = 'default'
        else:
            self.fields['connection'].widget = HiddenInput()

    def is_haystack1(self):
        return getattr(settings, 'HAYSTACK_SEARCH_ENGINE', None) is not None

    def is_haystack2(self):
        return getattr(settings, 'HAYSTACK_CONNECTIONS', None) is not None

    def guess_haystack_version(self):
        if self.is_haystack1():
            logger.debug("Guessed Haystack 1.2.x")
            return 1
        if self.is_haystack2():
            logger.debug("Guessed Haystack 2.x")
            return 2
        return None

    def has_multiple_connections(self):
        if self.version == 1:
            return False
        elif self.version == 2:
            engine_2x = getattr(settings, 'HAYSTACK_CONNECTIONS', {})
            return len(engine_2x) > 1

    def get_possible_connections(self):
        engine_2x = getattr(settings, 'HAYSTACK_CONNECTIONS', {})
        return ((force_text(x), force_text(x))
                for x in sorted(engine_2x.keys()))

    def configure_faceting(self):
        if self.version == 2:
            from haystack import connections
            facet_fields = connections['default'].get_unified_index()._facet_fieldnames
            possible_facets = facet_fields.keys()
        elif self.version == 1:
            possible_facets = []
            for k, v in self.searchqueryset.site._field_mapping().items():
                if v['facet_fieldname'] is not None:
                    possible_facets.append(v['facet_fieldname'])
        return [(x, x) for x in possible_facets]

    def should_allow_faceting(self):
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

    def no_query_found(self):
        """
        When nothing is entered, show everything, because it's a better
        useful default for our usage.
        """
        return self.searchqueryset.all()

    def search(self):
        sqs = super(PreSelectedModelSearchForm, self).search()
        cleaned_data = getattr(self, 'cleaned_data', {})
        to_facet_on = cleaned_data.get('possible_facets', [])
        connection = cleaned_data.get('connection', '')
        if self.has_multiple_connections() and connection:
            sqs = sqs.using(connection)
        if len(to_facet_on) > 0:
            for field in to_facet_on:
                sqs = sqs.facet(field)
        return sqs
