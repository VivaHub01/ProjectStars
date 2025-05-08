import { useState } from 'react';
import { requestPasswordReset } from '../../api/auth';
import { useNavigate } from 'react-router-dom';

const RequestResetForm = () => {
  const [email, setEmail] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      await requestPasswordReset(email);
      setSuccess(true);
      setError('');
    } catch (err) {
      setError(err.response?.data?.detail || 'Request failed');
    }
  };

  if (success) {
    return (
      <div className="auth-form">
        <h2>Check Your Email</h2>
        <p>If an account exists with this email, you will receive a password reset link.</p>
        <button onClick={() => navigate('/login')} className="submit-btn">
          Back to Login
        </button>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="auth-form">
      <h2>Reset Password</h2>
      {error && <div className="error-message">{error}</div>}
      <div className="form-group">
        <label htmlFor="email">Email</label>
        <input
          type="email"
          id="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
      </div>
      <button type="submit" className="submit-btn">Request Reset</button>
      <div className="form-footer">
        <p>
          Remember your password? <a href="/login">Login</a>
        </p>
      </div>
    </form>
  );
};

export default RequestResetForm;