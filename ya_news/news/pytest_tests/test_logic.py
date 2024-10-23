import pytest
from django.urls import reverse
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_cannot_post_comment(client, news):
    """
    Проверяет, что анонимные пользователи не могут оставлять
    комментарии к новости. Ожидается редирект на страницу входа
    и отсутствие новых комментариев в базе данных.
    """
    url = reverse('news:detail', kwargs={'pk': news.pk})
    response = client.post(url, data={'text': 'Test comment'})
    assert Comment.objects.count() == 0
    assert response.status_code == 302  # Редирект на страницу входа


@pytest.mark.django_db
def test_authorized_can_post_comment(auth_client, news):
    """
    Проверяет, что авторизованные пользователи могут оставлять
    комментарии к новости. Ожидается успешное создание
    комментария и редирект на страницу новости.
    """
    url = reverse('news:detail', kwargs={'pk': news.pk})
    response = auth_client.post(url, data={'text': 'Test comment'})
    assert Comment.objects.count() == 1
    assert response.status_code == 302  # Редирект на страницу новости


@pytest.mark.django_db
def test_comment_rejected_for_bad_words(auth_client, news):
    """
    Проверяет, что комментарии с недопустимыми словами
    (например, 'редиска') отклоняются. Ожидается отсутствие
    новых комментариев и сообщение об ошибке в форме.
    """
    url = reverse('news:detail', kwargs={'pk': news.pk})
    response = auth_client.post(url, data={'text': 'редиска'})
    assert Comment.objects.count() == 0
    assert 'Не ругайтесь!' in response.context['form'].errors['text']


@pytest.mark.django_db
def test_author_can_edit_delete_comment(author_client, comment):
    """
    Проверяет, что автор комментария может редактировать и
    удалять свой комментарий. Ожидается успешный редирект
    после выполнения этих действий.
    """
    edit_url = reverse('news:edit', kwargs={'pk': comment.pk})
    delete_url = reverse('news:delete', kwargs={'pk': comment.pk})
    assert author_client.post(
        edit_url, data={'text': 'Updated text'}
    ).status_code == 302
    assert author_client.post(delete_url).status_code == 302


@pytest.mark.django_db
def test_non_author_cannot_edit_delete_comment(auth_client, comment):
    """
    Проверяет, что пользователи, не являющиеся авторами комментария,
    не могут редактировать или удалять его. Ожидается статус 404
    при попытке редактирования или удаления.
    """
    edit_url = reverse('news:edit', kwargs={'pk': comment.pk})
    delete_url = reverse('news:delete', kwargs={'pk': comment.pk})
    assert auth_client.post(
        edit_url, data={'text': 'Updated text'}
    ).status_code == 404
    assert auth_client.post(delete_url).status_code == 404
