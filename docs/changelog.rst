Change history
--------------

A list of changes which affect the API and related code follows. Documentation
and other miscellaneous changes are not listed. See the git history for a
complete history.

January 2013
^^^^^^^^^^^^

  * |feature| Added template tag for rendering the data found in the haystack
    index for any given object;
  * |feature| Added two possible admin templates:

    * ``admin/haystackbrowser/change_form_with_link.html`` which adds a link
      (alongside the *history* and *view on site* links) to the corresponding
      stored data view for the current object.
    * ``admin/haystackbrowser/change_form_with_data.html`` which displays all
      the stored data for the current object, on the same screen, beneath the standard
      ``ModelAdmin`` submit row.

  * |feature| Exposed the discovered settings via the new function
    ``get_haystack_settings`` in the ``utils`` module.
  * |bugfix| Removed the template syntax which was previously causing the app
    to crash under 1.3.0, but not under 1.3.1, because of `this ticket`_ against
    Django.
  * |bugfix| Removed the ``{% blocktrans with x=y %}`` syntax, in favour of the
    ``{% blocktrans with y as x %}`` style, which allows the app to work under
    **Django 1.2**

November 2012
^^^^^^^^^^^^^

  * |bugfix| issue which caused the app not to work under Django 1.4+ because an
    attribute was removed quietly from the standard AdminSite.
  * |bugfix| No more ridiculous pagination in the list view.

September 2012
^^^^^^^^^^^^^^

  * Initial hackery to get things into a working state. Considered the first release,
    for lack of a better term.


.. |bugfix| replace:: **Bug fix:**
.. |feature| replace:: **New/changed:**
.. _this ticket: https://code.djangoproject.com/ticket/15721
