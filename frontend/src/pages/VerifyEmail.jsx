import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { authAPI } from "../api/auth";

function VerifyEmail() {
  const [searchParams] = useSearchParams();
  const [message, setMessage] = useState("Verifying email...");
  const [error, setError] = useState("");

  useEffect(() => {
    const token = searchParams.get("token");
    if (token) {
      authAPI
        .verifyEmail(token)
        .then(() => setMessage("Email verified successfully!"))
        .catch((err) => setError(err.response?.data?.detail || "Verification failed"));
    }
  }, [searchParams]);

  return (
    <div>
      <h2>Email Verification</h2>
      {message && <p>{message}</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}
    </div>
  );
}

export default VerifyEmail;