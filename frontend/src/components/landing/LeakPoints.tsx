import { motion } from "framer-motion";
import { Reveal } from "./Reveal";

const rows = [
  { n: "01", label: "Electricity", pct: 42, sev: "High" },
  { n: "02", label: "Diesel", pct: 28, sev: "High" },
  { n: "03", label: "Materials", pct: 21, sev: "Medium" },
  { n: "04", label: "Transport", pct: 6, sev: "Low" },
  { n: "05", label: "Waste", pct: 3, sev: "Low" },
];

const sevStyle: Record<string, string> = {
  High: "bg-primary text-primary-foreground",
  Medium: "bg-sage text-primary",
  Low: "bg-mist text-muted-foreground",
};

export function LeakPoints() {
  return (
    <section id="impact" className="border-t border-border/60 py-24 sm:py-32">
      <div className="mx-auto max-w-[1400px] px-5 sm:px-8 lg:px-14">
        <div className="grid gap-14 lg:grid-cols-[0.85fr_1.15fr] lg:items-center lg:gap-20">
          <Reveal>
            <p className="eyebrow">Emission leak points</p>
            <h2 className="display-lg mt-6 text-primary">
              Stop guessing.
              <br />
              Find the leak points.
            </h2>
            <p className="mt-6 max-w-[30rem] text-[0.9375rem] leading-relaxed text-muted-foreground">
              CarbonLoop ranks every emission source in your operation by contribution and
              severity, so the next decision is obvious rather than debatable.
            </p>
          </Reveal>

          <Reveal delay={0.12}>
            <div className="rounded-3xl border border-border bg-surface p-6 shadow-editorial sm:p-9">
              <div className="flex items-start justify-between gap-4 border-b border-border pb-6">
                <div>
                  <p className="text-[0.5625rem] font-semibold uppercase tracking-[0.2em] text-muted-foreground">
                    Total footprint
                  </p>
                  <p className="mt-2 text-3xl font-medium tracking-[-0.03em] text-primary sm:text-4xl">
                    1,240 <span className="text-lg text-muted-foreground">tCO₂e</span>
                  </p>
                </div>
                <span className="rounded-full border border-border px-3 py-1.5 text-[0.5625rem] font-semibold uppercase tracking-[0.16em] text-muted-foreground">
                  Sample analysis
                </span>
              </div>

              <div className="mt-6 space-y-5">
                {rows.map((r, i) => (
                  <div key={r.n}>
                    <div className="grid grid-cols-[auto_minmax(0,1fr)_auto] items-center gap-3">
                      <span className="text-[0.625rem] font-semibold tracking-[0.14em] text-muted-foreground">
                        {r.n}
                      </span>
                      <span className="truncate text-sm font-medium text-primary">{r.label}</span>
                      <span className="flex items-center gap-3">
                        <span className="text-sm tabular-nums text-secondary">{r.pct}%</span>
                        <span
                          className={`rounded-full px-2.5 py-1 text-[0.5rem] font-semibold uppercase tracking-[0.14em] ${sevStyle[r.sev]}`}
                        >
                          {r.sev}
                        </span>
                      </span>
                    </div>
                    <div className="mt-2.5 h-1.5 overflow-hidden rounded-full bg-mist">
                      <motion.div
                        className="h-full rounded-full bg-secondary"
                        initial={{ width: 0 }}
                        whileInView={{ width: `${r.pct}%` }}
                        viewport={{ once: true }}
                        transition={{ duration: 1.1, delay: 0.15 + i * 0.1, ease: [0.22, 1, 0.36, 1] }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </Reveal>
        </div>
      </div>
    </section>
  );
}
