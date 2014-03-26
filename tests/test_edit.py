from __future__ import unicode_literals

from unittest import expectedFailure

# from django.core.exceptions import ImproperlyConfigured
# from django.core.urlresolvers import reverse
# from django import forms
# from django.test import TestCase
# from django.test.client import RequestFactory
# from django.views.generic.base import View
# from django.views.generic.edit import FormMixin, ModelFormMixin, CreateView
import unittest
from pyramid.testing import DummyRequest
from webob.multidict import MultiDict
from wtforms_alchemy import ModelForm
from pyramid_views.utils import ImproperlyConfigured

from pyramid_views.views.base import View
from pyramid_views.views.edit import FormMixin, ModelFormMixin, CreateView

from . import views
from .models import Artist, Author
from tests.base import BaseTest, session
from tests.forms import AuthorForm


class FormMixinTests(BaseTest):
    def test_initial_data(self):
        """ Test instance independence of initial data dict (see #16138) """
        initial_1 = FormMixin().get_initial()
        initial_1['foo'] = 'bar'
        initial_2 = FormMixin().get_initial()
        self.assertNotEqual(initial_1, initial_2)

    def test_get_prefix(self):
        """ Test prefix can be set (see #18872) """
        test_string = 'test'

        get_request = DummyRequest()

        class TestFormMixin(FormMixin):
            request = get_request

        default_kwargs = TestFormMixin().get_form_kwargs()
        self.assertEqual(None, default_kwargs.get('prefix'))

        set_mixin = TestFormMixin()
        set_mixin.prefix = test_string
        set_kwargs = set_mixin.get_form_kwargs()
        self.assertEqual(test_string, set_kwargs.get('prefix'))


class BasicFormTests(BaseTest):
    urls = 'generic_views.urls'

    def test_post_data(self):
        view = views.ContactView.as_view()
        res = view(DummyRequest(method='POST', params=MultiDict(name='Me', message='Hello')))
        self.assertEqual(res.status_code, 302)
        self.assertEqual(res.headers['Location'], '/list/authors/')


class ModelFormMixinTests(BaseTest):
    def test_get_form(self):
        form_class = views.AuthorGetQuerySetFormView().get_form_class()
        self.assertEqual(form_class.Meta.model, Author)

    def test_get_form_checks_for_object(self):
        mixin = ModelFormMixin()
        mixin.request = DummyRequest()
        self.assertEqual({'data': {}, 'prefix': ''},
                         mixin.get_form_kwargs())


