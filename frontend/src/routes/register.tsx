import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { post } from "@/lib/api";
import { setToken, setUser } from "@/lib/auth";

type Step = "email" | "otp" | "details";

export const Route = createFileRoute("/register")({
  component: Register,
});

function Register() {
  const [step, setStep] = useState<Step>("email");
  const [email, setEmail] = useState("");
  const [otp, setOtp] = useState("");
  const [challengeToken, setChallengeToken] = useState("");
  const [emailVerificationToken, setEmailVerificationToken] = useState("");
  const [name, setName] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [resendCooldown, setResendCooldown] = useState(0);
  const navigate = useNavigate();

  useEffect(() => {
    if (resendCooldown === 0) return;
    const timer = window.setInterval(() => {
      setResendCooldown((seconds) => Math.max(seconds - 1, 0));
    }, 1000);
    return () => window.clearInterval(timer);
  }, [resendCooldown]);

  const requestOtp = async () => {
    const response = await post("/api/v1/auth/request-email-otp", { email });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "Failed to send verification code");
    setChallengeToken(data.challengeToken);
    setOtp("");
    setResendCooldown(30);
  };

  const handleEmailSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      await requestOtp();
      setStep("otp");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to send verification code");
    } finally {
      setLoading(false);
    }
  };

  const handleResendOtp = async () => {
    if (loading || resendCooldown > 0) return;
    setError("");
    setLoading(true);

    try {
      await requestOtp();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to resend verification code");
    } finally {
      setLoading(false);
    }
  };

  const handleOtpSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const response = await post("/api/v1/auth/verify-email-otp", {
        email,
        code: otp,
        challengeToken,
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Invalid verification code");
      setEmailVerificationToken(data.emailVerificationToken);
      setStep("details");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Invalid verification code");
    } finally {
      setLoading(false);
    }
  };

  const handleDetailsSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (password.length < 8) {
      setError("Password must be at least 8 characters long");
      return;
    }

    if (password !== confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    setLoading(true);

    try {
      const response = await post("/api/v1/auth/register", {
        fullName: name,
        email,
        password,
        emailVerificationToken,
      });
      const data = await response.json();

      if (response.ok) {
        setToken(data.token);
        setUser(data.user);
        navigate({ to: "/dashboard" });
      } else {
        setError(data.detail || "Registration failed");
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
        <img src="/register-img.png" alt="Register" className="h-full w-full object-cover" />
      </div>
      <div className="flex w-full items-center justify-center lg:w-1/2 min-h-screen">
        <div className="w-full max-w-md p-8">
          <h1 className="text-3xl font-semibold text-primary mb-2">Create Account</h1>
          <p className="text-sm text-muted-foreground mb-8">
            {step === "email" && "Enter your email to get started"}
            {step === "otp" && "Enter the verification code sent to your email"}
            {step === "details" && "Complete your profile"}
          </p>

          {error && (
            <div className="mb-6 p-3 rounded-lg bg-red-50 border border-red-200 text-red-600 text-sm">
              {error}
            </div>
          )}

          {step === "email" && (
            <form onSubmit={handleEmailSubmit} className="space-y-5">
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
              <button
                type="submit"
                disabled={loading}
                className="w-full rounded-full bg-primary px-4 py-3 text-sm font-semibold uppercase tracking-[0.16em] text-primary-foreground transition-opacity hover:opacity-90 disabled:opacity-50"
              >
                {loading ? "Sending..." : "Send Verification Code"}
              </button>
            </form>
          )}

          {step === "otp" && (
            <form onSubmit={handleOtpSubmit} className="space-y-5">
              <div>
                <label htmlFor="otp" className="block text-sm font-medium text-secondary mb-2">
                  Verification Code
                </label>
                <input
                  id="otp"
                  type="text"
                  value={otp}
                  onChange={(e) => setOtp(e.target.value)}
                  className="w-full rounded-lg border border-border bg-background px-4 py-3 text-sm text-primary placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/50"
                  placeholder="Enter 6-digit code"
                  maxLength={6}
                  required
                />
                <p className="mt-2 text-xs text-muted-foreground">Code sent to {email}</p>
              </div>
              <button
                type="submit"
                disabled={loading}
                className="w-full rounded-full bg-primary px-4 py-3 text-sm font-semibold uppercase tracking-[0.16em] text-primary-foreground transition-opacity hover:opacity-90 disabled:opacity-50"
              >
                {loading ? "Verifying..." : "Verify"}
              </button>
              <button
                type="button"
                onClick={handleResendOtp}
                disabled={loading || resendCooldown > 0}
                className="w-full text-xs text-muted-foreground hover:text-primary disabled:cursor-not-allowed disabled:opacity-50"
              >
                {resendCooldown > 0
                  ? `Resend code in ${resendCooldown}s`
                  : loading
                    ? "Sending..."
                    : "Resend verification code"}
              </button>
              <button
                type="button"
                onClick={() => setStep("email")}
                className="w-full text-xs text-muted-foreground hover:text-primary"
              >
                Change email
              </button>
            </form>
          )}

          {step === "details" && (
            <form onSubmit={handleDetailsSubmit} className="space-y-5">
              <div>
                <label htmlFor="name" className="block text-sm font-medium text-secondary mb-2">
                  Full Name
                </label>
                <input
                  id="name"
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full rounded-lg border border-border bg-background px-4 py-3 text-sm text-primary placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/50"
                  placeholder="John Doe"
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
                  minLength={8}
                  required
                />
                <p className="mt-1 text-xs text-muted-foreground">Must be at least 8 characters</p>
              </div>
              <div>
                <label
                  htmlFor="confirmPassword"
                  className="block text-sm font-medium text-secondary mb-2"
                >
                  Confirm Password
                </label>
                <input
                  id="confirmPassword"
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
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
                {loading ? "Creating account..." : "Create Account"}
              </button>
            </form>
          )}

          <p className="mt-6 text-center text-xs text-muted-foreground">
            Already have an account?{" "}
            <a href="/signin" className="text-primary hover:underline">
              Sign in
            </a>
          </p>
        </div>
      </div>
    </div>
  );
}
