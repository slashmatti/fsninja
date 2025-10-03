import { useState, useEffect, useCallback } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { readingsAPI } from '../api/api';

const SensorChart = ({ sensorId, readings: propReadings }) => {
  const [readings, setReadings] = useState(propReadings || []);
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState({
    timestamp_from: '',
    timestamp_to: '',
  });

  const loadReadings = useCallback(async () => {
    if (!sensorId) return;
    
    setLoading(true);
    try {
      const params = {};
      if (filters.timestamp_from) params.timestamp_from = filters.timestamp_from;
      if (filters.timestamp_to) params.timestamp_to = filters.timestamp_to;
      
      const response = await readingsAPI.list(sensorId, params);
      let readingsData = response.data;
      
      // Handle paginated response
      if (readingsData && readingsData.items && Array.isArray(readingsData.items)) {
        readingsData = readingsData.items;
      }
      
      console.log('Chart - Loaded readings:', readingsData.length);
      setReadings(readingsData);
    } catch (error) {
      console.error('Failed to load readings:', error);
      alert('Failed to load readings');
    } finally {
      setLoading(false);
    }
  }, [sensorId, filters.timestamp_from, filters.timestamp_to]);

  useEffect(() => {
    // If readings are passed as prop, use them
    if (propReadings) {
      setReadings(propReadings);
    } else if (sensorId) {
      // Otherwise load them
      loadReadings();
    }
  }, [sensorId, propReadings, loadReadings]);

  const handleFilterChange = (field, value) => {
    setFilters(prev => ({ ...prev, [field]: value }));
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  return (
    <div className="sensor-chart">
      <div className="chart-controls">
        <div className="filters">
          <label>
            From:
            <input
              type="datetime-local"
              value={filters.timestamp_from}
              onChange={(e) => handleFilterChange('timestamp_from', e.target.value)}
            />
          </label>
          <label>
            To:
            <input
              type="datetime-local"
              value={filters.timestamp_to}
              onChange={(e) => handleFilterChange('timestamp_to', e.target.value)}
            />
          </label>
          <button onClick={loadReadings} disabled={loading}>
            {loading ? 'Loading...' : 'Apply Filters'}
          </button>
        </div>
      </div>

      {readings.length > 0 ? (
        <ResponsiveContainer width="100%" height={400}>
          <LineChart data={readings} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              dataKey="timestamp" 
              tickFormatter={formatDate}
              angle={-45}
              textAnchor="end"
              height={80}
            />
            <YAxis yAxisId="left" label={{ value: 'Temperature (°C)', angle: -90, position: 'insideLeft' }} />
            <YAxis yAxisId="right" orientation="right" label={{ value: 'Humidity (%)', angle: -90, position: 'insideRight' }} />
            <Tooltip labelFormatter={formatDate} />
            <Legend />
            <Line 
              yAxisId="left"
              type="monotone" 
              dataKey="temperature" 
              stroke="#ff7300" 
              name="Temperature (°C)"
              dot={false}
            />
            <Line 
              yAxisId="right"
              type="monotone" 
              dataKey="humidity" 
              stroke="#387908" 
              name="Humidity (%)"
              dot={false}
            />
          </LineChart>
        </ResponsiveContainer>
      ) : (
        <div className="no-data">
          No readings available for the selected period
          <br />
          <small>Try adding a reading using the form below</small>
        </div>
      )}
    </div>
  );
};

export default SensorChart;