import { ArrowRight } from "lucide-react";
import { Reveal } from "./Reveal";

export function FinalCta() {
  return (
    <section id="cta" className="relative overflow-hidden border-t border-border/60 py-28 sm:py-40">
      <div className="pointer-events-none absolute inset-x-0 bottom-0 h-[420px] topo-grid opacity-30" />
      <div className="relative mx-auto max-w-[900px] px-5 text-center sm:px-8">
        <Reveal>
          <h2 className="display-lg text-primary">
            Every factory has hidden emissions.
            <br />
            <span className="text-muted-foreground">Find yours.</span>
          </h2>
          <p className="mx-auto mt-7 max-w-[36rem] text-[0.9375rem] leading-relaxed text-muted-foreground">
            Start with your existing operational data and get a ranked view of leak points and
            circular actions.
          </p>
          <div className="mt-10 flex flex-col items-center justify-center gap-3 sm:flex-row">
            <a
              href="#top"
              className="group inline-flex w-full items-center justify-center gap-2 rounded-full bg-primary px-8 py-4 text-sm font-medium text-primary-foreground transition-opacity hover:opacity-90 sm:w-auto"
            >
              Start Free Analysis
              <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
            </a>
            <a
              href="#how-it-works"
              className="inline-flex w-full items-center justify-center rounded-full border border-border bg-surface px-8 py-4 text-sm font-medium text-primary transition-colors hover:bg-mist sm:w-auto"
            >
              See How It Works
            </a>
          </div>
        </Reveal>
      </div>
    </section>
  );
}
