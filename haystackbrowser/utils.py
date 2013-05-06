# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.management.commands.diffsettings import module_to_dict


def get_haystack_settings():
    """
    Find all settings which are prefixed with `HAYSTACK_`
    """
    filtered_settings = []
    connections = getattr(settings, 'HAYSTACK_CONNECTIONS', {})
    try:
        # 2.x style (one giant dictionary)
        connections['default']  #: may be a KeyError, in which case, 1.x style.
        for named_backend, values in connections.items():
            for setting_name, setting_value in values.items():
                setting_name = setting_name.replace('_', ' ')
                filtered_settings.append((setting_name, setting_value, named_backend))
    except KeyError as e:
        # 1.x style, where everything is a separate setting.
        searching_for = u'HAYSTACK_'
        all_settings = module_to_dict(settings._wrapped)
        for setting_name, setting_value in all_settings.items():
            if setting_name.startswith(searching_for):
                setting_name = setting_name.replace(searching_for, '').replace('_', ' ')
                filtered_settings.append((setting_name, setting_value))
    return filtered_settings
