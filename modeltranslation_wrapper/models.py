from django.conf import settings
from django.db.models.base import ModelBase
from django.db.models import Manager


# Use the translation autodiscover
settings.MODELTRANSLATION_TRANSLATION_FILES = tuple(
    getattr(settings, 'MODELTRANSLATION_TRANSLATION_FILES', ()))
if getattr(settings, 'MODELTRANSLATION_TRANSLATION_REGISTRY', None):
    settings.MODELTRANSLATION_TRANSLATION_FILES += (settings.MODELTRANSLATION_TRANSLATION_REGISTRY,)
settings.MODELTRANSLATION_TRANSLATION_REGISTRY = 'modeltranslation_wrapper.translation_autodiscover'


# Patch Manager
from modeltranslation import translator


class TranslatorWithManager(translator.Translator):
    """Patches registered objects to have MultilingualManager"""

    def __init__(self, prev_registry=None):
        super(TranslatorWithManager, self).__init__()
        if prev_registry is not None:
            self._registry = prev_registry

    def register(self, model_or_iterable, translation_opts, **options):
        from modeltranslation_wrapper.manager import MultilingualManager
        super(TranslatorWithManager, self).register(model_or_iterable, translation_opts, **options)
        if isinstance(model_or_iterable, ModelBase):
            model_or_iterable = [model_or_iterable]
        for model in model_or_iterable:
            if not hasattr(model, 'objects'):
                continue
            current_manager = model.objects
            if current_manager.__class__ is Manager:
                current_manager.__class__ = MultilingualManager
            else:
                class NewMultilingualManager(current_manager.__class__, MultilingualManager):
                    pass
                current_manager.__class__ = NewMultilingualManager

translator.translator = TranslatorWithManager(translator.translator._registry)
