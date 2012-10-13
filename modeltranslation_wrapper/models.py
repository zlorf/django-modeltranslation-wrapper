from django.conf import settings

try:
    from modeltranslation import autodiscover
    # direct patch will not be possible.
    # one need to set 'modeltranslation_wrapper.patch' at end of MODELTRANSLATION_TRANSLATION_FILES
except ImportError:
    # modeltranslation < 0.4, so use the translation autodiscover
    settings.MODELTRANSLATION_TRANSLATION_FILES = list(
        getattr(settings, 'MODELTRANSLATION_TRANSLATION_FILES', ()))
    if getattr(settings, 'MODELTRANSLATION_TRANSLATION_REGISTRY', None):
        settings.MODELTRANSLATION_TRANSLATION_FILES.append(settings.MODELTRANSLATION_TRANSLATION_REGISTRY)
    if 'modeltranslation_wrapper.patch' in settings.MODELTRANSLATION_TRANSLATION_FILES:
        settings.MODELTRANSLATION_TRANSLATION_FILES.remove('modeltranslation_wrapper.patch')
    settings.MODELTRANSLATION_TRANSLATION_FILES.append('modeltranslation_wrapper.patch')
    settings.MODELTRANSLATION_TRANSLATION_REGISTRY = 'modeltranslation_wrapper.translation_autodiscover'
