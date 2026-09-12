import { createFileRoute } from "@tanstack/react-router";
import { Nav } from "@/components/landing/Nav";
import { SiteFooter } from "@/components/landing/SiteFooter";

const title = "Privacy Policy — CarbonLoop";
const description = "CarbonLoop's privacy policy and how we handle your data.";

export const Route = createFileRoute("/privacy-policy")({
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
  component: PrivacyPolicy,
});

function PrivacyPolicy() {
  return (
    <div className="min-h-screen bg-background">
      <Nav />
      <main className="mx-auto max-w-[1400px] px-5 py-24 sm:px-8 lg:px-14">
        <div className="max-w-3xl">
          <h1 className="text-4xl font-bold tracking-tight text-foreground sm:text-5xl">
            Privacy Policy
          </h1>
          <p className="mt-4 text-sm text-muted-foreground">
            Last updated: {new Date().toLocaleDateString()}
          </p>

          <div className="mt-12 space-y-8">
            <section>
              <h2 className="text-2xl font-semibold text-foreground">
                1. Information We Collect
              </h2>
              <p className="mt-4 text-sm leading-relaxed text-muted-foreground">
                CarbonLoop collects information you provide directly to us, such as when you create an account,
                register for our services, or communicate with us. This may include your name, email address,
                company information, and other relevant details necessary to provide our industrial emission
                detection and circular alternative recommendation services.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-foreground">
                2. How We Use Your Information
              </h2>
              <p className="mt-4 text-sm leading-relaxed text-muted-foreground">
                We use the information we collect to provide, maintain, and improve our services, including
                analyzing factory emissions data, generating leak-point detection reports, and recommending
                circular alternatives. We also use your information to communicate with you about our services,
                respond to your inquiries, and ensure the security of our platform.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-foreground">
                3. Data Security
              </h2>
              <p className="mt-4 text-sm leading-relaxed text-muted-foreground">
                We implement appropriate technical and organizational measures to protect your data against
                unauthorized access, alteration, disclosure, or destruction. Your data is stored securely and
                transmitted using industry-standard encryption protocols.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-foreground">
                4. Data Sharing
              </h2>
              <p className="mt-4 text-sm leading-relaxed text-muted-foreground">
                We do not sell, trade, or rent your personal identification information to others. We may share
                your data with trusted third parties who assist us in operating our platform, conducting our business,
                or servicing you, subject to strict confidentiality obligations. We may also disclose information
                when required by law or to protect our rights, property, or safety.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-foreground">
                5. Your Rights
              </h2>
              <p className="mt-4 text-sm leading-relaxed text-muted-foreground">
                You have the right to access, correct, update, or delete your personal information. You may also
                opt out of certain communications from us. To exercise these rights, please contact us through
                the channels provided in our platform.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-foreground">
                6. Changes to This Policy
              </h2>
              <p className="mt-4 text-sm leading-relaxed text-muted-foreground">
                We may update this privacy policy from time to time. We will notify you of any material changes
                by posting the new policy on this page and updating the "Last updated" date. Your continued use
                of our services after such changes constitutes your acceptance of the updated policy.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-foreground">
                7. Contact Us
              </h2>
              <p className="mt-4 text-sm leading-relaxed text-muted-foreground">
                If you have any questions about this privacy policy or our data practices, please contact us
                through our platform's support channels or at the contact information provided on our website.
              </p>
            </section>
          </div>
        </div>
      </main>
      <SiteFooter />
    </div>
  );
}
