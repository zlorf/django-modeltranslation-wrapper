===============================
django-modeltranslation-wrapper
===============================

This package is a bunch of patches for ``django-modeltranslation``
(http://code.google.com/p/django-modeltranslation/,
http://pypi.python.org/pypi/django-modeltranslation/),
which can enhance usage of this nice app and target some annoying aspects.

Two features were added:

* autodiscover of ``translation.py`` files within apps

    ``modeltranslation-0.4`` already has this feature (ported from this app :P), so it is no more
    needed here and is only left for use with older versions of ``modeltranslation``.
    Thus, the autodiscover is deactivated if the 0.4 version of ``modeltranslation`` is detected.

* intelligent manager: filtering, ordering, creating and so on takes current language into
  consideration

    (This feature was mainly ported from ``django-linguo`` (https://github.com/zmathew/django-linguo,
    http://pypi.python.org/pypi/django-linguo),
    another good app. However, ``modeltranslation`` idea of `translation fields` registration is
    better than ``linguo`` model code edition - especially with 3rd-party apps)

Later, ``modeltranslation`` will be referred as `MT`, and ``django-modeltranslation-wrapper`` as
`Wrapper`.

Features
========

Autodiscover
------------

This app changes the way that the translation files are sought for. In `MT`, you have
just one file per project. `Wrapper` makes it more like in the ``admin``: every application in
``INSTALLED_APPS`` is examined and its ``translation.py`` is imported (if present).

Moreover, if you still want to include some non-app translations (e.g. translation for 3rd-party apps),
there is new setting introduced: ``MODELTRANSLATION_TRANSLATION_FILES``. It should contain list of
additional modules (containing translations) to import.

So, when using `Wrapper`, the ``MODELTRANSLATION_TRANSLATION_REGISTRY`` setting is unnecessary.

For backward compatibility with `MT`, when ``MODELTRANSLATION_TRANSLATION_REGISTRY`` is present,
it is treated as if it was listed in ``MODELTRANSLATION_TRANSLATION_FILES``. So no changes are
required in existing projects using `MT`.

Intelligent manager
-------------------

`Wrapper` changes managers in translatable models so that they are aware of active language in their
operations. That means, unsuffixed attributes parameters are rewritten to the suffixed versions.

These statements give the same results, assuming current active language is ``pl``::

    X.objects.filter(foo='bar')
    X.objects.filter(foo_pl='bar')

    activate('de')
    X.objects.filter(foo_pl='bar')  # Still the same result

If the translatable model has own custom manager, intelligent manager will be gently added,
retaining old functions.

The ``X.objects.create()`` is special case, however. For backward compatibility it works as in `MT` by
default. But you can pass parameter ``_populate=True`` to populate suffixed fields with
values from unsuffixed ones.

Example will clarify it::

    x = X.objects.create(foo='bar', _populate=True)

is equivalent of::

    x = X.objects.create(foo_en='bar', foo_pl='bar', ... , foo_zu='bar')

or::

    x = X.objects.create(foo='bar')
    x.foo_en = 'bar'
    x.foo_pl = 'bar'
    ...
    x.foo_zu = 'bar'
    x.save()

Moreover, some field can be explicitly assigned different value::

    x = X.objects.create(foo='-- no translation yet --', foo_pl='nic', _populate=True)

It will result in ``foo_pl == 'nic'`` and other ``foo_?? == '-- no translation yet --'``.

There is more convenient way than passing ``_populate`` all the time:
``MODELTRANSLATION_AUTO_POPULATE`` setting. If ``_populate`` parameter is missing, ``create()`` will
look at the setting to determine if population should be used.

This useful feature is disabled by default for backward compatibility with `MT` tests.
However, if your code doesn't heavily rely on the fact that ``create()`` set None on suffixed fields,
it is advised to set ``MODELTRANSLATION_AUTO_POPULATE = True``.

New settings
------------

MODELTRANSLATION_TRANSLATION_FILES
    Default: ``()``

    List of additional translation modules to import.

MODELTRANSLATION_AUTO_POPULATE
    Default: ``False``

    This setting control if ``X.objects.create()`` function should populate language fields
    values.


Installation
============

1. Install app::

    $ pip install django-modeltranslation-wrapper

   or download it manually and put in python path.

#. Add ``modeltranslation_wrapper`` to ``INSTALLED_APPS`` **before** plain ``modeltranslation``::

    INSTALLED_APPS = (
        ...
        'modeltranslation_wrapper',
        'modeltranslation',
        ...
    )

#. Optionally, specify ``MODELTRANSLATION_TRANSLATION_FILES`` in settings::

    MODELTRANSLATION_TRANSLATION_FILES = (
        'myproject.flatpages_translation',
        'myproject.foo_translation',
    )

   These modules will be imported in addition to autodiscovered ones.

#. If you are using `MT` in version 0.4 or newer, unfortunatelly you must also add
   ``'modeltranslation_wrapper.patch'`` as last entry in ``MODELTRANSLATION_TRANSLATION_FILES``
   to enable inteligent manager::

    MODELTRANSLATION_TRANSLATION_FILES = (
        'myproject.flatpages_translation',
        'myproject.foo_translation',
        'modeltranslation_wrapper.patch',
    )

   This is caused by change in the way `MT` 0.4 loads translations.

#. Optionally, specify ``MODELTRANSLATION_AUTO_POPULATE`` (see above)::

    MODELTRANSLATION_AUTO_POPULATE = True

----------

Changelog
=========

**1.2.1** (23/09/2012)
    - Refactor code to work with modeltranslation-0.4
    - Update MultilingualManager to rewrite Q nad F queries

**1.1** (04/09/2012)
    Added testrunner

**1.0** (24/06/2012)
    Initial code

:Authors: Jacek Tomaszewski

          Zach Mathew (of ``django-linguo``)

          For details see AUTHORS file.
