import { useAuth } from '../context/AuthContext';
import Layout from '../components/Layout';
import '../styles/base.css';
import '../styles/layout.css';
import '../styles/dashboard.css';

const Dashboard = () => {
  const { user, logout } = useAuth();

  return (
    <Layout>
      <div className="dashboard">
        <h1>Welcome, {user?.email}</h1>
        <div className="dashboard-content">
          <p>You are now logged in to your account.</p>
          <div className="dashboard-actions">
            <button onClick={logout} className="logout-btn">
              Logout
            </button>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default Dashboard;