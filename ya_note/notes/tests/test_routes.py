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
        cls.one_specific_note_links = ('notes:edit',
                                       'notes:delete',
                                       'notes:detail')
        cls.other_notes_links = (
            ('notes:add', None),
            ('notes:success', None),
            ('notes:list', None)
        )

    def test_pages_availability(self):
        urls = (
            ('notes:home'),
            ('users:login'),
            ('users:logout'),
            ('users:signup'),
        )

        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_for_anonymous_client(self):
        login_url = reverse('users:login')
        for name in self.one_specific_note_links + self.other_notes_links:
            with self.subTest(name=name):
                if name in self.one_specific_note_links:
                    url = reverse(name, args=(self.notes.slug,))
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    def check_page_access(self, client, slug, expected_status):
        url = reverse('notes:edit', args=(slug,))
        response = client.get(url)
        self.assertEqual(response.status_code, expected_status)

    def test_author_can_access_edit_page(self):
        self.check_page_access(self.auth_client,
                               self.notes.slug,
                               HTTPStatus.OK)

    def test_reader_cannot_access_edit_page(self):
        self.check_page_access(self.reader_client,
                               self.notes.slug,
                               HTTPStatus.NOT_FOUND)

    def test_pages_availability_for_auth_client(self):
        for name, args in self.other_notes_links:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.auth_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
