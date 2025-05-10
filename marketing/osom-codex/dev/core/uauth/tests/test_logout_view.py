import pytest
from django.urls import reverse
from django.contrib.auth.models import User

# integration test
@pytest.mark.django_db
def test_logout(client):
    user = User.objects.create_user(username="testUser", password="p12345678")
    client.login(username="testUser", password="p12345678")
    url = reverse('core.uauth:logout')
    response = client.post(url)
    assert response.status_code == 302
