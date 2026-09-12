import { createFileRoute, Link } from "@tanstack/react-router";
import { useState } from "react";
import { post } from "@/lib/api";

export const Route = createFileRoute("/reset-password")({
  component: ResetPassword,
});

type Step = "email" | "code";

function ResetPassword() {
  const [step, setStep] = useState<Step>("email");
  const [email, setEmail] = useState("");
  const [code, setCode] = useState("");
  const [challengeToken, setChallengeToken] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleRequest = async (event: React.FormEvent) => {
    event.preventDefault();
    setError("");
    setMessage("");
    setLoading(true);

    try {
      const response = await post("/api/v1/auth/request-password-reset", { email });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Unable to request password reset");
      setChallengeToken(data.challengeToken);
      setMessage("If this email has an account, a reset code has been sent.");
      setStep("code");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to request password reset");
    } finally {
      setLoading(false);
    }
  };

  const handleReset = async (event: React.FormEvent) => {
    event.preventDefault();
    setError("");
    setMessage("");

    if (newPassword !== confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    setLoading(true);
    try {
      const response = await post("/api/v1/auth/confirm-password-reset", {
        email,
        code,
        challengeToken,
        newPassword,
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Unable to reset password");
      setMessage("Password reset successfully. You can now sign in.");
      setStep("email");
      setCode("");
      setChallengeToken("");
      setNewPassword("");
      setConfirmPassword("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to reset password");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex bg-background">
      <div className="hidden lg:block lg:w-1/2 h-screen overflow-hidden">
        <img src="/sign-img.png" alt="Reset password" className="h-full w-full object-cover" />
      </div>
      <div className="flex w-full items-center justify-center lg:w-1/2 min-h-screen">
        <div className="w-full max-w-md p-8">
          <h1 className="text-3xl font-semibold text-primary mb-2">Reset Password</h1>
          <p className="text-sm text-muted-foreground mb-8">
            {step === "email"
              ? "Enter your email to receive a reset code"
              : "Enter the code from your email and choose a new password"}
          </p>

          {message && (
            <div className="mb-6 p-3 rounded-lg bg-green-50 border border-green-200 text-green-700 text-sm">
              {message}
            </div>
          )}
          {error && (
            <div className="mb-6 p-3 rounded-lg bg-red-50 border border-red-200 text-red-600 text-sm">
              {error}
            </div>
          )}

          {step === "email" ? (
            <form onSubmit={handleRequest} className="space-y-5">
              <div>
                <label
                  htmlFor="reset-email"
                  className="block text-sm font-medium text-secondary mb-2"
                >
                  Email
                </label>
                <input
                  id="reset-email"
                  type="email"
                  value={email}
                  onChange={(event) => setEmail(event.target.value)}
                  className="w-full rounded-lg border border-border bg-background px-4 py-3 text-sm text-primary focus:outline-none focus:ring-2 focus:ring-primary/50"
                  required
                />
              </div>
              <button
                type="submit"
                disabled={loading}
                className="w-full rounded-full bg-primary px-4 py-3 text-sm font-semibold uppercase tracking-[0.16em] text-primary-foreground transition-opacity hover:opacity-90 disabled:opacity-50"
              >
                {loading ? "Sending..." : "Send Reset Code"}
              </button>
            </form>
          ) : (
            <form onSubmit={handleReset} className="space-y-5">
              <div>
                <label
                  htmlFor="reset-code"
                  className="block text-sm font-medium text-secondary mb-2"
                >
                  Reset Code
                </label>
                <input
                  id="reset-code"
                  inputMode="numeric"
                  value={code}
                  onChange={(event) => setCode(event.target.value)}
                  className="w-full rounded-lg border border-border bg-background px-4 py-3 text-sm text-primary focus:outline-none focus:ring-2 focus:ring-primary/50"
                  placeholder="Enter 6-digit code"
                  maxLength={6}
                  required
                />
              </div>
              <div>
                <label
                  htmlFor="new-password"
                  className="block text-sm font-medium text-secondary mb-2"
                >
                  New Password
                </label>
                <input
                  id="new-password"
                  type="password"
                  value={newPassword}
                  onChange={(event) => setNewPassword(event.target.value)}
                  className="w-full rounded-lg border border-border bg-background px-4 py-3 text-sm text-primary focus:outline-none focus:ring-2 focus:ring-primary/50"
                  minLength={8}
                  required
                />
              </div>
              <div>
                <label
                  htmlFor="confirm-password"
                  className="block text-sm font-medium text-secondary mb-2"
                >
                  Confirm Password
                </label>
                <input
                  id="confirm-password"
                  type="password"
                  value={confirmPassword}
                  onChange={(event) => setConfirmPassword(event.target.value)}
                  className="w-full rounded-lg border border-border bg-background px-4 py-3 text-sm text-primary focus:outline-none focus:ring-2 focus:ring-primary/50"
                  minLength={8}
                  required
                />
              </div>
              <button
                type="submit"
                disabled={loading}
                className="w-full rounded-full bg-primary px-4 py-3 text-sm font-semibold uppercase tracking-[0.16em] text-primary-foreground transition-opacity hover:opacity-90 disabled:opacity-50"
              >
                {loading ? "Resetting..." : "Reset Password"}
              </button>
              <button
                type="button"
                onClick={() => setStep("email")}
                className="w-full text-xs text-muted-foreground hover:text-primary"
              >
                Use a different email
              </button>
            </form>
          )}

          <p className="mt-6 text-center text-xs text-muted-foreground">
            <Link to="/signin" className="text-primary hover:underline">
              Back to sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
