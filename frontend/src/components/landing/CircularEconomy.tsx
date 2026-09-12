import { motion } from "framer-motion";
import { Reveal } from "./Reveal";

const nodes = [
  { label: "Input", copy: "Energy & raw materials" },
  { label: "Production", copy: "Process emissions" },
  { label: "Waste", copy: "By-products & losses" },
  { label: "Recovery", copy: "Reuse & recycling" },
  { label: "Reuse", copy: "Back into production" },
];

export function CircularEconomy() {
  return (
    <section className="border-t border-border/60 bg-primary py-24 text-primary-foreground sm:py-32">
      <div className="mx-auto max-w-[1400px] px-5 sm:px-8 lg:px-14">
        <div className="grid gap-14 lg:grid-cols-[0.9fr_1.1fr] lg:items-center lg:gap-20">
          <Reveal>
            <p className="text-[0.6875rem] font-semibold uppercase tracking-[0.22em] text-primary-foreground/55">
              Circular economy
            </p>
            <h2 className="display-lg mt-6">
              Linear industry ends in waste.
              <br />
              Circular industry compounds value.
            </h2>
            <p className="mt-6 max-w-[32rem] text-[0.9375rem] leading-relaxed text-primary-foreground/65">
              CarbonLoop maps every stage of your material and energy flow, then closes the loop by
              routing waste and losses back into productive use.
            </p>
          </Reveal>

          <Reveal delay={0.12}>
            <div className="relative">
              <div className="grid gap-px overflow-hidden rounded-3xl border border-primary-foreground/15 bg-primary-foreground/15 sm:grid-cols-2">
                {nodes.map((n, i) => (
                  <motion.div
                    key={n.label}
                    className={`bg-primary p-7 ${i === nodes.length - 1 ? "sm:col-span-2" : ""}`}
                    initial={{ opacity: 0, y: 16 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.7, delay: i * 0.1 }}
                  >
                    <div className="flex items-center gap-3">
                      <span className="h-1.5 w-1.5 rounded-full bg-primary-foreground/70" />
                      <p className="text-[0.625rem] font-semibold uppercase tracking-[0.2em]">
                        {n.label}
                      </p>
                    </div>
                    <p className="mt-4 text-sm text-primary-foreground/60">{n.copy}</p>
                  </motion.div>
                ))}
              </div>
            </div>
          </Reveal>
        </div>
      </div>
    </section>
  );
}
