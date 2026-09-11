import { Reveal } from "./Reveal";

const values = [
  { title: "Cut operational costs", copy: "Reduce energy, material and waste spend where it hurts the most." },
  { title: "Prepare for regulation", copy: "Build the emissions visibility that reporting frameworks increasingly expect." },
  { title: "Strengthen supply chains", copy: "Give buyers and partners defensible numbers instead of estimates." },
  { title: "Improve efficiency", copy: "Turn process losses into measurable recovery opportunities." },
  { title: "Support ESG goals", copy: "Track reduction progress against internal sustainability targets." },
  { title: "Prioritize with confidence", copy: "Rank actions by impact, cost and feasibility before committing capital." },
];

const audiences = [
  "Factory owners",
  "Sustainability teams",
  "Plant managers",
  "Manufacturing startups",
  "Industrial consultants",
];

export function BusinessValue() {
  return (
    <section className="border-t border-border/60 py-24 sm:py-32">
      <div className="mx-auto max-w-[1400px] px-5 sm:px-8 lg:px-14">
        <Reveal>
          <p className="eyebrow">Business value</p>
          <h2 className="display-lg mt-6 max-w-[22ch] text-primary">
            Sustainability that reads like an operations decision.
          </h2>
        </Reveal>

        <div className="mt-16 grid gap-px overflow-hidden rounded-3xl border border-border bg-border sm:grid-cols-2 lg:grid-cols-3">
          {values.map((v, i) => (
            <Reveal key={v.title} delay={(i % 3) * 0.08}>
              <div className="h-full bg-surface p-8 transition-colors hover:bg-mist/60">
                <h3 className="text-base font-medium tracking-[-0.015em] text-primary">
                  {v.title}
                </h3>
                <p className="mt-3 text-sm leading-relaxed text-muted-foreground">{v.copy}</p>
              </div>
            </Reveal>
          ))}
        </div>

        <Reveal delay={0.1}>
          <div className="mt-16 grid gap-8 rounded-3xl bg-mist/60 p-8 sm:p-12 lg:grid-cols-[auto_minmax(0,1fr)] lg:items-center lg:gap-16">
            <p className="text-[0.6875rem] font-semibold uppercase tracking-[0.2em] text-secondary">
              Built for
            </p>
            <div className="flex flex-wrap gap-2.5">
              {audiences.map((a) => (
                <span
                  key={a}
                  className="rounded-full border border-border bg-surface px-4 py-2 text-sm text-secondary"
                >
                  {a}
                </span>
              ))}
            </div>
          </div>
        </Reveal>
      </div>
    </section>
  );
}
