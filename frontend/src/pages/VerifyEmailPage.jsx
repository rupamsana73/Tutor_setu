import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";

import apiClient from "../api/axios";

export default function VerifyEmailPage() {
  const [params] = useSearchParams();
  const [message, setMessage] = useState("Verifying your email...");

  useEffect(() => {
    apiClient
      .post("/auth/verify-email/", {
        uid: params.get("uid"),
        token: params.get("token"),
      })
      .then(({ data }) => setMessage(data.detail))
      .catch((error) => setMessage(error.response?.data?.detail || "Invalid or expired verification link."));
  }, [params]);

  return (
    <main className="page-shell form-page">
      <h1>Email verification</h1>
      <p>{message}</p>
    </main>
  );
}
