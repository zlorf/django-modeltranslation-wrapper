"""Settings overrided for test time"""

SETTINGS = {
    'LANGUAGE_CODE': 'en',
    'LANGUAGES': (
        ('en', 'English'),
        ('pl', 'Polish'),
    ),
    'INSTALLED_APPS': (
        'modeltranslation_wrapper.tests.test_app',
        'modeltranslation_wrapper',
        'modeltranslation',
    ),
    'XYZ': 'abc',
    'MODELTRANSLATION_TRANSLATION_FILES': ('modeltranslation_wrapper.patch',), # for 0.4, see README
    'MODELTRANSLATION_TRANSLATION_REGISTRY': '',
    'MODELTRANSLATION_AUTO_POPULATE': False,
}
