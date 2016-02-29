# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals
import pytest

from django.conf import settings
from django.core.urlresolvers import reverse, resolve
from .admin import Search404


skip_old_haystack = pytest.mark.skipif(settings.OLD_HAYSTACK is True,
                                  reason="Doesn't apply to Haystack 1.2.x")

skip_new_haystack = pytest.mark.skipif(settings.OLD_HAYSTACK is False,
                                       reason="Doesn't apply to Haystack 2.x")

@skip_new_haystack
def test_env_setting_old_haystack():
    assert settings.OLD_HAYSTACK is True


@skip_old_haystack
def test_env_setting_new_haystack():
    assert settings.OLD_HAYSTACK is False


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
