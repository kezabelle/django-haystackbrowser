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
        self.output_url = '<a href="%s">%s</a>'
        self.admin = admin_site
        self.object = obj

    def get_app_url(self):
        try:
            url = reverse('%s:app_list' % self.admin, kwargs={
                'app_label': self.object.app_label,
                })
            output = self.output_url % (
                url,
                self.object.app_label
            )
        except NoReverseMatch:
            output = self.object.app_label
        return mark_safe(output)

    def get_model_url(self):
        try:
            parts = (self.admin, self.object.app_label, self.object.model_name)
            url = reverse('%s:%s_%s_changelist' % parts)
            output = self.output_url % (
                url,
                self.object.model_name
            )
        except NoReverseMatch:
            output = self.object.model_name
        return mark_safe(output)

    def get_pk_url(self):
        try:
            parts = (self.admin, self.object.app_label, self.object.model_name)
            url = reverse('%s:%s_%s_change' % parts, args=(self.object.pk,))
            output = self.output_url % (
                url,
                self.object.pk
            )
        except NoReverseMatch:
            output = self.object.pk
        return mark_safe(output)

    def get_additional_fields(self):
        additional_fields = {}
        stored_fields = self.get_stored_fields().keys()
        for key, value in self.object.get_additional_fields().items():
            if key not in stored_fields:
                additional_fields[key] = value
        return additional_fields

    def __getattr__(self, attr):
        return getattr(self.object, attr)


