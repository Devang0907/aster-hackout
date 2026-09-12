import { motion } from "framer-motion";

export function Hero() {
  return (
    <section
      id="top"
      className="relative flex min-h-svh flex-col items-center justify-start overflow-hidden pt-24 sm:pt-28"
    >
      <img
        src="/bg.png"
        alt="Illustrated green landscape surrounding a calm lake and distant contour-lined hills"
        width={1573}
        height={1000}
        fetchPriority="high"
        className="absolute inset-0 h-full w-full object-cover object-center"
      />
      <div className="absolute inset-0 bg-background/10" />
      <div className="relative mx-auto w-full max-w-[720px] px-5 text-center sm:px-8">
        <motion.h1
          className="mx-auto max-w-[24ch] text-3xl font-medium leading-snug tracking-tight text-primary sm:text-4xl md:text-5xl"
          initial={{ opacity: 0, y: 18 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.9, delay: 0.08, ease: [0.22, 1, 0.36, 1] }}
        >
          Turn Factory Emissions
          <br />
          Into Your Next Advantage.
        </motion.h1>
      </div>
    </section>
  );
}
