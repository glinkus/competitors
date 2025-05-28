import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from core.uauth.models import UserProfile

# integration test
@pytest.mark.django_db
def test_verify_email_success(client):
    user = User.objects.create_user(username="vardas", email="vardas@gmail.com", password="ps12345678")
    profile = UserProfile.objects.create(user=user, email_verified=False)
    url = reverse('core.uauth:verify_email', kwargs={"token": profile.verification_token})
    response = client.get(url)
    assert response.status_code == 302
    profile.refresh_from_db()
    assert profile.email_verified

# integration test
@pytest.mark.django_db
def test_verify_email_invalid_token(client):
    url = reverse('core.uauth:verify_email', kwargs={"token": "00000000-0000-0000-0000-000000000000"})
    response = client.get(url)
    assert response.status_code == 302

# integration test
@pytest.mark.django_db
def test_verification_sent_view(client, create_test_templates):
    user = User.objects.create_user(username="vardenis", email="vardenis@pastas.com", password="ps12345678")
    profile = UserProfile.objects.create(user=user)
    url = reverse('core.uauth:verification_sent', kwargs={"token": profile.verification_token})
    response = client.get(url)
    assert response.status_code == 200
    assert b"verification" in response.content.lower()
