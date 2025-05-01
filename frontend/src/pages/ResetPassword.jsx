import { useState } from "react";
import { useSearchParams } from "react-router-dom";
import { authAPI } from "../api/auth";

function ResetPassword() {
  const [searchParams] = useSearchParams();
  const [newPassword, setNewPassword] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const token = searchParams.get("token");

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await authAPI.resetPassword(token, newPassword);
      setMessage("Password has been reset successfully");
    } catch (err) {
      setError(err.response?.data?.detail || "Password reset failed");
    }
  };

  if (!token) {
    return <div>Invalid reset link</div>;
  }

  return (
    <div>
      <h2>Reset Password</h2>
      {message && <p>{message}</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}
      <form onSubmit={handleSubmit}>
        <input
          type="password"
          value={newPassword}
          onChange={(e) => setNewPassword(e.target.value)}
          placeholder="New password"
          required
        />
        <button type="submit">Reset Password</button>
      </form>
    </div>
  );
}

export default ResetPassword;