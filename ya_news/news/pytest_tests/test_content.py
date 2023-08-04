import re

from django.conf import settings
from django.urls import reverse
import pytest

from news.forms import CommentForm


HOME_URL = reverse('news:home')


@pytest.mark.django_db
def test_news_count_pytest(client, ten_news):
    response = client.get(HOME_URL)
    assert 'object_list' in response.context
    object_list = response.context['object_list']
    news_count = len(object_list)
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_comments_order(client, news, comments_data):
    response = client.get(reverse('news:detail', args=(news.id,)))
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    reversed_comment_texts = [comment.text[:20]
                              for comment in reversed(all_comments)
                              ]
    reversed_comment_list_pattern = re.compile(
        r'\s*'.join(re.escape(text) for text in reversed_comment_texts)
    )
    page_content = response.content.decode('utf-8')
    assert re.search(reversed_comment_list_pattern, page_content)


@pytest.mark.django_db
def test_comments_order(client, news, comments_data):
    response = client.get(reverse('news:detail', args=(news.id,)))
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    assert all_comments[0].created < all_comments[1].created


@pytest.mark.django_db
def test_anonymous_client_has_no_form(client, news):
    response = client.get(reverse('news:detail', args=(news.id,)))
    assert 'form' not in response.context


@pytest.mark.django_db
def test_authorized_client_has_form(client, news, author_client):
    response = author_client.get(reverse('news:detail', args=(news.id,)))
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
