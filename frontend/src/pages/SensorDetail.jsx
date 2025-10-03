import { useState, useEffect, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import { sensorsAPI, readingsAPI } from '../api/api';
import SensorChart from '../components/SensorChart';

const SensorDetail = () => {
  const { sensorId } = useParams();
  const [sensor, setSensor] = useState(null);
  const [readings, setReadings] = useState([]);
  const [loading, setLoading] = useState(false);
  const [apiError, setApiError] = useState(null);
  const [newReading, setNewReading] = useState({
    temperature: '',
    humidity: '',
    timestamp: new Date().toISOString().slice(0, 16),
  });

  const loadSensor = useCallback(async () => {
    setLoading(true);
    setApiError(null);
    try {
      console.log('Loading sensor:', sensorId);
      
      // Load sensor details
      const sensorResponse = await sensorsAPI.get(sensorId);
      console.log('Sensor response:', sensorResponse);
      setSensor(sensorResponse.data);
      
      // Load readings
      console.log('Loading readings for sensor:', sensorId);
      const readingsResponse = await readingsAPI.list(sensorId);
      console.log('Readings API response:', readingsResponse);
      console.log('Readings data:', readingsResponse.data);
      
      // Handle paginated response (items array) or direct array
      let readingsData = readingsResponse.data;
      if (readingsData && typeof readingsData === 'object') {
        if (readingsData.items && Array.isArray(readingsData.items)) {
          // Paginated response - use the items array
          readingsData = readingsData.items;
          console.log(`Loaded ${readingsData.length} readings from paginated response`);
        } else if (Array.isArray(readingsData)) {
          // Direct array response
          console.log(`Loaded ${readingsData.length} readings from direct array`);
        } else {
          console.error('Unexpected readings response format:', readingsResponse.data);
          setApiError('Unexpected response format from server');
          return;
        }
      }
      
      setReadings(readingsData);
      console.log(`Final readings count: ${readingsData.length}`);
      
    } catch (error) {
      console.error('API Error details:', error);
      setApiError(error.response?.data || error.message);
      alert('Failed to load sensor details');
    } finally {
      setLoading(false);
    }
  }, [sensorId]);

  useEffect(() => {
    if (sensorId) {
      loadSensor();
    }
  }, [sensorId, loadSensor]);

  const handleAddReading = async (e) => {
    e.preventDefault();
    try {
      await readingsAPI.create(sensorId, {
        ...newReading,
        temperature: parseFloat(newReading.temperature),
        humidity: parseFloat(newReading.humidity),
      });
      setNewReading({
        temperature: '',
        humidity: '',
        timestamp: new Date().toISOString().slice(0, 16),
      });
      alert('Reading added successfully!');
      loadSensor(); // Reload to show new reading
    } catch (error) {
      console.error('Failed to add reading:', error);
      alert('Failed to add reading');
    }
  };

  if (loading) return <div className="loading">Loading sensor details...</div>;
  if (!sensor) return <div className="error">Sensor not found</div>;

  return (
    <div className="sensor-detail">
      <div className="page-header">
        <h1>{sensor.name}</h1>
        <p><strong>Model:</strong> {sensor.model}</p>
        {sensor.description && <p><strong>Description:</strong> {sensor.description}</p>}
        <p><strong>Readings count:</strong> {readings.length}</p>
      </div>

      {apiError && (
        <div className="error-message">
          <strong>API Error:</strong> {JSON.stringify(apiError)}
        </div>
      )}

      {/* Readings Chart */}
      <div className="chart-section">
        <h2>Readings ({readings.length} total)</h2>
        <SensorChart sensorId={sensorId} readings={readings} />
      </div>

      {/* Add Reading Form */}
      <div className="add-reading-section">
        <h3>Add New Reading</h3>
        <form onSubmit={handleAddReading} className="reading-form">
          <div className="form-row">
            <div className="form-group">
              <label>Temperature (°C):</label>
              <input
                type="number"
                step="0.1"
                value={newReading.temperature}
                onChange={(e) => setNewReading(prev => ({ ...prev, temperature: e.target.value }))}
                required
              />
            </div>
            
            <div className="form-group">
              <label>Humidity (%):</label>
              <input
                type="number"
                step="0.1"
                min="0"
                max="100"
                value={newReading.humidity}
                onChange={(e) => setNewReading(prev => ({ ...prev, humidity: e.target.value }))}
                required
              />
            </div>
            
            <div className="form-group">
              <label>Timestamp:</label>
              <input
                type="datetime-local"
                value={newReading.timestamp}
                onChange={(e) => setNewReading(prev => ({ ...prev, timestamp: e.target.value }))}
                required
              />
            </div>
          </div>
          
          <button type="submit">Add Reading</button>
        </form>
      </div>
    </div>
  );
};

export default SensorDetail;