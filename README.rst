.. _Django: https://www.djangoproject.com/
.. _Haystack: http://www.haystacksearch.org/
.. _Django administration: https://docs.djangoproject.com/en/dev/ref/contrib/admin/
.. _GitHub: https://github.com/
.. _git: http://git-scm.com/
.. _PyPI: http://pypi.python.org/pypi
.. _kezabelle/django-haystackbrowser: https://github.com/kezabelle/django-haystackbrowser/
.. _master: https://github.com/kezabelle/django-haystackbrowser/tree/master
.. _develop: https://github.com/kezabelle/django-haystackbrowser/tree/develop
.. _issue tracker: https://github.com/kezabelle/django-haystackbrowser/issues/
.. _my Twitter account: https://twitter.com/kezabelle/
.. _FreeBSD: http://en.wikipedia.org/wiki/BSD_licenses#2-clause_license_.28.22Simplified_BSD_License.22_or_.22FreeBSD_License.22.29
.. _Ben Hastings: https://twitter.com/benjhastings/
.. _David Novakovic: http://blog.dpn.name/
.. _Jussi Räsänen: http://skyred.fi/
.. _REPL to inspect the SearchQuerySet: http://django-haystack.readthedocs.org/en/latest/debugging.html#no-results-found-on-the-web-page
.. _ticket 21056: https://code.djangoproject.com/ticket/21056

.. title:: About

django-haystackbrowser
======================

:author: Keryn Knight

In brief
--------

A plug-and-play `Django`_ application for viewing, browsing and debugging data
discovered in your `Haystack`_ Search Indexes.


Why I wrote it
--------------

I love `Haystack`_ but I'm sometimes not sure what data I have in it. When a
query isn't producing the result I'd expect, debugging it traditionally involves
using the Python `REPL to inspect the SearchQuerySet`_, and while I'm not allergic
to doing that, it can be inconvenient, and doesn't scale well when you need to
make multiple changes.

This application, a minor abuse of the `Django administration`_, aims to solve that
by providing a familiar interface in which to query and browse the data, in a
developer-friendly way.

What it does
------------

Any staff user with the correct permission (currently, ``request.user.is_superuser``
must be ``True``) has a new application available in the standard admin index.

There are two views, an overview for browsing and searching, and another for
inspecting the data found for an individual object.

.. _the_views:

List view
^^^^^^^^^

The default landing page, the list view, shows the following fields:

  * model verbose name;
  * the `Django`_ app name, with a link to that admin page;
  * the `Django`_ model name, linking to the admin changelist for that model, if
    it has been registered via ``admin.site.register``;
  * the database primary key for that object, linking to the admin change view for
    that specific object, if the app and model are both registered via
    ``admin.site.register``;
  * The *score* for the current query, as returned by `Haystack`_ - when no
    query is given, the default score of **1.0** is used;
  * The primary content field for each result;
  * The first few words of that primary content field.

It also allows you to perform searches against the index, optionally filtering
by specific models or faceted fields. That's functionality `Haystack`_ provides
out of the box, so should be familiar.

If your `Haystack`_ configuration includes multiple connections, you can pick
and choose which one to use on a per-query basis.

Stored data view
^^^^^^^^^^^^^^^^

From the list view, clicking on ``View stored data`` for any result will bring
up the stored data view, which is the most useful part of it.

  * Shows all ``stored`` fields defined in the SearchIndex, and their values;
  * Highlights which of the stored fields is the primary content field
    (usually, ``text``);
  * Shows all additional fields;
  * Shows any `Haystack`_ specific settings in the settings module.
  * Shows up to **5** similar objects, if the backend supports it.

The stored data view, like the list view, provides links to the relevant admin
pages for the app/model/instance if appropriate.

.. _requirements:

Requirements and dependencies
-----------------------------

django-haystackbrowser should hopefully run on:

  * **Django 1.3.1** or higher;
  * **Haystack 1.2** or higher (including **2.0**!)

It additionally depends on ``django-classy-tags``, though only to use the provided
template tags, which are entirely optional.

.. _installation:

Installation
------------

The only method of installation currently is via `git`_, as I've no intention of
polluting `PyPI`_ unless the app is provably not complete rubbish.

Using pip
^^^^^^^^^

The best way to grab the package is using ``pip`` to install via ``git``::

    pip install git+https://github.com/kezabelle/django-haystackbrowser.git@0.5.0#egg=django-haystackbrowser

Any missing dependencies will be resolved by ``pip`` automatically.

Using git directly
^^^^^^^^^^^^^^^^^^

If you're into living on the edge, or don't use ``pip``, you can get the latest version::

    git clone git@github.com:kezabelle/django-haystackbrowser.git

and then make sure the ``haystackbrowser`` package is on your python path.

.. _usage:

Usage
-----

Once it's on your Python path, add it to your settings module::

    INSTALLED_APPS += (
        'haystackbrowser',
    )

It's assumed that both `Haystack`_ and the `Django administration`_ are already in your
``INSTALLED_APPS``, but if they're not, they need to be, so go ahead and add
them::

    INSTALLED_APPS += (
        'django.contrib.admin',
        'haystack',
        'haystackbrowser',
    )

With the  `requirements`_ met and the `installation`_ complete, the only thing that's
left to do is sign in to the AdminSite, and verify the new *Search results* app
works.

Extending admin changeforms
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Assuming it works, you can augment your existing ModelAdmins by using
(or copy-pasting from) the templates available:

* ``admin/haystackbrowser/change_form_with_link.html`` adds a link
  (alongside the **history** and **view on site** links) to the corresponding
  stored data view for the current object.
* ``admin/haystackbrowser/change_form_with_data.html`` displays all
  the stored data for the current object, on the same screen, beneath the standard
  ``ModelAdmin`` submit row.

Both templates play nicely with the standard admin pages, and both ensure
they call their ``{% block %}``'s super context.

Their simplest usage would be::

    class MyModelAdmin(admin.ModelAdmin):
        change_form_template = 'admin/haystackbrowser/change_form_with_data.html'

Though if you've already changed your template, either via the aforementioned attribute or
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
repository. The main/stable branch is `master`_.

Bug reports and feature requests can be filed on the repository's `issue tracker`_.

If something can be discussed in 140 character chunks, there's also `my Twitter account`_.

Contributors
------------

The following people have been of help, in some capacity.

 * `Ben Hastings`_, for testing it under **Django 1.4** and subsequently forcing
   me to stop it blowing up uncontrollably.
 * `David Novakovic`_, for getting it to at least work under **Grappelli**, and
   fixing an omission in the setup script.
 * `Jussi Räsänen`_, for various fixes.

TODO
----

 * Ensure the new faceting features work as intended (the test database I
   have doesn't *really* cover enough, yet)

Known issues
------------

 * The links to the app admin may not actually work, because the app may not be
   mounted onto the AdminSite, but passing pretty much anything to the
   AdminSite app_list urlpattern will result in a valid URL. The other URLs
   should only ever work if they're mounted, though.
   This should be fixed in `Django`_ 1.7 though, assuming `ticket 21056`_ doesn't
   need reverting for any unforseen reason.

The license
-----------

It's `FreeBSD`_. There's a ``LICENSE`` file in the root of the repository, and
any downloads.
