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
    'MODELTRANSLATION_TRANSLATION_FILES': (),
    'MODELTRANSLATION_TRANSLATION_REGISTRY': '',
    'MODELTRANSLATION_AUTO_POPULATE': False,
}
