import pytest
from datetime import datetime, timedelta

from news.models import News, Comment

from yanews import settings
from django.utils import timezone

now = timezone.now()


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author, client):
    client.force_login(author)
    return client


@pytest.fixture
def news():
    note = News.objects.create(
        title='Заголовок',
        text='Текст заметки',
        date=now
    )
    return note


@pytest.fixture
def id_for_args(news):
    return news.pk,


@pytest.fixture
def ten_news():
    today = datetime.today()
    a = News.objects.bulk_create(
        News(title=f'Новость {index}',
             text='Просто текст.',
             date=today - timedelta(days=index))
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    )
    return a


@pytest.fixture
def comments_data(author, news):
    comments = []
    for index in range(2):
        comment = Comment.objects.create(
            news=news, author=author, text=f'Текст {index}',
        )
        comment.created = now + timedelta(days=index)
        comment.save()
        comments.append(comment)

    return comments


@pytest.fixture
def admin_comment(admin_user, news):
    comment = Comment.objects.create(
        news=news, author=admin_user, text='ТекстТт',
    )
    return comment


@pytest.fixture
def id_admin_comment(admin_comment):
    return admin_comment.pk,


@pytest.fixture
def form_comment():
    return {
        'text': 'Новый текст12345555566',
    }
