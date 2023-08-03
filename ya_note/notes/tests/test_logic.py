import pytils.translit
from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import WARNING
from notes.models import Note


User = get_user_model()


class TestNotesCreation(TestCase):
    NOTE_TEXT = 'Текст'
    NOTE_TITLE = 'Заголовок'

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='Коля')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.form_data = {'text': cls.NOTE_TEXT, 'title': cls.NOTE_TITLE}
        cls.note = Note.objects.create(
            title='Заголовок 01', text='Текст 01',
            slug='eto-slug', author=cls.user
        )
        cls.add_url = reverse('notes:add')
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.success_url = reverse('notes:success')

    def test_user_can_create_note(self):
        response = self.auth_client.post(self.add_url, data=self.form_data)
        self.assertRedirects(response, self.success_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 2)
        note = Note.objects.last()
        self.assertEqual(note.text, self.NOTE_TEXT)
        self.assertEqual(note.title, self.NOTE_TITLE)

    def test_anonymous_user_cant_create_note(self):
        self.client.post(self.add_url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_user_cant_use_same_slug(self):
        same_slug_data = {'text': 'Другой текст',
                          'title': 'Другой заголовок', 'slug': 'eto-slug'
                          }
        response = self.auth_client.post(self.add_url, data=same_slug_data)
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors=same_slug_data['slug'] + WARNING
        )
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_author_can_delete_comment(self):
        response = self.auth_client.delete(self.delete_url)
        self.assertRedirects(response, self.success_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_user_cant_delete_note_of_another_user(self):
        response = self.reader_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_author_can_edit_comment(self):
        response = self.auth_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, self.success_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_user_cant_edit_note_of_another_user(self):
        response = self.reader_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_auto_generate_slug(self):
        self.auth_client.post(self.add_url, data=self.form_data, follow=True)
        self.assertTrue(Note.objects.filter(
            title=self.NOTE_TITLE, text=self.NOTE_TEXT).exists()
        )
        new_note = Note.objects.get(title=self.NOTE_TITLE, text=self.NOTE_TEXT)
        expected_slug = pytils.translit.slugify(self.NOTE_TITLE)
        self.assertEqual(new_note.slug, expected_slug)
