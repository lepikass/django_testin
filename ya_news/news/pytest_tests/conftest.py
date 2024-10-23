import pytest
from django.contrib.auth.models import User
from news.models import News, Comment


@pytest.fixture
def user(db):
    """Создаём тестового пользователя."""
    return User.objects.create_user(username='testuser', password='password')


@pytest.fixture
def author_user(db):
    """Создаём автора комментария."""
    return User.objects.create_user(username='author', password='password')


@pytest.fixture
def auth_client(client, user):
    """Клиент с авторизацией обычного пользователя."""
    client.login(username='testuser', password='password')
    return client


@pytest.fixture
def author_client(client, author_user):
    """Клиент с авторизацией автора комментария."""
    client.login(username='author', password='password')
    return client


@pytest.fixture
def news(db):
    """Создаём тестовую новость."""
    return News.objects.create(title='Test News', text='Some text')


@pytest.fixture
def comment(db, author_user, news):
    """Создаём комментарий от авторизованного пользователя."""
    return Comment.objects.create(
        news=news, author=author_user, text='Test comment'
    )
