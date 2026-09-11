import { Zap, Boxes, Truck, Recycle } from "lucide-react";
import { Reveal } from "./Reveal";

const cards = [
  {
    n: "01",
    title: "Energy",
    copy: "Understand the real carbon cost of electricity and fuel.",
    Icon: Zap,
  },
  {
    n: "02",
    title: "Materials",
    copy: "Find high-impact materials and lower-carbon alternatives.",
    Icon: Boxes,
  },
  {
    n: "03",
    title: "Logistics",
    copy: "Reveal emissions hidden inside transportation and supply chains.",
    Icon: Truck,
  },
  {
    n: "04",
    title: "Waste",
    copy: "Turn waste streams into measurable circular opportunities.",
    Icon: Recycle,
  },
];

export function Problem() {
  return (
    <section id="product" className="border-t border-border/60 py-24 sm:py-32">
      <div className="mx-auto max-w-[1400px] px-5 sm:px-8 lg:px-14">
        <div className="grid gap-10 lg:grid-cols-[1.1fr_0.9fr] lg:items-end">
          <Reveal>
            <h2 className="display-lg text-primary">
              Most factories know
              <br />
              they emit carbon.
              <br />
              <span className="text-muted-foreground">Few know where it comes from.</span>
            </h2>
          </Reveal>
          <Reveal delay={0.1}>
            <p className="max-w-[34rem] text-[0.9375rem] leading-relaxed text-muted-foreground">
              Energy, materials, waste and logistics all contribute to your footprint. CarbonLoop
              turns disconnected operational data into a clear picture of where emissions originate
              — and where action matters most.
            </p>
          </Reveal>
        </div>

        <div className="mt-16 grid gap-px overflow-hidden rounded-3xl border border-border bg-border sm:grid-cols-2 lg:grid-cols-4">
          {cards.map((c, i) => (
            <Reveal key={c.title} delay={i * 0.08}>
              <div className="group h-full bg-surface p-8 transition-colors hover:bg-mist/60">
                <div className="flex items-center justify-between">
                  <span className="text-[0.6875rem] font-semibold tracking-[0.18em] text-muted-foreground">
                    {c.n}
                  </span>
                  <c.Icon
                    className="h-5 w-5 text-secondary/70 transition-transform duration-500 group-hover:-translate-y-0.5"
                    strokeWidth={1.4}
                  />
                </div>
                <h3 className="mt-16 text-xl font-medium tracking-[-0.02em] text-primary">
                  {c.title}
                </h3>
                <p className="mt-3 text-sm leading-relaxed text-muted-foreground">{c.copy}</p>
              </div>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  );
}
