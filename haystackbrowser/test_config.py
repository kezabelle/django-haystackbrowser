# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import pytest
from django.conf import settings

try:
    from django.utils.encoding import force_text
except ImportError:  # Django < 1.4 didn't have force_text because it predates 1.4-1.5 py3k support
    from django.utils.encoding import force_unicode as force_text
from haystackbrowser.utils import HaystackConfig

try:
    from django.test import override_settings
except ImportError:
    try:
        from django.test.utils import override_settings
    except ImportError:  # Django 1.3.x
        from .tests_compat import override_settings

skip_old_haystack = pytest.mark.skipif(settings.OLD_HAYSTACK is True,
                                  reason="Doesn't apply to Haystack 1.2.x")

skip_new_haystack = pytest.mark.skipif(settings.OLD_HAYSTACK is False,
                                       reason="Doesn't apply to Haystack 2.x")


@skip_old_haystack
def test_get_valid_filters_version2():
    conf = HaystackConfig()
    filters = tuple((x, force_text(y)) for x, y in conf.get_valid_filters())
    assert filters == (('contains', 'contains'),
                       ('exact', 'exact'),
                       ('fuzzy', 'similar to (fuzzy)'),
                       ('gt', 'greater than'), 
                       ('gte', 'greater than or equal to'), 
                       ('in', 'in'), 
                       ('lt', 'less than'), 
                       ('lte', 'less than or equal to'), 
                       ('range', 'range (inclusive)'), 
                       ('startswith', 'starts with'))

@skip_new_haystack
def test_get_valid_filters_version2():
    conf = HaystackConfig()
    filters = tuple((x, force_text(y)) for x, y in conf.get_valid_filters())
    assert filters == (('exact', 'exact'),
                       ('gt', 'greater than'),
                       ('gte', 'greater than or equal to'),
                       ('in', 'in'),
                       ('lt', 'less than'),
                       ('lte', 'less than or equal to'),
                       ('range', 'range (inclusive)'),
                       ('startswith', 'starts with'))
