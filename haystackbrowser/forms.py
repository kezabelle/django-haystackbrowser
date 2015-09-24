import logging
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.http import QueryDict
from django.template.defaultfilters import yesno
from django.forms import (MultipleChoiceField, CheckboxSelectMultiple,
                          ChoiceField, HiddenInput, IntegerField)
from django.utils.translation import ugettext_lazy as _
try:
    from django.forms.utils import ErrorDict
except ImportError: # < Django 1.8
    from django.forms.util import ErrorDict
try:
    from django.utils.encoding import force_text
except ImportError:  # < Django 1.5
    from django.utils.encoding import force_unicode as force_text
from haystack.forms import ModelSearchForm, model_choices
from haystackbrowser.models import AppliedFacets, Facet

logger = logging.getLogger(__name__)


class SelectedFacetsField(MultipleChoiceField):
    def __init__(self, *args, **kwargs):
        # takes the fieldname out of an iterable of Facet instances
        if 'possible_facets' in kwargs:
            self.possible_facets = [x[0] for x in kwargs.pop('possible_facets')]
        else:
            self.possible_facets = []
        super(SelectedFacetsField, self).__init__(*args, **kwargs)

    def valid_value(self, value):
        # doesn't contain `a:b` as a minimum
        if len(value) < 3:
            return False
        if ':' not in value:
            return False
        # shouldn't be `:aa` or `aa:`
        if value.startswith(':') or value.endswith(':'):
            return False
        facet_name, sep, facet_value = value.partition(':')

        return facet_name in self.possible_facets


class PreSelectedModelSearchForm(ModelSearchForm):
    possible_facets = MultipleChoiceField(widget=CheckboxSelectMultiple,
                                          choices=(), required=False,
                                          label=_("Finding facets on"))
    connection = ChoiceField(choices=(), required=False)
    p = IntegerField(required=False, label=_("Page"), min_value=0,
                     max_value=99999999, initial=1)

    def __init__(self, *args, **kwargs):
        """
        If we're in a recognised faceting engine, display and allow faceting.
        """
        super(PreSelectedModelSearchForm, self).__init__(*args, **kwargs)
        if 'models' in self.fields:
            self.fields['models'].initial = [x[0] for x in model_choices()]
            self.fields['models'].label = _("Only models")

        # provide support for discovering the version installed.
        self.version = self.guess_haystack_version()
        if self.should_allow_faceting():
            possible_facets = self.configure_faceting()
            self.fields['possible_facets'].choices = possible_facets
            self.fields['selected_facets'] = SelectedFacetsField(
                choices=(), required=False, possible_facets=possible_facets)


        if self.has_multiple_connections():
            wtf = self.get_possible_connections()
            self.fields['connection'].choices = tuple(wtf)  # noqa
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
        for engine, values in engine_2x.items():
            engine_name = force_text(engine)
            if 'TITLE' in values:
                title = force_text(values['TITLE'])
            else:
                title = engine_name
            yield (engine_name, title)

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
        return [Facet(x).choices() for x in sorted(possible_facets)]

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

    def __repr__(self):
        is_valid = self.is_bound and not bool(self._errors)
        return '<%(module)s.%(cls)s bound=%(is_bound)s valid=%(valid)s ' \
               'version=%(version)d multiple_connections=%(conns)s ' \
               'supports_faceting=%(facets)s>' % {
            'module': self.__class__.__module__,
            'cls': self.__class__.__name__,
            'is_bound': yesno(self.is_bound),
            'conns': yesno(self.has_multiple_connections()),
            'facets': yesno(self.should_allow_faceting()),
            'valid': yesno(is_valid),
            'version': self.guess_haystack_version(),
        }

    def no_query_found(self):
        """
        When nothing is entered, show everything, because it's a better
        useful default for our usage.
        """
        return self.searchqueryset.all()

    def search(self):
        sqs = self.searchqueryset.all()

        if not self.is_valid():
            # When nothing is entered, show everything, because it's a better
            # useful default for our usage.
            return sqs

        cleaned_data = getattr(self, 'cleaned_data', {})

        connection = cleaned_data.get('connection', ())
        if self.has_multiple_connections() and len(connection) == 1:
            sqs = sqs.using(*connection)

        if self.should_allow_faceting():
            for applied_facet in self.applied_facets():
                narrow_query = applied_facet.narrow.format(
                    cleaned_value=sqs.query.clean(applied_facet.value))
                sqs = sqs.narrow(narrow_query)

            to_facet_on = sorted(cleaned_data.get('possible_facets', ()))
            if len(to_facet_on) > 0:
                for field in to_facet_on:
                    sqs = sqs.facet(field)

        only_models = self.get_models()
        if len(only_models) > 0:
            sqs = sqs.models(*only_models)

        query = cleaned_data.get('q', [''])
        if query:
            sqs = sqs.auto_query(*query)

        if self.load_all:
            sqs = sqs.load_all()

        return sqs

    def clean_connection(self):
        return [self.cleaned_data.get('connection', 'default').strip()]

    def clean_possible_facets(self):
        return list(frozenset(self.cleaned_data.get('possible_facets', ())))

    def clean_selected_facets(self):
        return list(frozenset(self.cleaned_data.get('selected_facets', ())))

    def clean_q(self):
        return [self.cleaned_data.get('q', '')]

    def clean_p(self):
        page = self.cleaned_data.get('p', None)
        if page is None:
            page = self.fields['p'].min_value
        return [page]

    def full_clean(self):
        """
        Taken from Django master as of 5e06fa1469180909c51c07151692412269e51ea3
        but is mostly a copy-paste all the way back to 1.3.1
        Basically we want to keep cleaned_data around, not remove it
        if errors occured.
        """
        self._errors = ErrorDict()
        if not self.is_bound:  # Stop further processing.
            return
        self.cleaned_data = {}
        # If the form is permitted to be empty, and none of the form data has
        # changed from the initial data, short circuit any validation.
        if self.empty_permitted and not self.has_changed():
            return
        self._clean_fields()
        self._clean_form()
        self._post_clean()

    def clean(self):
        cd = self.cleaned_data
        selected = 'selected_facets'
        possible = 'possible_facets'
        if selected in cd and len(cd[selected]) > 0:
            if possible not in cd or len(cd[possible]) == 0:
                raise ValidationError('Unable to provide facet counts without selecting a field to facet on')
        return cd

    def applied_facets(self):
        cleaned_querydict = self.cleaned_data_querydict
        return AppliedFacets(querydict=cleaned_querydict)

    @property
    def cleaned_data_querydict(self):
        """
        Creates an immutable QueryDict instance from the form's cleaned_data
        """
        query = QueryDict('', mutable=True)
        # make sure cleaned_data is available, if possible ...
        self.is_valid()
        cleaned_data = getattr(self, 'cleaned_data', {})
        for key, values in cleaned_data.items():
            query.setlist(key=key, list_=values)
        query._mutable = False
        return query
