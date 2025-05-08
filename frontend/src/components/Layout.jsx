import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Layout = ({ children }) => {
  const { user } = useAuth();

  return (
    <div className="app">
      <header className="header">
        <nav className="nav">
          <Link to="/" className="logo">MyApp</Link>
          <div className="nav-links">
            {user ? (
              <Link to="/dashboard">Dashboard</Link>
            ) : (
              <>
                <Link to="/login">Login</Link>
                <Link to="/register">Register</Link>
              </>
            )}
          </div>
        </nav>
      </header>
      <main className="main-content">
        {children}
      </main>
      <footer className="footer">
        <p>© 2023 MyApp. All rights reserved.</p>
      </footer>
    </div>
  );
};

export default Layout;