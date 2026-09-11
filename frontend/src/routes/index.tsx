import { createFileRoute } from "@tanstack/react-router";
import { Nav } from "@/components/landing/Nav";
import { Hero } from "@/components/landing/Hero";
import { Problem } from "@/components/landing/Problem";
import { HowItWorks } from "@/components/landing/HowItWorks";
import { LeakPoints } from "@/components/landing/LeakPoints";
import { Recommendations } from "@/components/landing/Recommendations";
import { CircularEconomy } from "@/components/landing/CircularEconomy";
import { BusinessValue } from "@/components/landing/BusinessValue";
import { FinalCta } from "@/components/landing/FinalCta";
import { SiteFooter } from "@/components/landing/SiteFooter";

const title = "CarbonLoop — Industrial Emission Leak-Point Detector";
const description =
  "CarbonLoop finds where factory emissions come from, ranks the biggest leak points, and recommends circular alternatives with estimated cost, savings and CO₂ reduction.";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title },
      { name: "description", content: description },
      { property: "og:title", content: title },
      { property: "og:description", content: description },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
  }),
  component: Index,
});

function Index() {
  return (
    <div className="min-h-screen bg-background">
      <Nav />
      <main>
        <Hero />
        <Problem />
        <HowItWorks />
        <LeakPoints />
        <Recommendations />
        <CircularEconomy />
        <BusinessValue />
        <FinalCta />
      </main>
      <SiteFooter />
    </div>
  );
}
