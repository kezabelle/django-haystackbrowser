.. django-haystackbrowser documentation master file, created by
   sphinx-quickstart on Sun Sep 23 17:15:39 2012.

.. _Django: https://www.djangoproject.com/
.. _Haystack: http://www.haystacksearch.org/
.. _Django administration: https://docs.djangoproject.com/en/dev/ref/contrib/admin/
.. _GitHub: https://github.com/
.. _git: http://git-scm.com/
.. _PyPI: http://pypi.python.org/pypi
.. _kezabelle/django-haystackbrowser: https://github.com/kezabelle/django-haystackbrowser/
.. _issue tracker: https://github.com/kezabelle/django-haystackbrowser/issues/
.. _my Twitter account: https://twitter.com/kezabelle/
.. _FreeBSD: http://en.wikipedia.org/wiki/BSD_licenses#2-clause_license_.28.22Simplified_BSD_License.22_or_.22FreeBSD_License.22.29
.. _Ben Hastings: https://twitter.com/benjhastings/

django-haystackbrowser
======================

:author: Keryn Knight

In brief
--------

A reusable `Django`_ application for viewing and debugging all the data that
has been pushed into `Haystack`_.

Why I wrote it
--------------

I'm terrible at Haystack, and while I'm not allergic to the REPL, it's not a
convinient way to keep track of data I've managed to massage into the
`Haystack`_ backend.

This application, a minor hack of the `Django administration`_, aims to solve that
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
  * the `Django`_ app name, with a link to that admin page, if any model
    belonging to it has been registered via ``admin.site.register``;
  * the `Django`_ model name, linking to the admin changelist for that model, if
    it has been registered via ``admin.site.register``;
  * the database primary key for that object, linking to the admin change view for
    that specific object, if the app and model are both registered via
    ``admin.site.register``;
  * The primary content field for each result;
  * The first few words of that primary content field.

It also allows you to perform searches against the index, optionally limiting
to specific models. That's functionality `Haystack`_ provides out of the box, so
should be familiar.

Stored data view
^^^^^^^^^^^^^^^^

From the list view, clicking on ``View stored data`` for any result will bring
up the stored data view, which is the most useful part of it.

  * Shows all ``stored`` fields defined in the SearchIndex, and their values;
  * Highlights which of the stored fields is the primary content field
    (usually, ``text``);
  * Shows all additional fields;
  * Shows any `Haystack`_ specific settings in the settings module.

The stored data view, like the list view, provides links to the relevant admin
pages for the app/model/instance if appropriate.

.. _installation:

Installation
------------

The only method of installation currently is via `git`_, as I've no intention of
polluting `PyPI`_ unless the app is provably not complete rubbish.

To get the latest version::

    git clone git@github.com:kezabelle/django-haystackbrowser.git

and then make sure the ``haystackbrowser`` package is on your python path.

.. note::
    At some point, I'll put together a setup file, and then it'll be possible to install via ``pip``.

Once it's on your Python path, add it to your settings module::

    INSTALLED_APPS += (
        'haystackbrowser',
    )

Requirements
^^^^^^^^^^^^

The requirements are pretty specific, at this point. If the planets have
aligned, things might not blow up!

Specifically, it depends on **Django 1.2.0** or higher, and **Haystack 1.2.0** or
higher.

It's assumed that both `Haystack`_ and the `Django administration`_ are already in your
``INSTALLED_APPS``, but if they're not, they need to be, so go ahead and add
them::

    INSTALLED_APPS += (
        'django.contrib.admin',
        'haystack',
        'haystackbrowser',
    )



.. _usage:

Usage
-----

With the `installation`_ done and the `requirements`_ met, the only thing that's
left to do is sign in as a superuser, and verify the new *Search results* app
works. It probably won't, in which case you'd be doing me a favour if you filed
a ticket on the `issue tracker`_!

Assuming it does work, you can augment your existing ModelAdmins by using
(or copy-pasting from) the templates available:

* ``admin/haystackbrowser/change_form_with_link.html`` adds a link
  (alongside the *history* and *view on site* links) to the corresponding
  stored data view for the current object.
* ``admin/haystackbrowser/change_form_with_data.html`` displays all
  the stored data for the current object, on the same screen, beneath the standard
  ``ModelAdmin`` submit row.

Both templates play nicely with the standard admin pages, and both ensure
they call their ``{% block %}``'s super context.

Their simplest usage would be::

    class MyModelAdmin(admin.ModelAdmin):
        change_form_template = 'admin/haystackbrowser/change_form_with_data.html'

Though if you've already changed your template, either via the attribute or
via admin template discovery, you can easily take the minor changes from these listed
templates and adapt them for your own needs.

.. note::
    Both the provided templates check that the given context has ``change=True``
    and access to the ``original`` object being edited, so nothing will appear on
    the add screens.

.. _contributing:

Contributing
------------

Please do!

The project is hosted on `GitHub`_ in the `kezabelle/django-haystackbrowser`_
repository. The main branch is *master*, but all work is carried out on
*develop* and merged in.

Bug reports and feature requests can be filed on the repository's `issue tracker`_.

If something can be discussed in 140 character chunks, there's also `my Twitter account`_.

Contributors
------------

The following people have been of help, in some capacity.

 * `Ben Hastings`_

TODO
----

 * Possibly figure out how to turn the model filtering into a decent Faceted
   search.

Known issues
------------

 * The links to the app admin may not actually work, because the app may not be
   mounted onto the AdminSite, but passing pretty much anything to the
   AdminSite app_list urlpattern will result in a valid URL. The other URLs
   should only ever work if they're mounted, though.

The license
-----------

It's `FreeBSD`_. There's a ``LICENSE`` file in the root of the repository, and
any downloads.
