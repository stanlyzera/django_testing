from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note


User = get_user_model()


class TestContent(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Человек')
        cls.other_author = User.objects.create(username='Человек1')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.author)
        cls.list_notes_url = reverse('notes:list')
        cls.notes = Note.objects.bulk_create(
            Note(title=f'Тестовая записка {index}',
                 text=f'Тестовый текст {index}',
                 author=cls.author,
                 slug=f'slug-{index}'
                 )
            for index in range(3)
        )
        cls.other_note = Note.objects.create(
            title='title', text='t', author=cls.other_author
        )

    def test_individual_note_in_context(self):
        response = self.auth_client.get(self.list_notes_url)
        self.assertIn('object_list', response.context)
        object_list = response.context['object_list']
        for note in self.notes:
            self.assertTrue(
                any(
                    obj.title == note.title
                    and obj.text == note.text
                    and obj.author == note.author
                    and obj.slug == note.slug
                    for obj in object_list
                )
            )

    def test_authorized_client_has_add_form(self):
        urls = (
            ('notes:edit', (self.notes[0].slug,)),
            ('notes:add', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.auth_client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)

    def test_others_note_on_page_check(self):
        response = self.auth_client.get(self.list_notes_url)
        self.assertIn('object_list', response.context)
        object_list = response.context['object_list']
        self.assertNotIn(self.notes[0], object_list)
