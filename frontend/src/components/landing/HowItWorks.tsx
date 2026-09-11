import { Reveal } from "./Reveal";

const steps = [
  {
    n: "01",
    title: "Connect",
    copy: "Enter your factory's energy, material, waste and logistics data.",
  },
  {
    n: "02",
    title: "Detect",
    copy: "CarbonLoop calculates your footprint and ranks the biggest emission leak points.",
  },
  {
    n: "03",
    title: "Recommend",
    copy: "AI identifies practical circular alternatives based on emissions, cost and feasibility.",
  },
  {
    n: "04",
    title: "Act",
    copy: "Compare scenarios, estimate savings and prioritize the changes with the highest impact.",
  },
];

export function HowItWorks() {
  return (
    <section id="how-it-works" className="border-t border-border/60 bg-mist/40 py-24 sm:py-32">
      <div className="mx-auto max-w-[1400px] px-5 sm:px-8 lg:px-14">
        <Reveal>
          <p className="eyebrow">How it works</p>
          <h2 className="display-lg mt-6 max-w-[24ch] text-primary">
            From raw factory data to a clear action plan.
          </h2>
        </Reveal>

        <div className="relative mt-20">
          <div className="absolute left-0 right-0 top-[18px] hidden h-px bg-border lg:block" />
          <div className="grid gap-14 lg:grid-cols-4 lg:gap-8">
            {steps.map((s, i) => (
              <Reveal key={s.n} delay={i * 0.1}>
                <div className="relative lg:pr-8">
                  <div className="flex items-center gap-4">
                    <span className="grid h-9 w-9 shrink-0 place-items-center rounded-full border border-border bg-background text-[0.625rem] font-semibold tracking-[0.12em] text-secondary">
                      {s.n}
                    </span>
                    <span className="h-px flex-1 bg-border lg:hidden" />
                  </div>
                  <h3 className="mt-7 text-[0.6875rem] font-semibold uppercase tracking-[0.2em] text-primary">
                    {s.title}
                  </h3>
                  <p className="mt-3 max-w-[26rem] text-sm leading-relaxed text-muted-foreground">
                    {s.copy}
                  </p>
                </div>
              </Reveal>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
