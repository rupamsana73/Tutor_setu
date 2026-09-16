import { useNavigate } from "react-router-dom";

import { useAuth } from "../auth/AuthContext";

export default function AccountPage() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  async function handleLogout() {
    await logout();
    navigate("/", { replace: true });
  }

  return (
    <main className="page-shell form-page">
      <p className="eyebrow">Your account</p>
      <h1>Welcome, {user.first_name}</h1>
      <p className="hero-text">Signed in as {user.email}. Role: {user.role}.</p>
      <button className="button button-primary" onClick={handleLogout}>Log out</button>
    </main>
  );
}
