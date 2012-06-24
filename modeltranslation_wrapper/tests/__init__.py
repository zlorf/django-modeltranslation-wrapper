from copy import copy

from django.db import models
from django.db.models.loading import AppCache
from django.test import TestCase
from django.test.utils import override_settings
from django.utils.translation import activate, get_language, deactivate
from django.utils.datastructures import SortedDict

from modeltranslation_wrapper.translation_autodiscover import autodiscover
from modeltranslation_wrapper.tests.settings import SETTINGS


@override_settings(**SETTINGS)
class MyTestCase(TestCase):
    cache = AppCache()

    def clear_cache(self):
        """
        It is necessary to clear cache - otherwise model reloading won't
        recreate models, but just use old ones.
        """
        self.cache.app_store = SortedDict()
        self.cache.app_models = SortedDict()
        self.cache.app_errors = {}
        self.cache.handled = {}
        self.cache.loaded = False

    def reset_cache(self):
        """
        Rebuild whole cache, import all models again
        """
        self.clear_cache()
        self.cache._populate()
        for m in self.cache.get_apps():
            reload(m)

    @classmethod
    def setUpClass(cls):
        """
        Save registry (and restore it after tests)

        It is mainly needed for not spoiling modeltranslation tests.
        But it is good to clean after yourself anyway...
        """
        super(MyTestCase, cls).setUpClass()
        from modeltranslation.translator import translator
        cls.registry_cpy = copy(translator._registry)

    @classmethod
    def tearDownClass(cls):
        from modeltranslation.translator import translator
        translator._registry = cls.registry_cpy
        super(MyTestCase, cls).tearDownClass()


class TestAutodiscover(MyTestCase):
    def tearDown(self):
        self.clear_cache()
        from test_app import models
        reload(models)  # Rollback model classes

        # Delete translation modules from import cache
        import sys
        sys.modules.pop('modeltranslation_wrapper.tests.test_app.translation', None)
        sys.modules.pop('modeltranslation_wrapper.tests.project_translation', None)

    def check_news(self):
        from test_app.models import News
        fields = dir(News())
        self.assertIn('title', fields)
        self.assertIn('title_en', fields)
        self.assertIn('title_pl', fields)
        self.assertIn('visits', fields)
        self.assertNotIn('visits_en', fields)
        self.assertNotIn('visits_pl', fields)

    def check_other(self, present=True):
        from test_app.models import Other
        fields = dir(Other())
        self.assertIn('name', fields)
        if present:
            self.assertIn('name_en', fields)
            self.assertIn('name_pl', fields)
        else:
            self.assertNotIn('name_en', fields)
            self.assertNotIn('name_pl', fields)

    def test_simple(self):
        """Check if translation is imported for installed apps."""
        autodiscover()
        self.check_news()
        self.check_other(present=False)

    @override_settings(
        MODELTRANSLATION_TRANSLATION_FILES=('modeltranslation_wrapper.tests.project_translation',)
    )
    def test_global(self):
        """Check if translation is imported for global translation file."""
        autodiscover()
        self.check_news()
        self.check_other()

    @override_settings(
        MODELTRANSLATION_TRANSLATION_FILES=('modeltranslation_wrapper.tests.test_app.translation',)
    )
    def test_duplication(self):
        """Check if there is no problem with duplicated names."""
        autodiscover()
        self.check_news()

    @override_settings(
        MODELTRANSLATION_TRANSLATION_REGISTRY='modeltranslation_wrapper.tests.project_translation'
    )
    def test_backward_compatibility(self):
        """Check if typical modeltranslation configuration is handled properly."""
        self.clear_cache()
        from modeltranslation_wrapper import models
        reload(models)  # Registry changed - need to reload to recreate wrapper configuration
        autodiscover()
        self.check_news()
        self.check_other()


