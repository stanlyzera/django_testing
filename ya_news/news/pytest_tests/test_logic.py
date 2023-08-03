import pytest

from django.urls import reverse

from news.models import Comment
from news.forms import BAD_WORDS, WARNING


@pytest.mark.django_db
def test_anonymous_cant_create_comment(client, form_comment, news):
    url = reverse('news:detail', args=(news.id,))
    client.post(url, data=form_comment)
    assert Comment.objects.count() == 0


def test_auth_can_create_comment(admin_client, form_comment, news):
    url = reverse('news:detail', kwargs={'pk': news.id})
    admin_client.post(url, data=form_comment)
    assert Comment.objects.count() == 1


@pytest.mark.django_db
def test_user_cant_create_comment_with_badword(author_client, news):
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    url = reverse('news:detail', args=(news.id,))
    response = author_client.post(url, data=bad_words_data)
    assert WARNING in response.content.decode()
    assert Comment.objects.filter(news=news).count() == 0


@pytest.mark.django_db
def test_auth_can_edit_comment(
    admin_client, form_comment, admin_comment, id_admin_comment
):
    url = reverse('news:edit', args=(id_admin_comment))
    admin_client.post(url, form_comment)
    admin_comment.refresh_from_db()
    assert admin_comment.text == form_comment['text']


@pytest.mark.django_db
def test_auth_cant_edit_other_comment(
    author_client, form_comment, admin_comment, id_admin_comment
):
    url = reverse('news:edit', args=(id_admin_comment))
    author_client.post(url, form_comment)
    admin_comment.refresh_from_db()
    assert admin_comment.text != form_comment['text']
