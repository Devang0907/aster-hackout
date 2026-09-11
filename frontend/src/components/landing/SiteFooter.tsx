import { Logo } from "./Logo";

const sections = [
  { label: "Product", href: "#product" },
  { label: "How it works", href: "#how-it-works" },
  { label: "Solutions", href: "#solutions" },
  { label: "Impact", href: "#impact" },
];

export function SiteFooter() {
  return (
    <footer className="border-t border-border/60 bg-gradient-to-b from-mist/30 to-background">
      <div className="mx-auto max-w-[1400px] px-5 py-20 sm:px-8 lg:px-14">
        <div className="grid gap-12 lg:grid-cols-[1fr_1fr_1fr]">
          <div className="space-y-6">
            <Logo />
            <p className="max-w-[28rem] text-sm leading-relaxed text-muted-foreground">
              Industrial emission leak-point detection and circular alternative recommendations for
              modern manufacturing.
            </p>
          </div>
          <div>
            <p className="text-[0.5625rem] font-semibold uppercase tracking-[0.2em] text-secondary">
              Sections
            </p>
            <ul className="mt-6 space-y-4">
              {sections.map((s) => (
                <li key={s.label}>
                  <a
                    href={s.href}
                    className="text-sm text-muted-foreground transition-colors hover:text-primary hover:underline decoration-1 underline-offset-4"
                  >
                    {s.label}
                  </a>
                </li>
              ))}
            </ul>
          </div>
          <div className="space-y-6">
            <p className="text-[0.5625rem] font-semibold uppercase tracking-[0.2em] text-secondary">
              Get Started
            </p>
            <p className="text-sm text-muted-foreground">
              Ready to transform your factory emissions into a competitive advantage?
            </p>
            <a
              href="#cta"
              className="inline-block rounded-full bg-primary px-6 py-3 text-xs font-semibold uppercase tracking-[0.16em] text-primary-foreground transition-opacity hover:opacity-90"
            >
              Start Free Trial
            </a>
          </div>
        </div>

        <div className="mt-16 flex flex-col gap-4 border-t border-border/40 pt-8 sm:flex-row sm:items-center sm:justify-between">
          <p className="text-xs text-muted-foreground">
            © {new Date().getFullYear()} CarbonLoop. All rights reserved.
          </p>
          <div className="flex gap-6 text-xs text-muted-foreground">
            <a href="#top" className="transition-colors hover:text-primary">
              Privacy Policy
            </a>
            <a href="#top" className="transition-colors hover:text-primary">
              Terms of Service
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
}
