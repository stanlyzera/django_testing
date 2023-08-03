from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.author)
        cls.reader = User.objects.create(username='Читатель простой')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.notes = Note.objects.create(
            author=cls.author,
            title='Заголовок',
            text='Текст записки',
            slug='some-unique-slug',
        )

    def test_pages_availability(self):
        urls = (
            ('notes:home', None),
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None),
        )

        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_for_anonymous_client(self):
        login_url = reverse('users:login')
        for name in ('notes:edit', 'notes:delete', 'notes:add',
                     'notes:list', 'notes:detail', 'notes:success'
                     ):
            with self.subTest(name=name):
                if name in ('notes:edit', 'notes:delete', 'notes:detail'):
                    url = reverse(name, args=(self.notes.slug,))
                else:
                    url = reverse(name)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_edit_pages_availability_for_author_and_reader(self):
        for name in ('notes:edit', 'notes:delete', 'notes:detail'):
            with self.subTest(name=name):
                url = reverse(name, args=(self.notes.slug,))
                response = self.auth_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                response2 = self.reader_client.get(url)
                self.assertEqual(response2.status_code, HTTPStatus.NOT_FOUND)

    def test_pages_availability_for_auth_client(self):
        for name in ('notes:add', 'notes:success', 'notes:list'):
            with self.subTest(name=name):
                url = reverse(name)
                response = self.auth_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