class CreateViewTests(BaseTest):
    urls = 'generic_views.urls'

    def test_create(self):
        view = views.AuthorCreate.as_view()
        res = view(DummyRequest())
        self.assertEqual(res.status_code, 200)
        self.assertIsInstance(res.context['form'], ModelForm)
        self.assertIsInstance(res.context['view'], View)
        self.assertFalse('object' in res.context)
        self.assertFalse('author' in res.context)
        self.assertTemplateUsed(res, 'tests:templates/author_form.html')

        res = view(DummyRequest(
            method='POST',
            params=MultiDict({'name': 'Randall Munroe', 'slug': 'randall-munroe'})
        ))
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, '/list/authors/')
        self.assertQuerysetEqual(session.query(Author).all(), ['<Author: Randall Munroe>'])

    def test_create_invalid(self):
        view = views.AuthorCreate.as_view()
        res = view(DummyRequest(
            method='POST',
            params=MultiDict({'name': 'A' * 101, 'slug': 'randall-munroe'})
        ))
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, 'tests:templates/author_form.html')
        self.assertEqual(len(res.context['form'].errors), 1)
        self.assertEqual(session.query(Author).count(), 0)

    def test_create_with_object_url(self):
        view = views.ArtistCreate.as_view()
        res = view(DummyRequest(
            method='POST',
            params=MultiDict({'name': 'Rene Magritte'})
        ))
        self.assertEqual(res.status_code, 302)
        artist = session.query(Artist).filter(Artist.name=='Rene Magritte').one()
        self.assertRedirects(res, '/detail/artist/%d/' % artist.id)
        self.assertQuerysetEqual(session.query(Artist).all(), ['<Artist: Rene Magritte>'])

    def test_create_with_redirect(self):
        view = views.NaiveAuthorCreate.as_view(success_url='/edit/authors/create/')
        res = view(DummyRequest(
            method='POST',
            params=MultiDict({'name': 'Randall Munroe', 'slug': 'randall-munroe'})
        ))
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, '/edit/authors/create/')
        self.assertQuerysetEqual(session.query(Author).all(), ['<Author: Randall Munroe>'])

    def test_create_with_interpolated_redirect(self):
        view = views.NaiveAuthorCreate.as_view(success_url='/edit/author/%(id)d/update/')
        res = view(DummyRequest(
            method='POST',
            params=MultiDict({'name': 'Randall Munroe', 'slug': 'randall-munroe'})
        ))
        self.assertQuerysetEqual(session.query(Author).all(), ['<Author: Randall Munroe>'])
        self.assertEqual(res.status_code, 302)
        id = session.query(Author).all()[0].id
        self.assertRedirects(res, '/edit/author/%d/update/' % id)

    def test_create_with_special_properties(self):
        view = views.SpecializedAuthorCreate.as_view()
        res = view(DummyRequest())
        self.assertEqual(res.status_code, 200)
        self.assertIsInstance(res.context['form'], AuthorForm)
        self.assertFalse('object' in res.context)
        self.assertFalse('author' in res.context)
        self.assertTemplateUsed(res, 'tests:templates/form.html')

        res = view(DummyRequest(
            method='POST',
            params=MultiDict({'name': 'Randall Munroe', 'slug': 'randall-munroe'})
        ))
        self.assertEqual(res.status_code, 302)
        obj = session.query(Author).filter(Author.slug=='randall-munroe').one()
        self.assertRedirects(res, '/detail/author/%s/' % obj.id)
        self.assertQuerysetEqual(session.query(Author).all(), ['<Author: Randall Munroe>'])

    def test_create_without_redirect(self):
        view = views.NaiveAuthorCreate.as_view()
        request = DummyRequest(
            method='POST',
            params=MultiDict({'name': 'Randall Munroe', 'slug': 'randall-munroe'})
        )
        # Should raise exception -- No redirect URL provided, and no get_absolute_url provided
        self.assertRaises(ImproperlyConfigured, view, request)

    @unittest.skip('login_required() decorator is part of Django, so skipping this feature for now')
    def test_create_restricted(self):
        view = views.AuthorCreateRestricted.as_view()
        res = view(DummyRequest(
            method='POST',
            params=MultiDict({'name': 'Randall Munroe', 'slug': 'randall-munroe'})
        ))

        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, 'http://testserver/accounts/login/?next=/edit/authors/create/restricted/')

    def test_create_view_with_restricted_fields(self):

        class MyCreateView(CreateView):
            model = Author
            fields = ['name']
        form_class = MyCreateView().get_form_class()
        fields = [field.name for field in form_class()]
        self.assertEqual(fields, ['name'])

    def test_create_view_all_fields(self):
        class MyCreateView(CreateView):
            model = Author
            # Whereas in Django one uses '__all__', wtforms_alchemy
            # supports a None value and intelligently determining fields to use
            # fields = '__all__'
        form_class = MyCreateView().get_form_class()
        fields = [field.name for field in form_class()]
        self.assertEqual(fields, ['name', 'slug'])

    @unittest.skip('Omitting the "fields" attribute is actually supported')
    def test_create_view_without_explicit_fields(self):
        class MyCreateView(CreateView):
            model = Author

        message = (
            "Using ModelFormMixin (base class of MyCreateView) without the "
            "'fields' attribute is prohibited."
        )
        with self.assertRaisesMessage(ImproperlyConfigured, message):
            MyCreateView().get_form_class()


