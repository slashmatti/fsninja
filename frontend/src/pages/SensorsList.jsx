import { useState, useEffect, useCallback } from 'react';
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
  const [pagination, setPagination] = useState({
    page: 1,
    page_size: 10,
    total: 0,
    total_pages: 0
  });
  const [newSensor, setNewSensor] = useState({
    name: '',
    model: '',
    description: ''
  });

  const loadSensors = useCallback(async () => {
    setLoading(true);
    try {
      const response = await sensorsAPI.list(filters);
      const responseData = response.data;
      
      console.log('Sensors response:', responseData); // Debug log
      
      if (responseData.items !== undefined) {
        // Paginated response
        setSensors(responseData.items);
        setPagination({
          page: responseData.page,
          page_size: responseData.page_size,
          total: responseData.total,
          total_pages: Math.ceil(responseData.total / responseData.page_size)
        });
      } else {
        // Non-paginated response (array)
        setSensors(responseData);
        setPagination({
          page: 1,
          page_size: responseData.length,
          total: responseData.length,
          total_pages: 1
        });
      }
    } catch (error) {
      console.error('Failed to load sensors:', error);
      alert('Failed to load sensors');
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    loadSensors();
  }, [loadSensors]);

  const handleFilterChange = (field, value) => {
    setFilters(prev => ({ ...prev, [field]: value, page: 1 })); // Reset to page 1 on filter change
  };

  const handleSearch = (e) => {
    e.preventDefault();
    loadSensors();
  };

  const handleClearFilters = () => {
    setFilters({
      q: '',
      page: 1,
      page_size: 10,
    });
  };

  const handlePageChange = (newPage) => {
    setFilters(prev => ({ ...prev, page: newPage }));
  };

  const handlePageSizeChange = (newSize) => {
    setFilters(prev => ({ ...prev, page_size: parseInt(newSize), page: 1 }));
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

  // Generate page numbers for pagination
  const getPageNumbers = () => {
    const pages = [];
    const maxVisiblePages = 5;
    const startPage = Math.max(1, pagination.page - Math.floor(maxVisiblePages / 2));
    const endPage = Math.min(pagination.total_pages, startPage + maxVisiblePages - 1);
    
    for (let i = startPage; i <= endPage; i++) {
      pages.push(i);
    }
    return pages;
  };

  const hasFilters = filters.q !== '';

  return (
    <div className="sensors-list">
      <div className="page-header">
        <h1>Sensors Management</h1>
        <p>Manage your sensor devices and monitor their readings</p>
      </div>

      {/* Add Sensor Form */}
      <div className="add-sensor-section card">
        <h3>Add New Sensor</h3>
        <form onSubmit={handleCreateSensor} className="sensor-form">
          <div className="form-row">
            <input
              type="text"
              placeholder="Sensor Name *"
              value={newSensor.name}
              onChange={(e) => setNewSensor(prev => ({ ...prev, name: e.target.value }))}
              required
            />
            <input
              type="text"
              placeholder="Model *"
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
            <button type="submit" className="btn btn-primary">Add Sensor</button>
          </div>
        </form>
      </div>

      {/* Filters Section */}
      <div className="filters-section card">
        <div className="filters-header">
          <h3>Filters & Search</h3>
          {hasFilters && (
            <button onClick={handleClearFilters} className="btn btn-secondary btn-sm">
              Clear Filters
            </button>
          )}
        </div>
        
        <form onSubmit={handleSearch} className="search-form">
          <div className="search-input-group">
            <input
              type="text"
              placeholder="Search by sensor name or model..."
              value={filters.q}
              onChange={(e) => handleFilterChange('q', e.target.value)}
              className="search-input"
            />
            <button type="submit" className="btn btn-primary">
              <span className="search-icon">🔍</span> Search
            </button>
          </div>
        </form>

        {/* Results Summary */}
        {!loading && (
          <div className="results-summary">
            <span>
              Showing {sensors.length} of {pagination.total} sensors
              {filters.q && (
                <span> matching "<strong>{filters.q}</strong>"</span>
              )}
            </span>
          </div>
        )}
      </div>

      {/* Page Size Selector */}
      <div className="page-controls">
        <div className="page-size-selector">
          <label>Show:</label>
          <select 
            value={filters.page_size} 
            onChange={(e) => handlePageSizeChange(e.target.value)}
            className="page-size-select"
          >
            <option value="5">5 per page</option>
            <option value="10">10 per page</option>
            <option value="20">20 per page</option>
            <option value="50">50 per page</option>
          </select>
        </div>
      </div>

      {/* Sensors List */}
      {loading ? (
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Loading sensors...</p>
        </div>
      ) : sensors.length > 0 ? (
        <>
          <div className="sensors-grid">
            {sensors.map(sensor => (
              <div key={sensor.id} className="sensor-card card">
                <div className="sensor-info">
                  <h3>
                    <Link to={`/sensors/${sensor.id}`} className="sensor-link">
                      {sensor.name}
                    </Link>
                  </h3>
                  <p className="sensor-model"><strong>Model:</strong> {sensor.model}</p>
                  {sensor.description && (
                    <p className="sensor-description"><strong>Description:</strong> {sensor.description}</p>
                  )}
                  <p className="sensor-id"><strong>ID:</strong> {sensor.id}</p>
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
          {pagination.total_pages > 1 && (
            <div className="pagination-container">
              <div className="pagination-info">
                Page {pagination.page} of {pagination.total_pages} 
                ({pagination.total} total sensors)
              </div>
              
              <div className="pagination-controls">
                <button
                  onClick={() => handlePageChange(pagination.page - 1)}
                  disabled={pagination.page <= 1}
                  className="pagination-btn"
                >
                  ← Previous
                </button>

                <div className="page-numbers">
                  {getPageNumbers().map(pageNum => (
                    <button
                      key={pageNum}
                      onClick={() => handlePageChange(pageNum)}
                      className={`pagination-btn ${pageNum === pagination.page ? 'active' : ''}`}
                    >
                      {pageNum}
                    </button>
                  ))}
                </div>

                <button
                  onClick={() => handlePageChange(pagination.page + 1)}
                  disabled={pagination.page >= pagination.total_pages}
                  className="pagination-btn"
                >
                  Next →
                </button>
              </div>
            </div>
          )}
        </>
      ) : (
        <div className="empty-state">
          <div className="empty-icon">📡</div>
          <h3>No Sensors Found</h3>
          <p>
            {hasFilters 
              ? 'No sensors match your search criteria. Try adjusting your filters.'
              : "You haven't added any sensors yet. Add your first sensor to get started!"
            }
          </p>
          {hasFilters && (
            <button onClick={handleClearFilters} className="btn btn-primary">
              Clear Filters
            </button>
          )}
        </div>
      )}
    </div>
  );
};

export default SensorsList;