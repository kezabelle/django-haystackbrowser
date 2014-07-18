# -*- coding: utf-8 -*-
import logging
from django import template
register = template.Library()

logger = logging.getLogger(__name__)

try:
    from django.template.defaultfilters import truncatechars
except ImportError: # We're on Django < 1.4, fake a simple one ...
    logger.info("truncatechars template filter not found, backfilling a "
                "vague approximation for Django < 1.4")
    from django.utils.encoding import force_unicode
    def truncatechars(value, arg):
        try:
            length = int(arg)
        except ValueError: # Invalid literal for int().
            return value # Fail silently.
        return force_unicode(value)[:length]
    register.filter('truncatechars', truncatechars)
