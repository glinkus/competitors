import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from core.uauth.models import UserProfile

@pytest.mark.django_db
def test_register_get(client):
    url = reverse('core.uauth:register')
    response = client.get(url)
    assert response.status_code == 200
    assert b"Register" in response.content

# integration test
@pytest.mark.django_db
def test_register_duplicate_username(client):
    User.objects.create_user(username="exists", email="a@b.com", password="pass1234")
    url = reverse('core.uauth:register')
    data = {"first_name":"A","last_name":"B","username":"exists","email":"new@b.com","password":"pass1234"}
    response = client.post(url, data)
    assert response.status_code == 302
    assert b"Username already taken" in client.get(response.url).content

# integration test
@pytest.mark.django_db
def test_register_success(client):
    url = reverse('core.uauth:register')
    data = {"first_name":"vardenis","last_name":"pavardenis","username":"vardpav","email":"vardpav@gmail.com","password":"lopas1234"}
    response = client.post(url, data)
    assert response.status_code == 302
    assert User.objects.filter(username="vardpav").exists()
    user = User.objects.get(username="vardpav")
    assert UserProfile.objects.filter(user=user).exists()
