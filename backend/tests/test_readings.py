# test_readings.py
import pytest
import json
from datetime import datetime, timedelta
from readings.models import Reading

@pytest.mark.django_db
class TestReadingsCRUD:
    """Test readings CRUD operations"""
    
    def test_create_reading(self, authenticated_client, test_sensor):
        """Test creating a new reading"""
        timestamp = datetime.now().isoformat()
        
        response = authenticated_client.post(
            f'/api/sensors/{test_sensor.id}/readings/',
            data=json.dumps({
                'temperature': 22.5,
                'humidity': 45.2,
                'timestamp': timestamp
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['temperature'] == 22.5
        assert data['humidity'] == 45.2
        assert data['sensor_id'] == test_sensor.id
        
        # Verify reading was created in database
        assert Reading.objects.filter(sensor=test_sensor, temperature=22.5).exists()
    
    def test_create_reading_invalid_sensor(self, authenticated_client):
        """Test creating reading for non-existent sensor"""
        response = authenticated_client.post(
            '/api/sensors/999/readings/',
            data=json.dumps({
                'temperature': 22.5,
                'humidity': 45.2,
                'timestamp': datetime.now().isoformat()
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 404
    
    def test_create_reading_other_user_sensor(self, authenticated_client, another_user_sensor):
        """Test creating reading for another user's sensor"""
        response = authenticated_client.post(
            f'/api/sensors/{another_user_sensor.id}/readings/',
            data=json.dumps({
                'temperature': 22.5,
                'humidity': 45.2,
                'timestamp': datetime.now().isoformat()
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 404
    
    def test_list_readings(self, authenticated_client, test_sensor, test_readings):
        """Test listing readings for a sensor"""
        response = authenticated_client.get(f'/api/sensors/{test_sensor.id}/readings/')
        
        assert response.status_code == 200
        data = response.json()
        
        # Should get paginated response
        assert 'items' in data
        assert 'count' in data
        assert data['count'] == 10
        assert len(data['items']) == 10
        
        # Verify reading data
        reading = data['items'][0]
        assert 'id' in reading
        assert 'temperature' in reading
        assert 'humidity' in reading
        assert 'timestamp' in reading
        assert 'sensor_id' in reading
    
    def test_list_readings_time_filter(self, authenticated_client, test_sensor, test_readings):
        """Test filtering readings by time range"""
        # Get timestamps for filtering
        middle_time = test_readings[4].timestamp.isoformat()
        end_time = test_readings[8].timestamp.isoformat()
        
        # Filter from middle to end
        response = authenticated_client.get(
            f'/api/sensors/{test_sensor.id}/readings/',
            {'timestamp_from': middle_time, 'timestamp_to': end_time}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should get readings from index 4 to 8 (5 readings)
        assert len(data['items']) == 5
    
    def test_list_readings_from_filter_only(self, authenticated_client, test_sensor, test_readings):
        """Test filtering readings with only start time"""
        start_time = test_readings[2].timestamp.isoformat()
        
        response = authenticated_client.get(
            f'/api/sensors/{test_sensor.id}/readings/',
            {'timestamp_from': start_time}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should get readings from index 2 to end (8 readings)
        assert len(data['items']) == 8
    
    def test_list_readings_to_filter_only(self, authenticated_client, test_sensor, test_readings):
        """Test filtering readings with only end time"""
        end_time = test_readings[7].timestamp.isoformat()
        
        response = authenticated_client.get(
            f'/api/sensors/{test_sensor.id}/readings/',
            {'timestamp_to': end_time}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should get readings from start to index 7 (8 readings)
        assert len(data['items']) == 8
    
    def test_list_readings_invalid_sensor(self, authenticated_client):
        """Test listing readings for non-existent sensor"""
        response = authenticated_client.get('/api/sensors/999/readings/')
        
        assert response.status_code == 404
    
    def test_list_readings_other_user_sensor(self, authenticated_client, another_user_sensor):
        """Test listing readings for another user's sensor"""
        response = authenticated_client.get(f'/api/sensors/{another_user_sensor.id}/readings/')
        
        assert response.status_code == 404
    
    def test_duplicate_timestamp_prevention(self, authenticated_client, test_sensor):
        """Test that duplicate timestamps for same sensor are prevented"""
        timestamp = datetime.now().isoformat()
        
        # Create first reading
        response1 = authenticated_client.post(
            f'/api/sensors/{test_sensor.id}/readings/',
            data=json.dumps({
                'temperature': 22.5,
                'humidity': 45.2,
                'timestamp': timestamp
            }),
            content_type='application/json'
        )
        assert response1.status_code == 200
        
        # Try to create second reading with same timestamp
        response2 = authenticated_client.post(
            f'/api/sensors/{test_sensor.id}/readings/',
            data=json.dumps({
                'temperature': 23.0,
                'humidity': 46.0,
                'timestamp': timestamp
            }),
            content_type='application/json'
        )
        
        # Should get an error due to unique constraint
        assert response2.status_code == 400
    
    def test_reading_ordering(self, authenticated_client, test_sensor, test_readings):
        """Test that readings are ordered by timestamp"""
        response = authenticated_client.get(f'/api/sensors/{test_sensor.id}/readings/')
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify readings are in chronological order
        timestamps = [reading['timestamp'] for reading in data['items']]
        sorted_timestamps = sorted(timestamps)
        assert timestamps == sorted_timestamps