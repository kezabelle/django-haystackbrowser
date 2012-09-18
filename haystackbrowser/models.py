from django.db import models
from django.utils.translation import ugettext_lazy as _

class HaystackResultsProxy(models.Model):
    class Meta:
        managed = False
        verbose_name = _('Search result')
        verbose_name_plural = _('Search results')
