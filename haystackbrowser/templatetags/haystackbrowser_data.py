# -*- coding: utf-8 -*-
from classytags.arguments import Argument
from classytags.core import Options
from classytags.helpers import InclusionTag
from django import template
from haystack.query import SearchQuerySet
from haystackbrowser.models import SearchResultWrapper
from haystackbrowser.utils import get_haystack_settings

try:
    from haystack.constants import DJANGO_CT, DJANGO_ID
except ImportError:
    DJANGO_CT = 'django_ct'
    DJANGO_ID = 'django_id'


register = template.Library()

class HaystackBrowserForObject(InclusionTag):
    """
    Render a template which shows the given model object's data in the haystack
    search index.
    """
    template = 'admin/haystackbrowser/view_data.html'
    options = Options(
        Argument('obj', required=True, resolve=True),
    )

    def get_context(self, context, obj):
        object_id = obj.pk
        content_type_id = '%s.%s' % (obj._meta.app_label, obj._meta.module_name)
        query = {DJANGO_ID: object_id, DJANGO_CT: content_type_id}
        output_context = {
            'haystack_settings': get_haystack_settings(),
        }
        try:
            result = SearchQuerySet().filter(**query)[:1][0]
            result = SearchResultWrapper(obj=result)
            output_context.update(original=result)
        except IndexError:
            pass
        return output_context

register.tag('haystackbrowser_for_object', HaystackBrowserForObject)
