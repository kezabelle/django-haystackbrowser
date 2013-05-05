from django.conf import settings
from django.forms import MultipleChoiceField, CheckboxSelectMultiple
from haystack.forms import ModelSearchForm, FacetedModelSearchForm


class PreSelectedModelSearchForm(FacetedModelSearchForm):
    possible_facets = MultipleChoiceField(widget=CheckboxSelectMultiple,
                                          choices=())

    def __init__(self, *args, **kwargs):
        """
        If we're in a recognised faceting engine, display and allow faceting.
        """
        super(PreSelectedModelSearchForm, self).__init__(*args, **kwargs)
        engine = getattr(settings, 'HAYSTACK_SEARCH_ENGINE', 'none')
        if engine in ('solr', 'xapian'):
            possible_facets = []
            for k, v in self.searchqueryset.site._field_mapping().items():
                if v['facet_fieldname'] is not None:
                    possible_facets.append(v['facet_fieldname'])
            self.fields['possible_facets'].choices = [(x, x) for x in possible_facets]

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
