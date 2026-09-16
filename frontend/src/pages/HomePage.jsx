import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import apiClient from "../api/axios";

const highlights = [
  {
    title: "Search with confidence",
    description: "Compare subjects, class levels, teaching modes, locations, fees, and availability.",
  },
  {
    title: "Meet verified educators",
    description: "Discover professional tutor profiles designed to make the right choice clearer.",
  },
  {
    title: "Learn your way",
    description: "Find support for online learning or trusted local classes that fit your routine.",
  },
];

export default function HomePage() {
  const [apiStatus, setApiStatus] = useState("checking");

  useEffect(() => {
    apiClient
      .get("/health/")
      .then(() => setApiStatus("online"))
      .catch(() => setApiStatus("offline"));
  }, []);

  return (
    <div className="site">
      <header className="navbar page-shell">
        <Link className="brand" to="/">
          <span className="brand-mark">T</span>
          <span>TutorSetu</span>
        </Link>
        <nav className="nav-links" aria-label="Main navigation">
        <Link to="/how-it-works">How it works</Link>
          <a href="#why-tutorsetu">Why TutorSetu</a>
        <Link className="button button-outline" to="/register">
            Join the waitlist
        </Link>
        </nav>
      </header>

      <main>
        <section className="hero page-shell">
          <div className="hero-copy">
            <p className="eyebrow">Learning, made personal</p>
            <h1>Find a tutor who helps you move forward.</h1>
            <p className="hero-text">
              TutorSetu is building a trusted way for students and parents to discover
              the right tutor for every learning goal.
            </p>
            <div className="hero-actions">
              <Link className="button button-primary" to="/find-tutors">
                Explore tutors
              </Link>
              <Link className="button button-quiet" to="/become-tutor">
                I&apos;m a tutor <span aria-hidden="true">→</span>
              </Link>
            </div>
          </div>
          <div className="hero-card" aria-label="Tutor matching preview">
            <div className="card-glow" />
            <p className="card-label">A better match starts here</p>
            <div className="match-preview">
              <div className="avatar">AS</div>
              <div>
                <strong>Ananya Sharma</strong>
                <span>Mathematics · Classes 8–10</span>
              </div>
              <span className="match-score">98%</span>
            </div>
            <div className="preview-row">
              <span>Online &amp; offline</span>
              <span>₹500 / hour</span>
            </div>
            <div className="preview-bar">
              <span />
            </div>
            <p className="preview-note">Matched to your learning preferences</p>
          </div>
        </section>

        <section className="trust-strip">
          <div className="page-shell trust-content">
            <span>Built for meaningful learning relationships</span>
            <span className={`api-indicator ${apiStatus}`}>
              <span className="status-dot" />
              Platform API {apiStatus}
            </span>
          </div>
        </section>

        <section className="feature-section page-shell" id="why-tutorsetu">
          <div className="section-heading">
            <p className="eyebrow">Designed around you</p>
            <h2>Everything you need to make learning count.</h2>
          </div>
          <div className="feature-grid">
            {highlights.map((highlight, index) => (
              <article className="feature-card" key={highlight.title}>
                <span className="feature-number">0{index + 1}</span>
                <h3>{highlight.title}</h3>
                <p>{highlight.description}</p>
              </article>
            ))}
          </div>
        </section>

        <section className="cta-section page-shell" id="how-it-works">
          <div>
            <p className="eyebrow">The first step is simple</p>
            <h2>Better support. Brighter possibilities.</h2>
          </div>
          <Link className="button button-light" to="/register">
            Get early access <span aria-hidden="true">→</span>
          </Link>
        </section>
      </main>

      <footer className="footer page-shell">
        <span className="brand"><span className="brand-mark">T</span> TutorSetu</span>
        <span>© 2026 TutorSetu. Building the future of tutoring.</span>
      </footer>
    </div>
  );
}
