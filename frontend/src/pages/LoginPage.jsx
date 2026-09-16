import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";

import apiClient from "../api/axios";
import { useAuth } from "../auth/AuthContext";

export default function LoginPage() {
  const [form, setForm] = useState({ email: "", password: "" });
  const [error, setError] = useState("");
  const { setUser } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    try {
      const { data } = await apiClient.post("/auth/token/", form);
      localStorage.setItem("tutorset_access_token", data.access);
      localStorage.setItem("tutorset_refresh_token", data.refresh);
      const account = await apiClient.get("/auth/me/");
      setUser(account.data);
      navigate(location.state?.from?.pathname || "/account", { replace: true });
    } catch {
      setError("Invalid email or password.");
    }
  }

  return (
    <main className="page-shell form-page">
      <h1>Welcome back</h1>
      <form className="auth-form" onSubmit={handleSubmit}>
        <label>Email<input type="email" required value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} /></label>
        <label>Password<input type="password" required value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} /></label>
        {error && <p className="form-error">{error}</p>}
        <button className="button button-primary" type="submit">Log in</button>
      </form>
      <p><Link to="/password-reset">Forgot your password?</Link></p>
      <p>New to TutorSetu? <Link to="/register">Create an account</Link></p>
    </main>
  );
}
