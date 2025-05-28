import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from core.uauth.models import UserProfile

@pytest.mark.django_db
def test_login_get(client):
    url = reverse('core.uauth:login')
    response = client.get(url)
    assert response.status_code == 200
    assert b"Login" in response.content

@pytest.mark.django_db
def test_login_invalid_credentials(client):
    url = reverse('core.uauth:login')
    response = client.post(url, {"username":"no","password":"no"})
    assert response.status_code == 302

# integration test
@pytest.mark.django_db
def test_login_unverified_email(client):
    user = User.objects.create_user(username="user1", email="user1@user.com", password="pass1234")
    UserProfile.objects.create(user=user, email_verified=False)
    url = reverse('core.uauth:login')
    response = client.post(url, {"username":"user1","password":"pass1234"})
    assert response.status_code == 302

# integration test
@pytest.mark.django_db
def test_login_success(client):
    user = User.objects.create_user(username="ok", email="ok@ok.com", password="pass1234")
    UserProfile.objects.create(user=user, email_verified=True)
    url = reverse('core.uauth:login')
    response = client.post(url, {"username":"ok","password":"pass1234"})
    assert response.status_code == 302

# integration test
@pytest.mark.django_db
def test_login_with_email(client):
    user = User.objects.create_user(username="mail", email="mail@mail.com", password="pass1234")
    UserProfile.objects.create(user=user, email_verified=True)
    url = reverse('core.uauth:login')
    response = client.post(url, {"username":"mail@mail.com","password":"pass1234"})
    assert response.status_code == 302