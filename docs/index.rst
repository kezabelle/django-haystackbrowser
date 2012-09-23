.. django-haystackbrowser documentation master file, created by
   sphinx-quickstart on Sun Sep 23 17:15:39 2012.

django-haystackbrowser
======================

.. toctree::
   :maxdepth: 2

In brief
--------

A reusable Django application for viewing all the data that Haystack knows
about.

Why I wrote it
--------------

I'm terrible at Haystack, and while I'm not allergic to the REPL, it's not a
convinient way to keep track of data I've managed to massage into the Haystack
backend.

This application, a minor hack of the Django administration, aims to solve that
by making search results browseable, in a developer-friendly way, rather than a
client friendly way.

What it does
------------

Any admin with the correct permission (currently, ``request.user.is_superuser``
must be ``True``) has a new application available in the standard admin index.

.. _the_views:

List view
^^^^^^^^^

The default landing page, the list view, shows the following fields:

  * model verbose name;
  * the Django app name, with a link to that admin page, if it's mounted.
  * the Django model name, linking to the admin changelist for that model, if
    it's mounted.
  * the database primary key for that object, linking to the admin change view for
    that specific object, if the app and model are mounted.
  * The primary content field for each result.
  * The first few words of that primary content field.

It also allows you to perform searches against the index, optionally limiting
to specific models. That's functionality Haystack provides out of the box, so
should be familiar.

Stored data view
^^^^^^^^^^^^^^^^

From the list view, clicking on ``View stored data`` for any result will bring
up the stored data view, which is the most useful part of it.

  * Shows all ``stored`` fields defined in the SearchIndex, and their values.
  * Highlights which of the stored fields is the primary content field
    (usually, ``text``)
  * Shows all additional fields.
  * Shows any Haystack specific settings in the settings module.

The stored data view, like the list view, provides links to the relevant admin
pages for the app/model/instance if appropriate.

.. _installation:

Installation
------------

The only method of installation currently is via git, as I've no intention of
polluting PyPI unless the app is provably not complete rubbish.

.. todo: Add install example via pip, and git.

Once it's on your Python path, add it to your settings module::

    INSTALLED_APPS = (
        'django.contrib.admin',
        'haystack',
        'haystackbrowser',
    )

It's assumed that both Haystack and the Django admin are already in your
``INSTALLED_APPS``, but if they're not, they need to be, so go ahead and add
them.

With that done, the only thing that's left to do is sign in as a superuser, and
verify the new *Search results* app works.

.. _contributing:

Contributing
------------

Please do!

The project is hosted on `GitHub`_ in the `kezabelle/django-haystackbrowser`_
repository. The main branch is *master*, but all work is carried out on
*develop* and merged in.

Bug reports and feature requests can be filed on the repository's `issue tracker`_.

If something can be discussed in 140 character chunks, there's also `my Twitter account`_.

.. _GitHub: https://github.com/
.. _kezabelle/django-haystackbrowser: https://github.com/kezabelle/django-haystackbrowser/
.. _issue tracker: https://github.com/kezabelle/django-haystackbrowser/issues/
.. _my Twitter account: https://twitter.com/kezabelle/

