from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from notes.models import Note

User = get_user_model()


class NotesTests(TestCase):
    """
    Тесты для работы с заметками, включая создание,
    редактирование и отображение списка заметок.
    """

    @classmethod
    def setUpTestData(cls):
        """Создаёт тестовых пользователей и заметки для тестов."""
        cls.user1 = User.objects.create_user(
            username='user1',
            password='pass1'
        )
        cls.user2 = User.objects.create_user(
            username='user2',
            password='pass2'
        )
        cls.note1 = Note.objects.create(
            title='Note 1',
            text='Text 1',
            author=cls.user1
        )
        cls.note2 = Note.objects.create(
            title='Note 2',
            text='Text 2',
            author=cls.user2
        )

    def test_notes_list_only_user_notes(self):
        """
        Проверяет, что авторизованный пользователь видит только свои заметки
        на странице списка заметок.
        """
        self.client.login(username='user1', password='pass1')
        response = self.client.get(reverse('notes:list'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(
            response.context['object_list'],
            [repr(self.note1)],
            transform=repr
        )

    def test_create_note_form_in_context(self):
        """Проверяет, что на странице создания заметки передаётся форма."""
        self.client.login(username='user1', password='pass1')
        response = self.client.get(reverse('notes:add'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        self.assertContains(response, '<form')

    def test_update_note_form_in_context(self):
        """
        Проверяет, что на странице редактирования заметки передаётся форма
        и что другой пользователь не может редактировать чужую заметку.
        """
        self.client.login(username='user1', password='pass1')
        response = self.client.get(
            reverse('notes:edit', args=[self.note1.slug])
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        self.assertContains(response, '<form')

        self.client.login(username='user2', password='pass2')
        response = self.client.get(
            reverse('notes:edit', args=[self.note1.slug])
        )
        self.assertEqual(response.status_code, 404)


class NoteAccessTest(TestCase):
    """
    Тесты для проверки доступа к страницам заметок
    для анонимных пользователей.
    """

    def setUp(self):
        """Создаёт тестового пользователя и заметку для тестов."""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )
        self.note = Note.objects.create(
            title='Test Note',
            text='Test content',
            author=self.user,
            slug='test-note'
        )

    def test_notes_page_redirects_anonymous_user(self):
        """
        Проверяет, что анонимный пользователь перенаправляется на страницу
        логина при попытке доступа к странице списка заметок.
        """
        response = self.client.get(reverse('notes:list'))
        self.assertRedirects(response, '/auth/login/?next=/notes/')

    def test_add_page_redirects_anonymous_user(self):
        """
        Проверяет, что анонимный пользователь перенаправляется на страницу
        логина при попытке доступа к странице добавления заметки.
        """
        response = self.client.get(reverse('notes:add'))
        self.assertRedirects(response, '/auth/login/?next=/add/')

    def test_note_detail_redirects_anonymous_user(self):
        """
        Проверяет, что анонимный пользователь перенаправляется на страницу
        логина при попытке доступа к отдельной заметке.
        """
        response = self.client.get(
            reverse('notes:detail', args=[self.note.slug])
        )
        self.assertRedirects
        (response, f'/auth/login/?next=/note/{self.note.slug}/'
         )

    def test_edit_page_redirects_anonymous_user(self):
        """
        Проверяет, что анонимный пользователь перенаправляется на страницу
        логина при попытке доступа к странице редактирования заметки.
        """
        response = self.client.get(
            reverse('notes:edit', args=[self.note.slug])
        )
        self.assertRedirects(
            response, f'/auth/login/?next=/edit/{self.note.slug}/'
        )

    def test_delete_page_redirects_anonymous_user(self):
        """
        Проверяет, что анонимный пользователь перенаправляется на страницу
        логина при попытке доступа к странице удаления заметки.
        """
        response = self.client.get(
            reverse('notes:delete', args=[self.note.slug])
        )
        self.assertRedirects(
            response, f'/auth/login/?next=/delete/{self.note.slug}/'
        )

    def test_success_page_redirects_anonymous_user(self):
        """
        Проверяет, что анонимный пользователь перенаправляется на страницу
        логина при попытке доступа к странице успешного добавления заметки.
        """
        response = self.client.get(reverse('notes:success'))
        self.assertRedirects(response, '/auth/login/?next=/done/')
