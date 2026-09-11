import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";

type Step = "email" | "otp" | "details";

export const Route = createFileRoute("/register")({
  component: Register,
});

function Register() {
  const [step, setStep] = useState<Step>("email");
  const [email, setEmail] = useState("");
  const [otp, setOtp] = useState("");
  const [name, setName] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const handleEmailSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Simulate sending OTP
    console.log("Sending OTP to:", email);
    setStep("otp");
  };

  const handleOtpSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Simulate OTP verification
    console.log("Verifying OTP:", otp);
    setStep("details");
  };

  const handleDetailsSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (password !== confirmPassword) {
      alert("Passwords do not match");
      return;
    }
    console.log("Registration complete:", { email, name, password });
  };

  return (
    <div className="min-h-screen flex bg-background">
      <div className="hidden lg:block lg:w-1/2 h-screen overflow-hidden">
        <img
          src="/register-img.png"
          alt="Register"
          className="h-full w-full object-cover"
        />
      </div>
      <div className="flex w-full items-center justify-center lg:w-1/2 min-h-screen">
        <div className="w-full max-w-md p-8">
          <h1 className="text-3xl font-semibold text-primary mb-2">Create Account</h1>
          <p className="text-sm text-muted-foreground mb-8">
            {step === "email" && "Enter your email to get started"}
            {step === "otp" && "Enter the verification code sent to your email"}
            {step === "details" && "Complete your profile"}
          </p>

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
                className="w-full rounded-full bg-primary px-4 py-3 text-sm font-semibold uppercase tracking-[0.16em] text-primary-foreground transition-opacity hover:opacity-90"
              >
                Send Verification Code
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
                <p className="mt-2 text-xs text-muted-foreground">
                  Code sent to {email}
                </p>
              </div>
              <button
                type="submit"
                className="w-full rounded-full bg-primary px-4 py-3 text-sm font-semibold uppercase tracking-[0.16em] text-primary-foreground transition-opacity hover:opacity-90"
              >
                Verify
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
                  required
                />
              </div>
              <div>
                <label htmlFor="confirmPassword" className="block text-sm font-medium text-secondary mb-2">
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
                className="w-full rounded-full bg-primary px-4 py-3 text-sm font-semibold uppercase tracking-[0.16em] text-primary-foreground transition-opacity hover:opacity-90"
              >
                Create Account
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
