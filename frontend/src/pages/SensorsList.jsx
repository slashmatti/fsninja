import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { sensorsAPI } from '../api/api';

const SensorsList = () => {
  const [sensors, setSensors] = useState([]);
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState({
    q: '',
    page: 1,
    page_size: 10,
  });
  const [pagination, setPagination] = useState({});
  const [newSensor, setNewSensor] = useState({
    name: '',
    model: '',
    description: ''
  });

  const loadSensors = async () => {
    setLoading(true);
    try {
      const response = await sensorsAPI.list(filters);
      // Handle both paginated and non-paginated responses
      const responseData = response.data;
      
      if (responseData.items !== undefined) {
        // Paginated response
        setSensors(responseData.items);
        setPagination({
          page: responseData.page,
          page_size: responseData.page_size,
          total: responseData.total,
        });
      } else {
        // Non-paginated response (array)
        setSensors(responseData);
        setPagination({
          page: 1,
          page_size: responseData.length,
          total: responseData.length,
        });
      }
    } catch (error) {
      console.error('Failed to load sensors:', error);
      alert('Failed to load sensors');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSensors();
  }, [filters.page]);

  const handleFilterChange = (field, value) => {
    setFilters(prev => ({ ...prev, [field]: value, page: 1 }));
  };

  const handleSearch = (e) => {
    e.preventDefault();
    loadSensors();
  };

  const handleCreateSensor = async (e) => {
    e.preventDefault();
    try {
      await sensorsAPI.create(newSensor);
      setNewSensor({ name: '', model: '', description: '' });
      loadSensors();
    } catch (error) {
      console.error('Failed to create sensor:', error);
      alert('Failed to create sensor');
    }
  };

  const handleDeleteSensor = async (id) => {
    if (!window.confirm('Are you sure you want to delete this sensor?')) return;
    
    try {
      await sensorsAPI.delete(id);
      loadSensors();
    } catch (error) {
      console.error('Failed to delete sensor:', error);
      alert('Failed to delete sensor');
    }
  };

  const totalPages = Math.ceil(pagination.total / pagination.page_size);

  return (
    <div className="sensors-list">
      <div className="page-header">
        <h1>Sensors</h1>
      </div>

      {/* Add Sensor Form */}
      <div className="add-sensor-section">
        <h3>Add New Sensor</h3>
        <form onSubmit={handleCreateSensor} className="sensor-form">
          <input
            type="text"
            placeholder="Name"
            value={newSensor.name}
            onChange={(e) => setNewSensor(prev => ({ ...prev, name: e.target.value }))}
            required
          />
          <input
            type="text"
            placeholder="Model"
            value={newSensor.model}
            onChange={(e) => setNewSensor(prev => ({ ...prev, model: e.target.value }))}
            required
          />
          <input
            type="text"
            placeholder="Description (optional)"
            value={newSensor.description}
            onChange={(e) => setNewSensor(prev => ({ ...prev, description: e.target.value }))}
          />
          <button type="submit">Add Sensor</button>
        </form>
      </div>

      {/* Search and Filters */}
      <div className="filters-section">
        <form onSubmit={handleSearch} className="search-form">
          <input
            type="text"
            placeholder="Search by name or model..."
            value={filters.q}
            onChange={(e) => handleFilterChange('q', e.target.value)}
          />
          <button type="submit">Search</button>
        </form>
      </div>

      {/* Sensors List */}
      {loading ? (
        <div className="loading">Loading sensors...</div>
      ) : (
        <>
          <div className="sensors-grid">
            {sensors.map(sensor => (
              <div key={sensor.id} className="sensor-card">
                <div className="sensor-info">
                  <h3>
                    <Link to={`/sensors/${sensor.id}`}>{sensor.name}</Link>
                  </h3>
                  <p><strong>Model:</strong> {sensor.model}</p>
                  {sensor.description && <p><strong>Description:</strong> {sensor.description}</p>}
                </div>
                <div className="sensor-actions">
                  <Link to={`/sensors/${sensor.id}`} className="btn btn-primary">
                    View Details
                  </Link>
                  <button 
                    onClick={() => handleDeleteSensor(sensor.id)}
                    className="btn btn-danger"
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="pagination">
              <button
                disabled={filters.page <= 1}
                onClick={() => handleFilterChange('page', filters.page - 1)}
              >
                Previous
              </button>
              
              <span>Page {filters.page} of {totalPages}</span>
              
              <button
                disabled={filters.page >= totalPages}
                onClick={() => handleFilterChange('page', filters.page + 1)}
              >
                Next
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default SensorsList;