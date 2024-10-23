import pytest
from django.urls import reverse
from news.models import News, Comment


@pytest.mark.django_db
def test_homepage_accessible(client):
    """
    Проверяет, что главная страница доступна для пользователей.
    Ожидается статус 200.
    """
    url = reverse('news:home')
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_news_detail_accessible(client):
    """
    Проверяет, что страница подробностей новости доступна для
    пользователей. Ожидается статус 200.
    """
    news = News.objects.create(title='Test', text='Test text')
    url = reverse('news:detail', kwargs={'pk': news.pk})
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_comment_edit_delete_author_access(author_client, comment):
    """
    Проверяет, что автор комментария может получить доступ
    к страницам редактирования и удаления своего комментария.
    Ожидается статус 200 для обеих страниц.
    """
    edit_url = reverse('news:edit', kwargs={'pk': comment.pk})
    delete_url = reverse('news:delete', kwargs={'pk': comment.pk})
    assert author_client.get(edit_url).status_code == 200
    assert author_client.get(delete_url).status_code == 200


@pytest.mark.django_db
def test_comment_edit_delete_redirect_anonymous(client, comment):
    """
    Проверяет, что анонимные пользователи перенаправляются на
    страницу входа при попытке доступа к страницам редактирования
    и удаления комментариев. Ожидается статус 302 и URL
    перенаправления на страницу входа.
    """
    edit_url = reverse('news:edit', kwargs={'pk': comment.pk})
    delete_url = reverse('news:delete', kwargs={'pk': comment.pk})
    login_url = reverse('users:login')
    response = client.get(edit_url)
    assert response.status_code == 302
    assert response.url.startswith(login_url)
    response = client.get(delete_url)
    assert response.status_code == 302
    assert response.url.startswith(login_url)


@pytest.mark.django_db
def test_comment_edit_delete_404_non_author(auth_client, comment):
    """
    Проверяет, что пользователи, не являющиеся авторами комментария,
    получают статус 404 при попытке доступа к странице редактирования
    комментария. Ожидается статус 404.
    """
    url = reverse('news:edit', kwargs={'pk': comment.pk})
    response = auth_client.get(url)
    assert response.status_code == 404


@pytest.mark.django_db
def test_auth_pages_accessible_anonymous(client):
    """
    Проверяет, что страницы регистрации, входа и выхода доступны
    для анонимных пользователей. Ожидается статус 200 для всех
    страниц.
    """
    signup_url = reverse('users:signup')
    login_url = reverse('users:login')
    logout_url = reverse('users:logout')
    assert client.get(signup_url).status_code == 200
    assert client.get(login_url).status_code == 200
    assert client.get(logout_url).status_code == 200
