import { useState } from "react";
import { useSearchParams } from "react-router-dom";

import apiClient from "../api/axios";

export default function PasswordResetConfirmPage() {
  const [params] = useSearchParams();
  const [password, setPassword] = useState("");
  const [passwordConfirm, setPasswordConfirm] = useState("");
  const [message, setMessage] = useState("");

  async function submit(event) {
    event.preventDefault();
    try {
      await apiClient.post("/auth/password-reset/confirm/", {
        uid: params.get("uid"),
        token: params.get("token"),
        password,
        password_confirm: passwordConfirm,
      });
      setMessage("Password reset successful. You can now log in.");
    } catch (error) {
      setMessage(error.response?.data?.detail || "Invalid or expired reset link.");
    }
  }

  return (
    <main className="page-shell form-page">
      <h1>Choose a new password</h1>
      <form className="auth-form" onSubmit={submit}>
        <label>Password<input type="password" required value={password} onChange={(event) => setPassword(event.target.value)} /></label>
        <label>Confirm password<input type="password" required value={passwordConfirm} onChange={(event) => setPasswordConfirm(event.target.value)} /></label>
        <button className="button button-primary" type="submit">Reset password</button>
      </form>
      {message && <p>{message}</p>}
    </main>
  );
}
