from django.core.paginator import Paginator, InvalidPage
from django.utils.encoding import force_unicode
from django.utils.translation import ugettext_lazy as _
from django.http import Http404
from django.db import models
from django.utils.functional import update_wrapper
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib import admin
from django.contrib.admin.views.main import PAGE_VAR, ALL_VAR
from django.conf import settings
from haystack.query import SearchQuerySet
from haystackbrowser.models import HaystackResults

try:
    from haystack.constants import DJANGO_CT, DJANGO_ID
except ImportError:
    DJANGO_CT = 'django_ct'
    DJANGO_ID = 'django_id'

class HaystackResultsAdmin(object):
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

    def get_model_perms(self, request):
        return {
            'add': self.has_add_permission(request),
            'change': self.has_change_permission(request),
            'delete': self.has_delete_permission(request)
        }

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return False

    def urls(self):
        from django.conf.urls.defaults import patterns, url
        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            return update_wrapper(wrapper, view)
        return patterns('',
            url(regex=r'^(?P<content_type>.+)/(?P<pk>.+)/$',
                view=self.view,
                name='%s_%s_change' % (self.model._meta.app_label,
                    self.model._meta.module_name)
            ),
            url(regex=r'^$',
                view=self.index,
                name='%s_%s_changelist' % (self.model._meta.app_label,
                    self.model._meta.module_name)
            ),
        )
    urls = property(urls)

    def get_results_per_page(self, request):
        return getattr(settings, 'HAYSTACK_SEARCH_RESULTS_PER_PAGE', 20)

    def get_paginator_var(self, request):
        return PAGE_VAR

    def get_all_results_var(self, request):
        return ALL_VAR

    def index(self, request):
        sqs = SearchQuerySet().all().load_all()
        item_count = sqs.count()
        paginator = Paginator(sqs, self.get_results_per_page(request))
        try:
            page_qs = request.GET.get(self.get_paginator_var(request), 1)
            page = paginator.page(int(page_qs))
        except InvalidPage:
            raise Http404
        context = {
            'results': page.object_list,
            'pagination_required': page.has_other_pages(),
            'page_range': paginator.page_range,
            'page_num': page.number,
            'result_count': item_count,
            'opts': self.model._meta,
            'title': self.model._meta.verbose_name_plural,
            'root_path': self.admin_site.root_path,
            'app_label': self.model._meta.app_label,
            'module_name': force_unicode(self.model._meta.verbose_name_plural),
                }
        return render_to_response('admin/haystackbrowser/result_list.html', context,
            context_instance=RequestContext(request))

    def view(self, request, content_type, pk):
        query = {DJANGO_ID: pk, DJANGO_CT: content_type}
        try:
            sqs = SearchQuerySet().filter(**query)[:1][0]
        except IndexError:
            raise Http404
        context = {
            'original': sqs,
            'title': _('Indexed data'),
        }
        return render_to_response('admin/haystackbrowser/view.html', context,
            context_instance=RequestContext(request))
admin.site.register(HaystackResults, HaystackResultsAdmin)
