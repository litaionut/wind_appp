import { useState, type FormEvent } from "react";
import { Navigate } from "react-router-dom";
import { ApiError } from "../api";
import { useAuth } from "../auth";

export function LoginPage() {
  const { user, loading, login } = useAuth();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  if (!loading && user) return <Navigate to="/" replace />;

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await login(username, password);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Login failed");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="login-shell">
      <div className="login-atmosphere" aria-hidden="true" />
      <section className="login-panel">
        <p className="brand">Wind Platform</p>
        <h1>Sign in to your engineering workspace</h1>
        <p className="lede">
          Token-authenticated access to projects, layouts, and energy assessments.
        </p>
        <form className="stack" onSubmit={onSubmit}>
          <label>
            Username
            <input
              autoComplete="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
            />
          </label>
          <label>
            Password
            <input
              type="password"
              autoComplete="current-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </label>
          {error ? <p className="error">{error}</p> : null}
          <button type="submit" disabled={submitting}>
            {submitting ? "Signing in…" : "Sign in"}
          </button>
        </form>
      </section>
    </main>
  );
}
