import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { resetPassword } from '../../api/auth';

const ResetPasswordForm = () => {
  const { token } = useParams();
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (newPassword !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }
    
    try {
      await resetPassword(token, newPassword);
      setSuccess(true);
      setError('');
    } catch (err) {
      setError(err.response?.data?.detail || 'Password reset failed');
    }
  };

  if (success) {
    return (
      <div className="auth-form">
        <h2>Password Reset Successful</h2>
        <p>Your password has been successfully updated.</p>
        <button onClick={() => navigate('/login')} className="submit-btn">
          Go to Login
        </button>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="auth-form">
      <h2>Set New Password</h2>
      {error && <div className="error-message">{error}</div>}
      <div className="form-group">
        <label htmlFor="newPassword">New Password</label>
        <input
          type="password"
          id="newPassword"
          value={newPassword}
          onChange={(e) => setNewPassword(e.target.value)}
          required
        />
      </div>
      <div className="form-group">
        <label htmlFor="confirmPassword">Confirm Password</label>
        <input
          type="password"
          id="confirmPassword"
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
          required
        />
      </div>
      <button type="submit" className="submit-btn">Reset Password</button>
    </form>
  );
};

export default ResetPasswordForm;