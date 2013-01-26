# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.management.commands.diffsettings import module_to_dict

def get_haystack_settings():
    """Find all settings which are prefixed with HAYSTACK_"""
    filtered_settings = {}
    searching_for = u'HAYSTACK_'
    all_settings = module_to_dict(settings._wrapped)
    for setting_name, setting_value in all_settings.items():

        if setting_name.startswith(searching_for):
            setting_name = setting_name.replace(searching_for, '').replace('_', ' ')
            filtered_settings[setting_name] = setting_value
    return filtered_settings
