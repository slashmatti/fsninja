import { useAuth } from '../contexts/AuthContext';
import { Link, useNavigate } from 'react-router-dom';

const Layout = ({ children }) => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="layout">
      <header className="header">
        <div className="container">
          <Link to="/sensors" className="logo">
            Sensor Dashboard
          </Link>
          {user && (
            <nav className="nav">
              <Link to="/sensors">Sensors</Link>
              <button onClick={handleLogout} className="logout-btn">
                Logout
              </button>
            </nav>
          )}
        </div>
      </header>
      <main className="main">
        <div className="container">
          {children}
        </div>
      </main>
    </div>
  );
};

export default Layout;