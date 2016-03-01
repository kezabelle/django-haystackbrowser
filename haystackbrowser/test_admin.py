# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
import pytest
from functools import partial
from django.conf import settings
from django.core.urlresolvers import reverse, resolve
from haystack.exceptions import SearchBackendError
from haystackbrowser.admin import Search404
from haystackbrowser.forms import PreSelectedModelSearchForm
from haystackbrowser.models import SearchResultWrapper

skip_old_haystack = pytest.mark.skipif(settings.OLD_HAYSTACK is True,
                                  reason="Doesn't apply to Haystack 1.2.x")

skip_new_haystack = pytest.mark.skipif(settings.OLD_HAYSTACK is False,
                                       reason="Doesn't apply to Haystack 2.x")


@pytest.yield_fixture
def detailview(admin_user, rf):
    url = reverse('admin:haystackbrowser_haystackresults_change',
                  kwargs={'content_type': 1, 'pk': 1})
    request = rf.get(url)
    request.user = admin_user
    match = resolve(url)
    yield partial(match.func, request, *match.args, **match.kwargs)


def test_detailview_has_view_result_but_fails_because_mlt(mocker, detailview):
    """
    Gets as far as:
    raw_mlt = SearchQuerySet().more_like_this(model_instance)[:5]
    before raising.
    """
    mocker.patch('haystack.query.SearchQuerySet.filter').return_value = [mocker.Mock()]
    with pytest.raises(SearchBackendError):
        detailview()


def test_detailview_has_view_result_templateresponse(mocker, detailview):
    original = mocker.Mock()
    mlt = [mocker.Mock(), mocker.Mock()]
    mocker.patch('haystack.query.SearchQuerySet.filter').return_value = [original]
    mocker.patch('haystack.query.SearchQuerySet.more_like_this').return_value = mlt
    response = detailview()
    from django.template.response import TemplateResponse
    assert isinstance(response, TemplateResponse) is True
    assert response.status_code == 200
    assert sorted(response.context_data.keys()) == [
        'app_label',
        'form',
        'form_valid',
        'has_change_permission',
        'haystack_settings',
        'haystack_version',
        'module_name',
        'original',
        'similar_objects',
        'title'
    ]
    assert response.context_data['form_valid'] is False
    assert response.context_data['has_change_permission'] is True
    assert len(response.context_data['similar_objects']) == 2
    assert isinstance(response.context_data['original'], SearchResultWrapper)
    assert isinstance(response.context_data['form'], PreSelectedModelSearchForm)
    assert response.context_data['original'].object == original



@skip_new_haystack
def test_detailview_has_view_result_templateresponse_settings_version1(mocker, detailview):
    mlt = [mocker.Mock(), mocker.Mock()]
    mocker.patch('haystack.query.SearchQuerySet.filter').return_value = [mocker.Mock()]
    mocker.patch('haystack.query.SearchQuerySet.more_like_this').return_value = mlt
    response = detailview()
    assert len(response.context_data['haystack_settings']) == 3
    values = {x[0] for x in response.context_data['haystack_settings']}
    assert values == {'SEARCH ENGINE', 'SITECONF', 'WHOOSH PATH'}


@skip_old_haystack
def test_detailview_has_view_result_templateresponse_settings_version2(mocker, detailview):
    mlt = [mocker.Mock(), mocker.Mock()]
    mocker.patch('haystack.query.SearchQuerySet.filter').return_value = [mocker.Mock()]
    mocker.patch('haystack.query.SearchQuerySet.more_like_this').return_value = mlt
    response = detailview()
    assert len(response.context_data['haystack_settings']) == 4
    values = {x[0] for x in response.context_data['haystack_settings']}
    assert values == {'ENGINE', 'PATH'}



def test_detailview_no_result(mocker, detailview):
    mocker.patch('haystack.query.SearchQuerySet.filter').return_value = []
    with pytest.raises(Search404):
        detailview()
