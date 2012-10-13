# Patch Manager
from django.db.models.base import ModelBase
from django.db.models import Manager

from modeltranslation import translator


class TranslatorWithManager(translator.Translator):
    """Patches registered objects to have MultilingualManager"""

    def __init__(self, prev_registry=None):
        super(TranslatorWithManager, self).__init__()
        if prev_registry is not None:
            self._registry = prev_registry
            for model in self._registry.iterkeys():
                self._add_manager(model)

    def _add_manager(self, model):
        if not hasattr(model, 'objects'):
            return
        from modeltranslation_wrapper.manager import MultilingualManager
        current_manager = model.objects
        if isinstance(current_manager, MultilingualManager):
            return
        if current_manager.__class__ is Manager:
            current_manager.__class__ = MultilingualManager
        else:
            class NewMultilingualManager(current_manager.__class__, MultilingualManager):
                pass
            current_manager.__class__ = NewMultilingualManager

    def register(self, model_or_iterable, translation_opts, **options):
        super(TranslatorWithManager, self).register(model_or_iterable, translation_opts, **options)
        if isinstance(model_or_iterable, ModelBase):
            model_or_iterable = [model_or_iterable]
        for model in model_or_iterable:
            self._add_manager(model)

translator.translator = TranslatorWithManager(translator.translator._registry)
