# -*- coding: utf-8 -*-
import logging
from copy import deepcopy
try:
    from urllib import quote_plus
except ImportError:  # > Python 3
    from django.utils.six.moves.urllib import parse
    quote_plus = parse.quote_plus
from operator import itemgetter
from itertools import groupby
from collections import namedtuple
from django.db import models
try:
    from django.utils.encoding import force_text
except ImportError:  # < Django 1.5
    from django.utils.encoding import force_unicode as force_text
from django.utils.safestring import mark_safe
from django.utils.html import strip_tags
from django.core.urlresolvers import NoReverseMatch, reverse
from django.utils.translation import ugettext_lazy as _
from django.conf import settings


logger = logging.getLogger(__name__)


class HaystackResults(models.Model):
    """ Our fake model, used for mounting :py:class:`~haystackbrowser.admin.HaystackResultsAdmin`
    onto the appropriate AdminSite.

    .. note::

        the model is marked as unmanaged, so will never get created via ``syncdb``.
    """
    class Meta:
        managed = False
        verbose_name = _('Search result')
        verbose_name_plural = _('Search results')


class SearchResultWrapper(object):
    """Value object which consumes a standard Haystack SearchResult, and the current
    admin site, and exposes additional methods and attributes for displaying the data
    appropriately.

    :param obj: the item to be wrapped.
    :type obj: object
    :param admin_site: the parent site instance.
    :type admin_site: AdminSite object

    """
    def __init__(self, obj, admin_site=None):
        self.admin = admin_site
        self.object = obj
        if getattr(self.object, 'searchindex', None) is None:
            # < Haystack 1.2
            from haystack import site
            self.object.searchindex = site.get_index(self.object.model)


    def __repr__(self):
        return '<%(module)s.%(cls)s [%(app)s.%(model)s pk=%(pk)r]>' % {
            'module': self.__class__.__module__,
            'cls': self.__class__.__name__,
            'obj': self.object,
            'app': self.object.app_label,
            'model': self.object.model_name,
            'pk': self.object.pk,
        }

    def get_app_url(self):
        """Resolves a given object's app into a link to the app administration.

        .. warning::
            This link may return a 404, as pretty much anything may
            be reversed and fit into the ``app_list`` urlconf.

        :return: string or None
        """
        try:
            return reverse('%s:app_list' % self.admin, kwargs={
                'app_label': self.object.app_label,
            })
        except NoReverseMatch:
            return None

    def get_model_url(self):
        """Generates a link to the changelist for a specific Model in the administration.

        :return: string or None
        """
        try:
            parts = (self.admin, self.object.app_label, self.object.model_name)
            return reverse('%s:%s_%s_changelist' % parts)
        except NoReverseMatch:
            return None

    def get_pk_url(self):
        """Generates a link to the edit page for a specific object in the administration.

        :return: string or None
        """
        try:
            parts = (self.admin, self.object.app_label, self.object.model_name)
            return reverse('%s:%s_%s_change' % parts, args=(self.object.pk,))
        except NoReverseMatch:
            return None

    def get_detail_url(self):
        try:
            urlname = '%s:haystackbrowser_haystackresults_change' % self.admin
            return reverse(urlname, kwargs={
                'content_type': '.'.join([self.object.app_label,
                                          self.object.model_name]),
                'pk': self.object.pk})
        except NoReverseMatch:
            return None

    def get_model_attrs(self):
        outfields = {}
        try:
            fields = self.object.searchindex.fields
        except:
            fields = {}
        else:
            for key, field in fields.items():
                has_model_attr = getattr(field, 'model_attr', None)
                if has_model_attr is not None:
                    outfields[key] = force_text(has_model_attr)
        return outfields

    def get_stored_fields(self):
        stored_fields = {}
        model_attrs = self.get_model_attrs()
        for key, value in self.object.get_stored_fields().items():
            safe_value = force_text(value).strip()
            stored_fields[key] = {
                'raw': safe_value,
                'safe': mark_safe(strip_tags(safe_value))
            }
            if key in model_attrs:
                stored_fields[key].update(model_attr=model_attrs.get(key))
        return stored_fields

    def get_additional_fields(self):
        """Find all fields in the Haystack SearchResult which have not already
        appeared in the stored fields.

        :return: dictionary of field names and values.
        """
        additional_fields = {}
        stored_fields = self.get_stored_fields().keys()
        model_attrs = self.get_model_attrs()
        for key, value in self.object.get_additional_fields().items():
            if key not in stored_fields:
                safe_value = force_text(value).strip()
                additional_fields[key] = {
                    'raw': safe_value,
                    'safe': mark_safe(strip_tags(safe_value))
                }
                if key in model_attrs:
                    additional_fields[key].update(model_attr=model_attrs.get(key))
        return additional_fields

    def get_content_field(self):
        """Find the name of the main content field in the Haystack SearchIndex
        for this object.

        :return: string representing the attribute name.
        """
        return self.object.searchindex.get_content_field()

    def get_content(self):
        """Given the name of the main content field in the Haystack Search Index
         for this object, get the named attribute on this object.

         :return: whatever is in ``self.object.<content_field_name>``
        """
        return getattr(self.object, self.get_content_field())

    def get_stored_field_count(self):
        """
        Provides mechanism for finding the number of stored fields stored on
        this Search Result.

        :return: the count of all stored fields.
        :rtype: integer
        """
        return len(self.object.get_stored_fields().keys())

    def get_additional_field_count(self):
        """
        Provides mechanism for finding the number of stored fields stored on
        this Search Result.

        :return: the count of all stored fields.
        :rtype: integer
        """
        return len(self.get_additional_fields().keys())

    def __getattr__(self, attr):
        return getattr(self.object, attr)


