import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import apiClient from "../api/axios";

export default function RegisterPage() {
  const [form, setForm] = useState({ first_name: "", last_name: "", email: "", password: "", password_confirm: "", role: "student" });
  const [error, setError] = useState("");
  const navigate = useNavigate();

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    try {
      await apiClient.post("/auth/register/", form);
      navigate("/login", { replace: true });
    } catch (requestError) {
      setError(requestError.response?.data?.detail || "Unable to create the account.");
    }
  }

  function update(field) {
    return (event) => setForm({ ...form, [field]: event.target.value });
  }

  return (
    <main className="page-shell form-page">
      <h1>Create an account</h1>
      <form className="auth-form" onSubmit={handleSubmit}>
        <label>First name<input required value={form.first_name} onChange={update("first_name")} /></label>
        <label>Last name<input required value={form.last_name} onChange={update("last_name")} /></label>
        <label>Email<input type="email" required value={form.email} onChange={update("email")} /></label>
        <label>Role<select value={form.role} onChange={update("role")}><option value="student">Student</option><option value="parent">Parent</option><option value="tutor">Tutor</option></select></label>
        <label>Password<input type="password" required value={form.password} onChange={update("password")} /></label>
        <label>Confirm password<input type="password" required value={form.password_confirm} onChange={update("password_confirm")} /></label>
        {error && <p className="form-error">{error}</p>}
        <button className="button button-primary" type="submit">Create account</button>
      </form>
      <p>Already registered? <Link to="/login">Log in</Link></p>
    </main>
  );
}
