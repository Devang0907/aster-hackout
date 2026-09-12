export function Logo({ tone = "dark" }: { tone?: "dark" | "light" }) {
  const color = tone === "dark" ? "text-primary" : "text-background";
  return (
    <span className={`flex items-center gap-2.5 ${color}`}>
      <svg viewBox="0 0 32 32" className="h-6 w-6" fill="none" aria-hidden="true">
        <circle cx="16" cy="16" r="11" stroke="currentColor" strokeWidth="1.4" opacity="0.35" />
        <path
          d="M25 11.5A11 11 0 1 0 26.5 18"
          stroke="currentColor"
          strokeWidth="1.6"
          strokeLinecap="round"
        />
        <circle cx="16" cy="16" r="3.4" fill="currentColor" />
      </svg>
      <span className="text-[1.0625rem] font-semibold tracking-[-0.02em]">CarbonLoop</span>
    </span>
  );
}