class UpdateViewTests(BaseTest):
    urls = 'generic_views.urls'

    def test_update_post(self):
        a = Author.objects.create(
            name='Randall Munroe',
            slug='randall-munroe',
        )
        res = self.client.get('/edit/author/%d/update/' % a.pk)
        self.assertEqual(res.status_code, 200)
        self.assertIsInstance(res.context['form'], forms.ModelForm)
        self.assertEqual(res.context['object'], Author.objects.get(pk=a.pk))
        self.assertEqual(res.context['author'], Author.objects.get(pk=a.pk))
        self.assertTemplateUsed(res, 'tests:templates/author_form.html')

        # Modification with both POST and PUT (browser compatible)
        res = self.client.post('/edit/author/%d/update/' % a.pk,
                        {'name': 'Randall Munroe (xkcd)', 'slug': 'randall-munroe'})
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, 'http://testserver/list/authors/')
        self.assertQuerysetEqual(session.query(Author).all(), ['<Author: Randall Munroe (xkcd)>'])

    @expectedFailure
    def test_update_put(self):
        a = Author.objects.create(
            name='Randall Munroe',
            slug='randall-munroe',
        )
        res = self.client.get('/edit/author/%d/update/' % a.pk)
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, 'tests:templates/author_form.html')

        res = self.client.put('/edit/author/%d/update/' % a.pk,
                        {'name': 'Randall Munroe (author of xkcd)', 'slug': 'randall-munroe'})
        # Here is the expected failure. PUT data are not processed in any special
        # way by django. So the request will equal to a POST without data, hence
        # the form will be invalid and redisplayed with errors (status code 200).
        # See also #12635
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, 'http://testserver/list/authors/')
        self.assertQuerysetEqual(session.query(Author).all(), ['<Author: Randall Munroe (author of xkcd)>'])

    def test_update_invalid(self):
        a = Author.objects.create(
            name='Randall Munroe',
            slug='randall-munroe',
        )
        res = self.client.post('/edit/author/%d/update/' % a.pk,
                        {'name': 'A' * 101, 'slug': 'randall-munroe'})
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, 'tests:templates/author_form.html')
        self.assertEqual(len(res.context['form'].errors), 1)
        self.assertQuerysetEqual(session.query(Author).all(), ['<Author: Randall Munroe>'])

    def test_update_with_object_url(self):
        a = Artist.objects.create(name='Rene Magritte')
        res = self.client.post('/edit/artists/%d/update/' % a.pk,
                        {'name': 'Rene Magritte'})
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, 'http://testserver/detail/artist/%d/' % a.pk)
        self.assertQuerysetEqual(session.query(Artist).all(), ['<Artist: Rene Magritte>'])

    def test_update_with_redirect(self):
        a = Author.objects.create(
            name='Randall Munroe',
            slug='randall-munroe',
        )
        res = self.client.post('/edit/author/%d/update/redirect/' % a.pk,
                        {'name': 'Randall Munroe (author of xkcd)', 'slug': 'randall-munroe'})
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, 'http://testserver/edit/authors/create/')
        self.assertQuerysetEqual(session.query(Author).all(), ['<Author: Randall Munroe (author of xkcd)>'])

    def test_update_with_interpolated_redirect(self):
        a = Author.objects.create(
            name='Randall Munroe',
            slug='randall-munroe',
        )
        res = self.client.post('/edit/author/%d/update/interpolate_redirect/' % a.pk,
                        {'name': 'Randall Munroe (author of xkcd)', 'slug': 'randall-munroe'})
        self.assertQuerysetEqual(session.query(Author).all(), ['<Author: Randall Munroe (author of xkcd)>'])
        self.assertEqual(res.status_code, 302)
        pk = session.query(Author).all()[0].pk
        self.assertRedirects(res, 'http://testserver/edit/author/%d/update/' % pk)

    def test_update_with_special_properties(self):
        a = Author.objects.create(
            name='Randall Munroe',
            slug='randall-munroe',
        )
        res = self.client.get('/edit/author/%d/update/special/' % a.pk)
        self.assertEqual(res.status_code, 200)
        self.assertIsInstance(res.context['form'], views.AuthorForm)
        self.assertEqual(res.context['object'], Author.objects.get(pk=a.pk))
        self.assertEqual(res.context['thingy'], Author.objects.get(pk=a.pk))
        self.assertFalse('author' in res.context)
        self.assertTemplateUsed(res, 'tests:templates/form.html')

        res = self.client.post('/edit/author/%d/update/special/' % a.pk,
                        {'name': 'Randall Munroe (author of xkcd)', 'slug': 'randall-munroe'})
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, 'http://testserver/detail/author/%d/' % a.pk)
        self.assertQuerysetEqual(session.query(Author).all(), ['<Author: Randall Munroe (author of xkcd)>'])

    def test_update_without_redirect(self):
        a = Author.objects.create(
            name='Randall Munroe',
            slug='randall-munroe',
        )
        # Should raise exception -- No redirect URL provided, and no
        # get_absolute_url provided
        with self.assertRaises(ImproperlyConfigured):
            self.client.post('/edit/author/%d/update/naive/' % a.pk,
                            {'name': 'Randall Munroe (author of xkcd)', 'slug': 'randall-munroe'})

    def test_update_get_object(self):
        a = Author.objects.create(
            pk=1,
            name='Randall Munroe',
            slug='randall-munroe',
        )
        res = self.client.get('/edit/author/update/')
        self.assertEqual(res.status_code, 200)
        self.assertIsInstance(res.context['form'], forms.ModelForm)
        self.assertIsInstance(res.context['view'], View)
        self.assertEqual(res.context['object'], Author.objects.get(pk=a.pk))
        self.assertEqual(res.context['author'], Author.objects.get(pk=a.pk))
        self.assertTemplateUsed(res, 'tests:templates/author_form.html')

        # Modification with both POST and PUT (browser compatible)
        res = self.client.post('/edit/author/update/',
                        {'name': 'Randall Munroe (xkcd)', 'slug': 'randall-munroe'})
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, 'http://testserver/list/authors/')
        self.assertQuerysetEqual(session.query(Author).all(), ['<Author: Randall Munroe (xkcd)>'])


