from django.core.paginator import Paginator, InvalidPage
try:
    from django.utils.encoding import force_text
except ImportError:  # < Django 1.5
    from django.utils.encoding import force_unicode as force_text
from django.utils.translation import ugettext_lazy as _, string_concat
from django.http import Http404, HttpResponseRedirect
try:
    from functools import update_wrapper
except ImportError:  # < Django 1.6
    from django.utils.functional import update_wrapper
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib import admin
from django.contrib.admin.views.main import PAGE_VAR, SEARCH_VAR
from django.contrib.admin.options import ModelAdmin
from django.conf import settings
from haystack import __version__
from haystack.query import SearchQuerySet
from haystack.forms import model_choices
from haystackbrowser.models import HaystackResults, SearchResultWrapper, FacetWrapper
from haystackbrowser.forms import PreSelectedModelSearchForm
from haystackbrowser.utils import get_haystack_settings
from django.forms import Media

try:
    from haystack.constants import DJANGO_CT, DJANGO_ID
except ImportError:  # really old haystack, early in 1.2 series?
    DJANGO_CT = 'django_ct'
    DJANGO_ID = 'django_id'

_haystack_version = '.'.join([str(x) for x in __version__])

def get_query_string(query_params, new_params=None, remove=None):
    # TODO: make this bettererer. Use propery dicty stuff on the Querydict?
    if new_params is None:
        new_params = {}
    if remove is None:
        remove = []
    params = query_params.copy()
    for r in remove:
        for k in list(params):
            if k.startswith(r):
                del params[k]
    for k, v in new_params.items():
        if v is None:
            if k in params:
                del params[k]
        else:
            params[k] = v
    return '?%s' % params.urlencode()


class FakeChangeListForPaginator(object):
    """A value object to contain attributes required for Django's pagination template tag."""
    def __init__(self, request, page, per_page, model_opts):
        self.paginator = page.paginator
        self.page_num = page.number - 1
        self.can_show_all = False
        self.show_all = False
        self.result_count = self.paginator.count
        self.multi_page = self.result_count > per_page
        self.request = request
        self.opts = model_opts

    def get_query_string(self, a_dict):
        """ Method to return a querystring appropriate for pagination."""
        return get_query_string(self.request.GET, a_dict)


class Search404(Http404):
    pass


