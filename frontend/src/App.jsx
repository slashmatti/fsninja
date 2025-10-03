import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import Layout from './components/Layout';
import PrivateRoute from './components/PrivateRoute';
import Login from './pages/Login';
import Register from './pages/Register';
import SensorsList from './pages/SensorsList';
import SensorDetail from './pages/SensorDetail';
import './styles.css';

function App() {
  return (
    <AuthProvider>
      <Router>
        <Layout>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route
              path="/sensors"
              element={
                <PrivateRoute>
                  <SensorsList />
                </PrivateRoute>
              }
            />
            <Route
              path="/sensors/:sensorId"
              element={
                <PrivateRoute>
                  <SensorDetail />
                </PrivateRoute>
              }
            />
            <Route path="/" element={<Navigate to="/sensors" replace />} />
          </Routes>
        </Layout>
      </Router>
    </AuthProvider>
  );
}

export default App;