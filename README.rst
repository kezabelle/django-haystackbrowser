.. _Django: https://www.djangoproject.com/
.. _Haystack: http://www.haystacksearch.org/
.. _Django administration: https://docs.djangoproject.com/en/dev/ref/contrib/admin/
.. _GitHub: https://github.com/
.. _PyPI: http://pypi.python.org/pypi
.. _kezabelle/django-haystackbrowser: https://github.com/kezabelle/django-haystackbrowser/
.. _master: https://github.com/kezabelle/django-haystackbrowser/tree/master
.. _issue tracker: https://github.com/kezabelle/django-haystackbrowser/issues/
.. _my Twitter account: https://twitter.com/kezabelle/
.. _FreeBSD: http://en.wikipedia.org/wiki/BSD_licenses#2-clause_license_.28.22Simplified_BSD_License.22_or_.22FreeBSD_License.22.29
.. _Ben Hastings: https://twitter.com/benjhastings/
.. _David Novakovic: http://blog.dpn.name/
.. _Francois Lebel: http://flebel.com/
.. _Jussi Räsänen: http://skyred.fi/
.. _Michaël Krens: https://github.com/michi88/
.. _REPL to inspect the SearchQuerySet: http://django-haystack.readthedocs.org/en/latest/debugging.html#no-results-found-on-the-web-page
.. _ticket 21056: https://code.djangoproject.com/ticket/21056
.. _tagged on GitHub: https://github.com/kezabelle/django-haystackbrowser/tags
.. _my laziness: https://github.com/kezabelle/django-haystackbrowser/issues/6
.. _Anton Shurashov: https://github.com/Sinkler/

.. title:: About

django-haystackbrowser
======================

:author: Keryn Knight

.. |travis_stable| image:: https://travis-ci.org/kezabelle/django-haystackbrowser.svg?branch=0.6.3
  :target: https://travis-ci.org/kezabelle/django-haystackbrowser/branches

.. |travis_master| image:: https://travis-ci.org/kezabelle/django-haystackbrowser.svg?branch=master
  :target: https://travis-ci.org/kezabelle/django-haystackbrowser/branches

==============  ======
Release         Status
==============  ======
stable (0.6.3)  |travis_stable|
master          |travis_master|
==============  ======

.. contents:: Sections
    :depth: 2

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

.. _requirements:

Requirements and dependencies
-----------------------------

django-haystackbrowser should hopefully run on:

  * **Django 1.3.1** or higher;
  * **Haystack 1.2** or higher (including **2.x**)

It additionally depends on ``django-classy-tags``, though only to use the provided
template tags, which are entirely optional.

Supported versions
^^^^^^^^^^^^^^^^^^

In theory, the below should work, based on a few minimal sanity-checking
tests; if any of them don't, please open a ticket on the `issue tracker`_.

+--------+-------------------------------------+
| Django | Python                              |
+--------+-------+-----+-------+-------+-------+
|        | 2.7   | 3.3 | 3.4   | 3.5   | 3.6   |
+--------+-------+-----+-------+-------+-------+
| 1.3.x  | Yup   |     |       |       |       |
+--------+-------+-----+-------+-------+-------+
| 1.4.x  | Yup   |     |       |       |       |
+--------+-------+-----+-------+-------+-------+
| 1.5.x  | Yup   | Yup |       |       |       |
+--------+-------+-----+-------+-------+-------+
| 1.6.x  | Yup   | Yup | Yup   |       |       |
+--------+-------+-----+-------+-------+-------+
| 1.7.x  | Yup   | Yup | Yup   |       |       |
+--------+-------+-----+-------+-------+-------+
| 1.8.x  | Yup   | Yup | Yup   | Yup   |       |
+--------+-------+-----+-------+-------+-------+
| 1.9.x  | Yup   |     | Yup   | Yup   |       |
+--------+-------+-----+-------+-------+-------+
| 1.10.x | Maybe |     | Maybe | Yup   | Maybe |
+--------+-------+-----+-------+-------+-------+
| 1.11.x | Maybe |     | Maybe | Yup   | Maybe |
+--------+-------+-----+-------+-------+-------+
| 2.0.x  |       |     | Maybe | Maybe | Yup   |
+--------+-------+-----+-------+-------+-------+

Any instances of **Maybe** are because I haven't personally used it on that,
version, nor have I had anyone report problems with it which would indicate a
lack of support.

What it does
------------

Any staff user with the correct permission (currently, ``request.user.is_superuser``
must be ``True``) has a new application available in the standard admin index.

There are two views, an overview for browsing and searching, and another for
inspecting the data found for an individual object.

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
  * The first few words of that primary content field, or a relevant snippet
    with highlights, if searching by keywords.

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
  * Strips any HTML tags present in the raw data when displaying, with an
    option to display raw data on hover.
  * Shows any `Haystack`_ specific settings in the settings module.
  * Shows up to **5** similar objects, if the backend supports it.

The stored data view, like the list view, provides links to the relevant admin
pages for the app/model/instance if appropriate.

Installation
------------

It's taken many years of `my laziness`_ to get around to it, but it is now
possible to get the package from `PyPI`_.

Using pip
^^^^^^^^^

The best way to grab the package is using ``pip`` to grab latest release from
`PyPI`_::

    pip install django-haystackbrowser==0.6.3

The alternative is to use ``pip`` to install the master branch in ``git``::

    pip install git+https://github.com/kezabelle/django-haystackbrowser.git#egg=django-haystackbrowser

Any missing dependencies will be resolved by ``pip`` automatically.

If you want the last release (0.6.3), such as it is, you can do::

    pip install git+https://github.com/kezabelle/django-haystackbrowser.git@0.6.3#egg=django-haystackbrowser

You can find all previous releases `tagged on GitHub`_

Using git directly
^^^^^^^^^^^^^^^^^^

If you're not using ``pip``, you can get the latest version::

    git clone https://github.com/kezabelle/django-haystackbrowser.git

and then make sure the ``haystackbrowser`` package is on your python path.

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

Contributing
------------

Please do!

The project is hosted on `GitHub`_ in the `kezabelle/django-haystackbrowser`_
repository. The main/stable branch is `master`_.

Bug reports and feature requests can be filed on the repository's `issue tracker`_.

If something can be discussed in 140 character chunks, there's also `my Twitter account`_.

Contributors
^^^^^^^^^^^^

The following people have been of help, in some capacity.

 * `Ben Hastings`_, for testing it under **Django 1.4** and subsequently forcing
   me to stop it blowing up uncontrollably.
 * `David Novakovic`_, for getting it to at least work under **Grappelli**, and
   fixing an omission in the setup script.
 * `Francois Lebel`_, for various fixes.
 * `Jussi Räsänen`_, for various fixes.
 * Vadim Markovtsev, for minor fix related to Django 1.8+.
 * `Michaël Krens`_, for various fixes.
 * `Anton Shurashov`_, for fixes related to Django 2.0.

TODO
----

 * Ensure the new faceting features work as intended (the test database I
   have doesn't *really* cover enough, yet)

Known issues
------------

 * Prior to `Django`_ 1.7, the links to the app admin may not actually work,
   because the linked app may not be mounted onto the AdminSite, but passing
   pretty much anything to the AdminSite app_list urlpattern will result in
   a valid URL. The other URLs should only ever work if they're mounted, though.
   See `ticket 21056`_ for the change.

The license
-----------

It's `FreeBSD`_. There's a ``LICENSE`` file in the root of the repository, and
any downloads.
