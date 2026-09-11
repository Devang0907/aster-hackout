import { Logo } from "./Logo";

const columns = [
  { title: "Product", links: ["Overview", "Leak detection", "Recommendations", "Simulator"] },
  { title: "Company", links: ["About", "Careers", "Contact"] },
  { title: "Resources", links: ["Documentation", "Methodology", "Privacy", "Terms"] },
];

export function SiteFooter() {
  return (
    <footer className="border-t border-border/60 bg-mist/50">
      <div className="mx-auto max-w-[1400px] px-5 py-16 sm:px-8 lg:px-14">
        <div className="grid gap-12 lg:grid-cols-[1.4fr_2fr]">
          <div>
            <Logo />
            <p className="mt-5 max-w-[24rem] text-sm leading-relaxed text-muted-foreground">
              Industrial emission leak-point detection and circular alternative recommendations for
              modern manufacturing.
            </p>
          </div>
          <div className="grid grid-cols-2 gap-8 sm:grid-cols-3">
            {columns.map((c) => (
              <div key={c.title}>
                <p className="text-[0.5625rem] font-semibold uppercase tracking-[0.2em] text-muted-foreground">
                  {c.title}
                </p>
                <ul className="mt-5 space-y-3">
                  {c.links.map((l) => (
                    <li key={l}>
                      <a
                        href="#top"
                        className="text-sm text-secondary transition-colors hover:text-primary"
                      >
                        {l}
                      </a>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>

        <div className="mt-16 flex flex-col gap-3 border-t border-border pt-8 sm:flex-row sm:items-center sm:justify-between">
          <p className="text-xs text-muted-foreground">
            © {new Date().getFullYear()} CarbonLoop. All rights reserved.
          </p>
          <p className="text-xs text-muted-foreground">
            All figures shown are illustrative sample data.
          </p>
        </div>
      </div>
    </footer>
  );
}
