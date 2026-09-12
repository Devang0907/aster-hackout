import { useEffect } from "react";
import { useNavigate } from "@tanstack/react-router";
import { isAuthenticated } from "@/lib/auth";

export function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const navigate = useNavigate();

  useEffect(() => {
    if (!isAuthenticated()) {
      navigate({ to: "/signin" });
    }
  }, [navigate]);

  if (!isAuthenticated()) {
    return null;
  }

  return <>{children}</>;
}
