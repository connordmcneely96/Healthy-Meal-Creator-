import { SiteHeader } from "@/components/site-header";

export default function HomePage() {
  return (
    <main className="mx-auto flex min-h-screen w-full max-w-5xl flex-col items-center gap-12 px-6 pb-16">
      <SiteHeader />
      <section className="grid w-full gap-6 rounded-xl border border-border bg-card/40 p-6 text-left shadow-sm backdrop-blur">
        <h2 className="text-2xl font-semibold">Local developer experience</h2>
        <p className="text-muted-foreground">
          Run <code>pnpm dev</code> from the <code>/web</code> directory for the Next.js app,
          or <code>streamlit run app/Home.py</code> for the Python tool. GitHub Codespaces
          handles both automatically thanks to the devcontainer setup.
        </p>
      </section>
      <section className="grid w-full gap-6 rounded-xl border border-border bg-card/40 p-6 text-left shadow-sm backdrop-blur">
        <h2 className="text-2xl font-semibold">Deploy to Vercel</h2>
        <p className="text-muted-foreground">
          Point Vercel to the <code>web</code> directory, copy your environment variables, and
          you&apos;re live with modern infrastructure defaults.
        </p>
      </section>
    </main>
  );
}
