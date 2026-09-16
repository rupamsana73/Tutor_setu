import { useState } from "react";

import apiClient from "../api/axios";

export default function PasswordResetPage() {
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");

  async function submit(event) {
    event.preventDefault();
    await apiClient.post("/auth/password-reset/request/", { email });
    setMessage("If an account exists for that email, reset instructions have been sent.");
  }

  return (
    <main className="page-shell form-page">
      <h1>Reset your password</h1>
      <form className="auth-form" onSubmit={submit}>
        <label>Email<input type="email" required value={email} onChange={(event) => setEmail(event.target.value)} /></label>
        <button className="button button-primary" type="submit">Send reset instructions</button>
      </form>
      {message && <p>{message}</p>}
    </main>
  );
}
