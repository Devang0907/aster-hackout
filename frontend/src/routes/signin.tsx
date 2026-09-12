import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useState } from "react";
import { post } from "@/lib/api";
import { setToken, setUser, AuthUser } from "@/lib/auth";

export const Route = createFileRoute("/signin")({
  component: SignIn,
});

function SignIn() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const response = await post("/api/v1/auth/signin", { email, password });
      const data = await response.json();

      if (response.ok) {
        setToken(data.token);
        setUser(data.user);
        navigate({ to: "/dashboard" as any });
      } else {
        setError(data.detail || "Sign in failed");
      }
    } catch (err) {
      setError("Network error. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex bg-background">
      <div className="hidden lg:block lg:w-1/2 h-screen overflow-hidden">
        <img
          src="/sign-img.png"
          alt="Sign in"
          className="h-full w-full object-cover"
        />
      </div>
      <div className="flex w-full items-center justify-center lg:w-1/2 min-h-screen">
        <div className="w-full max-w-md p-8">
          <h1 className="text-3xl font-semibold text-primary mb-2">Sign In</h1>
          <p className="text-sm text-muted-foreground mb-8">
            Enter your credentials to access your account
          </p>
          
          {error && (
            <div className="mb-6 p-3 rounded-lg bg-red-50 border border-red-200 text-red-600 text-sm">
              {error}
            </div>
          )}
          
          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-secondary mb-2">
                Email
              </label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full rounded-lg border border-border bg-background px-4 py-3 text-sm text-primary placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/50"
                placeholder="you@example.com"
                required
              />
            </div>
            
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-secondary mb-2">
                Password
              </label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full rounded-lg border border-border bg-background px-4 py-3 text-sm text-primary placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/50"
                placeholder="••••••••"
                required
              />
            </div>
            
            <button
              type="submit"
              disabled={loading}
              className="w-full rounded-full bg-primary px-4 py-3 text-sm font-semibold uppercase tracking-[0.16em] text-primary-foreground transition-opacity hover:opacity-90 disabled:opacity-50"
            >
              {loading ? "Signing in..." : "Sign In"}
            </button>
          </form>
          
          <p className="mt-6 text-center text-xs text-muted-foreground">
            Don't have an account?{" "}
            <a href="/register" className="text-primary hover:underline">
              Sign up
            </a>
          </p>
        </div>
      </div>
    </div>
  );
}
