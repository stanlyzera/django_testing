import pytest

from django.urls import reverse

from yanews import settings

HOME_URL = reverse('news:home')


@pytest.mark.django_db
def test_news_count_pytest(client, ten_news):
    response = client.get(HOME_URL)
    object_list = response.context['object_list']
    news_count = len(object_list)
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(client, ten_news):
    response = client.get(HOME_URL)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


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
