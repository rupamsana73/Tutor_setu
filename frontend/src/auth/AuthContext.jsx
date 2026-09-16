import { createContext, useContext, useEffect, useMemo, useState } from "react";

import apiClient from "../api/axios";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!localStorage.getItem("tutorset_access_token")) {
      setLoading(false);
      return;
    }

    apiClient
      .get("/auth/me/")
      .then(({ data }) => setUser(data))
      .catch(() => {
        localStorage.removeItem("tutorset_access_token");
        localStorage.removeItem("tutorset_refresh_token");
      })
      .finally(() => setLoading(false));
  }, []);

  const value = useMemo(
    () => ({
      user,
      loading,
      setUser,
      logout() {
        const refresh = localStorage.getItem("tutorset_refresh_token");
        return apiClient
          .post("/auth/logout/", refresh ? { refresh } : {})
          .catch(() => undefined)
          .finally(() => {
            localStorage.removeItem("tutorset_access_token");
            localStorage.removeItem("tutorset_refresh_token");
            setUser(null);
          });
      },
    }),
    [loading, user],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  return useContext(AuthContext);
}