class HaystackResultsAdmin(object):
    """Object which emulates enough of the standard Django ModelAdmin that it may
    be mounted into an AdminSite instance and pass validation.
    Used to work around the fact that we don't actually have a concrete Django Model.

    :param model: the model being mounted for this object.
    :type model: class
    :param admin_site: the parent site instance.
    :type admin_site: AdminSite object
    """
    fields = None
    fieldsets = None
    exclude = None
    date_hierarchy = None
    ordering = None
    list_select_related = False
    save_as = False
    save_on_top = False

    def __init__(self, model, admin_site):
        self.model = model
        self.opts = model._meta
        self.admin_site = admin_site

    @classmethod
    def validate(cls, *args, **kwargs):
        return

    def get_model_perms(self, request):
        return {
            'add': self.has_add_permission(request),
            'change': self.has_change_permission(request),
            'delete': self.has_delete_permission(request)
        }

    def has_add_permission(self, request):
        """Emulates the equivalent Django ModelAdmin method.
        :param request: the current request.
        :type request: WSGIRequest

        :return: `False`
        """
        return False

    def has_change_permission(self, request, obj=None):
        """Emulates the equivalent Django ModelAdmin method.

        :param request: the current request.
        :param obj: the object is being viewed.
        :type request: WSGIRequest
        :type obj: None

        :return: The value of `request.user.is_superuser`
        """
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        """Emulates the equivalent Django ModelAdmin method.

        :param request: the current request.
        :param obj: the object is being viewed.
        :type request: WSGIRequest
        :type obj: None

        :return: `False`
        """
        return False

    def urls(self):
        """Sets up the required urlconf for the admin views."""
        try:
            # > 1.5
            from django.conf.urls import patterns, url
        except ImportError as e:
            # < 1.5
            from django.conf.urls.defaults import patterns, url


        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            return update_wrapper(wrapper, view)

        return patterns('',
            url(regex=r'^(?P<content_type>.+)/(?P<pk>.+)/$',
                view=wrap(self.view),
                name='%s_%s_change' % (self.model._meta.app_label,
                    self.model._meta.module_name)
            ),
            url(regex=r'^$',
                view=wrap(self.index),
                name='%s_%s_changelist' % (self.model._meta.app_label,
                    self.model._meta.module_name)
            ),
        )
    urls = property(urls)

    def get_results_per_page(self, request):
        """Allows for overriding the number of results shown.
        This differs from the usual way a ModelAdmin may declare pagination
        via ``list_per_page`` and instead looks in Django's ``LazySettings`` object
        for the item ``HAYSTACK_SEARCH_RESULTS_PER_PAGE``. If it's not found,
        falls back to **20**.

        :param request: the current request.
        :type request: WSGIRequest

        :return: The number of results to show, per page.
        """
        return getattr(settings, 'HAYSTACK_SEARCH_RESULTS_PER_PAGE',
                       ModelAdmin.list_per_page)

    def get_paginator_var(self, request):
        """Provides the name of the variable used in query strings to discover
        what page is being requested. Uses the same ``PAGE_VAR`` as the standard
        :py:class:`django.contrib.admin.views.main.ChangeList <django:django.contrib.admin.views.ChangeList>`

        :param request: the current request.
        :type request: WSGIRequest

        :return: the name of the variable used in query strings for pagination.
        """
        return PAGE_VAR

    def get_search_var(self, request):
        """Provides the name of the variable used in query strings to discover
        what text search has been requested. Uses the same ``SEARCH_VAR`` as the standard
        :py:class:`django.contrib.admin.views.main.ChangeList <django:django.contrib.admin.views.ChangeList>`

        :param request: the current request.
        :type request: WSGIRequest

        :return: the name of the variable used in query strings for text searching.
        """
        return SEARCH_VAR

    def get_searchresult_wrapper(self):
        """This method serves as a hook for potentially overriding which class
        is used for wrapping each result into a value object for display.

        :return: class for wrapping search results. Defaults to :py:class:`~haystackbrowser.models.SearchResultWrapper`
        """
        return SearchResultWrapper

    def get_wrapped_search_results(self, object_list):
        """Wraps each :py:class:`~haystack.models.SearchResult` from the
        :py:class:`~haystack.query.SearchQuerySet` in our own value object, whose
        responsibility is providing additional attributes required for display.

        :param object_list: :py:class:`~haystack.models.SearchResult` objects.

        :return: list of items wrapped with whatever :py:meth:`~haystackbrowser.admin.HaystackResultsAdmin.get_searchresult_wrapper` provides.
        """
        klass = self.get_searchresult_wrapper()
        return [klass(x, self.admin_site.name) for x in object_list]

    def get_current_query_string(self, request, add=None, remove=None):
        """ Method to return a querystring with modified parameters.

        :param request: the current request.
        :type request: WSGIRequest
        :param add: items to be added.
        :type add: dictionary
        :param remove: items to be removed.
        :type remove: dictionary

        :return: the new querystring.
        """
        return get_query_string(request.GET, new_params=add, remove=remove)

    def get_settings(self):
        """Find all Django settings prefixed with ``HAYSTACK_``

        :return: dictionary whose keys are setting names (tidied up).
        """
        return get_haystack_settings()

    def index(self, request):
        """The view for showing all the results in the Haystack index. Emulates
        the standard Django ChangeList mostly.

        :param request: the current request.
        :type request: WSGIRequest

        :return: A template rendered into an HttpReponse
        """
        if not self.has_change_permission(request, None):
            raise PermissionDenied

        page_var = self.get_paginator_var(request)
        form = PreSelectedModelSearchForm(request.GET or None, load_all=False)

        # Make sure there are some models indexed
        available_models = model_choices()
        if len(available_models) <= 0:
            raise Search404('No search indexes bound via Haystack')

        # We've not selected any models, so we're going to redirect and select
        # all of them. This will bite me in the ass if someone searches for a string
        # but no models, but I don't know WTF they'd expect to return, anyway.
        # Note that I'm only doing this to sidestep this issue:
        # https://gist.github.com/3766607
        if 'models' not in request.GET.keys():
            # TODO: make this betterererer.
            new_qs = ['&models=%s' % x[0] for x in available_models]
            # if we're in haystack2, we probably want to provide the 'default'
            # connection so that it behaves as if "initial" were in place.
            if form.has_multiple_connections():
                new_qs.append('&connection=' + form.fields['connection'].initial)
            new_qs = ''.join(new_qs)
            qs = self.get_current_query_string(request, remove=['p'])
            return HttpResponseRedirect(request.path_info + qs + new_qs)

        try:
            sqs = form.search()
            try:
                page_no = int(request.GET.get(PAGE_VAR, 0))
            except ValueError:
                page_no = 0
            #page_no = int(request.GET.get(page_var, 1))
            results_per_page = self.get_results_per_page(request)
            paginator = Paginator(sqs, results_per_page)
            page = paginator.page(page_no+1)
        except (InvalidPage, ValueError):
            # paginator.page may raise InvalidPage if we've gone too far
            # meanwhile, casting the querystring parameter may raise ValueError
            # if it's None, or '', or other silly input.
            raise Search404("Invalid page")

        query = request.GET.get(self.get_search_var(request), None)
        connection = request.GET.get('connection', None)
        title = self.model._meta.verbose_name_plural
        if query:
            title = string_concat(self.model._meta.verbose_name_plural, ' for "',
                                  query, '"')
        if connection:
            title = string_concat(title, ' using "', connection, '" connection')
        context = {
            'results': self.get_wrapped_search_results(page.object_list),
            'pagination_required': page.has_other_pages(),
            # this may be expanded into xrange(*page_range) to copy what
            # the paginator would yield. This prevents 50000+ pages making
            # the page slow to render because of django-debug-toolbar.
            'page_range': (1, paginator.num_pages + 1),
            'page_num': page.number,
            'result_count': paginator.count,
            'opts': self.model._meta,
            'title': force_text(title),
            'root_path': getattr(self.admin_site, 'root_path', None),
            'app_label': self.model._meta.app_label,
            'filtered': True,
            'form': form,
            'query_string': self.get_current_query_string(request, remove=['p']),
            'search_model_count': len(request.GET.getlist('models')),
            'search_facet_count': len(request.GET.getlist('possible_facets')),
            'search_var': self.get_search_var(request),
            'page_var': page_var,
            'facets': FacetWrapper(sqs.facet_counts()),
            'module_name': force_text(self.model._meta.verbose_name_plural),
            'cl': FakeChangeListForPaginator(request, page, results_per_page, self.model._meta),
            'haystack_version': _haystack_version,
            # Note: the empty Media object isn't specficially required for the
            # standard Django admin, but is apparently a pre-requisite for
            # things like Grappelli.
            # See #1 (https://github.com/kezabelle/django-haystackbrowser/pull/1)
            'media': Media()
        }
        return render_to_response('admin/haystackbrowser/result_list.html', context,
                                  context_instance=RequestContext(request))

    def view(self, request, content_type, pk):
        """The view for showing the results of a single item in the Haystack index.

        :param request: the current request.
        :type request: WSGIRequest
        :param content_type: ``app_label`` and ``model_name`` as stored in Haystack, separated by "."
        :type content_type: string.
        :param pk: the object identifier stored in Haystack
        :type pk: string.

        :return: A template rendered into an HttpReponse
        """
        if not self.has_change_permission(request, None):
            raise PermissionDenied
        
        query = {DJANGO_ID: pk, DJANGO_CT: content_type}
        try:
            raw_sqs = SearchQuerySet().filter(**query)[:1]
            wrapped_sqs = self.get_wrapped_search_results(raw_sqs)
            sqs = wrapped_sqs[0]
        except IndexError:
            raise Search404("Search result using query {q!r} does not exist".format(
                q=query))

        more_like_this = ()
        # the model may no longer be in the database, instead being only backed
        # by the search backend.
        model_instance = sqs.object.object
        if model_instance is not None:
            raw_mlt = SearchQuerySet().more_like_this(model_instance)[:5]
            more_like_this = self.get_wrapped_search_results(raw_mlt)

        context = {
            'original': sqs,
            'title': _('View stored data for this %s') % force_text(sqs.verbose_name),
            'app_label': self.model._meta.app_label,
            'module_name': force_text(self.model._meta.verbose_name_plural),
            'haystack_settings': self.get_settings(),
            'has_change_permission': self.has_change_permission(request, sqs),
            'similar_objects': more_like_this,
            'haystack_version': _haystack_version,
        }
        return render_to_response('admin/haystackbrowser/view.html', context,
                                  context_instance=RequestContext(request))
admin.site.register(HaystackResults, HaystackResultsAdmin)
