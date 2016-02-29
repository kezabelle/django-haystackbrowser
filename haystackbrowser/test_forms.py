# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
import pytest
from django.conf import settings
from django.test import override_settings
from haystackbrowser.forms import PreSelectedModelSearchForm
from mock import patch, Mock

skip_old_haystack = pytest.mark.skipif(settings.OLD_HAYSTACK is True,
                                  reason="Doesn't apply to Haystack 1.2.x")

skip_new_haystack = pytest.mark.skipif(settings.OLD_HAYSTACK is False,
                                       reason="Doesn't apply to Haystack 2.x")


Model = Mock(return_value='testmodel')
Meta = Mock(app_label='test', model_name='testing', module_name='anothertest')
Model.attach_mock(Meta, '_meta')


@skip_new_haystack
def test_guess_haystack_version1():
    form = PreSelectedModelSearchForm(data={})
    assert form.version == 1


@skip_old_haystack
def test_guess_haystack_version2():
    form = PreSelectedModelSearchForm(data={})
    assert form.version == 2


@skip_new_haystack
def test_should_allow_faceting_version1_ok_backend():
    form = PreSelectedModelSearchForm(data={})
    with override_settings(HAYSTACK_SEARCH_ENGINE='solr'):
        assert form.should_allow_faceting() is True


@skip_new_haystack
def test_should_allow_faceting_version1_ok_backend():
    form = PreSelectedModelSearchForm(data={})
    assert form.should_allow_faceting() is False


@skip_old_haystack
def test_should_allow_faceting_version2_ok_backend():
    form = PreSelectedModelSearchForm(data={})
    NEW_CONFIG = {
        'default': {
            'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
            'PATH': 'test',
        }
    }
    with override_settings(HAYSTACK_CONNECTIONS=NEW_CONFIG):
        assert form.should_allow_faceting() is True


@skip_old_haystack
def test_should_allow_faceting_version2_bad_backend():
    form = PreSelectedModelSearchForm(data={})
    # whoosh isn't supported for faceting
    assert form.should_allow_faceting() is False


@skip_old_haystack
@patch('haystack.backends.BaseEngine.get_unified_index')
def test_configure_faceting_version2_has_data(unified_index):
    # mock out enough of the backend to get data
    indexed_models = Mock(return_value=[Model, Model])
    facet_fieldnames = Mock(_facet_fieldnames={'a': 1, 'b':2})
    facet_fieldnames.attach_mock(indexed_models, 'get_indexed_models')
    unified_index.return_value = facet_fieldnames
    form = PreSelectedModelSearchForm(data={})
    assert form.configure_faceting() == [('a', 'A'), ('b', 'B')]


@skip_old_haystack
def test_configure_faceting_version2_without_data():
    form = PreSelectedModelSearchForm(data={})
    assert form.configure_faceting() == []
