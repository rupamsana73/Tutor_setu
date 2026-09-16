import { Link } from "react-router-dom";

export default function BasicPage({ title }) {
  return (
    <main className="page-shell">
      <section className="empty-state">
        <p className="eyebrow">TutorSetu Phase 1</p>
        <h1>{title}</h1>
        <p className="hero-text page-placeholder">
          This page is part of the foundation navigation. Its product workflow will
          be implemented in a later phase.
        </p>
        <Link className="button button-primary" to="/">
          Return home
        </Link>
      </section>
    </main>
  );
}
