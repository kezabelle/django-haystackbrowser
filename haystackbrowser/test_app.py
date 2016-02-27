# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals
import pytest
from django.core.urlresolvers import reverse, resolve
from .admin import Search404


def test_app_is_mounted_accessing_changelist_but_no_models_loaded(admin_user, rf):
    url = reverse('admin:haystackbrowser_haystackresults_changelist')
    request = rf.get(url)
    request.user = admin_user
    match = resolve(url)
    with pytest.raises(Search404):
        match.func(request, *match.args, **match.kwargs)


def test_app_is_mounted_viewing_details_but_no_models_loaded(admin_user, rf):
    url = reverse('admin:haystackbrowser_haystackresults_change',
                  kwargs={'content_type': 1, 'pk': 1})
    request = rf.get(url)
    request.user = admin_user
    match = resolve(url)
    with pytest.raises(Search404):
        match.func(request, *match.args, **match.kwargs)