class TestManager(MyTestCase):
    synced = False

    def setUp(self):
        """
        Prepare database:
            * Autodiscover
            * Call syncdb to create tables for test_app.models (since during
              default testrunner's db creation test_app was not in INSTALLED_APPS

        This must be run only once.
        """
        if not self.__class__.synced:
            sync_over = override_settings(MODELTRANSLATION_TRANSLATION_FILES=
                                          ('modeltranslation_wrapper.tests.project_translation',))
            with sync_over:
                self.reset_cache()
                autodiscover()
                from django.db import connections, DEFAULT_DB_ALIAS
                connections[DEFAULT_DB_ALIAS].creation.create_test_db(0, autoclobber=True)
                self.__class__.synced = True

    def test_settings(self):
        """Test if settings are correct and everything loaded fine."""
        from test_app.models import News
        fields = dir(News())
        self.assertIn('title', fields)
        self.assertIn('title_en', fields)
        self.assertIn('title_pl', fields)
        n = News.objects.create(title='q')  # Check if tables were created
        self.assertTrue(True)

    def test_filter_update(self):
        """Test if filtering and updating is language-aware."""
        from test_app.models import News
        n = News.objects.create(title='')
        n.title_en = 'en'
        n.title_pl = 'pl'
        n.save()

        m = News.objects.create(title='')
        m.title_en = 'title en'
        m.title_pl = 'pl'
        m.save()

        self.assertEqual('en', get_language()[:2])

        self.assertEqual(0, News.objects.filter(title='pl').count())
        self.assertEqual(1, News.objects.filter(title='en').count())
        self.assertEqual(2, News.objects.filter(title__contains='en').count())

        activate('pl')
        try:
            self.assertEqual(2, News.objects.filter(title='pl').count())
            self.assertEqual(0, News.objects.filter(title='en').count())
            # Spanning works
            self.assertEqual(2, News.objects.filter(title__endswith='l').count())

            # Still possible to use explicit language version
            self.assertEqual(1, News.objects.filter(title_en='en').count())
            self.assertEqual(2, News.objects.filter(title_en__contains='en').count())

            News.objects.update(title='new')
            n = News.objects.get(pk=n.pk)
            m = News.objects.get(pk=m.pk)
            self.assertEqual('en', n.title_en)
            self.assertEqual('new', n.title_pl)
            self.assertEqual('title en', m.title_en)
            self.assertEqual('new', m.title_pl)
        finally:
            deactivate()

    def test_custom_manager(self):
        """Test if user-defined manager is still working"""
        from test_app.models import Other
        n = Other.objects.create(name='')
        n.name_en = 'enigma'
        n.name_pl = 'foo'
        n.save()

        m = Other.objects.create(name='')
        m.name_en = 'enigma'
        m.name_pl = 'bar'
        m.save()

        self.assertEqual('en', get_language()[:2])

        # Custom method
        self.assertEqual('bar', Other.objects.foo())

        # Ensure that get_query_set is working!
        self.assertEqual(2, Other.objects.count())

        activate('pl')
        try:
            self.assertEqual(1, Other.objects.count())
        finally:
            deactivate()

    def test_creation(self):
        """Test if language fields are populated with default value on creation."""
        from test_app.models import News
        n = News.objects.create(title='foo', _populate=True)
        self.assertEqual('foo', n.title_en)
        self.assertEqual('foo', n.title_pl)
        self.assertEqual('foo', n.title)

        # You can specify some language...
        n = News.objects.create(title='foo', title_pl='bar', _populate=True)
        self.assertEqual('foo', n.title_en)
        self.assertEqual('bar', n.title_pl)
        self.assertEqual('foo', n.title)

        # ... and remember that still bare attribute points to current language
        n = News.objects.create(title='foo', title_en='bar', _populate=True)
        self.assertEqual('bar', n.title_en)
        self.assertEqual('foo', n.title_pl)
        self.assertEqual('bar', n.title)
        activate('pl')
        try:
            self.assertEqual('foo', n.title)
        finally:
            deactivate()

        # This feature (for backward-compatibility) require _populate keyword...
        n = News.objects.create(title='foo')
        self.assertEqual(None, n.title_en)
        self.assertEqual(None, n.title_pl)
        self.assertEqual('foo', n.title)

        # ... or MODELTRANSLATION_AUTO_POPULATE setting
        with override_settings(MODELTRANSLATION_AUTO_POPULATE=True):
            n = News.objects.create(title='foo')
            self.assertEqual('foo', n.title_en)
            self.assertEqual('foo', n.title_pl)
            self.assertEqual('foo', n.title)

            # _populate keyword has highest priority
            n = News.objects.create(title='foo', _populate=False)
            self.assertEqual(None, n.title_en)
            self.assertEqual(None, n.title_pl)
            self.assertEqual('foo', n.title)
