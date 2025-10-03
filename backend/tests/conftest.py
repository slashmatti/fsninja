# conftest.py
import pytest
import json
from django.contrib.auth.models import User
from sensors.models import Sensor
from readings.models import Reading
from datetime import datetime, timedelta
import random

@pytest.fixture
def test_user(db):
    """Create a test user"""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )

@pytest.fixture
def another_user(db):
    """Create another test user"""
    return User.objects.create_user(
        username='otheruser',
        email='other@example.com',
        password='testpass123'
    )

@pytest.fixture
def authenticated_client(client, test_user):
    """Authenticated API client using JWT - Uses EMAIL for login"""
    # Login to get token using EMAIL (as required by your AuthController)
    response = client.post(
        '/api/auth/token/',
        data=json.dumps({
            'email': 'test@example.com',  # Use email, not username
            'password': 'testpass123'
        }),
        content_type='application/json'
    )
    
    if response.status_code == 200:
        token = response.json()['access']
        # Set authorization header for all future requests
        client.defaults['HTTP_AUTHORIZATION'] = f'Bearer {token}'
        return client
    else:
        pytest.fail(f"Login failed: {response.status_code} - {response.json()}")

@pytest.fixture
def test_sensor(test_user):
    """Create a test sensor"""
    return Sensor.objects.create(
        owner=test_user,
        name='Test Sensor',
        model='TestModel',
        description='Test description'
    )

@pytest.fixture
def another_user_sensor(another_user):
    """Create a sensor owned by another user"""
    return Sensor.objects.create(
        owner=another_user,
        name='Other Sensor',
        model='OtherModel'
    )

@pytest.fixture
def test_readings(test_sensor):
    """Create test readings for a sensor"""
    readings = []
    base_time = datetime.now() - timedelta(days=1)
    
    for i in range(10):
        reading = Reading.objects.create(
            sensor=test_sensor,
            temperature=20.0 + random.uniform(-5, 5),
            humidity=50.0 + random.uniform(-20, 20),
            timestamp=base_time + timedelta(hours=i)
        )
        readings.append(reading)
    
    return readings