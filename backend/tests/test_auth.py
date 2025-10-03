# test_auth.py
import pytest
import json
from django.contrib.auth.models import User

@pytest.mark.django_db
class TestAuthFlows:
    """Test authentication flows"""
    
    def test_register_new_user(self, client):
        """Test user registration"""
        response = client.post(
            '/api/auth/register/',
            data=json.dumps({
                'username': 'newuser',
                'email': 'newuser@example.com',
                'password': 'newpass123'
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = response.json()
        assert 'access' in data
        assert data['username'] == 'newuser'
        assert data['email'] == 'newuser@example.com'
        
        # Verify user was created in database
        assert User.objects.filter(username='newuser').exists()
    
    def test_register_duplicate_email(self, client, test_user):
        """Test registration with duplicate email fails"""
        response = client.post(
            '/api/auth/register/',
            data=json.dumps({
                'username': 'differentuser',
                'email': 'test@example.com',  # Same email as existing user
                'password': 'testpass123'
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        assert 'error' in response.json()
    
    def test_login_success(self, client, test_user):
        """Test successful login - Uses EMAIL"""
        response = client.post(
            '/api/auth/token/',
            data=json.dumps({
                'email': 'test@example.com',  # Use email
                'password': 'testpass123'
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = response.json()
        assert 'access' in data
        assert 'refresh' in data
    
    def test_login_invalid_credentials(self, client, test_user):
        """Test login with invalid credentials"""
        response = client.post(
            '/api/auth/token/',
            data=json.dumps({
                'email': 'test@example.com',
                'password': 'wrongpassword'
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 401
        assert 'error' in response.json()
    
    def test_login_nonexistent_user(self, client):
        """Test login with non-existent user"""
        response = client.post(
            '/api/auth/token/',
            data=json.dumps({
                'email': 'nonexistent@example.com',
                'password': 'somepassword'
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 401
        assert 'error' in response.json()
    
    def test_protected_endpoint_without_auth(self, client):
        """Test accessing protected endpoint without authentication"""
        response = client.get('/api/sensors/')
        
        assert response.status_code == 401
        assert 'detail' in response.json()
    
    def test_protected_endpoint_with_invalid_token(self, client):
        """Test accessing protected endpoint with invalid token"""
        response = client.get(
            '/api/sensors/',
            HTTP_AUTHORIZATION='Bearer invalid_token'
        )
        
        assert response.status_code == 401
        assert 'detail' in response.json()
    
    def test_token_refresh(self, client, test_user):
        """Test token refresh functionality"""
        # First login to get tokens
        login_response = client.post(
            '/api/auth/token/',
            data=json.dumps({
                'email': 'test@example.com',  # Use email
                'password': 'testpass123'
            }),
            content_type='application/json'
        )
        
        assert login_response.status_code == 200
        refresh_token = login_response.json()['refresh']
        
        # Refresh token using your custom refresh endpoint
        refresh_response = client.post(
            '/api/auth/refresh/',
            data=json.dumps({
                'refresh': refresh_token
            }),
            content_type='application/json'
        )
        
        assert refresh_response.status_code == 200
        assert 'access' in refresh_response.json()