class FacetWrapper(object):
    """
    A simple wrapper around `sqs.facet_counts()` to filter out things with
    0, and re-arrange the data in such a way that the template can handle it.
    """
    __slots__ = ('dates', 'fields', 'queries', '_total_count', '_querydict')

    def __init__(self, facet_counts, querydict):
        self.dates = facet_counts.get('dates', {})
        self.fields = facet_counts.get('fields', {})
        self.queries = facet_counts.get('queries', {})

        self._total_count = len(self.dates) + len(self.fields) + len(self.queries)
        # querydict comes from the cleaned form data ...
        page_key = 'p'
        if querydict is not None and page_key in querydict:
            querydict.pop(page_key)
        self._querydict = querydict

    def __repr__(self):
        return '<%(module)s.%(cls)s fields=%(fields)r dates=%(dates)r ' \
               'queries=%(queries)r>' % {
            'module': self.__class__.__module__,
            'cls': self.__class__.__name__,
            'fields': self.fields,
            'dates': self.dates,
            'queries': self.queries,
        }

    def get_facets_from(self, x):
        if x not in ('dates', 'queries', 'fields'):
            raise AttributeError('Wrong field, silly.')

        for field, items in getattr(self, x).items():
            for content, count in items:
                content = content.strip()
                if count > 0 and content:
                    yield {'field': field, 'value': content, 'count': count,
                           'fieldvalue': quote_plus('%s:%s' % (field, content)),
                           'facet': Facet(field, querydict=self._querydict)}

    def get_grouped_facets_from(self, x):
        data = sorted(self.get_facets_from(x), key=itemgetter('field'))
        #return data
        results = ({'grouper': Facet(key), 'list': list(val)}
                   for key, val in groupby(data, key=itemgetter('field')))
        return results

    def get_field_facets(self):
        return self.get_grouped_facets_from('fields')

    def get_date_facets(self):
        return self.get_grouped_facets_from('dates')

    def get_query_facets(self):
        return self.get_grouped_facets_from('queries')

    def __bool__(self):
        """
        Used for doing `if facets: print(facets)` - this is the Python 2 magic
        method; __nonzero__ is the equivalent thing in Python 3
        """
        return self._total_count > 0
    __nonzero__ = __bool__

    def __len__(self):
        """
        For checking things via `if len(facets) > 0: print(facets)`
        """
        return self._total_count


class AppliedFacet(namedtuple('AppliedFacet', 'field value querydict')):
    __slots__ = ()
    def title(self):
        return self.value

    @property
    def facet(self):
        """ a richer object """
        return Facet(self.raw)

    @property
    def raw(self):
        """ the original data, rejoined """
        return '%s:%s' % (self.field, self.value)

    @property
    def narrow(self):
        """ returns a string format value """
        return '{0}:"{{cleaned_value}}"'.format(self.field)

    def link(self):
        """ link to just this facet """
        new_qd = self.querydict.copy()
        page_key = 'p'
        if page_key in new_qd:
            new_qd.pop(page_key)
        new_qd['selected_facets'] = self.raw
        new_qd['possible_facets'] = self.field
        return '?%s' % new_qd.urlencode()

    def remove_link(self):
        new_qd = self.querydict.copy()
        # remove page forcibly ...
        page_key = 'p'
        if page_key in new_qd:
            new_qd.pop(page_key)
        # remove self from the existing querydict/querystring ...
        key = 'selected_facets'
        if key in new_qd and self.raw in new_qd.getlist(key):
            new_qd.getlist(key).remove(self.raw)
        return '?%s' % new_qd.urlencode()


class AppliedFacets(object):
    __slots__ = ('_applied',)

    def __init__(self, querydict):
        self._applied = {}
        selected = ()
        if 'selected_facets' in querydict:
            selected = querydict.getlist('selected_facets')
        for raw_facet in selected:
            if ":" not in raw_facet:
                continue
            field, value = raw_facet.split(":", 1)
            to_add = AppliedFacet(field=field, value=value,
                                  querydict=querydict)
            self._applied[raw_facet] = to_add

    def __iter__(self):
        return iter(self._applied.values())

    def __len__(self):
        return len(self._applied)

    def __contains__(self, item):
        return item in self._applied

    def __repr__(self):
        raw = tuple(v.raw for k, v in self._applied.items())
        return '<{cls!s}.{name!s} selected_facets={raw}>'.format(
            cls=self.__class__.__module__, name=self.__class__.__name__,
            raw=raw)

    def __str__(self):
        raw = [v.facet.get_display() for k, v in self._applied.items()]
        return '{name!s} {raw!s}'.format(name=self.__class__.__name__, raw=raw)


class Facet(object):
    """
    Takes a facet field name, like `thing_exact`
    """

    __slots__ = ('fieldname', '_querydict')
    def __init__(self, fieldname, querydict=None):
        self.fieldname = fieldname
        self._querydict = querydict

    def __repr__(self):
        return '<%(module)s.%(cls)s - %(field)s>' % {
            'module': self.__class__.__module__,
            'cls': self.__class__.__name__,
            'field': self.fieldname,
        }

    def link(self):
        qd = self._querydict
        if qd is not None:
            return '?%s' % qd.urlencode()
        return '?'

    def get_display(self):
        return self.fieldname.replace('_', ' ').title()

    def choices(self):
        return (self.fieldname, self.get_display())
