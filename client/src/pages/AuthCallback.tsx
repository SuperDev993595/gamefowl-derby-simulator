import { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

export default function AuthCallback() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const code = searchParams.get("code");
    if (!code) {
      setError("No authorization code received");
      return;
    }
    const redirectUri = `${window.location.origin}/auth/callback`;
    fetch(`${API_BASE}/api/auth/google/token`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ code, redirect_uri: redirectUri }),
    })
      .then((res) => {
        if (!res.ok) return res.json().then((d) => Promise.reject(new Error(d.detail || "Sign-in failed")));
        return res.json();
      })
      .then((data) => {
        if (data.access_token) {
          localStorage.setItem("token", data.access_token);
          localStorage.setItem("username", data.username || "");
          localStorage.setItem("isAdmin", String(!!data.is_admin));
          localStorage.setItem("tokenBalance", String(data.token_balance ?? 0));
        }
        navigate("/", { replace: true });
        window.dispatchEvent(new Event("auth-login"));
      })
      .catch((err) => setError(err.message || "Sign-in failed"));
  }, [searchParams, navigate]);

  if (error) {
    return (
      <div className="page auth-page">
        <h1>Sign-in failed</h1>
        <p className="error">{error}</p>
        <a href="/login">Back to Sign in</a>
      </div>
    );
  }
  return (
    <div className="page auth-page">
      <p>Completing sign-in...</p>
    </div>
  );
}
