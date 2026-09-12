import { createFileRoute } from "@tanstack/react-router";
import { Nav } from "@/components/landing/Nav";
import { SiteFooter } from "@/components/landing/SiteFooter";

const title = "Terms of Service — CarbonLoop";
const description = "CarbonLoop's terms of service and user agreement.";

export const Route = createFileRoute("/terms-of-service")({
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
  component: TermsOfService,
});

function TermsOfService() {
  return (
    <div className="min-h-screen bg-background">
      <Nav />
      <main className="mx-auto max-w-[1400px] px-5 py-24 sm:px-8 lg:px-14">
        <div className="max-w-3xl">
          <h1 className="text-4xl font-bold tracking-tight text-foreground sm:text-5xl">
            Terms of Service
          </h1>
          <p className="mt-4 text-sm text-muted-foreground">
            Last updated: {new Date().toLocaleDateString()}
          </p>

          <div className="mt-12 space-y-8">
            <section>
              <h2 className="text-2xl font-semibold text-foreground">
                1. Acceptance of Terms
              </h2>
              <p className="mt-4 text-sm leading-relaxed text-muted-foreground">
                By accessing or using CarbonLoop's services, you agree to be bound by these Terms of Service.
                If you do not agree to these terms, please do not use our services. CarbonLoop reserves the right
                to modify these terms at any time, and your continued use of the service constitutes acceptance of
                any changes.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-foreground">
                2. Description of Service
              </h2>
              <p className="mt-4 text-sm leading-relaxed text-muted-foreground">
                CarbonLoop provides industrial emission leak-point detection and circular alternative recommendation
                services for manufacturing facilities. Our platform analyzes factory emissions data, identifies
                leak points, and recommends sustainable alternatives with estimated cost, savings, and CO₂ reduction metrics.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-foreground">
                3. User Responsibilities
              </h2>
              <p className="mt-4 text-sm leading-relaxed text-muted-foreground">
                Users are responsible for maintaining the confidentiality of their account credentials and for all
                activities that occur under their account. You agree to provide accurate and complete information
                when registering for our services and to update this information to keep it accurate. You must not
                use our services for any illegal or unauthorized purpose.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-foreground">
                4. Intellectual Property
              </h2>
              <p className="mt-4 text-sm leading-relaxed text-muted-foreground">
                All content, features, and functionality of the CarbonLoop platform, including but not limited to
                text, graphics, logos, and software, are the exclusive property of CarbonLoop and are protected by
                international copyright, trademark, and other intellectual property laws. You may not reproduce,
                modify, distribute, or create derivative works of our content without our express written permission.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-foreground">
                5. Data Accuracy and Disclaimers
              </h2>
              <p className="mt-4 text-sm leading-relaxed text-muted-foreground">
                While CarbonLoop strives to provide accurate and useful emissions data and recommendations, we make
                no warranties or representations about the completeness, accuracy, reliability, or suitability of
                the information provided. Our recommendations are estimates based on available data and should be
                used as guidance rather than definitive advice.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-foreground">
                6. Limitation of Liability
              </h2>
              <p className="mt-4 text-sm leading-relaxed text-muted-foreground">
                To the fullest extent permitted by law, CarbonLoop shall not be liable for any indirect, incidental,
                special, consequential, or punitive damages, including without limitation, loss of profits, data,
                use, goodwill, or other intangible losses, resulting from your access to or use of or inability to
                access or use the service.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-foreground">
                7. Termination
              </h2>
              <p className="mt-4 text-sm leading-relaxed text-muted-foreground">
                CarbonLoop reserves the right to terminate or suspend your account and access to the service at any
                time, without prior notice or liability, for any reason whatsoever, including without limitation if
                you breach these Terms of Service. Upon termination, your right to use the service will immediately cease.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-foreground">
                8. Governing Law
              </h2>
              <p className="mt-4 text-sm leading-relaxed text-muted-foreground">
                These Terms of Service shall be governed by and construed in accordance with the laws of the
                jurisdiction in which CarbonLoop is headquartered, without regard to its conflict of law provisions.
                Any disputes arising from these terms shall be resolved in the competent courts of that jurisdiction.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-foreground">
                9. Changes to Terms
              </h2>
              <p className="mt-4 text-sm leading-relaxed text-muted-foreground">
                CarbonLoop reserves the right to modify these terms at any time. We will notify users of any material
                changes by posting the updated terms on this page and updating the "Last updated" date. Your continued
                use of the service after such modifications constitutes your acceptance of the new terms.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-foreground">
                10. Contact Information
              </h2>
              <p className="mt-4 text-sm leading-relaxed text-muted-foreground">
                If you have any questions about these Terms of Service, please contact us through our platform's
                support channels or at the contact information provided on our website.
              </p>
            </section>
          </div>
        </div>
      </main>
      <SiteFooter />
    </div>
  );
}
