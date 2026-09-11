import { ArrowUpRight } from "lucide-react";
import { Reveal } from "./Reveal";

const recs = [
  {
    n: "Recommendation 01",
    title: "Switch to recycled polyester",
    reduction: "32 tCO₂e / year",
    stats: [
      ["Estimated investment", "₹2.0L"],
      ["Annual savings", "₹2.5L"],
      ["Payback", "9.6 months"],
    ],
    feasibility: 92,
  },
  {
    n: "Recommendation 02",
    title: "Recover waste heat",
    reduction: "86 tCO₂e / year",
    stats: [
      ["Estimated investment", "₹8.4L"],
      ["Annual savings", "₹7.2L"],
      ["Payback", "14 months"],
    ],
    feasibility: 78,
  },
  {
    n: "Recommendation 03",
    title: "Increase renewable electricity",
    reduction: "120 tCO₂e / year",
    stats: [
      ["Estimated investment", "₹14.0L"],
      ["Annual savings", "₹9.8L"],
      ["Payback", "17 months"],
    ],
    feasibility: 85,
  },
];

export function Recommendations() {
  return (
    <section id="solutions" className="border-t border-border/60 bg-mist/40 py-24 sm:py-32">
      <div className="mx-auto max-w-[1400px] px-5 sm:px-8 lg:px-14">
        <Reveal>
          <p className="eyebrow">Circular recommendations</p>
          <h2 className="display-lg mt-6 max-w-[20ch] text-primary">
            Don't just measure emissions. Know what to do next.
          </h2>
        </Reveal>

        <div className="mt-16 grid gap-6 lg:grid-cols-3">
          {recs.map((r, i) => (
            <Reveal key={r.title} delay={i * 0.1}>
              <article className="flex h-full flex-col rounded-3xl border border-border bg-surface p-8 transition-shadow duration-500 hover:shadow-float">
                <p className="text-[0.5625rem] font-semibold uppercase tracking-[0.2em] text-muted-foreground">
                  {r.n}
                </p>
                <h3 className="mt-5 text-xl font-medium leading-snug tracking-[-0.02em] text-primary">
                  {r.title}
                </h3>

                <div className="mt-7 rounded-2xl bg-sage/60 px-5 py-4">
                  <p className="text-[0.5625rem] font-semibold uppercase tracking-[0.18em] text-secondary/80">
                    Potential CO₂ reduction
                  </p>
                  <p className="mt-1.5 text-lg font-medium tracking-[-0.02em] text-primary">
                    {r.reduction}
                  </p>
                </div>

                <dl className="mt-6 space-y-3 border-t border-border pt-6">
                  {r.stats.map(([k, v]) => (
                    <div key={k} className="flex items-center justify-between gap-4 text-sm">
                      <dt className="text-muted-foreground">{k}</dt>
                      <dd className="font-medium text-primary">{v}</dd>
                    </div>
                  ))}
                </dl>

                <div className="mt-6">
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-muted-foreground">Feasibility</span>
                    <span className="tabular-nums text-secondary">{r.feasibility}%</span>
                  </div>
                  <div className="mt-2 h-1 overflow-hidden rounded-full bg-mist">
                    <div
                      className="h-full rounded-full bg-secondary"
                      style={{ width: `${r.feasibility}%` }}
                    />
                  </div>
                </div>

                <a
                  href="#cta"
                  className="group mt-8 inline-flex items-center gap-1.5 text-sm font-medium text-primary"
                >
                  View recommendation
                  <ArrowUpRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5 group-hover:-translate-y-0.5" />
                </a>
              </article>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  );
}