class DeleteViewTests(BaseTest):
    urls = 'generic_views.urls'

    def test_delete_by_post(self):
        a = Author.objects.create(**{'name': 'Randall Munroe', 'slug': 'randall-munroe'})
        res = self.client.get('/edit/author/%d/delete/' % a.pk)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.context['object'], Author.objects.get(pk=a.pk))
        self.assertEqual(res.context['author'], Author.objects.get(pk=a.pk))
        self.assertTemplateUsed(res, 'tests:templates/author_confirm_delete.html')

        # Deletion with POST
        res = self.client.post('/edit/author/%d/delete/' % a.pk)
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, 'http://testserver/list/authors/')
        self.assertQuerysetEqual(session.query(Author).all(), [])

    def test_delete_by_delete(self):
        # Deletion with browser compatible DELETE method
        a = Author.objects.create(**{'name': 'Randall Munroe', 'slug': 'randall-munroe'})
        res = self.client.delete('/edit/author/%d/delete/' % a.pk)
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, 'http://testserver/list/authors/')
        self.assertQuerysetEqual(session.query(Author).all(), [])

    def test_delete_with_redirect(self):
        a = Author.objects.create(**{'name': 'Randall Munroe', 'slug': 'randall-munroe'})
        res = self.client.post('/edit/author/%d/delete/redirect/' % a.pk)
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, 'http://testserver/edit/authors/create/')
        self.assertQuerysetEqual(session.query(Author).all(), [])

    def test_delete_with_interpolated_redirect(self):
        a = Author.objects.create(**{'name': 'Randall Munroe', 'slug': 'randall-munroe'})
        res = self.client.post('/edit/author/%d/delete/interpolate_redirect/' % a.pk)
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, 'http://testserver/edit/authors/create/?deleted=%d' % a.pk)
        self.assertQuerysetEqual(session.query(Author).all(), [])

    def test_delete_with_special_properties(self):
        a = Author.objects.create(**{'name': 'Randall Munroe', 'slug': 'randall-munroe'})
        res = self.client.get('/edit/author/%d/delete/special/' % a.pk)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.context['object'], Author.objects.get(pk=a.pk))
        self.assertEqual(res.context['thingy'], Author.objects.get(pk=a.pk))
        self.assertFalse('author' in res.context)
        self.assertTemplateUsed(res, 'tests:templates/confirm_delete.html')

        res = self.client.post('/edit/author/%d/delete/special/' % a.pk)
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, 'http://testserver/list/authors/')
        self.assertQuerysetEqual(session.query(Author).all(), [])

    def test_delete_without_redirect(self):
        a = Author.objects.create(
            name='Randall Munroe',
            slug='randall-munroe',
        )
        # Should raise exception -- No redirect URL provided, and no
        # get_absolute_url provided
        with self.assertRaises(ImproperlyConfigured):
            self.client.post('/edit/author/%d/delete/naive/' % a.pk)
