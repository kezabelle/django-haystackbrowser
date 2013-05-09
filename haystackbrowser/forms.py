from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.forms import MultipleChoiceField, CheckboxSelectMultiple
from haystack.forms import ModelSearchForm, FacetedModelSearchForm


class PreSelectedModelSearchForm(FacetedModelSearchForm):
    possible_facets = MultipleChoiceField(widget=CheckboxSelectMultiple,
                                          choices=(), required=False)

    def __init__(self, *args, **kwargs):
        """
        If we're in a recognised faceting engine, display and allow faceting.
        """
        super(PreSelectedModelSearchForm, self).__init__(*args, **kwargs)
        if self.should_allow_faceting():
            self.fields['possible_facets'].choices = self.configure_faceting()

    def configure_faceting(self):
        try:
            # 2.x
            from haystack import connections
            facet_fields = connections['default'].get_unified_index()._facet_fieldnames
            possible_facets = facet_fields.keys()
        except ImportError as e:
            # 1.x
            possible_facets = []
            for k, v in self.searchqueryset.site._field_mapping().items():
                if v['facet_fieldname'] is not None:
                    possible_facets.append(v['facet_fieldname'])
        return [(x, x) for x in possible_facets]

    def should_allow_faceting(self):
        engine = getattr(settings, 'HAYSTACK_SEARCH_ENGINE', None)
        if engine is not None and engine in ('solr', 'xapian'):
            return True
        engine = getattr(settings, 'HAYSTACK_CONNECTIONS', {})
        try:
            engine = engine['default']['ENGINE']
            if 'solr' in engine or 'xapian' in engine:
                return True
        except KeyError as e:
            raise ImproperlyConfigured("I think you're on Haystack 2.x without "
                                       "a `HAYSTACK_CONNECTIONS` dictionary")
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
        if len(to_facet_on) > 0:
            for field in to_facet_on:
                sqs = sqs.facet(field)
        return sqs
