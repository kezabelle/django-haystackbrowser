Change history
--------------

A list of changes which affect the API and related code follows. Documentation
and other miscellaneous changes are not listed. See the git history for a
complete history.

May 2013
^^^^^^^^

  * |feature| Supports the **Haystack 2.0 beta** changes, while maintaining
    1.x support.
  * |feature| support for faceting (**experimental**)

    * Requires a faceting backend (see `backend capabilities`_) - currently
      only Solr and Xapian are whitelisted, and only Solr tested.
    * Provides a list of possible fields on which to facet.
    * Faceting is done based on selected fields.

  * |feature| the *Stored data view* now makes use of `more like this`_
    to display other objects in the index which are similar.
  * |feature| If a query is present in the changelist view, discovered
    results are fed through the ``highlight`` template tag to display
    the appropriate snippet.
  * |feature| Stored data view now includes a (translatable) count of the
    stored/additional fields on the index.
  * |feature| The changelist title now better reflects the view by including
    the query, if given.
  * |bugfix| *Content field*, *Score* and *Content* headers on the changelist
    were previously not available for translation.
  * |bugfix| the *Clear filters* action on the changelist view is now only
    displayed if the model count in the querystring does not match the
    available models. Previously it was always displayed.
  * |bugfix| *clear filters* is now a translatable string *clear all filters*

April 2013
^^^^^^^^^^

  * |bugfix| Lack of media prevents the page from working under Grappelli.
    Thanks to `David Novakovic`_ (`dpnova`_ on `GitHub`_) for the fix.
  * |bugfix| Templates weren't getting included when using the setup.py,
    probably because I've always been using `setup.py develop`.
    Thanks to `David Novakovic`_ (`dpnova`_ on `GitHub`_) for the fix.

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
.. _David Novakovic: http://blog.dpn.name/
.. _dpnova: https://github.com/dpnova/
.. _GitHub: https://github.com/
.. _backend capabilities: http://django-haystack.readthedocs.org/en/latest/backend_support.html#backend-capabilities
.. _more like this: http://django-haystack.readthedocs.org/en/latest/searchqueryset_api.html#more-like-this
