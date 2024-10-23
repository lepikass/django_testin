import pytest
from django.urls import reverse
from news.models import News, Comment
from datetime import datetime, timedelta
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
def test_homepage_news_count(client, settings):
    """
    Проверяет, что на главной странице не отображается больше
    новостей, чем задано в настройках (NEWS_COUNT_ON_HOME_PAGE).
    """
    settings.NEWS_COUNT_ON_HOME_PAGE = 10
    for i in range(15):
        News.objects.create(title=f'News {i}', text='Some text')
    url = reverse('news:home')
    response = client.get(url)
    assert len(response.context['news_list']) <= 10


def test_news_ordering(db):
    """
    Проверяет, что новости сортируются по дате в порядке
    убывания (новейшие сначала).
    """
    news1 = News.objects.create(
        title='News 1', date=datetime.today() - timedelta(days=2)
    )
    news2 = News.objects.create(
        title='News 2', date=datetime.today() - timedelta(days=1)
    )
    news3 = News.objects.create(
        title='News 3', date=datetime.today()
    )
    sorted_news = News.objects.order_by('-date')
    assert list(sorted_news) == [news3, news2, news1]


@pytest.mark.django_db
def test_comment_ordering():
    """
    Проверяет, что комментарии к новости сортируются по дате
    создания в порядке возрастания (старые комментарии первыми).
    """
    author = User.objects.create_user(username='testuser', password='password')
    news = News.objects.create(title='Test News', date=datetime.now())
    comment1 = Comment.objects.create(
        news=news, author=author,
        text='Comment 1',
        created=datetime.now() - timedelta(days=2)
    )
    comment2 = Comment.objects.create(
        news=news, author=author,
        text='Comment 2',
        created=datetime.now() - timedelta(days=1)
    )
    comment3 = Comment.objects.create(
        news=news, author=author, text='Comment 3', created=datetime.now()
    )
    sorted_comments = news.comment_set.all()
    assert list(sorted_comments) == [comment1, comment2, comment3]


@pytest.mark.django_db
def test_anonymous_user_cannot_access_comment_form(client):
    """
    Проверяет, что анонимные пользователи не могут видеть
    форму для комментариев на странице новости.
    """
    news = News.objects.create(title='Test News', date='2024-10-23')
    url = reverse('news:detail', args=[news.pk])
    response = client.get(url)
    assert response.status_code == 200
    assert 'comment_form' not in response.content.decode()


@pytest.mark.django_db
def test_authenticated_user_can_access_comment_form(client):
    """
    Проверяет, что авторизованные пользователи могут видеть
    форму для комментариев на странице новости.
    """
    user = User.objects.create_user(username='testuser', password='password')
    news = News.objects.create(title='Test News', date='2024-10-23')
    client.login(username='testuser', password='password')
    url = reverse('news:detail', args=[news.pk])
    response = client.get(url)
    assert response.status_code == 200
