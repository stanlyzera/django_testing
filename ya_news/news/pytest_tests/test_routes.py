from http import HTTPStatus

from django.urls import reverse
import pytest
from pytest_django.asserts import assertRedirects


URLS_TO_TEST = (
    ('news:edit', pytest.lazy_fixture('id_admin_comment')),
    ('news:delete', pytest.lazy_fixture('id_admin_comment')),
)


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, args',
    (
        ('news:home', None),
        ('news:detail', pytest.lazy_fixture('id_for_args')),
        ('users:login', None),
        ('users:logout', None),
        ('users:signup', None),
    ),
)
def test_pages_availability(client, name, args):
    url = reverse(name, args=args)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, args',
    (
        ('news:edit', pytest.lazy_fixture('id_for_args')),
        ('news:delete', pytest.lazy_fixture('id_for_args')),
    ),
)
def test_redirect_for_anonymous_client(client, name, args):
    login_url = reverse('users:login')
    url = reverse(name, args=args)
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)


@pytest.mark.parametrize('name, args', URLS_TO_TEST)
def test_other_author_cant_update_comments(author_client, admin_client,
                                           name, args):
    url = reverse(name, args=args)
    response = author_client.get(url)
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.parametrize('name, args', URLS_TO_TEST)
def test_author_can_update_comment(admin_client, name, args):
    url = reverse(name, args=args)
    response = admin_client.get(url)
    assert response.status_code == HTTPStatus.OK
