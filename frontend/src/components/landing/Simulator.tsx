import { useState } from "react";
import { motion } from "framer-motion";
import { Reveal } from "./Reveal";

const BASE = 1240;

export function Simulator() {
  const [renewable, setRenewable] = useState(20);
  const [recycled, setRecycled] = useState(15);
  const [logistics, setLogistics] = useState(10);

  const reduction = Math.round(
    BASE * (0.42 * (renewable / 100) + 0.21 * (recycled / 100) * 0.8 + 0.06 * (logistics / 100)),
  );
  const projected = BASE - reduction;
  const pct = Math.round((reduction / BASE) * 100);

  const sliders = [
    { label: "Renewable energy share", value: renewable, set: setRenewable, suffix: "%" },
    { label: "Recycled material share", value: recycled, set: setRecycled, suffix: "%" },
    { label: "Logistics optimization", value: logistics, set: setLogistics, suffix: "%" },
  ];

  return (
    <section id="simulator" className="border-t border-border/60 py-24 sm:py-32">
      <div className="mx-auto max-w-[1400px] px-5 sm:px-8 lg:px-14">
        <div className="grid gap-14 lg:grid-cols-2 lg:items-center lg:gap-20">
          <Reveal>
            <p className="eyebrow">What-if simulator</p>
            <h2 className="display-lg mt-6 text-primary">See the impact before you invest.</h2>
            <p className="mt-6 max-w-[32rem] text-[0.9375rem] leading-relaxed text-muted-foreground">
              Adjust operational levers and watch the projected footprint respond instantly. Values
              shown are illustrative estimates from sample factory data.
            </p>

            <div className="mt-10 space-y-8">
              {sliders.map((s) => (
                <div key={s.label}>
                  <div className="grid grid-cols-[minmax(0,1fr)_auto] items-center gap-4">
                    <label htmlFor={s.label} className="truncate text-sm text-secondary">
                      {s.label}
                    </label>
                    <span className="shrink-0 text-sm font-medium tabular-nums text-primary">
                      {s.value}
                      {s.suffix}
                    </span>
                  </div>
                  <input
                    id={s.label}
                    type="range"
                    min={0}
                    max={100}
                    value={s.value}
                    onChange={(e) => s.set(Number(e.target.value))}
                    className="mt-3 h-1 w-full cursor-pointer appearance-none rounded-full bg-mist accent-secondary"
                  />
                </div>
              ))}
            </div>
          </Reveal>

          <Reveal delay={0.12}>
            <div className="rounded-3xl border border-border bg-surface p-8 shadow-editorial sm:p-10">
              <p className="text-[0.5625rem] font-semibold uppercase tracking-[0.2em] text-muted-foreground">
                Projected annual footprint
              </p>
              <motion.p
                key={projected}
                initial={{ opacity: 0.4, y: 6 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.35 }}
                className="mt-4 text-5xl font-medium tracking-[-0.04em] text-primary sm:text-6xl"
              >
                {projected.toLocaleString()}
                <span className="ml-2 text-base text-muted-foreground">tCO₂e</span>
              </motion.p>

              <div className="mt-8 h-2 overflow-hidden rounded-full bg-mist">
                <motion.div
                  className="h-full rounded-full bg-secondary"
                  animate={{ width: `${100 - pct}%` }}
                  transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
                />
              </div>

              <div className="mt-8 grid gap-px overflow-hidden rounded-2xl border border-border bg-border sm:grid-cols-3">
                {[
                  ["Baseline", `${BASE.toLocaleString()} tCO₂e`],
                  ["Reduction", `${reduction.toLocaleString()} tCO₂e`],
                  ["Change", `−${pct}%`],
                ].map(([k, v]) => (
                  <div key={k} className="bg-surface px-5 py-5">
                    <p className="text-[0.5625rem] font-semibold uppercase tracking-[0.16em] text-muted-foreground">
                      {k}
                    </p>
                    <p className="mt-2 text-sm font-medium tabular-nums text-primary">{v}</p>
                  </div>
                ))}
              </div>

              <p className="mt-6 text-xs leading-relaxed text-muted-foreground">
                Estimates are modelled on sample data and are for illustration only.
              </p>
            </div>
          </Reveal>
        </div>
      </div>
    </section>
  );
}
