from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from notes.models import Note

User = get_user_model()


class NoteLogicTests(TestCase):
    """Тесты для проверки логики работы с заметками."""

    @classmethod
    def setUpTestData(cls):
        """Создаёт тестового пользователя для последующих тестов."""
        cls.user1 = User.objects.create_user(
            username='user1', password='pass1'
        )

    def test_authenticated_user_can_create_note(self):
        """Проверяет, что авторизованный пользователь может создать заметку."""
        self.client.login(username='user1', password='pass1')
        response = self.client.post(reverse('notes:add'), {
            'title': 'New Note',
            'text': 'This is a new note',
        })
        self.assertEqual(response.status_code, 302)

        new_note = Note.objects.get(title='New Note')
        self.assertEqual(new_note.author, self.user1)

    def test_anonymous_user_cannot_create_note(self):
        """Проверяет, что анонимный пользователь не может создать заметку."""
        response = self.client.post(reverse('notes:add'), {
            'title': 'Anonymous Note',
            'text': 'This should not work',
        })
        self.assertRedirects(response, '/auth/login/?next=/add/')
        self.assertFalse(Note.objects.filter(title='Anonymous Note').exists())

    def test_slug_must_be_unique(self):
        """Проверяет, что slug должен быть уникальным при создании заметки."""
        self.client.login(username='user1', password='pass1')

        response = self.client.post(reverse('notes:add'), {
            'title': 'First Note',
            'text': 'This is the first note',
            'slug': 'unique-slug',
        })
        self.assertEqual(response.status_code, 302)

        response = self.client.post(reverse('notes:add'), {
            'title': 'Second Note',
            'text': 'This is the second note',
            'slug': 'unique-slug',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response, 'form', 'slug',
            'unique-slug - такой slug уже существует, '
            'придумайте уникальное значение!'
        )
        self.assertEqual(Note.objects.filter(slug='unique-slug').count(), 1)
