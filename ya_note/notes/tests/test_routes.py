from django.test import TestCase
from django.urls import reverse
from notes.models import Note
from django.contrib.auth.models import User


class NoteRoutesTest(TestCase):
    """Тесты для проверки маршрутизации и доступа к страницам заметок."""

    def setUp(self):
        """Создаёт тестовых пользователей и заметку для тестов."""
        self.author = User.objects.create_user(
            username='author', password='password'
        )
        self.other_user = User.objects.create_user(
            username='other', password='password'
        )
        self.note = Note.objects.create(
            title='Test Note',
            text='This is a test note.',
            author=self.author
        )

    def test_home_page_access(self):
        """Проверяет, что главная страница доступна анонимному пользователю."""
        response = self.client.get(reverse('notes:home'))
        self.assertEqual(response.status_code, 200)

    def test_notes_list_access_authenticated_user(self):
        """Проверяет, что страница со списком заметок доступна
        аутентифицированному пользователю.
        """
        self.client.login(username='author', password='password')
        response = self.client.get(reverse('notes:list'))
        self.assertEqual(response.status_code, 200)

    def test_done_page_access_authenticated_user(self):
        """Проверяет, что страница успешного добавления заметки доступна
        аутентифицированному пользователю.
        """
        self.client.login(username='author', password='password')
        response = self.client.get(reverse('notes:success'))
        self.assertEqual(response.status_code, 200)

    def test_add_note_access_authenticated_user(self):
        """Проверяет, что страница добавления новой заметки доступна
        аутентифицированному пользователю.
        """
        self.client.login(username='author', password='password')
        response = self.client.get(reverse('notes:add'))
        self.assertEqual(response.status_code, 200)

    def test_note_detail_access_as_author(self):
        """Проверяет, что страница отдельной заметки доступна автору."""
        self.client.login(username='author', password='password')
        response = self.client.get(
            reverse('notes:detail', args=[self.note.slug])
        )
        self.assertEqual(response.status_code, 200)

    def test_note_detail_access_as_other_user(self):
        """Проверяет, что страница отдельной заметки недоступна для
        другого пользователя.
        """
        self.client.login(username='other', password='password')
        response = self.client.get(
            reverse('notes:detail', args=[self.note.slug])
        )
        self.assertEqual(response.status_code, 404)

    def test_edit_note_access_as_author(self):
        """Проверяет, что страница редактирования доступна автору."""
        self.client.login(username='author', password='password')
        response = self.client.get(
            reverse('notes:edit', args=[self.note.slug])
        )
        self.assertEqual(response.status_code, 200)

    def test_edit_note_access_as_other_user(self):
        """Проверяет, что страница редактирования недоступна для
        другого пользователя.
        """
        self.client.login(username='other', password='password')
        response = self.client.get(
            reverse('notes:edit', args=[self.note.slug])
        )
        self.assertEqual(response.status_code, 404)

    def test_delete_note_access_as_author(self):
        """Проверяет, что страница удаления доступна автору."""
        self.client.login(username='author', password='password')
        response = self.client.get(
            reverse('notes:delete', args=[self.note.slug])
        )
        self.assertEqual(response.status_code, 200)

    def test_delete_note_access_as_other_user(self):
        """Проверяет, что страница удаления недоступна для другого
        пользователя.
        """
        self.client.login(username='other', password='password')
        response = self.client.get(
            reverse('notes:delete', args=[self.note.slug])
        )
        self.assertEqual(response.status_code, 404)

    def test_redirect_anonymous_user_to_login(self):
        """Проверяет перенаправление анонимного пользователя на страницу
        логина.
        """
        response = self.client.get(reverse('notes:list'))
        self.assertRedirects(response, '/auth/login/?next=/notes/')

        response = self.client.get(reverse('notes:success'))
        self.assertRedirects(response, '/auth/login/?next=/done/')

        response = self.client.get(reverse('notes:add'))
        self.assertRedirects(response, '/auth/login/?next=/add/')

        response = self.client.get(
            reverse('notes:detail', args=[self.note.slug])
        )
        self.assertRedirects(response,
                             f'/auth/login/?next=/note/{self.note.slug}/')

        response = self.client.get(
            reverse('notes:edit', args=[self.note.slug])
        )
        self.assertRedirects(response,
                             f'/auth/login/?next=/edit/{self.note.slug}/')

        response = self.client.get(
            reverse('notes:delete', args=[self.note.slug])
        )
        self.assertRedirects(response,
                             f'/auth/login/?next=/delete/{self.note.slug}/')

    def test_registration_login_logout_access(self):
        """Проверяет доступность страниц регистрации, входа и выхода для
        всех пользователей.
        """
        response = self.client.get(reverse('users:signup'))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('users:login'))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('users:logout'))
        self.assertEqual(response.status_code, 200)
