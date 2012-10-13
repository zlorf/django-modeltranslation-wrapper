#!/usr/bin/env python
from django.conf import settings
from django.core.management import call_command


if not settings.configured:
    settings.configure(
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            }
        },
        INSTALLED_APPS = (
            'modeltranslation_wrapper',
        ),
        # This is necessary since modeltranslation-0.4 enforces some value (bug reported)
        MODELTRANSLATION_TRANSLATION_FILES = ('modeltranslation_wrapper.tests.nothing',),
    )

call_command('test', 'modeltranslation_wrapper')
