import { Link, Route, Routes } from "react-router-dom";

import HomePage from "./pages/HomePage";
import BasicPage from "./pages/BasicPage";

function NotFoundPage() {
  return (
    <main className="page-shell">
      <section className="empty-state">
        <p className="eyebrow">404</p>
        <h1>Page not found</h1>
        <Link className="button button-primary" to="/">
          Return home
        </Link>
      </section>
    </main>
  );
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/find-tutors" element={<BasicPage title="Find tutors" />} />
      <Route path="/become-tutor" element={<BasicPage title="Become a tutor" />} />
      <Route path="/how-it-works" element={<BasicPage title="How TutorSetu works" />} />
      <Route path="/about" element={<BasicPage title="About TutorSetu" />} />
      <Route path="/login" element={<BasicPage title="Login" />} />
      <Route path="/register" element={<BasicPage title="Create an account" />} />
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
}
