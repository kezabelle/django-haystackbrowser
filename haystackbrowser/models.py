from django.utils.safestring import mark_safe
from django.db import models
from django.core.urlresolvers import NoReverseMatch, reverse
from django.utils.translation import ugettext_lazy as _

class HaystackResults(models.Model):
    class Meta:
        managed = False
        verbose_name = _('Search result')
        verbose_name_plural = _('Search results')

class SearchResultWrapper(object):
    def __init__(self, obj, admin_site=None):
        self.admin = admin_site
        self.object = obj

    def get_app_url(self):
        try:
            return reverse('%s:app_list' % self.admin, kwargs={
                'app_label': self.object.app_label,
            })
        except NoReverseMatch:
            return None

    def get_model_url(self):
        try:
            parts = (self.admin, self.object.app_label, self.object.model_name)
            return reverse('%s:%s_%s_changelist' % parts)
        except NoReverseMatch:
            return None

    def get_pk_url(self):
        try:
            parts = (self.admin, self.object.app_label, self.object.model_name)
            return reverse('%s:%s_%s_change' % parts, args=(self.object.pk,))
        except NoReverseMatch:
            return None

    def get_additional_fields(self):
        additional_fields = {}
        stored_fields = self.get_stored_fields().keys()
        for key, value in self.object.get_additional_fields().items():
            if key not in stored_fields:
                additional_fields[key] = value
        return additional_fields

    def __getattr__(self, attr):
        return getattr(self.object, attr)


