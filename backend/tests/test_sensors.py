# test_sensors.py
import pytest
import json
from sensors.models import Sensor

@pytest.mark.django_db
class TestSensorCRUD:
    """Test sensor CRUD operations"""
    
    def test_create_sensor(self, authenticated_client, test_user):
        """Test creating a new sensor"""
        response = authenticated_client.post(
            '/api/sensors/',
            data=json.dumps({
                'name': 'New Sensor',
                'model': 'DHT22',
                'description': 'A new test sensor'
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['name'] == 'New Sensor'
        assert data['model'] == 'DHT22'
        assert data['description'] == 'A new test sensor'
        assert data['owner_id'] == test_user.id
        
        # Verify sensor was created in database
        assert Sensor.objects.filter(name='New Sensor').exists()
    
    def test_create_sensor_minimal_data(self, authenticated_client, test_user):
        """Test creating sensor with minimal data (no description)"""
        response = authenticated_client.post(
            '/api/sensors/',
            data=json.dumps({
                'name': 'Minimal Sensor',
                'model': 'DHT11'
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['name'] == 'Minimal Sensor'
        assert data['model'] == 'DHT11'
        assert data['description'] is None
    
    def test_list_sensors(self, authenticated_client, test_sensor, another_user_sensor):
        """Test listing sensors (should only show user's sensors)"""
        response = authenticated_client.get('/api/sensors/')
        
        assert response.status_code == 200
        data = response.json()
        
        # Should only see own sensors
        assert len(data['items']) == 1
        assert data['items'][0]['name'] == 'Test Sensor'
        assert data['items'][0]['owner_id'] == test_sensor.owner.id
        
        # Should not see other user's sensor
        sensor_names = [s['name'] for s in data['items']]
        assert 'Other Sensor' not in sensor_names
    
    def test_list_sensors_pagination(self, authenticated_client, test_user):
        """Test sensor list pagination"""
        # Create multiple sensors
        for i in range(15):
            Sensor.objects.create(
                owner=test_user,
                name=f'Sensor {i}',
                model=f'Model {i}'
            )
        
        response = authenticated_client.get('/api/sensors/?page=2&page_size=5')
        
        assert response.status_code == 200
        data = response.json()
        
        assert data['page'] == 2
        assert data['page_size'] == 5
        assert len(data['items']) == 5
        assert data['total'] == 16  # 15 new + 1 existing
    
    def test_list_sensors_search(self, authenticated_client, test_user):
        """Test sensor search functionality"""
        # Create sensors with different names
        Sensor.objects.create(owner=test_user, name='Office Temp', model='DHT22')
        Sensor.objects.create(owner=test_user, name='Lab Humidity', model='DHT11')
        Sensor.objects.create(owner=test_user, name='Outside Temp', model='BME280')
        
        # Search by name
        response = authenticated_client.get('/api/sensors/?q=Office')
        
        assert response.status_code == 200
        data = response.json()
        assert len(data['items']) == 1
        assert data['items'][0]['name'] == 'Office Temp'
        
        # Search by model
        response = authenticated_client.get('/api/sensors/?q=DHT')
        
        assert response.status_code == 200
        data = response.json()
        assert len(data['items']) == 2  # DHT22 and DHT11
    
    def test_get_sensor_detail(self, authenticated_client, test_sensor):
        """Test getting sensor details"""
        response = authenticated_client.get(f'/api/sensors/{test_sensor.id}/')
        
        assert response.status_code == 200
        data = response.json()
        assert data['id'] == test_sensor.id
        assert data['name'] == 'Test Sensor'
        assert data['model'] == 'TestModel'
    
    def test_get_nonexistent_sensor(self, authenticated_client):
        """Test getting non-existent sensor"""
        response = authenticated_client.get('/api/sensors/999/')
        
        assert response.status_code == 404
    
    def test_get_other_user_sensor(self, authenticated_client, another_user_sensor):
        """Test getting sensor owned by another user"""
        response = authenticated_client.get(f'/api/sensors/{another_user_sensor.id}/')
        
        assert response.status_code == 404  # Should not find other user's sensor
    
    def test_update_sensor(self, authenticated_client, test_sensor):
        """Test updating sensor"""
        response = authenticated_client.put(
            f'/api/sensors/{test_sensor.id}/',
            data=json.dumps({
                'name': 'Updated Sensor',
                'model': 'Updated Model',
                'description': 'Updated description'
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['name'] == 'Updated Sensor'
        assert data['model'] == 'Updated Model'
        assert data['description'] == 'Updated description'
        
        # Verify update in database
        test_sensor.refresh_from_db()
        assert test_sensor.name == 'Updated Sensor'
    
    def test_update_other_user_sensor(self, authenticated_client, another_user_sensor):
        """Test updating sensor owned by another user"""
        response = authenticated_client.put(
            f'/api/sensors/{another_user_sensor.id}/',
            data=json.dumps({
                'name': 'Hacked Sensor',
                'model': 'Hacked Model'
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 404  # Should not find other user's sensor
    
    def test_delete_sensor(self, authenticated_client, test_sensor):
        """Test deleting sensor"""
        response = authenticated_client.delete(f'/api/sensors/{test_sensor.id}/')
        
        assert response.status_code == 204
        
        # Verify sensor was deleted
        assert not Sensor.objects.filter(id=test_sensor.id).exists()
    
    def test_delete_other_user_sensor(self, authenticated_client, another_user_sensor):
        """Test deleting sensor owned by another user"""
        response = authenticated_client.delete(f'/api/sensors/{another_user_sensor.id}/')
        
        assert response.status_code == 404  # Should not find other user's sensor
        
        # Verify sensor still exists
        assert Sensor.objects.filter(id=another_user_sensor.id).exists()
    
    def test_sensor_cascade_delete_readings(self, authenticated_client, test_sensor, test_readings):
        """Test that readings are deleted when sensor is deleted"""
        # Verify readings exist
        assert test_sensor.readings.count() == 10
        
        # Delete sensor
        response = authenticated_client.delete(f'/api/sensors/{test_sensor.id}/')
        assert response.status_code == 204
        
        # Verify readings were also deleted
        from readings.models import Reading
        assert Reading.objects.filter(sensor_id=test_sensor.id).count() == 0